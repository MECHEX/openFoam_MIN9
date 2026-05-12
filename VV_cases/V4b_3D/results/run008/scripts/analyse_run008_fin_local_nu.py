"""
Run008 local fin Nusselt analysis.

Layer 005:
- Nu_local(x,t) for hot_fin_z_min and hot_fin_z_max,
- mean/RMS profiles,
- harmonic amplitude/phase relative to Cl,
- coherence and lag maps Cl -> Nu_local(x),
- symmetry/antisymmetry between the two fins.
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
DATA_DIR = RUN_DIR / "data" / "005"
FIG_DIR = RUN_DIR / "figures" / "005"
CASE_DIR = Path("/home/hexmachina/of_runs/V4b_3D_run008")
POST_DIR = CASE_DIR / "postProcessing"
FIN_DIR = POST_DIR / "hot_fin_surface"

D = 0.012
T_IN = 293.15
T_HOT = 343.15
CP_AIR = 1005.0
MU_AIR = 1.827e-05
PR_AIR = 0.713
K_AIR = CP_AIR * MU_AIR / PR_AIR

WINDOW = (2.0, 10.0)
N_X = 80
F_SHED = 3.2787


@dataclass
class FinSummary:
    metric: str
    value: float


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def lmtd(t_out: float) -> float:
    d1 = T_HOT - T_IN
    d2 = T_HOT - t_out
    return (d1 - d2) / math.log(d1 / d2)


def list_times() -> np.ndarray:
    times = []
    for path in FIN_DIR.iterdir():
        if not path.is_dir():
            continue
        try:
            t = float(path.name)
        except ValueError:
            continue
        if (
            WINDOW[0] - 1e-12 <= t <= WINDOW[1] + 1e-12
            and (path / "hot_fin_z_min.vtk").exists()
            and (path / "hot_fin_z_max.vtk").exists()
        ):
            times.append(t)
    return np.asarray(sorted(times), dtype=float)


def read_vtk_text(time_value: float, patch: str) -> str:
    return (FIN_DIR / f"{time_value:g}" / f"{patch}.vtk").read_text(encoding="utf-8", errors="replace")


def read_vtk_points_and_wall_heat_flux(time_value: float, patch: str, read_points: bool = False) -> tuple[np.ndarray | None, np.ndarray]:
    text = read_vtk_text(time_value, patch)
    n_points_match = re.search(r"POINTS\s+(\d+)\s+\w+\s+(.*?)\nPOLYGONS", text, flags=re.S)
    if not n_points_match:
        raise ValueError(f"Could not parse POINTS for {patch} at t={time_value:g}")
    n_points = int(n_points_match.group(1))
    points = None
    if read_points:
        vals = np.fromstring(n_points_match.group(2), sep=" ")
        points = vals.reshape((-1, 3))
        if len(points) != n_points:
            raise ValueError(f"Expected {n_points} points, got {len(points)}")
    field_match = re.search(r"wallHeatFlux\s+1\s+(\d+)\s+float\s+(.*)", text, flags=re.S)
    if not field_match:
        raise ValueError(f"Could not parse wallHeatFlux for {patch} at t={time_value:g}")
    n_values = int(field_match.group(1))
    values = np.fromstring(field_match.group(2), sep=" ", count=n_values)
    if len(values) != n_points:
        raise ValueError(f"Expected {n_points} values, got {len(values)}")
    return points, values


def boundary_patch(patch_name: str) -> dict[str, int]:
    text = (CASE_DIR / "constant" / "polyMesh" / "boundary").read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\}}", text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name} not found")
    section = match.group(1)
    return {
        "nFaces": int(re.search(r"nFaces\s+(\d+)\s*;", section).group(1)),
        "startFace": int(re.search(r"startFace\s+(\d+)\s*;", section).group(1)),
    }


def parse_points(path: Path) -> np.ndarray:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    count = None
    start = None
    for i, line in enumerate(lines):
        if line.strip().isdigit():
            count = int(line.strip())
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == "(":
                    start = j + 1
                    break
            break
    if count is None or start is None:
        raise ValueError(f"Could not parse points from {path}")
    values = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped == ")":
            break
        values.extend(float(v) for v in stripped.strip("()").split())
    return np.asarray(values).reshape((-1, 3))


def outlet_faces(start_face: int, n_faces: int) -> list[list[int]]:
    faces = []
    face_index = 0
    in_list = False
    end_face = start_face + n_faces
    with (CASE_DIR / "constant" / "polyMesh" / "faces").open("r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if not in_list:
                if line == "(":
                    in_list = True
                continue
            if line == ")":
                break
            if start_face <= face_index < end_face:
                nums = [int(v) for v in re.findall(r"\d+", line)]
                faces.append(nums[1 : 1 + nums[0]])
            face_index += 1
            if face_index >= end_face:
                break
    return faces


def polygon_area(points: np.ndarray) -> float:
    origin = points[0]
    area_vec = np.zeros(3)
    for i in range(1, len(points) - 1):
        area_vec += np.cross(points[i] - origin, points[i + 1] - origin)
    return 0.5 * float(np.linalg.norm(area_vec))


def field_patch_values(time_name: str, field_name: str, patch_name: str, n_faces: int) -> np.ndarray:
    text = (CASE_DIR / time_name / field_name).read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch_name)}\s*\{{(.*?)\n\s*\}}", text, flags=re.S)
    if not match:
        raise ValueError(f"Patch {patch_name} not found in {field_name} at {time_name}")
    section = match.group(1)
    uniform = re.search(r"value\s+uniform\s+([0-9eE.+\-]+)", section)
    if uniform:
        return np.full(n_faces, float(uniform.group(1)))
    vals_match = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)", section, flags=re.S)
    if not vals_match:
        raise ValueError(f"Could not parse {field_name}:{patch_name} at {time_name}")
    return np.fromstring(vals_match.group(2), sep=" ")


def outlet_lmtd_series() -> tuple[np.ndarray, np.ndarray]:
    patch = boundary_patch("outlet")
    points = parse_points(CASE_DIR / "constant" / "polyMesh" / "points")
    faces = outlet_faces(patch["startFace"], patch["nFaces"])
    areas = np.asarray([polygon_area(points[face]) for face in faces])
    area_total = float(np.sum(areas))
    times = []
    lmt = []
    for path in CASE_DIR.iterdir():
        if not path.is_dir():
            continue
        try:
            t = float(path.name)
        except ValueError:
            continue
        if WINDOW[0] - 1e-12 <= t <= WINDOW[1] + 1e-12 and (path / "T").exists():
            t_vals = field_patch_values(f"{t:g}", "T", "outlet", patch["nFaces"])
            t_area = float(np.sum(t_vals * areas) / area_total)
            times.append(t)
            lmt.append(lmtd(t_area))
    order = np.argsort(times)
    return np.asarray(times)[order], np.asarray(lmt)[order]


def load_cl_phase_and_signal(times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    phase_path = RUN_DIR / "data" / "002" / "run008_002_hilbert_phase.npz"
    if phase_path.exists():
        data = np.load(phase_path)
        phase = np.interp(times, data["time"], np.unwrap(data["phase_rad"]))
        phase = np.mod(phase, 2 * np.pi)
    else:
        phase = np.mod(2 * np.pi * F_SHED * (times - times[0]), 2 * np.pi)

    path = POST_DIR / "forceCoeffs" / "0" / "forceCoeffs.dat"
    rows = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            vals = [float(x) for x in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", stripped)]
            if len(vals) >= 4:
                rows.append(vals)
    arr = np.asarray(rows)
    cl = np.interp(times, arr[:, 0], arr[:, 3])
    return phase, cl


def build_x_bins(points_min: np.ndarray, points_max: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x_all = np.concatenate([points_min[:, 0], points_max[:, 0]])
    edges = np.linspace(float(np.min(x_all)), float(np.max(x_all)), N_X + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    return edges, centers


def bin_x(values: np.ndarray, x: np.ndarray, edges: np.ndarray) -> np.ndarray:
    idx = np.clip(np.digitize(x, edges) - 1, 0, N_X - 1)
    counts = np.bincount(idx, minlength=N_X).astype(float)
    sums = np.bincount(idx, weights=values, minlength=N_X)
    return np.divide(sums, counts, out=np.full(N_X, np.nan), where=counts > 0)


def harmonic_coeff(series: np.ndarray, phase: np.ndarray, harmonic: int) -> tuple[np.ndarray, np.ndarray]:
    valid_counts = np.sum(np.isfinite(series), axis=0)
    mean = np.divide(
        np.nansum(series, axis=0),
        valid_counts,
        out=np.full(series.shape[1], np.nan),
        where=valid_counts > 0,
    )
    e = np.exp(-1j * harmonic * phase)
    coeff = np.full(series.shape[1], np.nan + 1j * np.nan, dtype=complex)
    amp = np.full(series.shape[1], np.nan)
    ph = np.full(series.shape[1], np.nan)
    for i in range(series.shape[1]):
        valid = np.isfinite(series[:, i])
        if np.sum(valid) < 8:
            continue
        ev = e[valid]
        coeff_i = np.sum(series[valid, i] * ev) - mean[i] * np.sum(ev)
        coeff[i] = coeff_i
        amp[i] = 2.0 * np.abs(coeff_i) / np.sum(valid)
        ph[i] = np.angle(coeff_i)
    return amp, ph


def coherence_and_lag(times: np.ndarray, cl: np.ndarray, series: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    fs = 1.0 / float(np.median(np.diff(times)))
    cl0 = cl - np.mean(cl)
    coh = np.zeros(N_X)
    lag = np.zeros(N_X)
    corr = np.zeros(N_X)
    for i in range(N_X):
        y = series[:, i]
        valid = np.isfinite(y)
        if np.sum(valid) < 64 or float(np.nanstd(y[valid])) <= 0.0:
            coh[i] = float("nan")
            lag[i] = float("nan")
            corr[i] = float("nan")
            continue
        y0 = y[valid] - np.mean(y[valid])
        x0 = cl0[valid]
        f, cxy = signal.coherence(x0, y0, fs=fs, nperseg=min(512, len(x0)), noverlap=min(256, len(x0) // 2))
        band = np.where((f >= F_SHED - 0.7) & (f <= F_SHED + 0.7))[0]
        coh[i] = float(np.nanmax(cxy[band])) if len(band) else float("nan")
        xnorm = x0 / np.linalg.norm(x0)
        ynorm = y0 / np.linalg.norm(y0)
        cc = np.correlate(ynorm, xnorm, mode="full")
        lag_grid = (np.arange(len(cc)) - (len(xnorm) - 1)) / fs
        mask = np.abs(lag_grid) <= 1.0
        j = int(np.argmax(np.abs(cc[mask])))
        lag[i] = float(lag_grid[mask][j])
        corr[i] = float(cc[mask][j])
    return coh, lag, corr


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_profiles(x_centers: np.ndarray, profiles: dict[str, np.ndarray]) -> None:
    x_mm = x_centers * 1000.0
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    axes[0, 0].plot(x_mm, profiles["mean_min"], label="z_min")
    axes[0, 0].plot(x_mm, profiles["mean_max"], label="z_max")
    axes[0, 0].set_title("Mean Nu_local(x)")
    axes[0, 1].plot(x_mm, profiles["rms_min"], label="z_min")
    axes[0, 1].plot(x_mm, profiles["rms_max"], label="z_max")
    axes[0, 1].set_title("RMS Nu_local(x)")
    axes[1, 0].plot(x_mm, profiles["sym_mean"], label="symmetric mean")
    axes[1, 0].plot(x_mm, profiles["anti_mean"], label="antisymmetric mean")
    axes[1, 0].set_title("Fin symmetry components")
    axes[1, 1].plot(x_mm, profiles["A1_min"], label="A1 z_min")
    axes[1, 1].plot(x_mm, profiles["A1_max"], label="A1 z_max")
    axes[1, 1].plot(x_mm, profiles["A2_min"], ls="--", label="A2 z_min")
    axes[1, 1].plot(x_mm, profiles["A2_max"], ls="--", label="A2 z_max")
    axes[1, 1].set_title("Harmonic amplitudes")
    for ax in axes.ravel():
        ax.set_xlabel("x [mm]")
        ax.set_ylabel("Nu")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)
    fig.savefig(FIG_DIR / "run008_005_fin_nu_x_profiles.png", dpi=180)
    plt.close(fig)


def plot_phase_coherence_lag(x_centers: np.ndarray, profiles: dict[str, np.ndarray]) -> None:
    x_mm = x_centers * 1000.0
    fig, axes = plt.subplots(3, 1, figsize=(11, 10), constrained_layout=True)
    axes[0].plot(x_mm, np.degrees(profiles["phase1_min"]), label="phase A1 z_min")
    axes[0].plot(x_mm, np.degrees(profiles["phase1_max"]), label="phase A1 z_max")
    axes[0].set_ylabel("phase [deg]")
    axes[0].set_title("Phase of local fin Nu relative to Cl")
    axes[1].plot(x_mm, profiles["coh_min"], label="coherence z_min")
    axes[1].plot(x_mm, profiles["coh_max"], label="coherence z_max")
    axes[1].axhline(0.5, color="black", ls="--", lw=0.8)
    axes[1].set_ylabel("coherence")
    axes[1].set_title("Coherence(Cl, Nu_local(x)) near f_shed")
    axes[2].plot(x_mm, profiles["lag_min"], label="lag z_min")
    axes[2].plot(x_mm, profiles["lag_max"], label="lag z_max")
    axes[2].axhline(0, color="black", lw=0.8)
    axes[2].set_ylabel("lag [s]")
    axes[2].set_xlabel("x [mm]")
    axes[2].set_title("Lag at max cross-correlation, positive = Nu lags Cl")
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)
    fig.savefig(FIG_DIR / "run008_005_fin_phase_coherence_lag.png", dpi=180)
    plt.close(fig)


def plot_time_maps(times: np.ndarray, x_centers: np.ndarray, min_series: np.ndarray, max_series: np.ndarray) -> None:
    x_mm = x_centers * 1000.0
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, constrained_layout=True)
    for ax, data, title in [(axes[0], min_series, "hot_fin_z_min Nu_local(x,t)"), (axes[1], max_series, "hot_fin_z_max Nu_local(x,t)")]:
        im = ax.pcolormesh(times, x_mm, data.T, shading="auto", cmap="viridis")
        ax.set_ylabel("x [mm]")
        ax.set_title(title)
        plt.colorbar(im, ax=ax, label="Nu")
    axes[1].set_xlabel("t [s]")
    fig.savefig(FIG_DIR / "run008_005_fin_nu_xt_maps.png", dpi=180)
    plt.close(fig)


def plot_active_zones(x_centers: np.ndarray, profiles: dict[str, np.ndarray]) -> None:
    x_mm = x_centers * 1000.0
    valid_min = np.isfinite(profiles["mean_min"]) & np.isfinite(profiles["coh_min"]) & np.isfinite(profiles["A1_min"])
    valid_max = np.isfinite(profiles["mean_max"]) & np.isfinite(profiles["coh_max"]) & np.isfinite(profiles["A1_max"])
    active_min = valid_min & (profiles["coh_min"] >= 0.5) & (profiles["A1_min"] >= np.nanmedian(profiles["A1_min"]))
    active_max = valid_max & (profiles["coh_max"] >= 0.5) & (profiles["A1_max"] >= np.nanmedian(profiles["A1_max"]))
    fig, ax = plt.subplots(figsize=(11, 4), constrained_layout=True)
    ax.plot(x_mm, profiles["coh_min"], label="coh z_min", color="#1d4e89")
    ax.plot(x_mm, profiles["coh_max"], label="coh z_max", color="#9b2226")
    ax.fill_between(x_mm, 0, 1, where=active_min, color="#1d4e89", alpha=0.12, label="active z_min")
    ax.fill_between(x_mm, 0, 1, where=active_max, color="#9b2226", alpha=0.12, label="active z_max")
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("coherence")
    ax.set_title("Actively coupled fin zones: coherence >= 0.5 and above-median A1")
    ax.grid(alpha=0.25)
    ax.legend(ncol=2, fontsize=8)
    fig.savefig(FIG_DIR / "run008_005_fin_active_coupled_zones.png", dpi=180)
    plt.close(fig)
    profiles["active_min"] = active_min.astype(float)
    profiles["active_max"] = active_max.astype(float)
    profiles["valid_min"] = valid_min.astype(float)
    profiles["valid_max"] = valid_max.astype(float)


def main() -> None:
    ensure_dirs()
    times = list_times()
    points_min, _ = read_vtk_points_and_wall_heat_flux(float(times[0]), "hot_fin_z_min", read_points=True)
    points_max, _ = read_vtk_points_and_wall_heat_flux(float(times[0]), "hot_fin_z_max", read_points=True)
    assert points_min is not None and points_max is not None
    x_edges, x_centers = build_x_bins(points_min, points_max)
    lmt_t, lmt = outlet_lmtd_series()
    phase, cl = load_cl_phase_and_signal(times)
    lmtd_i = np.interp(times, lmt_t, lmt)

    min_series = np.full((len(times), N_X), np.nan)
    max_series = np.full((len(times), N_X), np.nan)
    for i, t in enumerate(times):
        _, q_min = read_vtk_points_and_wall_heat_flux(float(t), "hot_fin_z_min", read_points=False)
        _, q_max = read_vtk_points_and_wall_heat_flux(float(t), "hot_fin_z_max", read_points=False)
        min_series[i] = bin_x(q_min * D / (K_AIR * lmtd_i[i]), points_min[:, 0], x_edges)
        max_series[i] = bin_x(q_max * D / (K_AIR * lmtd_i[i]), points_max[:, 0], x_edges)

    sym_series = 0.5 * (min_series + max_series)
    anti_series = 0.5 * (max_series - min_series)
    A1_min, phase1_min = harmonic_coeff(min_series, phase, 1)
    A1_max, phase1_max = harmonic_coeff(max_series, phase, 1)
    A2_min, phase2_min = harmonic_coeff(min_series, phase, 2)
    A2_max, phase2_max = harmonic_coeff(max_series, phase, 2)
    coh_min, lag_min, corr_min = coherence_and_lag(times, cl, min_series)
    coh_max, lag_max, corr_max = coherence_and_lag(times, cl, max_series)
    fin_pair_corr = np.full(N_X, np.nan)
    for i in range(N_X):
        valid = np.isfinite(min_series[:, i]) & np.isfinite(max_series[:, i])
        if np.sum(valid) >= 64:
            fin_pair_corr[i] = float(np.corrcoef(min_series[valid, i], max_series[valid, i])[0, 1])

    profiles = {
        "mean_min": np.nanmean(min_series, axis=0),
        "mean_max": np.nanmean(max_series, axis=0),
        "rms_min": np.nanstd(min_series, axis=0, ddof=1),
        "rms_max": np.nanstd(max_series, axis=0, ddof=1),
        "sym_mean": np.nanmean(sym_series, axis=0),
        "anti_mean": np.nanmean(anti_series, axis=0),
        "A1_min": A1_min,
        "A1_max": A1_max,
        "A2_min": A2_min,
        "A2_max": A2_max,
        "phase1_min": phase1_min,
        "phase1_max": phase1_max,
        "phase2_min": phase2_min,
        "phase2_max": phase2_max,
        "coh_min": coh_min,
        "coh_max": coh_max,
        "lag_min": lag_min,
        "lag_max": lag_max,
        "corr_min": corr_min,
        "corr_max": corr_max,
        "fin_pair_corr": fin_pair_corr,
    }
    plot_profiles(x_centers, profiles)
    plot_phase_coherence_lag(x_centers, profiles)
    plot_time_maps(times, x_centers, min_series, max_series)
    plot_active_zones(x_centers, profiles)

    profile_rows = []
    for i, x in enumerate(x_centers):
        row = {"x_m": float(x), "x_mm": float(x * 1000.0)}
        for key, values in profiles.items():
            row[key] = float(values[i])
        profile_rows.append(row)
    write_csv(DATA_DIR / "run008_005_fin_nu_x_profiles.csv", profile_rows)

    valid_min = profiles["valid_min"].astype(bool)
    valid_max = profiles["valid_max"].astype(bool)
    valid_pair = valid_min & valid_max & np.isfinite(phase1_min) & np.isfinite(phase1_max)
    phase_lag_max_minus_min = float(np.degrees(np.angle(np.nanmean(np.exp(1j * (phase1_max[valid_pair] - phase1_min[valid_pair])))))) if np.any(valid_pair) else float("nan")
    median_lag_difference = float(np.nanmedian(lag_max[valid_pair] - lag_min[valid_pair])) if np.any(valid_pair) else float("nan")
    active_min_fraction = float(np.sum(profiles["active_min"][valid_min]) / np.sum(valid_min))
    active_max_fraction = float(np.sum(profiles["active_max"][valid_max]) / np.sum(valid_max))
    summary = [
        FinSummary("n_times", float(len(times))),
        FinSummary("n_x_bins", float(N_X)),
        FinSummary("n_valid_x_bins_z_min", float(np.sum(valid_min))),
        FinSummary("n_valid_x_bins_z_max", float(np.sum(valid_max))),
        FinSummary("Nu_mean_z_min", float(np.nanmean(min_series))),
        FinSummary("Nu_mean_z_max", float(np.nanmean(max_series))),
        FinSummary("Nu_rms_z_min_mean", float(np.nanmean(profiles["rms_min"]))),
        FinSummary("Nu_rms_z_max_mean", float(np.nanmean(profiles["rms_max"]))),
        FinSummary("A1_z_min_mean", float(np.nanmean(A1_min))),
        FinSummary("A1_z_max_mean", float(np.nanmean(A1_max))),
        FinSummary("A2_z_min_mean", float(np.nanmean(A2_min))),
        FinSummary("A2_z_max_mean", float(np.nanmean(A2_max))),
        FinSummary("mean_abs_antisymmetric_Nu", float(np.nanmean(np.abs(profiles["anti_mean"])))),
        FinSummary("mean_fin_pair_corr", float(np.nanmean(fin_pair_corr))),
        FinSummary("mean_coherence_z_min", float(np.nanmean(coh_min))),
        FinSummary("mean_coherence_z_max", float(np.nanmean(coh_max))),
        FinSummary("active_fraction_z_min", active_min_fraction),
        FinSummary("active_fraction_z_max", active_max_fraction),
        FinSummary("median_lag_z_min_s", float(np.nanmedian(lag_min))),
        FinSummary("median_lag_z_max_s", float(np.nanmedian(lag_max))),
        FinSummary("phase1_z_max_minus_z_min_deg", phase_lag_max_minus_min),
        FinSummary("median_lag_z_max_minus_z_min_s", median_lag_difference),
    ]
    write_csv(DATA_DIR / "run008_005_fin_nu_summary.csv", [asdict(s) for s in summary])
    np.savez_compressed(
        DATA_DIR / "run008_005_fin_nu_arrays.npz",
        times=times,
        x_centers=x_centers,
        min_series=min_series,
        max_series=max_series,
        cl=cl,
        phase=phase,
        **profiles,
    )
    (DATA_DIR / "run008_005_fin_nu_summary.json").write_text(
        json.dumps({"summary": [asdict(s) for s in summary], "definition": "Nu=q''*D/(k*LMTD(t)); coherence uses scipy.signal.coherence near f_shed"}, indent=2),
        encoding="utf-8",
    )

    lookup = {s.metric: s.value for s in summary}
    lines = [
        "# V4b_3D run008 local fin Nu",
        "",
        f"Primary window: `{WINDOW[0]:.1f}..{WINDOW[1]:.1f} s`, samples `{len(times)}`.",
        "Definition: `Nu_local(x,t) = q''(x,t) D / (k LMTD(t))`; x-profiles are point-averaged over each fin surface.",
        "Phase and coupling reference: `Cl` from layer `002`.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for s in summary:
        lines.append(f"| {s.metric} | {s.value:.6f} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Mean fin Nu is nearly symmetric: z_min `{lookup['Nu_mean_z_min']:.3f}`, z_max `{lookup['Nu_mean_z_max']:.3f}`.",
            f"- Mean absolute antisymmetric component is `{lookup['mean_abs_antisymmetric_Nu']:.4f}` Nu and the mean fin-pair time correlation is `{lookup['mean_fin_pair_corr']:.3f}`.",
            f"- Cl-coupled zones occupy `{100.0 * lookup['active_fraction_z_min']:.1f}%` of x bins on z_min and `{100.0 * lookup['active_fraction_z_max']:.1f}%` on z_max using coherence >= 0.5 and above-median A1.",
            f"- Median lag estimates are `{lookup['median_lag_z_min_s']:+.4f} s` for z_min and `{lookup['median_lag_z_max_s']:+.4f} s` for z_max; median z_max-z_min lag difference is `{lookup['median_lag_z_max_minus_z_min_s']:+.4f} s`.",
            f"- Mean `A1` phase difference z_max-z_min is `{lookup['phase1_z_max_minus_z_min_deg']:+.2f} deg`, so the two fin surfaces are nearly in phase for the Cl-coupled component.",
            "",
            "## Figures",
            "",
            "- `../../figures/005/run008_005_fin_nu_x_profiles.png`",
            "- `../../figures/005/run008_005_fin_phase_coherence_lag.png`",
            "- `../../figures/005/run008_005_fin_nu_xt_maps.png`",
            "- `../../figures/005/run008_005_fin_active_coupled_zones.png`",
        ]
    )
    (DATA_DIR / "run008_005_fin_local_nu.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print((DATA_DIR / "run008_005_fin_local_nu.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
