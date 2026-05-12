"""
Run008 coherence and cross-spectral analysis.

Layer 007:
- coherence and cross-phase for Cl vs Q_wall/Q_tube/Q_fins,
- spatial coherence maps for Cl vs tube Nu(theta,z),
- fin coherence profiles Cl vs Nu_local(x),
- cross-correlation lag diagnostics,
- separate reporting near f_shed and 2*f_shed.
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
DATA_DIR = RUN_DIR / "data" / "007"
FIG_DIR = RUN_DIR / "figures" / "007"
CASE_DIR = Path("/home/hexmachina/of_runs/V4b_3D_run008")
POST_DIR = CASE_DIR / "postProcessing"
TUBE_DIR = POST_DIR / "hot_tube_surface"

D = 0.012
T_IN = 293.15
T_HOT = 343.15
CP_AIR = 1005.0
MU_AIR = 1.827e-05
PR_AIR = 0.713
K_AIR = CP_AIR * MU_AIR / PR_AIR

WINDOW = (2.0, 10.0)
F_SHED = 3.2787
N_THETA = 64
N_Z = 20


@dataclass
class CouplingRow:
    signal: str
    band: str
    frequency_hz: float
    coherence: float
    cross_phase_deg: float
    phase_lag_s: float
    xcorr_lag_s: float
    xcorr_corr: float


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def read_force_cl() -> tuple[np.ndarray, np.ndarray]:
    rows = []
    with (POST_DIR / "forceCoeffs" / "0" / "forceCoeffs.dat").open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            vals = [float(x) for x in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", stripped)]
            if len(vals) >= 4:
                rows.append(vals)
    arr = np.asarray(rows)
    mask = (arr[:, 0] >= WINDOW[0] - 1e-12) & (arr[:, 0] <= WINDOW[1] + 1e-12)
    return arr[mask, 0], arr[mask, 3]


def read_heat_timeseries(time: np.ndarray) -> dict[str, np.ndarray]:
    path = RUN_DIR / "data" / "003" / "run008_003_heat_balance_timeseries.csv"
    cols: dict[str, list[float]] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for key, val in row.items():
                cols.setdefault(key, []).append(float(val))
    src_t = np.asarray(cols["time"])
    return {
        "Q_wall": np.interp(time, src_t, np.asarray(cols["Q_wall"])),
        "Q_tube": np.interp(time, src_t, np.asarray(cols["Q_tube"])),
        "Q_fins": np.interp(time, src_t, np.asarray(cols["Q_fins"])),
        "Nu_tube": np.interp(time, src_t, np.asarray(cols["Nu_tube_wall"])),
        "Nu_fins": np.interp(time, src_t, np.asarray(cols["Nu_fins_wall"])),
    }


def load_fin_arrays(time: np.ndarray) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    data = np.load(RUN_DIR / "data" / "005" / "run008_005_fin_nu_arrays.npz")
    t_fin = data["times"]
    x = data["x_centers"]
    min_series = np.asarray([np.interp(time, t_fin, data["min_series"][:, i]) for i in range(len(x))]).T
    max_series = np.asarray([np.interp(time, t_fin, data["max_series"][:, i]) for i in range(len(x))]).T
    return x, {"fin_z_min": min_series, "fin_z_max": max_series}


def lmtd(t_out: float) -> float:
    d1 = T_HOT - T_IN
    d2 = T_HOT - t_out
    return (d1 - d2) / math.log(d1 / d2)


def read_lmtd_for_tube(time: np.ndarray) -> np.ndarray:
    # Reuse the already interpolated LMTD from layer 003.
    path = RUN_DIR / "data" / "003" / "run008_003_heat_balance_timeseries.csv"
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append((float(row["time"]), float(row["LMTD"])))
    arr = np.asarray(rows)
    return np.interp(time, arr[:, 0], arr[:, 1])


def list_tube_times() -> np.ndarray:
    times = []
    for path in TUBE_DIR.iterdir():
        if not path.is_dir():
            continue
        try:
            t = float(path.name)
        except ValueError:
            continue
        if WINDOW[0] - 1e-12 <= t <= WINDOW[1] + 1e-12 and (path / "hot_tube.vtk").exists():
            times.append(t)
    return np.asarray(sorted(times), dtype=float)


def read_tube_vtk(time_value: float, read_points: bool = False) -> tuple[np.ndarray | None, np.ndarray]:
    text = (TUBE_DIR / f"{time_value:g}" / "hot_tube.vtk").read_text(encoding="utf-8", errors="replace")
    match = re.search(r"POINTS\s+(\d+)\s+\w+\s+(.*?)\nPOLYGONS", text, flags=re.S)
    if not match:
        raise ValueError(f"Could not parse POINTS at {time_value:g}")
    n_points = int(match.group(1))
    points = None
    if read_points:
        points = np.fromstring(match.group(2), sep=" ").reshape((-1, 3))
    field_match = re.search(r"wallHeatFlux\s+1\s+(\d+)\s+float\s+(.*)", text, flags=re.S)
    if not field_match:
        raise ValueError(f"Could not parse wallHeatFlux at {time_value:g}")
    q = np.fromstring(field_match.group(2), sep=" ", count=int(field_match.group(1)))
    if len(q) != n_points:
        raise ValueError(f"Expected {n_points}, got {len(q)}")
    return points, q


def build_tube_bins(points: np.ndarray) -> dict[str, np.ndarray]:
    theta = np.arctan2(points[:, 1], points[:, 0])
    z = points[:, 2]
    theta_edges = np.linspace(-np.pi, np.pi, N_THETA + 1)
    z_edges = np.linspace(float(np.min(z)), float(np.max(z)), N_Z + 1)
    theta_idx = np.clip(np.digitize(theta, theta_edges) - 1, 0, N_THETA - 1)
    z_idx = np.clip(np.digitize(z, z_edges) - 1, 0, N_Z - 1)
    flat = z_idx * N_THETA + theta_idx
    counts = np.bincount(flat, minlength=N_THETA * N_Z).astype(float)
    return {
        "flat": flat,
        "counts": counts,
        "theta_centers": 0.5 * (theta_edges[:-1] + theta_edges[1:]),
        "z_centers": 0.5 * (z_edges[:-1] + z_edges[1:]),
    }


def bin_mean(values: np.ndarray, flat: np.ndarray, counts: np.ndarray) -> np.ndarray:
    sums = np.bincount(flat, weights=values, minlength=N_THETA * N_Z)
    return np.divide(sums, counts, out=np.full(N_THETA * N_Z, np.nan), where=counts > 0)


def load_tube_nu_series(time: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    tube_times = list_tube_times()
    points, _ = read_tube_vtk(float(tube_times[0]), read_points=True)
    assert points is not None
    bins = build_tube_bins(points)
    lmtd = read_lmtd_for_tube(tube_times)
    series = np.full((len(tube_times), N_THETA * N_Z), np.nan)
    for i, t in enumerate(tube_times):
        _, q = read_tube_vtk(float(t), read_points=False)
        nu = q * D / (K_AIR * lmtd[i])
        series[i] = bin_mean(nu, bins["flat"], bins["counts"])
    # tube_times match force times in production, but interpolate defensively.
    interp_series = np.asarray([np.interp(time, tube_times, series[:, i]) for i in range(series.shape[1])]).T
    return bins["theta_centers"], bins["z_centers"], interp_series


def spectral_metrics(time: np.ndarray, x: np.ndarray, y: np.ndarray, freq: float) -> tuple[float, float, float]:
    fs = 1.0 / float(np.median(np.diff(time)))
    x0 = x - np.nanmean(x)
    y0 = y - np.nanmean(y)
    valid = np.isfinite(x0) & np.isfinite(y0)
    x0 = x0[valid]
    y0 = y0[valid]
    f, cxy = signal.coherence(x0, y0, fs=fs, nperseg=min(512, len(x0)), noverlap=min(256, len(x0) // 2))
    fc, pxy = signal.csd(x0, y0, fs=fs, nperseg=min(512, len(x0)), noverlap=min(256, len(x0) // 2))
    idx = int(np.argmin(np.abs(f - freq)))
    idx_c = int(np.argmin(np.abs(fc - freq)))
    phase = float(np.angle(pxy[idx_c]))
    phase_lag = phase / (2.0 * np.pi * freq)
    return float(f[idx]), float(cxy[idx]), phase_lag


def xcorr_lag(time: np.ndarray, x: np.ndarray, y: np.ndarray, max_lag: float = 1.0) -> tuple[float, float]:
    fs = 1.0 / float(np.median(np.diff(time)))
    valid = np.isfinite(x) & np.isfinite(y)
    x0 = x[valid] - np.mean(x[valid])
    y0 = y[valid] - np.mean(y[valid])
    if len(x0) < 32 or np.linalg.norm(x0) == 0 or np.linalg.norm(y0) == 0:
        return float("nan"), float("nan")
    cc = np.correlate(y0 / np.linalg.norm(y0), x0 / np.linalg.norm(x0), mode="full")
    lags = (np.arange(len(cc)) - (len(x0) - 1)) / fs
    mask = np.abs(lags) <= max_lag
    idx = int(np.argmax(np.abs(cc[mask])))
    return float(lags[mask][idx]), float(cc[mask][idx])


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_global(time: np.ndarray, cl: np.ndarray, signals: dict[str, np.ndarray]) -> list[CouplingRow]:
    rows = []
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
    for name, y in signals.items():
        fs = 1.0 / float(np.median(np.diff(time)))
        f, cxy = signal.coherence(cl - np.mean(cl), y - np.mean(y), fs=fs, nperseg=512, noverlap=256)
        axes[0].plot(f, cxy, label=name)
        fc, pxy = signal.csd(cl - np.mean(cl), y - np.mean(y), fs=fs, nperseg=512, noverlap=256)
        phase = np.unwrap(np.angle(pxy))
        axes[1].plot(fc, np.degrees(phase), label=name)
        for band_name, freq in [("f_shed", F_SHED), ("2f_shed", 2 * F_SHED)]:
            f_actual, coh, phase_lag = spectral_metrics(time, cl, y, freq)
            lag, corr = xcorr_lag(time, cl, y)
            rows.append(
                CouplingRow(
                    signal=name,
                    band=band_name,
                    frequency_hz=f_actual,
                    coherence=coh,
                    cross_phase_deg=phase_lag * 360.0 * freq,
                    phase_lag_s=phase_lag,
                    xcorr_lag_s=lag,
                    xcorr_corr=corr,
                )
            )
    for ax in axes:
        ax.axvline(F_SHED, color="black", ls="--", lw=0.8)
        ax.axvline(2 * F_SHED, color="black", ls=":", lw=0.8)
        ax.set_xlim(0, 15)
        ax.grid(alpha=0.25)
        ax.legend(ncol=3, fontsize=8)
    axes[0].set_ylabel("coherence")
    axes[0].set_title("Global coherence: Cl vs heat-transfer signals")
    axes[1].set_xlabel("f [Hz]")
    axes[1].set_ylabel("cross phase [deg]")
    fig.savefig(FIG_DIR / "run008_007_global_coherence_crossphase.png", dpi=180)
    plt.close(fig)
    return rows


def map_spatial_coherence(time: np.ndarray, cl: np.ndarray, series: np.ndarray, freq: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    coh = np.full(series.shape[1], np.nan)
    phase_lag = np.full(series.shape[1], np.nan)
    lag = np.full(series.shape[1], np.nan)
    corr = np.full(series.shape[1], np.nan)
    for i in range(series.shape[1]):
        y = series[:, i]
        if np.sum(np.isfinite(y)) < 64 or np.nanstd(y) <= 0:
            continue
        _, coh[i], phase_lag[i] = spectral_metrics(time, cl, y, freq)
        lag[i], corr[i] = xcorr_lag(time, cl, y)
    return coh, phase_lag, lag, corr


def plot_tube_maps(theta: np.ndarray, z: np.ndarray, maps: dict[str, np.ndarray]) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), constrained_layout=True)
    specs = [
        ("coh_f1", "coherence f_shed", "viridis"),
        ("lag_phase_f1", "phase lag f_shed [s]", "coolwarm"),
        ("xcorr_lag_f1", "xcorr lag [s]", "coolwarm"),
        ("coh_f2", "coherence 2f_shed", "viridis"),
        ("lag_phase_f2", "phase lag 2f_shed [s]", "coolwarm"),
        ("xcorr_corr_f1", "xcorr corr", "coolwarm"),
    ]
    for ax, (key, title, cmap) in zip(axes.ravel(), specs):
        im = ax.pcolormesh(np.degrees(theta), z * 1000.0, maps[key].reshape((N_Z, N_THETA)), shading="auto", cmap=cmap)
        ax.set_xlabel("theta [deg]")
        ax.set_ylabel("z [mm]")
        ax.set_title(title)
        plt.colorbar(im, ax=ax)
    fig.savefig(FIG_DIR / "run008_007_tube_coherence_lag_maps.png", dpi=180)
    plt.close(fig)


def plot_fin_maps(x: np.ndarray, fin_results: dict[str, dict[str, np.ndarray]]) -> None:
    x_mm = x * 1000.0
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), constrained_layout=True)
    for side, color in [("fin_z_min", "#1d4e89"), ("fin_z_max", "#9b2226")]:
        axes[0, 0].plot(x_mm, fin_results[side]["coh_f1"], color=color, label=side)
        axes[0, 1].plot(x_mm, fin_results[side]["coh_f2"], color=color, label=side)
        axes[1, 0].plot(x_mm, fin_results[side]["lag_phase_f1"], color=color, label=side)
        axes[1, 1].plot(x_mm, fin_results[side]["xcorr_lag_f1"], color=color, label=side)
    titles = ["coherence f_shed", "coherence 2f_shed", "cross-phase lag f_shed [s]", "xcorr lag [s]"]
    for ax, title in zip(axes.ravel(), titles):
        ax.set_xlabel("x [mm]")
        ax.set_title(title)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)
    fig.savefig(FIG_DIR / "run008_007_fin_coherence_lag_profiles.png", dpi=180)
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    time, cl = read_force_cl()
    heat = read_heat_timeseries(time)
    global_rows = plot_global(time, cl, heat)

    theta, z, tube_series = load_tube_nu_series(time)
    tube_maps = {}
    for label, freq in [("f1", F_SHED), ("f2", 2 * F_SHED)]:
        coh, phase_lag, lag, corr = map_spatial_coherence(time, cl, tube_series, freq)
        tube_maps[f"coh_{label}"] = coh
        tube_maps[f"lag_phase_{label}"] = phase_lag
        tube_maps[f"xcorr_lag_{label}"] = lag
        tube_maps[f"xcorr_corr_{label}"] = corr
    plot_tube_maps(theta, z, tube_maps)

    fin_x, fin_series = load_fin_arrays(time)
    fin_results = {}
    for side, series in fin_series.items():
        result = {}
        for label, freq in [("f1", F_SHED), ("f2", 2 * F_SHED)]:
            coh, phase_lag, lag, corr = map_spatial_coherence(time, cl, series, freq)
            result[f"coh_{label}"] = coh
            result[f"lag_phase_{label}"] = phase_lag
            result[f"xcorr_lag_{label}"] = lag
            result[f"xcorr_corr_{label}"] = corr
        fin_results[side] = result
    plot_fin_maps(fin_x, fin_results)

    tube_rows = []
    for iz, zz in enumerate(z):
        for it, th in enumerate(theta):
            idx = iz * N_THETA + it
            tube_rows.append(
                {
                    "theta_rad": float(th),
                    "theta_deg": float(np.degrees(th)),
                    "z_m": float(zz),
                    **{key: float(val[idx]) for key, val in tube_maps.items()},
                }
            )
    write_csv(DATA_DIR / "run008_007_tube_coherence_maps.csv", tube_rows)
    fin_rows = []
    for side, result in fin_results.items():
        for i, x in enumerate(fin_x):
            fin_rows.append(
                {
                    "side": side,
                    "x_m": float(x),
                    "x_mm": float(x * 1000.0),
                    **{key: float(val[i]) for key, val in result.items()},
                }
            )
    write_csv(DATA_DIR / "run008_007_fin_coherence_profiles.csv", fin_rows)
    write_csv(DATA_DIR / "run008_007_global_coherence.csv", [asdict(r) for r in global_rows])
    np.savez_compressed(
        DATA_DIR / "run008_007_coherence_arrays.npz",
        time=time,
        cl=cl,
        theta=theta,
        z=z,
        fin_x=fin_x,
        **{f"tube_{k}": v for k, v in tube_maps.items()},
        **{f"{side}_{k}": v for side, result in fin_results.items() for k, v in result.items()},
    )

    summary = {
        "global": [asdict(r) for r in global_rows],
        "tube": {
            "mean_coh_f1": float(np.nanmean(tube_maps["coh_f1"])),
            "mean_coh_f2": float(np.nanmean(tube_maps["coh_f2"])),
            "active_fraction_f1_coh_gt_0p5": float(np.nanmean(tube_maps["coh_f1"] > 0.5)),
            "median_phase_lag_f1_s": float(np.nanmedian(tube_maps["lag_phase_f1"])),
            "median_xcorr_lag_f1_s": float(np.nanmedian(tube_maps["xcorr_lag_f1"])),
        },
        "fin": {
            side: {
                "mean_coh_f1": float(np.nanmean(result["coh_f1"])),
                "mean_coh_f2": float(np.nanmean(result["coh_f2"])),
                "active_fraction_f1_coh_gt_0p5": float(np.nanmean(result["coh_f1"] > 0.5)),
                "median_phase_lag_f1_s": float(np.nanmedian(result["lag_phase_f1"])),
                "median_xcorr_lag_f1_s": float(np.nanmedian(result["xcorr_lag_f1"])),
            }
            for side, result in fin_results.items()
        },
    }
    (DATA_DIR / "run008_007_coherence_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# V4b_3D run008 coherence and cross-spectral analysis",
        "",
        f"Primary window: `{WINDOW[0]:.1f}..{WINDOW[1]:.1f} s`.",
        "",
        "## Global signals",
        "",
        "| Signal | band | f [Hz] | coherence | cross phase | phase lag [s] | xcorr lag [s] | xcorr corr |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in global_rows:
        lines.append(
            f"| {row.signal} | {row.band} | {row.frequency_hz:.4f} | {row.coherence:.4f} | "
            f"{row.cross_phase_deg:+.2f} deg | {row.phase_lag_s:+.4f} | {row.xcorr_lag_s:+.4f} | {row.xcorr_corr:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## Spatial summaries",
            "",
            f"- Tube mean coherence: f_shed `{summary['tube']['mean_coh_f1']:.3f}`, 2f_shed `{summary['tube']['mean_coh_f2']:.3f}`.",
            f"- Tube active fraction with coherence > 0.5 at f_shed: `{100.0 * summary['tube']['active_fraction_f1_coh_gt_0p5']:.1f}%`.",
            f"- Tube median cross-phase lag at f_shed: `{summary['tube']['median_phase_lag_f1_s']:+.4f} s`; median cross-correlation lag: `{summary['tube']['median_xcorr_lag_f1_s']:+.4f} s`.",
            f"- Fin z_min mean coherence: f_shed `{summary['fin']['fin_z_min']['mean_coh_f1']:.3f}`, 2f_shed `{summary['fin']['fin_z_min']['mean_coh_f2']:.3f}`.",
            f"- Fin z_max mean coherence: f_shed `{summary['fin']['fin_z_max']['mean_coh_f1']:.3f}`, 2f_shed `{summary['fin']['fin_z_max']['mean_coh_f2']:.3f}`.",
            "",
            "## Figures",
            "",
            "- `../../figures/007/run008_007_global_coherence_crossphase.png`",
            "- `../../figures/007/run008_007_tube_coherence_lag_maps.png`",
            "- `../../figures/007/run008_007_fin_coherence_lag_profiles.png`",
        ]
    )
    (DATA_DIR / "run008_007_coherence_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print((DATA_DIR / "run008_007_coherence_analysis.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
