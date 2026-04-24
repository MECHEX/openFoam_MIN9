"""
analyse_run001.py
-----------------
Full post-processing for V4b_3D run001 (Re=100, steady flow, Ri=1.26).

Analyses performed
------------------
1. POD          — Ux, Uy, T on midspan z=6mm slice (10 snapshots, t=0.5..5 s)
2. EPOD         — Ux temporal modes -> T reconstruction, and T -> Ux
3. Transfer Entropy — Ux ↔ T causality from 4 wake probes (500 pts, DT=0.01 s)
4. Spectral coherence — Welch cross-spectral Ux–T coherence on probes

Physical note
-------------
Re=100 gives STEADY flow (Ri=1.26). The 10 VTP snapshots capture spin-up
from a uniform IC to the steady wake. All modal analyses therefore describe
the CONVERGENCE structure, not vortex-shedding modes. Results serve as:
  (a) pipeline validation for future periodic-flow runs (Re > Re_crit)
  (b) causality structure of the thermal field even in steady convection

Outputs are written to this script's directory:
  pod/Ux/, pod/Uy/, pod/T/
  epod/Ux_to_T/, epod/T_to_Ux/
  transfer_entropy/
  spectral_coherence/
  analysis_summary.json
"""

from __future__ import annotations

import base64
import csv
import json
import re
import struct
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.signal import coherence as scipy_coherence, welch

# ── paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
VTP_ROOT  = Path(r"\\wsl.localhost\Ubuntu\home\kik\of_runs\V4b_3D_run001\postProcessing\midspan_slice")
PROBE_DIR = Path(r"\\wsl.localhost\Ubuntu\home\kik\of_runs\V4b_3D_run001\postProcessing\probes_wake\0")

# Physical constants for this run
RE    = 100
D     = 0.012
UIN   = 0.12633
T_IN  = 293.15
T_HOT = 343.15
DT_PROBE = 0.01   # probe write interval [s]


# ══════════════════════════════════════════════════════════════════════════════
# I/O helpers
# ══════════════════════════════════════════════════════════════════════════════

