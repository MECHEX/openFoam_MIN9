"""
Run008 local tube Nusselt analysis.

Layer 004:
- mean/RMS Nu(theta,z),
- first and second harmonic amplitude/phase maps relative to Cl phase,
- phase-averaged Nu(theta,z,phi),
- theta/z profiles and top-bottom asymmetry.
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


RUN_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = RUN_DIR / "data" / "004"
FIG_DIR = RUN_DIR / "figures" / "004"
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
N_THETA = 96
N_Z = 30
N_PHASE = 32
F_SHED = 3.2787


@dataclass
class TubeSummary:
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


def read_vtk_text(time_value: float) -> str:
    return (TUBE_DIR / f"{time_value:g}" / "hot_tube.vtk").read_text(encoding="utf-8", errors="replace")


def read_vtk_points_and_wall_heat_flux(time_value: float, read_points: bool = False) -> tuple[np.ndarray | None, np.ndarray]:
    text = read_vtk_text(time_value)
    n_points_match = re.search(r"POINTS\s+(\d+)\s+\w+\s+(.*?)\nPOLYGONS", text, flags=re.S)
    if not n_points_match:
        raise ValueError(f"Could not parse POINTS at t={time_value:g}")
    n_points = int(n_points_match.group(1))
    points = None
    if read_points:
        vals = np.fromstring(n_points_match.group(2), sep=" ")
        points = vals.reshape((-1, 3))
        if len(points) != n_points:
            raise ValueError(f"Expected {n_points} points, got {len(points)}")
    field_match = re.search(r"wallHeatFlux\s+1\s+(\d+)\s+float\s+(.*)", text, flags=re.S)
    if not field_match:
        raise ValueError(f"Could not parse wallHeatFlux at t={time_value:g}")
    n_values = int(field_match.group(1))
    values = np.fromstring(field_match.group(2), sep=" ", count=n_values)
    if len(values) != n_points:
        raise ValueError(f"Expected {n_points} wallHeatFlux values, got {len(values)}")
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


def load_cl_phase(times: np.ndarray) -> np.ndarray:
    phase_path = RUN_DIR / "data" / "002" / "run008_002_hilbert_phase.npz"
    if phase_path.exists():
        data = np.load(phase_path)
        phase = np.interp(times, data["time"], np.unwrap(data["phase_rad"]))
        return np.mod(phase, 2 * np.pi)
    return np.mod(2 * np.pi * F_SHED * (times - times[0]), 2 * np.pi)


def load_cl(times: np.ndarray) -> np.ndarray:
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
    arr = np.asarray(rows, dtype=float)
    return np.interp(times, arr[:, 0], arr[:, 3])


def build_bins(points: np.ndarray) -> dict[str, np.ndarray]:
    theta = np.arctan2(points[:, 1], points[:, 0])
    z = points[:, 2]
    theta_edges = np.linspace(-np.pi, np.pi, N_THETA + 1)
    z_edges = np.linspace(float(np.min(z)), float(np.max(z)), N_Z + 1)
    theta_idx = np.clip(np.digitize(theta, theta_edges) - 1, 0, N_THETA - 1)
    z_idx = np.clip(np.digitize(z, z_edges) - 1, 0, N_Z - 1)
    flat = z_idx * N_THETA + theta_idx
    counts = np.bincount(flat, minlength=N_THETA * N_Z).astype(float)
    return {
        "theta": theta,
        "z": z,
        "theta_idx": theta_idx,
        "z_idx": z_idx,
        "flat": flat,
        "counts": counts,
        "theta_edges": theta_edges,
        "theta_centers": 0.5 * (theta_edges[:-1] + theta_edges[1:]),
        "z_edges": z_edges,
        "z_centers": 0.5 * (z_edges[:-1] + z_edges[1:]),
    }


def bin_mean(values: np.ndarray, flat: np.ndarray, counts: np.ndarray) -> np.ndarray:
    sums = np.bincount(flat, weights=values, minlength=N_THETA * N_Z)
    out = np.divide(sums, counts, out=np.full_like(sums, np.nan), where=counts > 0)
    return out.reshape((N_Z, N_THETA))


def wrapped_diff(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.angle(np.exp(1j * (a - b)))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def pcolormesh(ax, theta_centers: np.ndarray, z_centers: np.ndarray, values: np.ndarray, title: str, label: str, cmap: str = "viridis"):
    im = ax.pcolormesh(np.degrees(theta_centers), z_centers * 1000.0, values, shading="auto", cmap=cmap)
    ax.set_xlabel("theta [deg]")
    ax.set_ylabel("z [mm]")
    ax.set_title(title)
    plt.colorbar(im, ax=ax, label=label)
    return im


def main() -> None:
    ensure_dirs()
    times = list_times()
    points, first_q = read_vtk_points_and_wall_heat_flux(float(times[0]), read_points=True)
    assert points is not None
    bins = build_bins(points)
    lmt_t, lmt = outlet_lmtd_series()
    phase = load_cl_phase(times)
    cl = load_cl(times)
    lmtd_i = np.interp(times, lmt_t, lmt)

    n_bins = N_THETA * N_Z
    counts = bins["counts"]
    theta_centers = bins["theta_centers"]
    z_centers = bins["z_centers"]
    upper_mask = theta_centers > 0.0
    lower_mask = theta_centers < 0.0
    sum_nu = np.zeros(n_bins)
    sum_nu2 = np.zeros(n_bins)
    c1 = np.zeros(n_bins, dtype=complex)
    c2 = np.zeros(n_bins, dtype=complex)
    e1_sum = 0.0j
    e2_sum = 0.0j
    phase_sum = np.zeros((N_PHASE, n_bins))
    phase_count = np.zeros(N_PHASE)
    asym_ts = np.zeros(len(times))
    upper_ts = np.zeros(len(times))
    lower_ts = np.zeros(len(times))

    for i, t in enumerate(times):
        _, q = read_vtk_points_and_wall_heat_flux(float(t), read_points=False)
        nu_points = q * D / (K_AIR * lmtd_i[i])
        binned = bin_mean(nu_points, bins["flat"], counts).reshape(-1)
        valid = np.isfinite(binned)
        sum_nu[valid] += binned[valid]
        sum_nu2[valid] += binned[valid] ** 2
        e1 = np.exp(-1j * phase[i])
        e2 = np.exp(-2j * phase[i])
        e1_sum += e1
        e2_sum += e2
        c1[valid] += binned[valid] * e1
        c2[valid] += binned[valid] * e2
        phase_bin = int(np.floor((phase[i] / (2 * np.pi)) * N_PHASE)) % N_PHASE
        phase_sum[phase_bin, valid] += binned[valid]
        phase_count[phase_bin] += 1.0
        map_i = binned.reshape((N_Z, N_THETA))
        upper_ts[i] = float(np.nanmean(map_i[:, upper_mask]))
        lower_ts[i] = float(np.nanmean(map_i[:, lower_mask]))
        asym_ts[i] = upper_ts[i] - lower_ts[i]

    n = float(len(times))
    mean_map = (sum_nu / n).reshape((N_Z, N_THETA))
    rms_map = np.sqrt(np.maximum(sum_nu2 / n - (sum_nu / n) ** 2, 0.0)).reshape((N_Z, N_THETA))
    mean_flat = sum_nu / n
    # Remove leakage of the steady mean into harmonic coefficients. The Cl phase
    # coverage over a finite record is close to, but not exactly, uniform.
    c1_fluct = c1 - mean_flat * e1_sum
    c2_fluct = c2 - mean_flat * e2_sum
    a1_map = (2.0 * np.abs(c1_fluct) / n).reshape((N_Z, N_THETA))
    phase1_map = np.angle(c1_fluct).reshape((N_Z, N_THETA))
    a2_map = (2.0 * np.abs(c2_fluct) / n).reshape((N_Z, N_THETA))
    phase_avg = np.divide(
        phase_sum,
        phase_count[:, None],
        out=np.full_like(phase_sum, np.nan),
        where=phase_count[:, None] > 0,
    ).reshape((N_PHASE, N_Z, N_THETA))

    theta_profile = np.nanmean(mean_map, axis=0)
    theta_rms_profile = np.nanmean(rms_map, axis=0)
    z_profile = np.nanmean(mean_map, axis=1)

    def theta_nearest(deg: float) -> int:
        return int(np.argmin(np.abs(wrapped_diff(theta_centers, math.radians(deg)))))

    characteristic = {
        "stagnation_0deg": theta_nearest(0.0),
        "side_plus90deg": theta_nearest(90.0),
        "side_minus90deg": theta_nearest(-90.0),
        "wake_180deg": theta_nearest(180.0),
    }

    opposite_idx = np.asarray([int(np.argmin(np.abs(wrapped_diff(theta_centers, -th)))) for th in theta_centers])
    asym_map = mean_map - mean_map[:, opposite_idx]
    asym_theta = theta_profile - theta_profile[opposite_idx]

    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    pcolormesh(axes[0, 0], theta_centers, z_centers, mean_map, "Mean Nu(theta,z)", "Nu")
    pcolormesh(axes[0, 1], theta_centers, z_centers, rms_map, "RMS Nu(theta,z)", "Nu RMS")
    pcolormesh(axes[1, 0], theta_centers, z_centers, a1_map, "A1 at f_shed", "Nu amplitude")
    pcolormesh(axes[1, 1], theta_centers, z_centers, a2_map, "A2 at 2*f_shed", "Nu amplitude")
    fig.savefig(FIG_DIR / "run008_004_tube_nu_maps_mean_rms_harmonics.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    pcolormesh(axes[0], theta_centers, z_centers, phase1_map, "Phase A1 relative to Cl phase", "phase [rad]", cmap="twilight")
    pcolormesh(axes[1], theta_centers, z_centers, asym_map, "Mean Nu(theta,z) - Nu(-theta,z)", "Delta Nu", cmap="coolwarm")
    fig.savefig(FIG_DIR / "run008_004_tube_nu_phase_asymmetry_maps.png", dpi=180)
    plt.close(fig)

    selected_phase = [0, N_PHASE // 8, N_PHASE // 4, 3 * N_PHASE // 8, N_PHASE // 2, 5 * N_PHASE // 8, 3 * N_PHASE // 4, 7 * N_PHASE // 8]
    fig, axes = plt.subplots(2, 4, figsize=(16, 8), constrained_layout=True)
    for ax, p in zip(axes.ravel(), selected_phase):
        pcolormesh(ax, theta_centers, z_centers, phase_avg[p], f"phase bin {p:02d}", "Nu")
    fig.suptitle("Phase-averaged Nu(theta,z,phi)")
    fig.savefig(FIG_DIR / "run008_004_tube_phase_averaged_nu_maps.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
    axes[0].plot(np.degrees(theta_centers), theta_profile, label="mean Nu")
    axes[0].plot(np.degrees(theta_centers), theta_rms_profile, label="RMS Nu")
    axes[0].set_xlabel("theta [deg]")
    axes[0].set_ylabel("Nu")
    axes[0].set_title("Tube Nu(theta), z-averaged")
    axes[0].legend()
    axes[0].grid(alpha=0.25)
    axes[1].plot(np.degrees(theta_centers), asym_theta, color="#8f2d56")
    axes[1].axhline(0, color="black", lw=0.8)
    axes[1].set_xlabel("theta [deg]")
    axes[1].set_ylabel("Delta Nu")
    axes[1].set_title("Top-bottom/as angular antisymmetry: Nu(theta)-Nu(-theta)")
    axes[1].grid(alpha=0.25)
    fig.savefig(FIG_DIR / "run008_004_tube_nu_theta_profiles_asymmetry.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    for label, idx in characteristic.items():
        ax.plot(z_centers * 1000.0, mean_map[:, idx], label=f"{label} ({math.degrees(theta_centers[idx]):.1f} deg)")
    ax.set_xlabel("z [mm]")
    ax.set_ylabel("Mean Nu")
    ax.set_title("Nu(z) at characteristic angular stations")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.savefig(FIG_DIR / "run008_004_tube_nu_z_characteristic_angles.png", dpi=180)
    plt.close(fig)

    asym0 = asym_ts - float(np.mean(asym_ts))
    cl0 = cl - float(np.mean(cl))
    asym_cl_corr = float(np.corrcoef(asym0, cl0)[0, 1])
    dt = float(np.median(np.diff(times)))
    cc = np.correlate(asym0 / np.linalg.norm(asym0), cl0 / np.linalg.norm(cl0), mode="full")
    lag_grid = (np.arange(len(cc)) - (len(cl0) - 1)) * dt
    lag_mask = np.abs(lag_grid) <= 1.0
    lag_best = float(lag_grid[lag_mask][int(np.argmax(cc[lag_mask]))])
    corr_best = float(np.max(cc[lag_mask]))

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
    axes[0].plot(times, (cl0 / np.std(cl0)), label="Cl, standardized", color="#1d4e89")
    axes[0].plot(times, (asym0 / np.std(asym0)), label="upper-lower Nu asymmetry, standardized", color="#9b2226")
    axes[0].set_xlabel("t [s]")
    axes[0].set_ylabel("standardized signal")
    axes[0].set_title("Tube upper-lower Nu asymmetry vs Cl")
    axes[0].legend()
    axes[0].grid(alpha=0.25)
    axes[1].plot(lag_grid[lag_mask], cc[lag_mask], color="#5f0f40")
    axes[1].axvline(0, color="black", lw=0.8)
    axes[1].axvline(lag_best, color="#5f0f40", ls="--", lw=0.9)
    axes[1].set_xlabel("lag [s], positive = asymmetry lags Cl")
    axes[1].set_ylabel("normalized cross-correlation")
    axes[1].set_title(f"corr0={asym_cl_corr:+.3f}, best={corr_best:+.3f} at lag={lag_best:+.3f}s")
    axes[1].grid(alpha=0.25)
    fig.savefig(FIG_DIR / "run008_004_tube_asymmetry_vs_cl.png", dpi=180)
    plt.close(fig)

    phase_centers = (np.arange(N_PHASE) + 0.5) * 2 * np.pi / N_PHASE
    rows = []
    for iz, zc in enumerate(z_centers):
        for it, th in enumerate(theta_centers):
            rows.append(
                {
                    "theta_rad": float(th),
                    "theta_deg": float(math.degrees(th)),
                    "z_m": float(zc),
                    "Nu_mean": float(mean_map[iz, it]),
                    "Nu_rms": float(rms_map[iz, it]),
                    "A1": float(a1_map[iz, it]),
                    "phase1_rad": float(phase1_map[iz, it]),
                    "A2": float(a2_map[iz, it]),
                    "asym_mean_minus_opposite": float(asym_map[iz, it]),
                }
            )
    write_csv(DATA_DIR / "run008_004_tube_nu_theta_z_maps.csv", rows)
    write_csv(
        DATA_DIR / "run008_004_tube_nu_theta_profile.csv",
        [
            {
                "theta_rad": float(th),
                "theta_deg": float(math.degrees(th)),
                "Nu_mean_zavg": float(theta_profile[i]),
                "Nu_rms_zavg": float(theta_rms_profile[i]),
                "asym_Nu_theta_minus_minus_theta": float(asym_theta[i]),
            }
            for i, th in enumerate(theta_centers)
        ],
    )
    z_rows = []
    for label, idx in characteristic.items():
        for iz, zc in enumerate(z_centers):
            z_rows.append(
                {
                    "station": label,
                    "theta_deg": float(math.degrees(theta_centers[idx])),
                    "z_m": float(zc),
                    "Nu_mean": float(mean_map[iz, idx]),
                    "Nu_rms": float(rms_map[iz, idx]),
                }
            )
    write_csv(DATA_DIR / "run008_004_tube_nu_z_characteristic_angles.csv", z_rows)
    phase_rows = []
    for p, ph in enumerate(phase_centers):
        phase_rows.append(
            {
                "phase_bin": p,
                "phase_rad": float(ph),
                "Nu_mean_global": float(np.nanmean(phase_avg[p])),
                "Nu_max_global": float(np.nanmax(phase_avg[p])),
                "Nu_min_global": float(np.nanmin(phase_avg[p])),
            }
        )
    write_csv(DATA_DIR / "run008_004_tube_phase_average_summary.csv", phase_rows)
    write_csv(
        DATA_DIR / "run008_004_tube_asymmetry_vs_cl.csv",
        [
            {
                "time": float(times[i]),
                "Cl": float(cl[i]),
                "Nu_upper_mean": float(upper_ts[i]),
                "Nu_lower_mean": float(lower_ts[i]),
                "Nu_upper_minus_lower": float(asym_ts[i]),
            }
            for i in range(len(times))
        ],
    )
    np.savez_compressed(
        DATA_DIR / "run008_004_tube_nu_arrays.npz",
        theta_centers=theta_centers,
        z_centers=z_centers,
        phase_centers=phase_centers,
        mean_map=mean_map,
        rms_map=rms_map,
        A1=a1_map,
        phase1=phase1_map,
        A2=a2_map,
        phase_average=phase_avg,
        asym_map=asym_map,
    )

    summary = [
        TubeSummary("n_times", float(len(times))),
        TubeSummary("n_theta_bins", float(N_THETA)),
        TubeSummary("n_z_bins", float(N_Z)),
        TubeSummary("Nu_mean_area_proxy", float(np.nanmean(mean_map))),
        TubeSummary("Nu_rms_area_proxy", float(np.nanmean(rms_map))),
        TubeSummary("A1_mean", float(np.nanmean(a1_map))),
        TubeSummary("A1_max", float(np.nanmax(a1_map))),
        TubeSummary("A2_mean", float(np.nanmean(a2_map))),
        TubeSummary("A2_max", float(np.nanmax(a2_map))),
        TubeSummary("asym_abs_mean", float(np.nanmean(np.abs(asym_map)))),
        TubeSummary("asym_abs_max", float(np.nanmax(np.abs(asym_map)))),
        TubeSummary("theta_profile_max_deg", float(math.degrees(theta_centers[int(np.nanargmax(theta_profile))]))),
        TubeSummary("theta_profile_min_deg", float(math.degrees(theta_centers[int(np.nanargmin(theta_profile))]))),
        TubeSummary("upper_lower_asym_corr_with_Cl_zero_lag", asym_cl_corr),
        TubeSummary("upper_lower_asym_best_lag_s_positive_asym_lags_Cl", lag_best),
        TubeSummary("upper_lower_asym_best_lag_corr", corr_best),
    ]
    write_csv(DATA_DIR / "run008_004_tube_nu_summary.csv", [asdict(s) for s in summary])
    (DATA_DIR / "run008_004_tube_nu_summary.json").write_text(
        json.dumps({"summary": [asdict(s) for s in summary], "definition": "Nu=q''*D/(k*LMTD(t)); phase from Cl analytic signal"}, indent=2),
        encoding="utf-8",
    )

    lookup = {s.metric: s.value for s in summary}
    lines = [
        "# V4b_3D run008 local tube Nu",
        "",
        f"Primary window: `{WINDOW[0]:.1f}..{WINDOW[1]:.1f} s`, samples `{len(times)}`.",
        "Definition: `Nu(theta,z,t) = q''(theta,z,t) D / (k LMTD(t))`; `LMTD(t)` comes from reconstructed outlet `T`.",
        "Phase reference: `Cl` analytic signal from layer `002`.",
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
            f"- Mean local tube Nu proxy is `{lookup['Nu_mean_area_proxy']:.3f}`; peak z-averaged Nu occurs near `theta = {lookup['theta_profile_max_deg']:.1f} deg`.",
            f"- First-harmonic local modulation is modest on average (`A1_mean = {lookup['A1_mean']:.3f}`) but localized peaks reach `A1_max = {lookup['A1_max']:.3f}`.",
            f"- Second-harmonic modulation is comparable in places (`A2_max = {lookup['A2_max']:.3f}`), consistent with the strong `2*f_shed` component seen in forces.",
            f"- Mean angular asymmetry magnitude is `{lookup['asym_abs_mean']:.3f}` Nu, with local extrema up to `{lookup['asym_abs_max']:.3f}` Nu.",
            f"- Global upper-lower Nu asymmetry has zero-lag correlation `{lookup['upper_lower_asym_corr_with_Cl_zero_lag']:+.3f}` with `Cl`; best short-lag correlation is `{lookup['upper_lower_asym_best_lag_corr']:+.3f}` at `{lookup['upper_lower_asym_best_lag_s_positive_asym_lags_Cl']:+.3f} s`.",
            "",
            "## Figures",
            "",
            "- `../../figures/004/run008_004_tube_nu_maps_mean_rms_harmonics.png`",
            "- `../../figures/004/run008_004_tube_nu_phase_asymmetry_maps.png`",
            "- `../../figures/004/run008_004_tube_phase_averaged_nu_maps.png`",
            "- `../../figures/004/run008_004_tube_nu_theta_profiles_asymmetry.png`",
            "- `../../figures/004/run008_004_tube_nu_z_characteristic_angles.png`",
            "- `../../figures/004/run008_004_tube_asymmetry_vs_cl.png`",
        ]
    )
    (DATA_DIR / "run008_004_tube_local_nu.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print((DATA_DIR / "run008_004_tube_local_nu.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
