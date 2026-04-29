"""
Full modal post-processing for V4b_3D run003 (Re=200, periodic shedding).

Outputs are written next to this script:
  pod/Ux/, pod/Uy/, pod/T/
  epod/Ux_to_T/, epod/T_to_Ux/, epod/Uy_to_T/
  transfer_entropy/
  spectral_coherence/
  force_spectra/
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


SCRIPT_DIR = Path(__file__).resolve().parent
CASE_ROOT = Path(r"\\wsl.localhost\Ubuntu\home\kik\of_runs\V4b_3D_run003")
POST_ROOT = CASE_ROOT / "postProcessing"
VTP_ROOT = POST_ROOT / "midspan_slice"
PROBE_ROOT = POST_ROOT / "probes_wake"
FORCE_ROOT = POST_ROOT / "forces_tube"

RUN_ID = "run003"
RE = 200
D = 0.012
UIN = 0.25267
F_SHED_REF = 3.125
T_IN = 293.15
T_HOT = 343.15

N_BINS = 5
N_SURR = 100
RNG_SEED = 20260429


def _ensure(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _fmt(v) -> str:
    if isinstance(v, (float, np.floating)):
        return f"{float(v):.10g}"
    return str(v)


def _write_csv(path: Path, headers: list[str], rows) -> None:
    _ensure(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for row in rows:
            w.writerow([_fmt(v) for v in row])


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
    dirs = sorted([d for d in VTP_ROOT.iterdir() if d.is_dir()], key=lambda d: float(d.name))
    times, cols, coords = [], {}, None
    for d in dirs:
        vtp = d / "midspan.vtp"
        if not vtp.exists():
            continue
        snap = _read_vtp(vtp)
        times.append(float(d.name))
        if coords is None:
            coords = {"x": snap["x"], "y": snap["y"]}
        for key in ("Ux", "Uy", "T", "p_rgh"):
            cols.setdefault(key, []).append(snap.get(key, np.zeros_like(snap["x"])))
    if coords is None:
        raise FileNotFoundError(f"No midspan VTP snapshots found in {VTP_ROOT}")
    fields = {**coords}
    for key, values in cols.items():
        fields[key] = np.column_stack(values)
    return times, fields


def _parse_tuple(s: str) -> list[float]:
    return [float(x) for x in s.strip("()").split()]


def _time_dirs(root: Path) -> list[Path]:
    return sorted([d for d in root.iterdir() if d.is_dir()], key=lambda d: float(d.name))


def _dedupe_sort(times: list[float], rows: list) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(np.asarray(times))
    seen = set()
    out_t, out_rows = [], []
    for i in order:
        t = round(float(times[i]), 12)
        if t in seen:
            continue
        seen.add(t)
        out_t.append(float(times[i]))
        out_rows.append(rows[i])
    return np.asarray(out_t), np.asarray(out_rows)


def _read_vector_probe_segments(root: Path, name: str):
    times, data = [], []
    for d in _time_dirs(root):
        path = d / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            parts = re.split(r"\s+", line.strip(), maxsplit=1)
            tuples = re.findall(r"\([^)]+\)", parts[1])
            times.append(float(parts[0]))
            data.append([_parse_tuple(tp) for tp in tuples])
    return _dedupe_sort(times, data)


def _read_scalar_probe_segments(root: Path, name: str):
    times, data = [], []
    for d in _time_dirs(root):
        path = d / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            vals = line.split()
            times.append(float(vals[0]))
            data.append([float(v) for v in vals[1:]])
    return _dedupe_sort(times, data)


def load_probes() -> dict[str, np.ndarray]:
    t_u, U = _read_vector_probe_segments(PROBE_ROOT, "U")
    t_t, T = _read_scalar_probe_segments(PROBE_ROOT, "T")
    if len(t_u) != len(t_t) or np.max(np.abs(t_u - t_t)) > 1e-9:
        raise ValueError("Probe U and T time vectors do not match")
    out = {"time": t_u}
    for p in range(U.shape[1]):
        out[f"Ux_p{p}"] = U[:, p, 0]
        out[f"Uy_p{p}"] = U[:, p, 1]
        out[f"Uz_p{p}"] = U[:, p, 2]
        out[f"T_p{p}"] = T[:, p]
    return out


def load_force_coefficients() -> dict[str, np.ndarray] | None:
    times, rows = [], []
    for d in _time_dirs(FORCE_ROOT):
        path = d / "force.dat"
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            vals = [float(v) for v in line.replace("(", " ").replace(")", " ").split()]
            if len(vals) >= 10:
                times.append(vals[0])
                rows.append(vals[1:])
    if not times:
        return None
    t, arr = _dedupe_sort(times, rows)
    return {"time": t, "force_columns": arr}


def compute_pod(X: np.ndarray) -> dict:
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
    for i in range(n):
        piv = int(np.argmax(np.abs(spatial[:, i])))
        if spatial[piv, i] < 0:
            spatial[:, i] *= -1
            temporal[i, :] *= -1
    ef = eigvals[:n] / eigvals[:n].sum() if eigvals[:n].sum() > 0 else eigvals[:n]
    return {"mean": mean[:, 0], "Xc": Xc, "spatial": spatial, "sv": sigma[:n],
            "temporal": temporal, "ef": ef, "cum_ef": np.cumsum(ef), "n": n}


def write_pod(pod: dict, times: list[float], x, y, field: str, out_dir: Path):
    _write_csv(out_dir / "singular_values.csv",
               ["mode", "singular_value", "energy_pct", "cum_energy_pct"],
               [(i + 1, pod["sv"][i], pod["ef"][i] * 100, pod["cum_ef"][i] * 100)
                for i in range(pod["n"])])
    _write_csv(out_dir / "temporal_coefficients.csv",
               ["mode"] + [f"t={t:g}" for t in times],
               [(i + 1, *pod["temporal"][i]) for i in range(pod["n"])])
    _write_csv(out_dir / "spatial_modes.csv",
               ["x", "y", "mean"] + [f"mode_{i + 1}" for i in range(pod["n"])],
               [(x[p], y[p], pod["mean"][p], *pod["spatial"][p]) for p in range(len(x))])
    result = {
        "run_id": RUN_ID,
        "field": field,
        "n_points": int(x.shape[0]),
        "times": times,
        "n_active_modes": pod["n"],
        "singular_values": pod["sv"].tolist(),
        "energy_fraction": pod["ef"].tolist(),
        "note": "run003 Re=200 periodic shedding; POD uses available midspan snapshots t=0.5..6.5s.",
    }
    (out_dir / "pod_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"  POD {field}: {pod['n']} modes, mode1={pod['ef'][0]*100:.1f}%, mode2={pod['ef'][1]*100:.1f}%")


def compute_epod(source_pod: dict, target_Xc: np.ndarray, x, y, src_name: str, tgt_name: str, out_dir: Path):
    A = source_pod["temporal"]
    Yc = target_Xc
    G = A @ A.T
    Psi = Yc @ A.T @ np.linalg.pinv(G)
    norm = float(np.linalg.norm(Yc))
    metrics = []
    for k in range(1, source_pod["n"] + 1):
        Yhat = Psi[:, :k] @ A[:k, :]
        rel = float(np.linalg.norm(Yc - Yhat)) / norm if norm > 0 else 0.0
        metrics.append({"modes": k, "rel_error": rel, "captured_pct": max(0.0, 1.0 - rel**2) * 100})
    for i in range(Psi.shape[1]):
        piv = int(np.argmax(np.abs(Psi[:, i])))
        if Psi[piv, i] < 0:
            Psi[:, i] *= -1
    _write_csv(out_dir / "reconstruction_metrics.csv",
               ["n_modes", "rel_error", "captured_target_energy_pct"],
               [(m["modes"], m["rel_error"], m["captured_pct"]) for m in metrics])
    _write_csv(out_dir / "extended_modes.csv",
               ["x", "y"] + [f"emode_{i + 1}" for i in range(Psi.shape[1])],
               [(x[p], y[p], *Psi[p]) for p in range(len(x))])
    best = metrics[-1]
    result = {
        "run_id": RUN_ID,
        "source": src_name,
        "target": tgt_name,
        "n_source_modes": source_pod["n"],
        "formula": "Psi = Y_c A^T (A A^T)^-1",
        "all_modes_rel_error": best["rel_error"],
        "all_modes_captured_pct": best["captured_pct"],
        "metrics": metrics,
        "note": "run003 EPOD on synchronized midspan snapshots.",
    }
    (out_dir / "epod_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"  EPOD {src_name}->{tgt_name}: captured={best['captured_pct']:.1f}%, rel_err={best['rel_error']:.3e}")
    return result


def _quantize(x: np.ndarray, bins: int) -> np.ndarray:
    edges = np.percentile(x, np.linspace(0, 100, bins + 1))
    edges = np.unique(edges)
    if len(edges) <= 2:
        return np.zeros(len(x), dtype=int)
    return np.searchsorted(edges[1:-1], x, side="right").astype(int)


def _te(source: np.ndarray, target: np.ndarray, lag: int, bins=N_BINS) -> float:
    xs = _quantize(source, bins)
    yt = _quantize(target, bins)
    joint, yp_xp, yf_yp, yp_count = Counter(), Counter(), Counter(), Counter()
    for i in range(lag, len(xs)):
        yf, yp, xp = int(yt[i]), int(yt[i - 1]), int(xs[i - lag])
        joint[(yf, yp, xp)] += 1
        yp_xp[(yp, xp)] += 1
        yf_yp[(yf, yp)] += 1
        yp_count[yp] += 1
    total = float(sum(joint.values()))
    val = 0.0
    for (yf, yp, xp), count in joint.items():
        num = count * yp_count[yp]
        den = yp_xp[(yp, xp)] * yf_yp[(yf, yp)]
        if num > 0 and den > 0:
            val += (count / total) * np.log2(num / den)
    return float(max(val, 0.0))


def _norm(x):
    std = x.std()
    return (x - x.mean()) / std if std > 0 else x * 0.0


def run_transfer_entropy(probes: dict, out_dir: Path):
    rng = np.random.default_rng(RNG_SEED)
    t = probes["time"]
    dt = float(np.median(np.diff(t)))
    max_lag = min(120, max(10, len(t) // 8))
    pairs = [
        ("Ux_p0", "T_p0", "Ux_1D_to_T_1D"),
        ("T_p0", "Ux_p0", "T_1D_to_Ux_1D"),
        ("Ux_p2", "T_p2", "Ux_3D_to_T_3D"),
        ("T_p2", "Ux_p2", "T_3D_to_Ux_3D"),
        ("Uy_p0", "T_p0", "Uy_1D_to_T_1D"),
    ]
    all_rows, summary = [], []
    for src_key, tgt_key, label in pairs:
        src, tgt = _norm(probes[src_key]), _norm(probes[tgt_key])
        print(f"  TE {label} ...", end=" ", flush=True)
        lags = np.arange(1, max_lag + 1)
        te_vals, surr_mean, surr_p95 = [], [], []
        for lag in lags:
            raw = _te(src, tgt, int(lag))
            sur = np.array([_te(rng.permutation(src), tgt, int(lag)) for _ in range(N_SURR)])
            te_vals.append(raw)
            surr_mean.append(float(sur.mean()))
            surr_p95.append(float(np.percentile(sur, 95)))
        te_vals = np.asarray(te_vals)
        surr_mean = np.asarray(surr_mean)
        surr_p95 = np.asarray(surr_p95)
        excess = np.maximum(te_vals - surr_mean, 0.0)
        peak = int(np.argmax(excess))
        row = {
            "pair": label,
            "peak_lag_samples": int(lags[peak]),
            "peak_lag_s": float(lags[peak] * dt),
            "te_bits": float(te_vals[peak]),
            "excess_te_bits": float(excess[peak]),
            "surr_p95_bits": float(surr_p95[peak]),
        }
        summary.append(row)
        for i, lag in enumerate(lags):
            all_rows.append([label, int(lag), float(lag * dt), te_vals[i], surr_mean[i], surr_p95[i], excess[i]])
        print(f"peak lag={row['peak_lag_s']:.3f}s, excess={row['excess_te_bits']:.4f} bits")
    _write_csv(out_dir / "te_curves.csv",
               ["pair", "lag_samples", "lag_s", "te_bits", "surr_mean_bits", "surr_p95_bits", "excess_te_bits"],
               all_rows)
    _write_csv(out_dir / "te_peak_summary.csv",
               ["pair", "peak_lag_samples", "peak_lag_s", "te_bits", "excess_te_bits", "surr_p95_bits"],
               [list(row.values()) for row in summary])
    (out_dir / "te_result.json").write_text(json.dumps({
        "run_id": RUN_ID,
        "pairs": summary,
        "n_surrogates": N_SURR,
        "n_bins": N_BINS,
        "max_lag_samples": max_lag,
        "dt_probe": dt,
        "note": "Quantile-discretized lagged TE with shuffled-source surrogate baseline.",
    }, indent=2), encoding="utf-8")
    return summary


def _peak_near(freqs, values, target, width):
    mask = (freqs >= target - width) & (freqs <= target + width)
    if not np.any(mask):
        idx = int(np.argmin(np.abs(freqs - target)))
        return idx
    candidates = np.where(mask)[0]
    return int(candidates[np.argmax(values[candidates])])


def run_spectral_coherence(probes: dict, pods: dict, out_dir: Path):
    t = probes["time"]
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    nperseg = min(512, max(64, len(t) // 4))
    probe_pairs = [
        ("Ux_p0", "T_p0", "probe_0_1D"),
        ("Ux_p1", "T_p1", "probe_1_2D"),
        ("Ux_p2", "T_p2", "probe_2_3D"),
        ("Uy_p0", "T_p0", "Uy_probe_0"),
    ]
    rows, summary = [], []
    for src_key, tgt_key, label in probe_pairs:
        src = probes[src_key] - probes[src_key].mean()
        tgt = probes[tgt_key] - probes[tgt_key].mean()
        freqs, coh = scipy_coherence(src, tgt, fs=fs, nperseg=nperseg)
        peak = _peak_near(freqs, coh, F_SHED_REF, width=0.5)
        summary.append({"pair": label, "peak_freq_Hz": float(freqs[peak]), "peak_coherence": float(coh[peak])})
        for i in range(len(freqs)):
            rows.append([label, float(freqs[i]), float(coh[i])])
        print(f"  Coherence {label}: peak near shed f={freqs[peak]:.3f} Hz, coh={coh[peak]:.3f}")
    _write_csv(out_dir / "coherence_curves.csv", ["pair", "freq_Hz", "coherence"], rows)
    _write_csv(out_dir / "coherence_peak_summary.csv",
               ["pair", "peak_freq_Hz", "peak_coherence"], [list(s.values()) for s in summary])

    psd_rows = []
    for key in ("Ux_p0", "Uy_p0", "T_p0"):
        sig = probes[key] - probes[key].mean()
        f, psd = welch(sig, fs=fs, nperseg=nperseg)
        for i in range(len(f)):
            psd_rows.append([key, float(f[i]), float(psd[i])])
    _write_csv(out_dir / "power_spectra.csv", ["signal", "freq_Hz", "psd"], psd_rows)

    pod_rows = []
    for src, tgt in (("Ux", "T"), ("Uy", "T"), ("Ux", "Uy")):
        n = min(4, pods[src]["n"], pods[tgt]["n"])
        for i in range(n):
            a = pods[src]["temporal"][i] - pods[src]["temporal"][i].mean()
            b = pods[tgt]["temporal"][i] - pods[tgt]["temporal"][i].mean()
            f, coh = scipy_coherence(a, b, fs=1.0 / np.median(np.diff(np.asarray(load_vtp_snapshots()[0]))),
                                     nperseg=min(len(a), 8))
            peak = int(np.argmax(coh))
            pod_rows.append([f"{src}_mode{i+1}_vs_{tgt}_mode{i+1}", float(f[peak]), float(coh[peak])])
    _write_csv(out_dir / "pod_pair_coherence.csv", ["pair", "peak_freq_Hz", "peak_coherence"], pod_rows)

    (out_dir / "coherence_result.json").write_text(json.dumps({
        "run_id": RUN_ID,
        "fs_Hz": fs,
        "nperseg": nperseg,
        "target_shedding_frequency_Hz": F_SHED_REF,
        "probe_pairs": summary,
        "pod_pair_coherence": [
            {"pair": r[0], "peak_freq_Hz": r[1], "peak_coherence": r[2]} for r in pod_rows
        ],
        "note": "Welch coherence on wake probes; probe peaks reported near the known shedding band.",
    }, indent=2), encoding="utf-8")
    return summary, pod_rows


def run_force_spectra(out_dir: Path):
    data = load_force_coefficients()
    if data is None:
        return None
    t = data["time"]
    arr = data["force_columns"]
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    nperseg = min(512, max(64, len(t) // 4))
    rows, summary = [], []
    labels = [f"force_col_{i+1}" for i in range(arr.shape[1])]
    for j, label in enumerate(labels):
        sig = arr[:, j] - arr[:, j].mean()
        f, psd = welch(sig, fs=fs, nperseg=nperseg)
        peak = _peak_near(f, psd, F_SHED_REF, width=0.5)
        summary.append([label, float(f[peak]), float(psd[peak])])
        for i in range(len(f)):
            rows.append([label, float(f[i]), float(psd[i])])
    _write_csv(out_dir / "force_power_spectra.csv", ["signal", "freq_Hz", "psd"], rows)
    _write_csv(out_dir / "force_peak_summary.csv", ["signal", "peak_freq_Hz", "peak_psd"], summary)
    (out_dir / "force_spectra_result.json").write_text(json.dumps({
        "run_id": RUN_ID,
        "fs_Hz": fs,
        "nperseg": nperseg,
        "target_shedding_frequency_Hz": F_SHED_REF,
        "peaks_near_shedding": [
            {"signal": r[0], "peak_freq_Hz": r[1], "peak_psd": r[2]} for r in summary
        ],
        "note": "Columns are raw OpenFOAM force.dat numeric columns after time.",
    }, indent=2), encoding="utf-8")
    return summary


def write_summary_md(summary: dict) -> None:
    lines = [
        "# V4b_3D run003 Modal Analysis",
        "",
        "Analyses executed on the available run003 postProcessing data in the same repo layout as run001.",
        "",
        "## Input Data",
        "",
        f"- Midspan snapshots: {summary['n_snapshots']} at t={summary['snapshot_times']}",
        f"- Probe samples: {summary['n_probe_samples']}, dt={summary['probe_dt_s']:.6g} s",
        f"- Target shedding frequency: {F_SHED_REF:.3f} Hz",
        "",
        "## POD Energy",
        "",
        "| Field | modes | mode 1 | mode 2 | cumulative 2 |",
        "|---|---:|---:|---:|---:|",
    ]
    for field, data in summary["pod"].items():
        lines.append(f"| {field} | {data['n_modes']} | {data['mode1_energy_pct']:.2f}% | "
                     f"{data['mode2_energy_pct']:.2f}% | {data['mode1_mode2_cum_pct']:.2f}% |")
    lines += ["", "## EPOD", "", "| Source -> target | captured target energy | rel. error |", "|---|---:|---:|"]
    for row in summary["epod"]:
        lines.append(f"| {row['source']} -> {row['target']} | {row['captured_pct']:.2f}% | {row['rel_error']:.4g} |")
    lines += ["", "## Spectral Coherence Near Shedding", "", "| Pair | peak f [Hz] | coherence |", "|---|---:|---:|"]
    for row in summary["spectral_coherence_peaks"]:
        lines.append(f"| {row['pair']} | {row['peak_freq_Hz']:.3f} | {row['peak_coherence']:.3f} |")
    lines += ["", "## Transfer Entropy Peaks", "", "| Pair | lag [s] | excess TE [bits] |", "|---|---:|---:|"]
    for row in summary["transfer_entropy_peaks"]:
        lines.append(f"| {row['pair']} | {row['peak_lag_s']:.4f} | {row['excess_te_bits']:.5f} |")
    lines += [
        "",
        "## Notes",
        "",
        "- POD/EPOD use 13 midspan snapshots, so they are useful exploratory results, not final publication-grade modal statistics.",
        "- Probe coherence and TE use the denser wake-probe time series and are better suited to identifying the shedding band.",
        "- Full final POD/EPOD should use a longer post-transient snapshot database with uniform sampling over many shedding cycles.",
        "",
    ]
    (SCRIPT_DIR / "modal_analysis_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    print("=" * 72)
    print("V4b_3D run003 full modal analysis")
    print("=" * 72)

    print("\n[1/6] Loading VTP midspan snapshots")
    times, fields = load_vtp_snapshots()
    x, y = fields["x"], fields["y"]
    print(f"  {len(times)} snapshots x {len(x)} points")

    print("\n[2/6] POD (Ux, Uy, T)")
    pods = {}
    for field_name in ("Ux", "Uy", "T"):
        pod = compute_pod(fields[field_name])
        write_pod(pod, times, x, y, field_name, SCRIPT_DIR / "pod" / field_name)
        pods[field_name] = pod

    print("\n[3/6] EPOD (Ux->T, T->Ux, Uy->T)")
    epod_results = []
    for src, tgt in (("Ux", "T"), ("T", "Ux"), ("Uy", "T")):
        epod_results.append(compute_epod(pods[src], pods[tgt]["Xc"], x, y, src, tgt,
                                         SCRIPT_DIR / "epod" / f"{src}_to_{tgt}"))

    print("\n[4/6] Loading probes + transfer entropy")
    probes = load_probes()
    te_summary = run_transfer_entropy(probes, SCRIPT_DIR / "transfer_entropy")

    print("\n[5/6] Spectral coherence")
    coherence_summary, pod_pair_coherence = run_spectral_coherence(probes, pods, SCRIPT_DIR / "spectral_coherence")

    print("\n[6/6] Force spectra")
    force_summary = run_force_spectra(SCRIPT_DIR / "force_spectra")

    dt_probe = float(np.median(np.diff(probes["time"])))
    summary = {
        "run_id": RUN_ID,
        "Re": RE,
        "flow_regime": "periodic",
        "n_snapshots": len(times),
        "snapshot_times": times,
        "n_probe_samples": int(len(probes["time"])),
        "probe_dt_s": dt_probe,
        "St_reference": F_SHED_REF * D / UIN,
        "pod": {
            f: {
                "n_modes": pods[f]["n"],
                "mode1_energy_pct": float(pods[f]["ef"][0] * 100),
                "mode2_energy_pct": float(pods[f]["ef"][1] * 100) if pods[f]["n"] > 1 else 0.0,
                "mode1_mode2_cum_pct": float(pods[f]["cum_ef"][min(1, pods[f]["n"] - 1)] * 100),
            }
            for f in ("Ux", "Uy", "T")
        },
        "epod": [
            {"source": r["source"], "target": r["target"],
             "captured_pct": float(r["all_modes_captured_pct"]),
             "rel_error": float(r["all_modes_rel_error"])}
            for r in epod_results
        ],
        "transfer_entropy_peaks": te_summary,
        "spectral_coherence_peaks": coherence_summary,
        "pod_pair_coherence": [
            {"pair": r[0], "peak_freq_Hz": r[1], "peak_coherence": r[2]} for r in pod_pair_coherence
        ],
        "force_spectra_peaks": force_summary,
        "note": "Exploratory run003 modal analysis using available partial-run data t<=6.505s.",
    }
    (SCRIPT_DIR / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_summary_md(summary)

    print("\n" + "=" * 72)
    print(f"Done. Results in: {SCRIPT_DIR}")
    print("=" * 72)
    print("POD mode-1 energy: Ux={:.1f}% Uy={:.1f}% T={:.1f}%".format(
        summary["pod"]["Ux"]["mode1_energy_pct"],
        summary["pod"]["Uy"]["mode1_energy_pct"],
        summary["pod"]["T"]["mode1_energy_pct"],
    ))


if __name__ == "__main__":
    main()