def _ensure(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _fmt(v) -> str:
    return f"{float(v):.10g}"


def _write_csv(path: Path, headers: list[str], rows) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for row in rows:
            w.writerow([_fmt(v) if isinstance(v, (float, np.floating)) else v for v in row])


# ══════════════════════════════════════════════════════════════════════════════
# VTP reader
# ══════════════════════════════════════════════════════════════════════════════

def _decode_vtp_bin(text: str, dtype) -> np.ndarray:
    raw = base64.b64decode(text.strip())
    n_bytes = struct.unpack_from("<I", raw, 0)[0]
    return np.frombuffer(raw[4: 4 + n_bytes], dtype=dtype)


def _read_vtp(path: Path) -> dict[str, np.ndarray]:
    tree = ET.parse(path)
    piece = tree.getroot().find(".//Piece")
    pts = _decode_vtp_bin(piece.find("Points/DataArray").text, np.float32).reshape(-1, 3)
    out = {"x": pts[:, 0].astype(float), "y": pts[:, 1].astype(float)}
    for da in piece.findall("PointData/DataArray"):
        name = da.attrib["Name"]
        nc = int(da.attrib.get("NumberOfComponents", "1"))
        arr = _decode_vtp_bin(da.text, np.float32).astype(float)
        if nc == 3:
            arr = arr.reshape(-1, 3)
            for i, c in enumerate("xyz"):
                out[f"{name}{c}"] = arr[:, i]
        else:
            out[name] = arr
    return out


def load_vtp_snapshots() -> tuple[list[float], dict[str, np.ndarray]]:
    dirs = sorted([d for d in VTP_ROOT.iterdir() if d.is_dir()],
                  key=lambda d: float(d.name))
    times, cols = [], {}
    coords = None
    for d in dirs:
        vtp = d / "midspan.vtp"
        if not vtp.exists():
            continue
        s = _read_vtp(vtp)
        times.append(float(d.name))
        if coords is None:
            coords = {"x": s["x"], "y": s["y"]}
        for k in ("Ux", "Uy", "T", "p_rgh"):
            cols.setdefault(k, []).append(s.get(k, np.zeros_like(s["x"])))
    fields = {**coords}
    for k, v in cols.items():
        fields[k] = np.column_stack(v)
    return times, fields


# ══════════════════════════════════════════════════════════════════════════════
# Probe reader
# ══════════════════════════════════════════════════════════════════════════════

def _parse_tuple(s: str) -> list[float]:
    return [float(x) for x in s.strip("()").split()]


def load_probes() -> dict[str, np.ndarray]:
    """Returns dict: time, Ux_p0..p3, Uy_p0..p3, T_p0..p3"""
    U_path = PROBE_DIR / "U"
    T_path = PROBE_DIR / "T"

    def read_vector_probe(path: Path):
        times, data = [], []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                continue
            parts = re.split(r"\s+", line.strip(), maxsplit=1)
            t = float(parts[0])
            tuples = re.findall(r"\([^)]+\)", parts[1])
            row = [_parse_tuple(tp) for tp in tuples]
            times.append(t)
            data.append(row)
        return np.array(times), np.array(data)   # (N,), (N, n_probe, 3)

    def read_scalar_probe(path: Path):
        times, data = [], []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                continue
            vals = line.split()
            times.append(float(vals[0]))
            data.append([float(v) for v in vals[1:]])
        return np.array(times), np.array(data)   # (N,), (N, n_probe)

    t, U = read_vector_probe(U_path)
    _, T = read_scalar_probe(T_path)

    out = {"time": t}
    for p in range(U.shape[1]):
        out[f"Ux_p{p}"] = U[:, p, 0]
        out[f"Uy_p{p}"] = U[:, p, 1]
        out[f"T_p{p}"]  = T[:, p]
    return out


# ══════════════════════════════════════════════════════════════════════════════
# POD core (method of snapshots)
# ══════════════════════════════════════════════════════════════════════════════

def compute_pod(X: np.ndarray) -> dict:
    """X: (N_space, N_time). Returns POD dict."""
    mean = X.mean(axis=1, keepdims=True)
    Xc = X - mean
    C = Xc.T @ Xc
    eigvals, V = np.linalg.eigh(C)
    idx = np.argsort(eigvals)[::-1]
    eigvals, V = eigvals[idx], V[:, idx]
    sigma = np.sqrt(np.maximum(eigvals, 0.0))
    tol = sigma[0] * 1e-10 if sigma[0] > 0 else 1e-14
    n = int(np.sum(sigma > tol))
    spatial = Xc @ V[:, :n] / sigma[:n]
    temporal = np.diag(sigma[:n]) @ V[:, :n].T
    # deterministic sign
    for i in range(n):
        piv = int(np.argmax(np.abs(spatial[:, i])))
        if spatial[piv, i] < 0:
            spatial[:, i] *= -1
            temporal[i, :] *= -1
    ef = eigvals[:n] / eigvals[:n].sum() if eigvals[:n].sum() > 0 else eigvals[:n]
    return {"mean": mean[:, 0], "Xc": Xc, "spatial": spatial,
            "sv": sigma[:n], "temporal": temporal,
            "ef": ef, "cum_ef": np.cumsum(ef), "n": n}


def write_pod(pod: dict, times: list[float], x, y, field: str, out_dir: Path):
    _ensure(out_dir)
    _write_csv(out_dir / "singular_values.csv",
               ["mode", "singular_value", "energy_pct", "cum_energy_pct"],
               [(i+1, pod["sv"][i], pod["ef"][i]*100, pod["cum_ef"][i]*100)
                for i in range(pod["n"])])
    _write_csv(out_dir / "temporal_coefficients.csv",
               ["mode"] + [f"t={t}" for t in times],
               [(i+1, *pod["temporal"][i]) for i in range(pod["n"])])
    # spatial modes + coords in one file
    _write_csv(out_dir / "spatial_modes.csv",
               ["x", "y", "mean"] + [f"mode_{i+1}" for i in range(pod["n"])],
               [(x[p], y[p], pod["mean"][p], *pod["spatial"][p])
                for p in range(len(x))])
    result = {
        "field": field, "n_points": int(x.shape[0]),
        "times": times, "n_active_modes": pod["n"],
        "singular_values": pod["sv"].tolist(),
        "energy_fraction": pod["ef"].tolist(),
        "note": "run001 steady flow — modes describe spin-up transient, not shedding"
    }
    (out_dir / "pod_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"  POD {field}: {pod['n']} modes. Mode-1={pod['ef'][0]*100:.1f}%, Mode-2={pod['ef'][1]*100:.1f}%")
    return pod


# ══════════════════════════════════════════════════════════════════════════════
# EPOD
# ══════════════════════════════════════════════════════════════════════════════

def compute_epod(source_pod: dict, target_Xc: np.ndarray,
                 target_mean: np.ndarray, times: list[float],
                 x, y, src_name: str, tgt_name: str, out_dir: Path):
    """Extended POD: project target fluctuations onto source temporal modes."""
    _ensure(out_dir)
    A = source_pod["temporal"]        # (n_src_modes, N_t)
    Yc = target_Xc                    # (N_tgt_pts, N_t)

    # Gram matrix and extended modes
    G = A @ A.T                       # (n_src, n_src)
    Psi = Yc @ A.T @ np.linalg.pinv(G)   # (N_tgt_pts, n_src)

    # Reconstruction metrics
    Yc_norm = float(np.linalg.norm(Yc))
    metrics = []
    for k in range(1, source_pod["n"] + 1):
        Yc_hat = Psi[:, :k] @ A[:k, :]
        err = float(np.linalg.norm(Yc - Yc_hat))
        rel_err = err / Yc_norm if Yc_norm > 0 else 0.0
        cap = max(0.0, 1.0 - rel_err**2)
        metrics.append({"modes": k, "rel_error": rel_err, "captured_pct": cap * 100})

    # Sign convention
    for i in range(Psi.shape[1]):
        piv = int(np.argmax(np.abs(Psi[:, i])))
        if Psi[piv, i] < 0:
            Psi[:, i] *= -1

    # Write
    _write_csv(out_dir / "reconstruction_metrics.csv",
               ["n_modes", "rel_error", "captured_target_energy_pct"],
               [(m["modes"], m["rel_error"], m["captured_pct"]) for m in metrics])
    _write_csv(out_dir / "extended_modes.csv",
               ["x", "y"] + [f"emode_{i+1}" for i in range(Psi.shape[1])],
               [(x[p], y[p], *Psi[p]) for p in range(len(x))])

    best = metrics[-1]
    result = {
        "source": src_name, "target": tgt_name,
        "n_source_modes": source_pod["n"],
        "formula": "Psi = Y_c A^T (A A^T)^-1",
        "all_modes_rel_error": best["rel_error"],
        "all_modes_captured_pct": best["captured_pct"],
        "metrics": metrics,
        "note": "run001: high captured % expected — Ux and T covary during spin-up"
    }
    (out_dir / "epod_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"  EPOD {src_name}->{tgt_name}: {source_pod['n']} modes, "
          f"captured={best['captured_pct']:.1f}%, rel_err={best['rel_error']:.3e}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# Transfer Entropy
# ══════════════════════════════════════════════════════════════════════════════

N_BINS = 5
N_SURR = 100
RNG_SEED = 20260415


def _quantize(x: np.ndarray, bins: int) -> np.ndarray:
    edges = np.percentile(x, np.linspace(0, 100, bins + 1))
    edges = np.unique(edges)
    if len(edges) <= 2:
        return np.zeros(len(x), dtype=int)
    return np.searchsorted(edges[1:-1], x, side="right").astype(int)


def _te(source: np.ndarray, target: np.ndarray, lag: int, bins=N_BINS) -> float:
    """TE_{X->Y}(lag) = I(Y_t ; X_{t-lag} | Y_{t-1}) in bits."""
    xs = _quantize(source, bins)
    yt = _quantize(target, bins)
    jfpp: Counter = Counter()
    jpp: Counter = Counter()
    jfp: Counter = Counter()
    cp: Counter = Counter()
    for t in range(lag, len(xs)):
        yf, yp, xp = int(yt[t]), int(yt[t-1]), int(xs[t-lag])
        jfpp[(yf, yp, xp)] += 1
        jpp[(yp, xp)] += 1
        jfp[(yf, yp)] += 1
        cp[yp] += 1
    total = float(sum(jfpp.values()))
    te = 0.0
    for (yf, yp, xp), cnt in jfpp.items():
        denom = jpp[(yp, xp)] * jfp[(yf, yp)]
        num = cnt * cp[yp]
        if denom > 0 and num > 0:
            te += (cnt / total) * np.log2(num / denom)
    return float(max(te, 0.0))


def _te_curve(source, target, max_lag, rng):
    lags = np.arange(1, max_lag + 1)
    raw = np.zeros(len(lags))
    surr_mean = np.zeros(len(lags))
    surr_p95 = np.zeros(len(lags))
    for i, lag in enumerate(lags):
        raw[i] = _te(source, target, int(lag))
        sv = np.array([_te(rng.permutation(source), target, int(lag))
                       for _ in range(N_SURR)])
        surr_mean[i] = sv.mean()
        surr_p95[i] = np.percentile(sv, 95)
    excess = np.maximum(raw - surr_mean, 0.0)
    return {"lag": lags, "te": raw, "surr_mean": surr_mean,
            "surr_p95": surr_p95, "excess": excess}


def run_transfer_entropy(probes: dict, out_dir: Path):
    _ensure(out_dir)
    rng = np.random.default_rng(RNG_SEED)
    t = probes["time"]

    # Use full signal (500 pts). Normalise to zero-mean unit-std.
    def norm(x):
        s = x.std()
        return (x - x.mean()) / s if s > 0 else x * 0.0

    max_lag = 40          # 0.4 s maximum lead time
    pairs = [
        ("Ux_p0", "T_p0", "Ux_1D->T_1D"),
        ("T_p0",  "Ux_p0", "T_1D->Ux_1D"),
        ("Ux_p2", "T_p2", "Ux_3D->T_3D"),
        ("T_p2",  "Ux_p2", "T_3D->Ux_3D"),
        ("Uy_p0", "T_p0", "Uy_1D->T_1D"),   # buoyancy channel
    ]

    all_rows = []
    summary = []
    for src_key, tgt_key, label in pairs:
        src = norm(probes[src_key])
        tgt = norm(probes[tgt_key])
        print(f"  TE {label} ...", end=" ", flush=True)
        c = _te_curve(src, tgt, max_lag, rng)
        peak_i = int(np.argmax(c["excess"]))
        summary.append({
            "pair": label, "peak_lag_samples": int(c["lag"][peak_i]),
            "peak_lag_s": float(c["lag"][peak_i]) * DT_PROBE,
            "te_bits": float(c["te"][peak_i]),
            "excess_te_bits": float(c["excess"][peak_i]),
            "surr_p95_bits": float(c["surr_p95"][peak_i]),
        })
        for i in range(len(c["lag"])):
            all_rows.append([label, int(c["lag"][i]),
                             float(c["lag"][i]) * DT_PROBE,
                             c["te"][i], c["surr_mean"][i],
                             c["surr_p95"][i], c["excess"][i]])
        print(f"peak lag={c['lag'][peak_i]} steps ({c['lag'][peak_i]*DT_PROBE:.2f}s), "
              f"excess={c['excess'][peak_i]:.4f} bits")

    _write_csv(out_dir / "te_curves.csv",
               ["pair", "lag_samples", "lag_s", "te_bits",
                "surr_mean_bits", "surr_p95_bits", "excess_te_bits"],
               all_rows)
    _write_csv(out_dir / "te_peak_summary.csv",
               ["pair", "peak_lag_samples", "peak_lag_s",
                "te_bits", "excess_te_bits", "surr_p95_bits"],
               [list(s.values()) for s in summary])
    (out_dir / "te_result.json").write_text(
        json.dumps({"pairs": summary,
                    "n_surrogates": N_SURR, "n_bins": N_BINS,
                    "max_lag_samples": max_lag, "dt_probe": DT_PROBE,
                    "note": ("run001 steady after t~1s. TE signal reflects spin-up "
                             "transient. Expected: Ux->T > T->Ux (advective causality).")},
                   indent=2), encoding="utf-8")
    return summary


# ══════════════════════════════════════════════════════════════════════════════
# Spectral Coherence
# ══════════════════════════════════════════════════════════════════════════════

def run_spectral_coherence(probes: dict, out_dir: Path):
    _ensure(out_dir)
    FS = 1.0 / DT_PROBE       # 100 Hz
    NPERSEG = 128              # ~7 Welch segments from 500 pts
    pairs = [
        ("Ux_p0", "T_p0", "probe_0_1D"),
        ("Ux_p1", "T_p1", "probe_1_2D"),
        ("Ux_p2", "T_p2", "probe_2_3D"),
        ("Uy_p0", "T_p0", "Uy_probe_0"),
    ]

    all_rows = []
    summary = []
    for src_key, tgt_key, label in pairs:
        src = probes[src_key] - probes[src_key].mean()
        tgt = probes[tgt_key] - probes[tgt_key].mean()
        freqs, coh = scipy_coherence(src, tgt, fs=FS, nperseg=NPERSEG)
        peak_i = int(np.argmax(coh))
        summary.append({
            "pair": label,
            "peak_freq_Hz": float(freqs[peak_i]),
            "peak_coherence": float(coh[peak_i]),
        })
        for i in range(len(freqs)):
            all_rows.append([label, float(freqs[i]), float(coh[i])])
        print(f"  Coherence {label}: peak f={freqs[peak_i]:.2f} Hz, "
              f"coh={coh[peak_i]:.3f}")

    _write_csv(out_dir / "coherence_curves.csv",
               ["pair", "freq_Hz", "coherence"], all_rows)
    _write_csv(out_dir / "coherence_peak_summary.csv",
               ["pair", "peak_freq_Hz", "peak_coherence"],
               [list(s.values()) for s in summary])
    (out_dir / "coherence_result.json").write_text(
        json.dumps({"pairs": summary,
                    "fs_Hz": FS, "nperseg": NPERSEG,
                    "note": ("Welch method. run001 steady -> coherence reflects "
                             "IC transient. No shedding frequency expected.")},
                   indent=2), encoding="utf-8")

    # power spectra for reference
    psd_rows = []
    for key in ("Ux_p0", "Uy_p0", "T_p0"):
        sig = probes[key] - probes[key].mean()
        f, psd = welch(sig, fs=FS, nperseg=NPERSEG)
        for i in range(len(f)):
            psd_rows.append([key, float(f[i]), float(psd[i])])
    _write_csv(out_dir / "power_spectra.csv",
               ["signal", "freq_Hz", "psd"], psd_rows)
    return summary


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("V4b_3D run001 — full analysis (Re=100, steady)")
    print("=" * 60)

    # ── 1. Load VTP snapshots ──────────────────────────────────────
    print("\n[1/5] Loading VTP midspan snapshots ...")
    times, fields = load_vtp_snapshots()
    x, y = fields["x"], fields["y"]
    N_pts, N_t = fields["Ux"].shape
    print(f"  {N_t} snapshots × {N_pts} points. t = {times}")

    # ── 2. POD ────────────────────────────────────────────────────
    print("\n[2/5] POD (Ux, Uy, T) ...")
    pods = {}
    for field_name in ("Ux", "Uy", "T"):
        X = fields[field_name]
        pod = compute_pod(X)
        write_pod(pod, times, x, y, field_name,
                  SCRIPT_DIR / "pod" / field_name)
        pods[field_name] = pod

    # ── 3. EPOD ───────────────────────────────────────────────────
    print("\n[3/5] EPOD (Ux->T, T->Ux, Uy->T) ...")
    epod_results = []
    for src, tgt in [("Ux", "T"), ("T", "Ux"), ("Uy", "T")]:
        res = compute_epod(
            pods[src], pods[tgt]["Xc"], pods[tgt]["mean"],
            times, x, y, src, tgt,
            SCRIPT_DIR / "epod" / f"{src}_to_{tgt}"
        )
        epod_results.append(res)

    # ── 4. Transfer Entropy ───────────────────────────────────────
    print("\n[4/5] Transfer Entropy on probe time series ...")
    probes = load_probes()
    te_summary = run_transfer_entropy(probes, SCRIPT_DIR / "transfer_entropy")

    # ── 5. Spectral Coherence ─────────────────────────────────────
    print("\n[5/5] Spectral Coherence (Ux–T, Welch) ...")
    coh_summary = run_spectral_coherence(probes, SCRIPT_DIR / "spectral_coherence")

    # ── Summary JSON ──────────────────────────────────────────────
    summary = {
        "run_id": "run001", "Re": RE, "flow_regime": "steady",
        "Ri": round(12576 / RE**2, 3),
        "pod": {f: {"n_modes": pods[f]["n"],
                    "mode1_energy_pct": round(pods[f]["ef"][0]*100, 2),
                    "mode2_energy_pct": round(pods[f]["ef"][1]*100, 2)}
                for f in ("Ux", "Uy", "T")},
        "epod": [{"source": r["source"], "target": r["target"],
                  "captured_pct": round(r["all_modes_captured_pct"], 1),
                  "rel_error": round(r["all_modes_rel_error"], 4)}
                 for r in epod_results],
        "transfer_entropy_peaks": te_summary,
        "spectral_coherence_peaks": coh_summary,
        "note": (
            "All analyses on STEADY run001. Modal structure reflects "
            "spin-up transient. For vortex-shedding POD/EPOD, run Re>Re_crit."
        )
    }
    (SCRIPT_DIR / "analysis_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"Done. Results in: {SCRIPT_DIR}")
    print("=" * 60)

    # Print key numbers
    print("\n  POD mode-1 energy: Ux={:.1f}%  Uy={:.1f}%  T={:.1f}%".format(
        pods["Ux"]["ef"][0]*100, pods["Uy"]["ef"][0]*100, pods["T"]["ef"][0]*100))
    te_fw = next(s for s in te_summary if "Ux_1D->T" in s["pair"])
    te_rv = next(s for s in te_summary if "T_1D->Ux" in s["pair"])
    print(f"  TE peak:  Ux->T = {te_fw['excess_te_bits']:.4f} bits  |  "
          f"T->Ux = {te_rv['excess_te_bits']:.4f} bits")
    direction = "Ux->T" if te_fw["excess_te_bits"] > te_rv["excess_te_bits"] else "T->Ux"
    print(f"  Dominant TE direction: {direction} (advective causality)")


if __name__ == "__main__":
    main()
