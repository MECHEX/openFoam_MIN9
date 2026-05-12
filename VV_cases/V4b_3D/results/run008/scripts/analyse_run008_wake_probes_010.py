"""
Run008 wake-probe dynamics.

Layer 010:
- PSD of probe velocities,
- cross-correlation lag between probe U_y and Cl / Q_wall,
- lag from wake probes to outlet T_out,
- coherence ranking between probe U_y and local fin Nu_local(x).
"""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal


RUN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = RUN_DIR / "data" / "010"
FIG_DIR = RUN_DIR / "figures" / "010"

WINDOW = (2.0, 10.0)
F_SHED = 3.2787
F2_SHED = 2.0 * F_SHED


@dataclass
class Probe:
    index: int
    x: float
    y: float
    z: float


@dataclass
class ProbeMetric:
    probe: int
    x_m: float
    y_m: float
    z_m: float
    uy_rms: float
    uy_psd_peak_hz: float
    uy_psd_peak_power: float
    uy_psd_f1_power: float
    uy_psd_f2_power: float
    coh_uy_cl_f1: float
    coh_uy_qwall_f1: float
    lag_uy_to_cl_s: float
    corr_uy_cl: float
    lag_uy_to_qwall_s: float
    corr_uy_qwall: float
    lag_uy_to_tout_s: float
    corr_uy_tout: float
    lag_probeT_to_tout_s: float
    corr_probeT_tout: float


@dataclass
class LocalNuRank:
    probe: int
    probe_x_m: float
    probe_y_m: float
    side: str
    x_bin_m: float
    coherence_f1: float
    coherence_f2: float
    frequency_f1_hz: float
    frequency_f2_hz: float


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def resolve_case_dir() -> Path:
    candidates = [
        Path("/home/hexmachina/of_runs/V4b_3D_run008"),
        Path(r"\\wsl$\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run008"),
        Path(r"\\wsl$\Ubuntu\home\hexmachina\of_runs\V4b_3D_run008"),
    ]
    for path in candidates:
        if (path / "postProcessing" / "probes_wake" / "0" / "U").exists():
            return path
    raise FileNotFoundError("Cannot find run008 probes_wake")


CASE_DIR = resolve_case_dir()
POST_DIR = CASE_DIR / "postProcessing"
PROBE_DIR = POST_DIR / "probes_wake" / "0"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_csv_cols(path: Path) -> dict[str, np.ndarray]:
    cols: dict[str, list[float]] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for key, val in row.items():
                cols.setdefault(key, []).append(float(val))
    return {k: np.asarray(v, dtype=float) for k, v in cols.items()}


def parse_probe_header(path: Path) -> list[Probe]:
    probes = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.startswith("# Probe"):
                if line.startswith("# Time"):
                    break
                continue
            m = re.match(r"# Probe\s+(\d+)\s+\(([^)]+)\)", line.strip())
            if m:
                idx = int(m.group(1))
                xyz = [float(v) for v in m.group(2).split()]
                probes.append(Probe(idx, xyz[0], xyz[1], xyz[2]))
    return probes


def read_probe_u() -> tuple[list[Probe], np.ndarray, np.ndarray]:
    path = PROBE_DIR / "U"
    probes = parse_probe_header(path)
    rows = []
    vector_re = re.compile(r"\(([^)]+)\)")
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split(None, 1)
            if len(parts) != 2:
                continue
            t = float(parts[0])
            vecs = []
            for m in vector_re.finditer(parts[1]):
                vecs.append([float(v) for v in m.group(1).split()])
            if len(vecs) == len(probes):
                rows.append((t, vecs))
    time = np.asarray([r[0] for r in rows], dtype=float)
    data = np.asarray([r[1] for r in rows], dtype=float)
    return probes, time, data


def read_probe_scalar(name: str, n_probes: int) -> tuple[np.ndarray, np.ndarray]:
    rows = []
    with (PROBE_DIR / name).open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            vals = [float(v) for v in stripped.split()]
            if len(vals) >= n_probes + 1:
                rows.append(vals[: n_probes + 1])
    arr = np.asarray(rows, dtype=float)
    return arr[:, 0], arr[:, 1:]


