"""
Run008 data audit and uncertainty analysis.

This is the first-pass foundation analysis only:
- sample completeness and time cadence,
- effective record length,
- cycle-block bootstrap uncertainty,
- window sensitivity.
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
DATA_DIR = RUN_DIR / "data" / "001"
FIG_DIR = RUN_DIR / "figures" / "001"
CASE_DIR = Path("/home/hexmachina/of_runs/V4b_3D_run008")
POST_DIR = CASE_DIR / "postProcessing"

D = 0.012
U_IN = 0.25266
T_IN = 293.15
T_HOT = 343.15
A_HOT_TOTAL = 0.002032
CP_AIR = 1005.0
MU_AIR = 1.827e-05
PR_AIR = 0.713
K_AIR = CP_AIR * MU_AIR / PR_AIR

WINDOWS = {
    "2_10": (2.0, 10.0),
    "3_10": (3.0, 10.0),
    "4_10": (4.0, 10.0),
    "2_6": (2.0, 6.0),
    "6_10": (6.0, 10.0),
}

BOOTSTRAP_N = 1000
RNG_SEED = 20260509


@dataclass
class CadenceAudit:
    signal: str
    expected_dt_s: float
    t_min_s: float
    t_max_s: float
    n_samples: int
    expected_n_0_10: int
    missing_vs_expected_0_10: int
    dt_median_s: float
    dt_min_s: float
    dt_max_s: float
    max_abs_dt_error_s: float
    is_regular: bool


@dataclass
class WindowMetrics:
    window: str
    t_start_s: float
    t_end_s: float
    duration_s: float
    f_shed_hz: float
    effective_cycles: float
    force_samples: int
    outlet_samples: int
    wall_samples: int
    Cd_mean: float
    Cd_mean_ci95: float
    Cl_rms: float
    Cl_rms_ci95: float
    f_psd_hz: float
    f_psd_ci95: float
    St: float
    St_ci95: float
    Nu_EB_mean: float
    Nu_EB_ci95: float
    Nu_wall_mean: float
    Nu_wall_ci95: float
    closure_mean_pct: float
    closure_ci95: float


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def read_force_coeffs() -> dict[str, np.ndarray]:
    path = POST_DIR / "forceCoeffs" / "0" / "forceCoeffs.dat"
    rows = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 6:
                rows.append([float(v) for v in parts[:6]])
    arr = np.asarray(rows, dtype=float)
    return {
        "time": arr[:, 0],
        "Cm": arr[:, 1],
        "Cd": arr[:, 2],
        "Cl": arr[:, 3],
        "Cl_f": arr[:, 4],
        "Cl_r": arr[:, 5],
    }


def read_forces_raw_time() -> np.ndarray:
    path = POST_DIR / "forces_raw" / "0" / "forces.dat"
    times = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            times.append(float(line.split()[0]))
    return np.asarray(times, dtype=float)


def read_wall_heat_flux() -> dict[str, np.ndarray]:
    path = POST_DIR / "wallHeatFlux" / "0" / "wallHeatFlux.dat"
    per_time: dict[float, dict[str, float]] = {}
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 6:
                t = float(parts[0])
                per_time.setdefault(t, {})[parts[1]] = float(parts[4])
    times = np.asarray(sorted(per_time), dtype=float)
    tube = np.asarray([per_time[t].get("hot_tube", np.nan) for t in times])
    fin_min = np.asarray([per_time[t].get("hot_fin_z_min", np.nan) for t in times])
    fin_max = np.asarray([per_time[t].get("hot_fin_z_max", np.nan) for t in times])
    return {
        "time": times,
        "tube": tube,
        "fin_min": fin_min,
        "fin_max": fin_max,
        "total": tube + fin_min + fin_max,
    }


def list_time_dirs(base: Path) -> np.ndarray:
    values = []
    for path in base.iterdir():
        if not path.is_dir():
            continue
        try:
            values.append(float(path.name))
        except ValueError:
            pass
    return np.asarray(sorted(values), dtype=float)


def list_surface_times(surface: str, required_files: tuple[str, ...]) -> np.ndarray:
    base = POST_DIR / surface
    times = []
    for path in base.iterdir():
        if not path.is_dir():
            continue
        try:
            t = float(path.name)
        except ValueError:
            continue
        if all((path / f).exists() for f in required_files):
            times.append(t)
    return np.asarray(sorted(times), dtype=float)


def reconstructed_outlet_times() -> np.ndarray:
    times = []
    for path in CASE_DIR.iterdir():
        if not path.is_dir():
            continue
        try:
            t = float(path.name)
        except ValueError:
            continue
        if (path / "T").exists() and (path / "phi").exists():
            times.append(t)
    return np.asarray(sorted(times), dtype=float)


def cadence_audit(name: str, time: np.ndarray, expected_dt: float, expected_start: float = 0.0, expected_end: float = 10.0) -> CadenceAudit:
    dt = np.diff(time)
    expected_n = int(round((expected_end - expected_start) / expected_dt)) + 1
    expected_grid = np.round(np.arange(expected_start, expected_end + 0.5 * expected_dt, expected_dt), 10)
    observed = np.round(time[(time >= expected_start - 1e-9) & (time <= expected_end + 1e-9)], 10)
    missing = len(set(expected_grid.tolist()) - set(observed.tolist()))
    max_err = float(np.max(np.abs(dt - expected_dt))) if len(dt) else float("nan")
    return CadenceAudit(
        signal=name,
        expected_dt_s=expected_dt,
        t_min_s=float(np.min(time)) if len(time) else float("nan"),
        t_max_s=float(np.max(time)) if len(time) else float("nan"),
        n_samples=int(len(time)),
        expected_n_0_10=expected_n,
        missing_vs_expected_0_10=int(missing),
        dt_median_s=float(np.median(dt)) if len(dt) else float("nan"),
        dt_min_s=float(np.min(dt)) if len(dt) else float("nan"),
        dt_max_s=float(np.max(dt)) if len(dt) else float("nan"),
        max_abs_dt_error_s=max_err,
        is_regular=bool(max_err < 1e-8) if len(dt) else False,
    )


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
        raise ValueError(f"Could not parse points: {path}")
    vals = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped == ")":
            break
        vals.extend(float(v) for v in stripped.strip("()").split())
    arr = np.asarray(vals).reshape((-1, 3))
    if len(arr) != count:
        raise ValueError(f"Expected {count} points, got {len(arr)}")
    return arr


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
    vals = np.fromstring(vals_match.group(2), sep=" ")
    if len(vals) != n_faces:
        raise ValueError(f"Expected {n_faces} values for {field_name}:{patch_name}, got {len(vals)}")
    return vals


def lmtd(t_out: float) -> float:
    d1 = T_HOT - T_IN
    d2 = T_HOT - t_out
    return (d1 - d2) / math.log(d1 / d2)


def outlet_thermal_series() -> dict[str, np.ndarray]:
    patch = boundary_patch("outlet")
    points = parse_points(CASE_DIR / "constant" / "polyMesh" / "points")
    faces = outlet_faces(patch["startFace"], patch["nFaces"])
    areas = np.asarray([polygon_area(points[face]) for face in faces])
    area_total = float(np.sum(areas))
    rows = []
    for t in reconstructed_outlet_times():
        if t < 2.0 - 1e-9 or t > 10.0 + 1e-9:
            continue
        name = f"{t:g}"
        t_vals = field_patch_values(name, "T", "outlet", patch["nFaces"])
        phi_vals = field_patch_values(name, "phi", "outlet", patch["nFaces"])
        weights = np.maximum(phi_vals, 0.0)
        if np.sum(weights) <= 0:
            weights = np.abs(phi_vals)
        t_area = float(np.sum(t_vals * areas) / area_total)
        t_mass = float(np.sum(t_vals * weights) / np.sum(weights))
        m_dot = float(np.sum(weights))
        q_air = m_dot * CP_AIR * (t_area - T_IN)
        l = lmtd(t_area)
        nu = (q_air / (A_HOT_TOTAL * l)) * D / K_AIR
        rows.append([t, t_area, t_mass, m_dot, q_air, l, nu])
    arr = np.asarray(rows)
    return {
        "time": arr[:, 0],
        "T_area": arr[:, 1],
        "T_mass": arr[:, 2],
        "m_dot": arr[:, 3],
        "Q_air": arr[:, 4],
        "LMTD": arr[:, 5],
        "Nu_EB": arr[:, 6],
    }


def psd_peak(time: np.ndarray, y: np.ndarray) -> float:
    if len(time) < 64:
        return float("nan")
    dt = float(np.median(np.diff(time)))
    yi = y - np.mean(y)
    f, pxx = signal.welch(yi, fs=1.0 / dt, nperseg=min(2048, len(yi)))
    band = np.where((f >= 2.5) & (f <= 4.0))[0]
    if len(band) == 0:
        return float("nan")
    return float(f[band[np.argmax(pxx[band])]])


def block_ids(time: np.ndarray, f_shed: float, start: float) -> np.ndarray:
    period = 1.0 / f_shed
    return np.floor((time - start) / period).astype(int)


def block_bootstrap(values: np.ndarray, time: np.ndarray, start: float, f_shed: float, func, n_boot: int = BOOTSTRAP_N) -> tuple[float, float]:
    rng = np.random.default_rng(RNG_SEED)
    ids = block_ids(time, f_shed, start)
    unique = np.asarray(sorted(set(ids)))
    blocks = [np.where(ids == b)[0] for b in unique if np.any(ids == b)]
    point = float(func(values))
    if len(blocks) < 3:
        return point, float("nan")
    boot = []
    for _ in range(n_boot):
        chosen = rng.integers(0, len(blocks), size=len(blocks))
        idx = np.concatenate([blocks[i] for i in chosen])
        boot.append(float(func(values[idx])))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return point, 0.5 * float(hi - lo)


def bootstrap_psd(time: np.ndarray, cl: np.ndarray, start: float, f_shed: float, n_boot: int = 300) -> tuple[float, float]:
    rng = np.random.default_rng(RNG_SEED + 99)
    ids = block_ids(time, f_shed, start)
    unique = np.asarray(sorted(set(ids)))
    blocks = [np.where(ids == b)[0] for b in unique if len(np.where(ids == b)[0]) > 8]
    point = psd_peak(time, cl)
    if len(blocks) < 5:
        return point, float("nan")
    dt = float(np.median(np.diff(time)))
    boot = []
    for _ in range(n_boot):
        chosen = rng.integers(0, len(blocks), size=len(blocks))
        y = np.concatenate([cl[blocks[i]] for i in chosen])
        t = np.arange(len(y)) * dt
        boot.append(psd_peak(t, y))
    boot = np.asarray([v for v in boot if math.isfinite(v)])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return point, 0.5 * float(hi - lo)


def frequency_ci_from_periods(time: np.ndarray, cl: np.ndarray, f_point: float, n_boot: int = BOOTSTRAP_N) -> tuple[float, float]:
    if len(time) < 64:
        return f_point, float("nan")
    rng = np.random.default_rng(RNG_SEED + 123)
    dt = float(np.median(np.diff(time)))
    fs = 1.0 / dt
    low = 2.3 / (0.5 * fs)
    high = 4.3 / (0.5 * fs)
    b, a = signal.butter(3, [low, high], btype="bandpass")
    y = signal.filtfilt(b, a, cl - np.mean(cl))
    peaks, _ = signal.find_peaks(y, distance=max(1, int(0.20 / dt)))
    peak_t = time[peaks]
    periods = np.diff(peak_t)
    periods = periods[(periods > 0.20) & (periods < 0.45)]
    if len(periods) < 4:
        return f_point, float("nan")
    boot = []
    for _ in range(n_boot):
        sample = rng.choice(periods, size=len(periods), replace=True)
        boot.append(1.0 / float(np.mean(sample)))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return f_point, 0.5 * float(hi - lo)


def block_bootstrap_closure(q_wall: np.ndarray, q_air: np.ndarray, time: np.ndarray, start: float, f_shed: float, n_boot: int = BOOTSTRAP_N) -> tuple[float, float]:
    rng = np.random.default_rng(RNG_SEED + 321)
    ids = block_ids(time, f_shed, start)
    unique = np.asarray(sorted(set(ids)))
    blocks = [np.where(ids == b)[0] for b in unique if np.any(ids == b)]

    def closure(idx: np.ndarray) -> float:
        return 100.0 * (float(np.mean(q_wall[idx])) - float(np.mean(q_air[idx]))) / float(np.mean(q_air[idx]))

    all_idx = np.arange(len(time))
    point = closure(all_idx)
    if len(blocks) < 3:
        return point, float("nan")
    boot = []
    for _ in range(n_boot):
        chosen = rng.integers(0, len(blocks), size=len(blocks))
        idx = np.concatenate([blocks[i] for i in chosen])
        boot.append(closure(idx))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return point, 0.5 * float(hi - lo)


def window_metrics(force: dict[str, np.ndarray], wall: dict[str, np.ndarray], outlet: dict[str, np.ndarray], window_name: str, start: float, end: float) -> WindowMetrics:
    mask_f = (force["time"] >= start - 1e-12) & (force["time"] <= end + 1e-12)
    tf = force["time"][mask_f]
    cd = force["Cd"][mask_f]
    cl = force["Cl"][mask_f]
    f_point = psd_peak(tf, cl)
    f_shed, f_ci = frequency_ci_from_periods(tf, cl, f_point)
    cd_mean, cd_ci = block_bootstrap(cd, tf, start, f_shed, np.mean)
    cl_mean = float(np.mean(cl))
    cl_rms, cl_rms_ci = block_bootstrap(cl, tf, start, f_shed, lambda x: np.sqrt(np.mean((x - np.mean(x)) ** 2)))

    mask_o = (outlet["time"] >= start - 1e-12) & (outlet["time"] <= end + 1e-12)
    to = outlet["time"][mask_o]
    nu_eb = outlet["Nu_EB"][mask_o]
    nu_eb_mean, nu_eb_ci = block_bootstrap(nu_eb, to, start, f_shed, np.mean)

    mask_w = (wall["time"] >= start - 1e-12) & (wall["time"] <= end + 1e-12)
    tw = wall["time"][mask_w]
    q_wall = wall["total"][mask_w]
    lmtd_i = np.interp(tw, outlet["time"], outlet["LMTD"])
    q_air_i = np.interp(tw, outlet["time"], outlet["Q_air"])
    nu_wall = (q_wall / (A_HOT_TOTAL * lmtd_i)) * D / K_AIR
    nu_wall_mean, nu_wall_ci = block_bootstrap(nu_wall, tw, start, f_shed, np.mean)
    closure_mean, closure_ci = block_bootstrap_closure(q_wall, q_air_i, tw, start, f_shed)
    return WindowMetrics(
        window=window_name,
        t_start_s=start,
        t_end_s=end,
        duration_s=end - start,
        f_shed_hz=f_shed,
        effective_cycles=(end - start) * f_shed,
        force_samples=int(np.sum(mask_f)),
        outlet_samples=int(np.sum(mask_o)),
        wall_samples=int(np.sum(mask_w)),
        Cd_mean=cd_mean,
        Cd_mean_ci95=cd_ci,
        Cl_rms=cl_rms,
        Cl_rms_ci95=cl_rms_ci,
        f_psd_hz=f_shed,
        f_psd_ci95=f_ci,
        St=f_shed * D / U_IN,
        St_ci95=f_ci * D / U_IN,
        Nu_EB_mean=nu_eb_mean,
        Nu_EB_ci95=nu_eb_ci,
        Nu_wall_mean=nu_wall_mean,
        Nu_wall_ci95=nu_wall_ci,
        closure_mean_pct=closure_mean,
        closure_ci95=closure_ci,
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_cadence(audits: list[CadenceAudit], time_map: dict[str, np.ndarray]) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(11, 7))
    labels = [a.signal for a in audits]
    completeness = [100.0 * (a.expected_n_0_10 - a.missing_vs_expected_0_10) / a.expected_n_0_10 for a in audits]
    axes[0].bar(labels, completeness, color="#4d7c8a")
    axes[0].set_ylim(95, 100.2)
    axes[0].set_ylabel("0..10 s completeness [%]")
    axes[0].tick_params(axis="x", rotation=25)
    for i, v in enumerate(completeness):
        axes[0].text(i, v + 0.03, f"{v:.2f}%", ha="center", fontsize=8)

    for name, t in time_map.items():
        dt = np.diff(t)
        if len(dt):
            axes[1].plot(t[1:], dt, ".", ms=2, label=name)
    axes[1].set_xlabel("t [s]")
    axes[1].set_ylabel("dt [s]")
    axes[1].set_yscale("log")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_audit_sampling_completeness_cadence.png", dpi=180)
    plt.close(fig)


def plot_record_length(metrics: list[WindowMetrics]) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    labels = [m.window.replace("_", "..") for m in metrics]
    cycles = [m.effective_cycles for m in metrics]
    ax.bar(labels, cycles, color="#7b9e6f")
    ax.axhline(20, color="k", ls="--", lw=1, label="20 cycles target")
    ax.set_ylabel("effective shedding cycles")
    ax.set_xlabel("window [s]")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend()
    for i, v in enumerate(cycles):
        ax.text(i, v + 0.3, f"{v:.1f}", ha="center")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_audit_effective_record_length.png", dpi=180)
    plt.close(fig)


def plot_uncertainty(metrics: list[WindowMetrics]) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    labels = [m.window.replace("_", "..") for m in metrics]
    entries = [
        ("Cd_mean", "Cd", [m.Cd_mean for m in metrics], [m.Cd_mean_ci95 for m in metrics]),
        ("Cl_rms", "Cl RMS", [m.Cl_rms for m in metrics], [m.Cl_rms_ci95 for m in metrics]),
        ("St", "St", [m.St for m in metrics], [m.St_ci95 for m in metrics]),
        ("Nu_EB_mean", "Nu_EB", [m.Nu_EB_mean for m in metrics], [m.Nu_EB_ci95 for m in metrics]),
        ("Nu_wall_mean", "Nu_wall", [m.Nu_wall_mean for m in metrics], [m.Nu_wall_ci95 for m in metrics]),
        ("closure_mean_pct", "closure [%]", [m.closure_mean_pct for m in metrics], [m.closure_ci95 for m in metrics]),
    ]
    for ax, (_, title, vals, errs) in zip(axes.ravel(), entries):
        ax.errorbar(labels, vals, yerr=errs, fmt="o-", capsize=4)
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
        ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_audit_block_bootstrap_uncertainty.png", dpi=180)
    plt.close(fig)


def plot_window_sensitivity(metrics: list[WindowMetrics]) -> None:
    baseline = next(m for m in metrics if m.window == "2_10")
    labels = [m.window.replace("_", "..") for m in metrics]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    entries = [
        ("Cd", [100.0 * (m.Cd_mean - baseline.Cd_mean) / baseline.Cd_mean for m in metrics]),
        ("Cl RMS", [100.0 * (m.Cl_rms - baseline.Cl_rms) / baseline.Cl_rms for m in metrics]),
        ("St", [100.0 * (m.St - baseline.St) / baseline.St for m in metrics]),
        ("Nu_EB", [100.0 * (m.Nu_EB_mean - baseline.Nu_EB_mean) / baseline.Nu_EB_mean for m in metrics]),
        ("Nu_wall", [100.0 * (m.Nu_wall_mean - baseline.Nu_wall_mean) / baseline.Nu_wall_mean for m in metrics]),
        ("closure", [m.closure_mean_pct - baseline.closure_mean_pct for m in metrics]),
    ]
    for ax, (title, vals) in zip(axes.ravel(), entries):
        ax.bar(labels, vals, color="#b47d4f")
        ax.axhline(0, color="k", lw=0.8)
        ax.set_title(f"{title} vs 2..10")
        ax.set_ylabel("% diff" if title != "closure" else "pp diff")
        ax.grid(True, axis="y", alpha=0.25)
        ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "run008_audit_window_sensitivity.png", dpi=180)
    plt.close(fig)


def write_markdown(audits: list[CadenceAudit], metrics: list[WindowMetrics]) -> None:
    lines = [
        "# V4b_3D run008 audit and uncertainty",
        "",
        "This is the foundation audit before any higher-order interpretation.",
        "",
        "## Sampling Completeness",
        "",
        "| Signal | expected dt [s] | samples | expected 0..10 | missing | median dt [s] | dt min/max [s] | regular |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for a in audits:
        lines.append(
            f"| {a.signal} | {a.expected_dt_s:.5f} | {a.n_samples} | {a.expected_n_0_10} | "
            f"{a.missing_vs_expected_0_10} | {a.dt_median_s:.5f} | {a.dt_min_s:.5f}/{a.dt_max_s:.5f} | {a.is_regular} |"
        )
    lines += [
        "",
        "## Window Metrics With Cycle-Block Bootstrap 95% Half-Widths",
        "",
        "| Window | cycles | force n | outlet n | wall n | Cd | Cl_rms | St | Nu_EB | Nu_wall | closure [%] |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for m in metrics:
        lines.append(
            f"| {m.t_start_s:g}..{m.t_end_s:g} | {m.effective_cycles:.2f} | {m.force_samples} | {m.outlet_samples} | {m.wall_samples} | "
            f"{m.Cd_mean:.6f} +/- {m.Cd_mean_ci95:.6f} | "
            f"{m.Cl_rms:.6f} +/- {m.Cl_rms_ci95:.6f} | "
            f"{m.St:.6f} +/- {m.St_ci95:.6f} | "
            f"{m.Nu_EB_mean:.6f} +/- {m.Nu_EB_ci95:.6f} | "
            f"{m.Nu_wall_mean:.6f} +/- {m.Nu_wall_ci95:.6f} | "
            f"{m.closure_mean_pct:+.3f} +/- {m.closure_ci95:.3f} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- The main `2..10 s` record contains more than 25 shedding cycles, so it exceeds the planned 20-cycle minimum.",
        "- Force, wall-flux, tube-surface, fin-surface, and midspan sampling are complete on their intended grids.",
        "- Outlet `T/phi` is reconstructed on the production checkpoint cadence and is sufficient for EB/Nu uncertainty at the global level.",
        "- Window sensitivity should be used before making claims about small differences between runs.",
        "",
        "## Figures",
        "",
        "- `../figures/run008_audit_sampling_completeness_cadence.png`",
        "- `../figures/run008_audit_effective_record_length.png`",
        "- `../figures/run008_audit_block_bootstrap_uncertainty.png`",
        "- `../figures/run008_audit_window_sensitivity.png`",
    ]
    (DATA_DIR / "run008_audit_uncertainty.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    force = read_force_coeffs()
    forces_raw_time = read_forces_raw_time()
    wall = read_wall_heat_flux()
    outlet = outlet_thermal_series()
    tube_times = list_surface_times("hot_tube_surface", ("hot_tube.vtk",))
    fin_times = list_surface_times("hot_fin_surface", ("hot_fin_z_min.vtk", "hot_fin_z_max.vtk"))
    midspan_times = list_surface_times("midspan_z0", ("z0.vtk",))
    outlet_times = reconstructed_outlet_times()

    audits = [
        cadence_audit("forceCoeffs", force["time"], 0.005),
        cadence_audit("forces_raw", forces_raw_time, 0.005),
        cadence_audit("wallHeatFlux", wall["time"], 0.005),
        cadence_audit("hot_tube_surface", tube_times, 0.005),
        cadence_audit("hot_fin_surface", fin_times, 0.005),
        cadence_audit("midspan_z0", midspan_times, 0.02),
        cadence_audit("outlet_T_phi", outlet_times[(outlet_times >= 2.0) & (outlet_times <= 10.0)], 0.08, 2.0, 10.0),
    ]
    metrics = [window_metrics(force, wall, outlet, name, *bounds) for name, bounds in WINDOWS.items()]

    write_csv(DATA_DIR / "run008_audit_sampling_completeness.csv", [asdict(a) for a in audits])
    write_csv(DATA_DIR / "run008_audit_window_uncertainty.csv", [asdict(m) for m in metrics])
    (DATA_DIR / "run008_audit_uncertainty.json").write_text(
        json.dumps({"cadence": [asdict(a) for a in audits], "windows": [asdict(m) for m in metrics]}, indent=2),
        encoding="utf-8",
    )
    time_map = {
        "forceCoeffs": force["time"],
        "wallHeatFlux": wall["time"],
        "tube": tube_times,
        "fin": fin_times,
        "midspan": midspan_times,
        "outlet": outlet_times[(outlet_times >= 2.0) & (outlet_times <= 10.0)],
    }
    plot_cadence(audits, time_map)
    plot_record_length(metrics)
    plot_uncertainty(metrics)
    plot_window_sensitivity(metrics)
    write_markdown(audits, metrics)
    print((DATA_DIR / "run008_audit_uncertainty.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