def read_force_coeffs(time: np.ndarray) -> dict[str, np.ndarray]:
    rows = []
    with (POST_DIR / "forceCoeffs" / "0" / "forceCoeffs.dat").open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            vals = [float(x) for x in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", stripped)]
            if len(vals) >= 5:
                rows.append(vals)
    arr = np.asarray(rows, dtype=float)
    return {"Cd": np.interp(time, arr[:, 0], arr[:, 2]), "Cl": np.interp(time, arr[:, 0], arr[:, 3]), "Cm": np.interp(time, arr[:, 0], arr[:, 4])}


def read_heat(time: np.ndarray) -> dict[str, np.ndarray]:
    cols = read_csv_cols(RUN_DIR / "data" / "003" / "run008_003_heat_balance_timeseries.csv")
    return {
        "Q_wall": np.interp(time, cols["time"], cols["Q_wall"]),
        "Q_tube": np.interp(time, cols["time"], cols["Q_tube"]),
        "Q_fins": np.interp(time, cols["time"], cols["Q_fins"]),
        "T_out": np.interp(time, cols["time"], cols["T_out"]),
        "Nu_tube": np.interp(time, cols["time"], cols["Nu_tube_wall"]),
        "Nu_fins": np.interp(time, cols["time"], cols["Nu_fins_wall"]),
    }


def demean(x: np.ndarray) -> np.ndarray:
    return x - np.nanmean(x)


def nearest_value(freq: np.ndarray, values: np.ndarray, target: float) -> tuple[float, float]:
    idx = int(np.argmin(np.abs(freq - target)))
    return float(freq[idx]), float(values[idx])


def psd_metrics(time: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float, float]:
    fs = 1.0 / float(np.median(np.diff(time)))
    nperseg = min(512, len(y))
    f, pxx = signal.welch(demean(y), fs=fs, nperseg=nperseg, noverlap=min(nperseg // 2, len(y) // 2))
    band = (f >= 1.0) & (f <= 12.0)
    peak_idx = np.where(band)[0][int(np.argmax(pxx[band]))]
    _, p1 = nearest_value(f, pxx, F_SHED)
    _, p2 = nearest_value(f, pxx, F2_SHED)
    return float(f[peak_idx]), float(pxx[peak_idx]), p1, p2, float(np.sqrt(np.nanmean(demean(y) ** 2)))


def coherence_at(time: np.ndarray, x: np.ndarray, y: np.ndarray, freq: float) -> tuple[float, float]:
    fs = 1.0 / float(np.median(np.diff(time)))
    valid = np.isfinite(x) & np.isfinite(y)
    x0 = demean(x[valid])
    y0 = demean(y[valid])
    nperseg = min(512, len(x0))
    f, cxy = signal.coherence(x0, y0, fs=fs, nperseg=nperseg, noverlap=min(nperseg // 2, len(x0) // 2))
    return nearest_value(f, cxy, freq)


def xcorr_lag(time: np.ndarray, source: np.ndarray, target: np.ndarray, max_lag_s: float = 1.5) -> tuple[float, float]:
    valid = np.isfinite(source) & np.isfinite(target)
    x = demean(source[valid])
    y = demean(target[valid])
    if len(x) < 16 or np.linalg.norm(x) == 0 or np.linalg.norm(y) == 0:
        return float("nan"), float("nan")
    cc = np.correlate(y / np.linalg.norm(y), x / np.linalg.norm(x), mode="full")
    lags = np.arange(-len(x) + 1, len(x))
    dt = float(np.median(np.diff(time)))
    keep = np.abs(lags * dt) <= max_lag_s
    sub = cc[keep]
    sub_lags = lags[keep]
    i = int(np.argmax(np.abs(sub)))
    return float(sub_lags[i] * dt), float(sub[i])


def load_fin_nu(time: np.ndarray) -> tuple[np.ndarray, dict[str, np.ndarray], dict[str, np.ndarray]]:
    data = np.load(RUN_DIR / "data" / "005" / "run008_005_fin_nu_arrays.npz")
    t_src = data["times"]
    x = data["x_centers"]
    out = {}
    valid = {}
    for side, key, vkey in [("fin_z_min", "min_series", "valid_min"), ("fin_z_max", "max_series", "valid_max")]:
        arr = np.asarray(data[key], dtype=float)
        out[side] = np.asarray([np.interp(time, t_src, arr[:, i]) for i in range(arr.shape[1])]).T
        valid[side] = np.asarray(data[vkey], dtype=bool)
    return x, out, valid


def plot_probe_layout(probes: list[Probe], metrics: list[ProbeMetric]) -> None:
    metric_by_probe = {m.probe: m for m in metrics}
    fig, ax = plt.subplots(figsize=(7, 5))
    values = np.asarray([metric_by_probe[p.index].coh_uy_cl_f1 for p in probes])
    sc = ax.scatter([p.x * 1000 for p in probes], [p.y * 1000 for p in probes], c=values, s=90, cmap="viridis", vmin=0, vmax=1)
    for p in probes:
        ax.text(p.x * 1000 + 0.8, p.y * 1000 + 0.3, str(p.index), fontsize=8)
    ax.axhline(0, color="0.7", lw=0.8)
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_title("Wake probe layout colored by coherence(Uy, Cl) near f_shed")
    ax.set_aspect("equal", adjustable="box")
    fig.colorbar(sc, ax=ax, label="coherence")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_010_probe_layout_coherence.png", dpi=180)
    plt.close(fig)


def plot_psd(time: np.ndarray, u: np.ndarray, probes: list[Probe]) -> None:
    fs = 1.0 / float(np.median(np.diff(time)))
    fig, ax = plt.subplots(figsize=(10, 6))
    for p in probes:
        uy = u[:, p.index, 1]
        f, pxx = signal.welch(demean(uy), fs=fs, nperseg=min(512, len(uy)), noverlap=256)
        alpha = 0.9 if p.index in [0, 7, 10, 8, 11] else 0.35
        ax.semilogy(f, pxx, lw=1.0, alpha=alpha, label=f"P{p.index}" if alpha > 0.5 else None)
    ax.axvline(F_SHED, color="#9b2226", ls="--", lw=1, label="f_shed")
    ax.axvline(F2_SHED, color="#5f0f40", ls=":", lw=1, label="2f_shed")
    ax.set_xlim(0, 15)
    ax.set_xlabel("frequency [Hz]")
    ax.set_ylabel("PSD Uy")
    ax.set_title("Wake-probe Uy spectra")
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_010_probe_uy_psd.png", dpi=180)
    plt.close(fig)


def plot_lag_bars(metrics: list[ProbeMetric]) -> None:
    probes = [m.probe for m in metrics]
    x = np.arange(len(probes))
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    axes[0].bar(x - 0.2, [m.lag_uy_to_cl_s for m in metrics], width=0.2, label="Uy -> Cl")
    axes[0].bar(x, [m.lag_uy_to_qwall_s for m in metrics], width=0.2, label="Uy -> Q_wall")
    axes[0].bar(x + 0.2, [m.lag_uy_to_tout_s for m in metrics], width=0.2, label="Uy -> T_out")
    axes[0].axhline(0, color="0.5", lw=0.8)
    axes[0].set_ylabel("lag [s]")
    axes[0].set_title("Cross-correlation lags, positive = target lags probe")
    axes[0].legend()
    axes[1].plot(x, [m.corr_uy_cl for m in metrics], marker="o", label="corr Uy-Cl")
    axes[1].plot(x, [m.corr_uy_qwall for m in metrics], marker="o", label="corr Uy-Q_wall")
    axes[1].plot(x, [m.corr_uy_tout for m in metrics], marker="o", label="corr Uy-T_out")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([str(p) for p in probes])
    axes[1].set_xlabel("probe index")
    axes[1].set_ylabel("signed corr at best lag")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_010_probe_cross_correlation_lags.png", dpi=180)
    plt.close(fig)


def plot_local_nu_rank(ranks: list[LocalNuRank]) -> None:
    best = sorted(ranks, key=lambda r: r.coherence_f1, reverse=True)[:20]
    labels = [f"P{r.probe} {r.side} x={1000*r.x_bin_m:.1f}" for r in best]
    x = np.arange(len(best))
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(x, [r.coherence_f1 for r in best], label="f_shed")
    ax.scatter(x, [r.coherence_f2 for r in best], color="#9b2226", s=28, label="2f_shed")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("coherence")
    ax.set_title("Top probe Uy to local fin Nu_local(x) coherence")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_010_probe_to_local_nu_coherence_rank.png", dpi=180)
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    probes, t_u, u_all = read_probe_u()
    t_t, probe_t = read_probe_scalar("T", len(probes))
    mask = (t_u >= WINDOW[0] - 1e-12) & (t_u <= WINDOW[1] + 1e-12)
    time = t_u[mask]
    u = u_all[mask]
    probe_t_interp = np.asarray([np.interp(time, t_t, probe_t[:, i]) for i in range(len(probes))]).T
    force = read_force_coeffs(time)
    heat = read_heat(time)

    metrics: list[ProbeMetric] = []
    for p in probes:
        uy = u[:, p.index, 1]
        peak_f, peak_power, p1, p2, rms = psd_metrics(time, uy)
        _, coh_cl = coherence_at(time, uy, force["Cl"], F_SHED)
        _, coh_q = coherence_at(time, uy, heat["Q_wall"], F_SHED)
        lag_cl, corr_cl = xcorr_lag(time, uy, force["Cl"])
        lag_q, corr_q = xcorr_lag(time, uy, heat["Q_wall"])
        lag_tout, corr_tout = xcorr_lag(time, uy, heat["T_out"])
        lag_pt, corr_pt = xcorr_lag(time, probe_t_interp[:, p.index], heat["T_out"])
        metrics.append(
            ProbeMetric(
                probe=p.index,
                x_m=p.x,
                y_m=p.y,
                z_m=p.z,
                uy_rms=rms,
                uy_psd_peak_hz=peak_f,
                uy_psd_peak_power=peak_power,
                uy_psd_f1_power=p1,
                uy_psd_f2_power=p2,
                coh_uy_cl_f1=coh_cl,
                coh_uy_qwall_f1=coh_q,
                lag_uy_to_cl_s=lag_cl,
                corr_uy_cl=corr_cl,
                lag_uy_to_qwall_s=lag_q,
                corr_uy_qwall=corr_q,
                lag_uy_to_tout_s=lag_tout,
                corr_uy_tout=corr_tout,
                lag_probeT_to_tout_s=lag_pt,
                corr_probeT_tout=corr_pt,
            )
        )

    x_fin, fin_nu, fin_valid = load_fin_nu(time)
    ranks: list[LocalNuRank] = []
    for p in probes:
        uy = u[:, p.index, 1]
        for side in ["fin_z_min", "fin_z_max"]:
            valid_idx = np.where(fin_valid[side])[0]
            for j in valid_idx:
                f1, c1 = coherence_at(time, uy, fin_nu[side][:, j], F_SHED)
                f2, c2 = coherence_at(time, uy, fin_nu[side][:, j], F2_SHED)
                ranks.append(LocalNuRank(p.index, p.x, p.y, side, float(x_fin[j]), c1, c2, f1, f2))

    write_csv(DATA_DIR / "run008_010_probe_metrics.csv", [asdict(m) for m in metrics])
    write_csv(DATA_DIR / "run008_010_probe_local_nu_coherence_rank.csv", [asdict(r) for r in ranks])

    plot_probe_layout(probes, metrics)
    plot_psd(time, u, probes)
    plot_lag_bars(metrics)
    plot_local_nu_rank(ranks)

    best_cl = max(metrics, key=lambda m: m.coh_uy_cl_f1)
    best_q = max(metrics, key=lambda m: m.coh_uy_qwall_f1)
    best_nu_f1 = max(ranks, key=lambda r: r.coherence_f1)
    best_nu_f2 = max(ranks, key=lambda r: r.coherence_f2)
    strongest_uy = max(metrics, key=lambda m: m.uy_rms)
    summary = {
        "method": {
            "window_s": WINDOW,
            "n_probes": len(probes),
            "samples": len(time),
            "sampling_hz": float(1.0 / np.median(np.diff(time))),
            "case_dir": str(CASE_DIR),
            "lag_sign": "positive lag means target lags probe/source",
            "local_nu_source": "fin Nu_local(x,t) from layer 005",
        },
        "best_probe_coherence_uy_cl_f1": asdict(best_cl),
        "best_probe_coherence_uy_qwall_f1": asdict(best_q),
        "strongest_uy_rms_probe": asdict(strongest_uy),
        "best_probe_to_local_nu_f1": asdict(best_nu_f1),
        "best_probe_to_local_nu_f2": asdict(best_nu_f2),
    }
    (DATA_DIR / "run008_010_wake_probes_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    top_metrics = sorted(metrics, key=lambda m: m.coh_uy_cl_f1, reverse=True)[:6]
    top_nu = sorted(ranks, key=lambda r: r.coherence_f1, reverse=True)[:8]
    lines = [
        "# V4b_3D run008 wake probes and wake dynamics",
        "",
        "Wake-probe analysis links local wake velocity/temperature signals with lift, wall heat transfer, outlet temperature, and local fin Nu.",
        "",
        "## Probe setup",
        "",
        f"- probes: `{len(probes)}`",
        f"- window: `{WINDOW[0]}..{WINDOW[1]} s`",
        f"- samples: `{len(time)}`",
        f"- sampling: `{1.0 / np.median(np.diff(time)):.1f} Hz`",
        "",
        "## Best wake probes",
        "",
        f"- strongest `Uy` RMS: probe `{strongest_uy.probe}` at `(x,y)=({1000*strongest_uy.x_m:.1f}, {1000*strongest_uy.y_m:.1f}) mm`, RMS `{strongest_uy.uy_rms:.5f} m/s`.",
        f"- highest coherence `Uy-Cl` near `f_shed`: probe `{best_cl.probe}`, coherence `{best_cl.coh_uy_cl_f1:.3f}`, lag `Uy -> Cl` `{best_cl.lag_uy_to_cl_s:+.4f} s`.",
        f"- highest coherence `Uy-Q_wall` near `f_shed`: probe `{best_q.probe}`, coherence `{best_q.coh_uy_qwall_f1:.3f}`, lag `Uy -> Q_wall` `{best_q.lag_uy_to_qwall_s:+.4f} s`.",
        f"- best `Uy -> local Nu` at `f_shed`: probe `{best_nu_f1.probe}`, `{best_nu_f1.side}`, x=`{1000*best_nu_f1.x_bin_m:.2f} mm`, coherence `{best_nu_f1.coherence_f1:.3f}`.",
        f"- best `Uy -> local Nu` at `2f_shed`: probe `{best_nu_f2.probe}`, `{best_nu_f2.side}`, x=`{1000*best_nu_f2.x_bin_m:.2f} mm`, coherence `{best_nu_f2.coherence_f2:.3f}`.",
        "",
        "## Top probes by coherence(Uy, Cl)",
        "",
        "| probe | x [mm] | y [mm] | Uy RMS | PSD peak [Hz] | coh Uy-Cl | lag Uy->Cl [s] | coh Uy-Qwall | lag Uy->Qwall [s] |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for m in top_metrics:
        lines.append(
            f"| {m.probe} | {1000*m.x_m:.1f} | {1000*m.y_m:.1f} | {m.uy_rms:.5f} | {m.uy_psd_peak_hz:.3f} | "
            f"{m.coh_uy_cl_f1:.3f} | {m.lag_uy_to_cl_s:+.4f} | {m.coh_uy_qwall_f1:.3f} | {m.lag_uy_to_qwall_s:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## Top probe/local-Nu coherence pairs",
            "",
            "| probe | probe x [mm] | probe y [mm] | side | Nu x [mm] | coh f_shed | coh 2f_shed |",
            "|---:|---:|---:|---|---:|---:|---:|",
        ]
    )
    for r in top_nu:
        lines.append(
            f"| {r.probe} | {1000*r.probe_x_m:.1f} | {1000*r.probe_y_m:.1f} | {r.side} | "
            f"{1000*r.x_bin_m:.2f} | {r.coherence_f1:.3f} | {r.coherence_f2:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `Uy` probes closest to the near wake carry the strongest lift-related signal; downstream/centerline probes are useful for PSD but can lose phase specificity.",
            "- Positive lag means the target signal lags the probe signal in the cross-correlation convention.",
            "- Local fin Nu coherence identifies which wake probe is the best reduced sensor for heat-transfer coupling.",
            "",
            "## Figures",
            "",
            "- `../../figures/010/run008_010_probe_layout_coherence.png`",
            "- `../../figures/010/run008_010_probe_uy_psd.png`",
            "- `../../figures/010/run008_010_probe_cross_correlation_lags.png`",
            "- `../../figures/010/run008_010_probe_to_local_nu_coherence_rank.png`",
        ]
    )
    report = DATA_DIR / "run008_010_wake_probes_analysis.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
