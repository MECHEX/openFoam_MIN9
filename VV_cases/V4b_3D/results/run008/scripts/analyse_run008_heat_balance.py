"""
Run008 heat-balance closure analysis.

Layer 003:
- Q_air, Q_wall, Q_tube, Q_fin_z_min, Q_fin_z_max time histories,
- instantaneous and mean wall-air closure,
- transport lag between wall heat release and outlet response,
- tube/fin heat share,
- Nu_wall split by tube/fins and comparison with Nu_EB.
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
DATA_DIR = RUN_DIR / "data" / "003"
FIG_DIR = RUN_DIR / "figures" / "003"
CASE_DIR = Path("/home/hexmachina/of_runs/V4b_3D_run008")
POST_DIR = CASE_DIR / "postProcessing"

D = 0.012
U_IN = 0.25266
T_IN = 293.15
T_HOT = 343.15
CP_AIR = 1005.0
MU_AIR = 1.827e-05
PR_AIR = 0.713
K_AIR = CP_AIR * MU_AIR / PR_AIR

A_HOT_TOTAL = 0.002032

WINDOW = (2.0, 10.0)


@dataclass
class HeatSummary:
    metric: str
    mean: float
    std: float
    minimum: float
    maximum: float


@dataclass
class LagSummary:
    pair: str
    lag_s: float
    lag_over_period: float
    correlation: float
    interpretation: str


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def read_wall_heat_flux() -> dict[str, np.ndarray]:
    path = POST_DIR / "wallHeatFlux" / "0" / "wallHeatFlux.dat"
    per_time: dict[float, dict[str, dict[str, float]]] = {}
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 6:
                per_time.setdefault(float(parts[0]), {})[parts[1]] = {
                    "Q": float(parts[4]),
                    "q": float(parts[5]),
                }
    times = np.asarray(sorted(per_time), dtype=float)
    tube = np.asarray([per_time[t].get("hot_tube", {}).get("Q", np.nan) for t in times])
    fin_min = np.asarray([per_time[t].get("hot_fin_z_min", {}).get("Q", np.nan) for t in times])
    fin_max = np.asarray([per_time[t].get("hot_fin_z_max", {}).get("Q", np.nan) for t in times])
    tube_area_raw = np.asarray([per_time[t].get("hot_tube", {}).get("Q", np.nan) / per_time[t].get("hot_tube", {}).get("q", np.nan) for t in times])
    fin_min_area_raw = np.asarray([per_time[t].get("hot_fin_z_min", {}).get("Q", np.nan) / per_time[t].get("hot_fin_z_min", {}).get("q", np.nan) for t in times])
    fin_max_area_raw = np.asarray([per_time[t].get("hot_fin_z_max", {}).get("Q", np.nan) / per_time[t].get("hot_fin_z_max", {}).get("q", np.nan) for t in times])
    return {
        "time": times,
        "Q_tube": tube,
        "Q_fin_min": fin_min,
        "Q_fin_max": fin_max,
        "Q_fins": fin_min + fin_max,
        "Q_wall": tube + fin_min + fin_max,
        "A_tube_raw": tube_area_raw,
        "A_fin_min_raw": fin_min_area_raw,
        "A_fin_max_raw": fin_max_area_raw,
    }


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
    arr = np.asarray(values).reshape((-1, 3))
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
        if t < WINDOW[0] - 1e-9 or t > WINDOW[1] + 1e-9:
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
        q_air_area = m_dot * CP_AIR * (t_area - T_IN)
        q_air_mass = m_dot * CP_AIR * (t_mass - T_IN)
        l_area = lmtd(t_area)
        l_mass = lmtd(t_mass)
        nu_area = (q_air_area / (A_HOT_TOTAL * l_area)) * D / K_AIR
        nu_mass = (q_air_mass / (A_HOT_TOTAL * l_mass)) * D / K_AIR
        rows.append([t, t_area, t_mass, m_dot, q_air_area, q_air_mass, l_area, l_mass, nu_area, nu_mass])
    arr = np.asarray(rows)
    return {
        "time": arr[:, 0],
        "T_area": arr[:, 1],
        "T_mass": arr[:, 2],
        "m_dot": arr[:, 3],
        "Q_air": arr[:, 4],
        "Q_air_massT": arr[:, 5],
        "LMTD": arr[:, 6],
        "LMTD_massT": arr[:, 7],
        "Nu_EB": arr[:, 8],
        "Nu_EB_massT": arr[:, 9],
    }


def mask_window(time: np.ndarray) -> np.ndarray:
    return (time >= WINDOW[0] - 1e-12) & (time <= WINDOW[1] + 1e-12)


def interp_to(time_new: np.ndarray, source_time: np.ndarray, source_values: np.ndarray) -> np.ndarray:
    return np.interp(time_new, source_time, source_values)


def summarize(name: str, values: np.ndarray) -> HeatSummary:
    return HeatSummary(
        metric=name,
        mean=float(np.mean(values)),
        std=float(np.std(values, ddof=1)),
        minimum=float(np.min(values)),
        maximum=float(np.max(values)),
    )


def cross_correlation_lag(time: np.ndarray, x: np.ndarray, y: np.ndarray, f_shed: float, pair: str) -> LagSummary:
    dt = float(np.median(np.diff(time)))
    x0 = x - float(np.mean(x))
    y0 = y - float(np.mean(y))
    corr = signal.correlate(y0, x0, mode="full")
    lags = signal.correlation_lags(len(y0), len(x0), mode="full") * dt
    max_lag = 2.0
    valid = np.abs(lags) <= max_lag
    idx = np.argmax(corr[valid])
    lag = float(lags[valid][idx])
    denom = float(np.linalg.norm(x0) * np.linalg.norm(y0))
    c = float(corr[valid][idx] / denom) if denom else float("nan")
    interpretation = "positive lag means the second signal lags the first"
    return LagSummary(pair=pair, lag_s=lag, lag_over_period=lag * f_shed, correlation=c, interpretation=interpretation)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def scaled_patch_areas(wall: dict[str, np.ndarray]) -> dict[str, float]:
    mw = mask_window(wall["time"])
    raw = {
        "A_tube": float(np.nanmean(wall["A_tube_raw"][mw])),
        "A_fin_min": float(np.nanmean(wall["A_fin_min_raw"][mw])),
        "A_fin_max": float(np.nanmean(wall["A_fin_max_raw"][mw])),
    }
    raw_total = raw["A_tube"] + raw["A_fin_min"] + raw["A_fin_max"]
    scale = A_HOT_TOTAL / raw_total
    return {
        "A_tube": raw["A_tube"] * scale,
        "A_fin_min": raw["A_fin_min"] * scale,
        "A_fin_max": raw["A_fin_max"] * scale,
        "A_hot_total": A_HOT_TOTAL,
        "A_tube_raw": raw["A_tube"],
        "A_fin_min_raw": raw["A_fin_min"],
        "A_fin_max_raw": raw["A_fin_max"],
        "A_hot_total_raw": raw_total,
        "area_scale_to_reference": scale,
    }


def build_heat_series(wall: dict[str, np.ndarray], outlet: dict[str, np.ndarray], areas: dict[str, float]) -> dict[str, np.ndarray]:
    mw = mask_window(wall["time"])
    time = wall["time"][mw]
    q_tube = wall["Q_tube"][mw]
    q_fin_min = wall["Q_fin_min"][mw]
    q_fin_max = wall["Q_fin_max"][mw]
    q_fins = wall["Q_fins"][mw]
    q_wall = wall["Q_wall"][mw]
    q_air = interp_to(time, outlet["time"], outlet["Q_air"])
    q_air_mass = interp_to(time, outlet["time"], outlet["Q_air_massT"])
    t_out = interp_to(time, outlet["time"], outlet["T_area"])
    lmtd_i = interp_to(time, outlet["time"], outlet["LMTD"])

    nu_tube = (q_tube / (areas["A_tube"] * lmtd_i)) * D / K_AIR
    nu_fin_min = (q_fin_min / (areas["A_fin_min"] * lmtd_i)) * D / K_AIR
    nu_fin_max = (q_fin_max / (areas["A_fin_max"] * lmtd_i)) * D / K_AIR
    nu_fins = (q_fins / ((areas["A_fin_min"] + areas["A_fin_max"]) * lmtd_i)) * D / K_AIR
    nu_wall = (q_wall / (A_HOT_TOTAL * lmtd_i)) * D / K_AIR
    nu_eb = interp_to(time, outlet["time"], outlet["Nu_EB"])
    closure = 100.0 * (q_wall - q_air) / q_air
    closure_mass = 100.0 * (q_wall - q_air_mass) / q_air_mass
    return {
        "time": time,
        "Q_air": q_air,
        "Q_air_massT": q_air_mass,
        "Q_wall": q_wall,
        "Q_tube": q_tube,
        "Q_fin_min": q_fin_min,
        "Q_fin_max": q_fin_max,
        "Q_fins": q_fins,
        "T_out": t_out,
        "LMTD": lmtd_i,
        "closure_pct": closure,
        "closure_ratio_of_means_pct": np.full_like(time, 100.0 * (float(np.mean(q_wall)) - float(np.mean(q_air))) / float(np.mean(q_air))),
        "closure_massT_pct": closure_mass,
        "tube_share_pct": 100.0 * q_tube / q_wall,
        "fins_share_pct": 100.0 * q_fins / q_wall,
        "fin_min_share_pct": 100.0 * q_fin_min / q_wall,
        "fin_max_share_pct": 100.0 * q_fin_max / q_wall,
        "Nu_tube_wall": nu_tube,
        "Nu_fin_min_wall": nu_fin_min,
        "Nu_fin_max_wall": nu_fin_max,
        "Nu_fins_wall": nu_fins,
        "Nu_total_wall": nu_wall,
        "Nu_EB": nu_eb,
    }


def plot_heat_timeseries(series: dict[str, np.ndarray]) -> None:
    t = series["time"]
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True, constrained_layout=True)
    axes[0].plot(t, series["Q_air"], color="#1d4e89", lw=1.2, label="Q_air")
    axes[0].plot(t, series["Q_wall"], color="#9b2226", lw=1.0, label="Q_wall")
    axes[0].set_ylabel("Q [W]")
    axes[0].set_title("Wall-air heat balance")
    axes[0].legend(ncol=2)
    axes[1].plot(t, series["Q_tube"], label="Q_tube", color="#005f73")
    axes[1].plot(t, series["Q_fin_min"], label="Q_fin_min", color="#ca6702")
    axes[1].plot(t, series["Q_fin_max"], label="Q_fin_max", color="#ee9b00")
    axes[1].set_ylabel("Q [W]")
    axes[1].set_title("Patch heat contributions")
    axes[1].legend(ncol=3)
    axes[2].plot(t, series["closure_pct"], color="#5f0f40", lw=0.9)
    axes[2].axhline(np.mean(series["closure_pct"]), color="black", ls="--", lw=0.9)
    axes[2].set_ylabel("closure [%]")
    axes[2].set_xlabel("t [s]")
    axes[2].set_title("Instantaneous closure: 100*(Q_wall-Q_air)/Q_air")
    for ax in axes:
        ax.grid(alpha=0.25)
    fig.savefig(FIG_DIR / "run008_003_heat_balance_timeseries_closure.png", dpi=180)
    plt.close(fig)


def plot_lag(time: np.ndarray, q_wall: np.ndarray, q_air: np.ndarray, t_out: np.ndarray, lags: list[LagSummary]) -> None:
    dt = float(np.median(np.diff(time)))
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    for y, label, color in [(q_air, "Q_air", "#1d4e89"), (t_out, "T_out", "#588157")]:
        x0 = q_wall - np.mean(q_wall)
        y0 = y - np.mean(y)
        corr = signal.correlate(y0, x0, mode="full")
        lag_grid = signal.correlation_lags(len(y0), len(x0), mode="full") * dt
        corr = corr / (np.linalg.norm(x0) * np.linalg.norm(y0))
        mask = np.abs(lag_grid) <= 2.0
        axes[0].plot(lag_grid[mask], corr[mask], label=label, color=color)
    axes[0].axvline(0, color="black", lw=0.8)
    axes[0].set_xlabel("lag [s], positive = outlet signal lags Q_wall")
    axes[0].set_ylabel("normalized cross-correlation")
    axes[0].set_title("Transport lag estimate")
    axes[0].legend()
    axes[0].grid(alpha=0.25)

    labels = [l.pair for l in lags]
    values = [l.lag_s for l in lags]
    axes[1].bar(labels, values, color=["#1d4e89", "#588157"])
    axes[1].axhline(0, color="black", lw=0.8)
    axes[1].set_ylabel("lag [s]")
    axes[1].set_title("Lag at maximum correlation")
    axes[1].tick_params(axis="x", rotation=20)
    axes[1].grid(axis="y", alpha=0.25)
    fig.savefig(FIG_DIR / "run008_003_heat_balance_lag.png", dpi=180)
    plt.close(fig)


def plot_shares_nu(series: dict[str, np.ndarray]) -> None:
    t = series["time"]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    axes[0, 0].plot(t, series["tube_share_pct"], label="tube", color="#005f73")
    axes[0, 0].plot(t, series["fins_share_pct"], label="fins", color="#ca6702")
    axes[0, 0].set_ylabel("Q share [%]")
    axes[0, 0].set_title("Tube vs fins heat share")
    axes[0, 0].legend()
    axes[0, 1].plot(t, series["fin_min_share_pct"], label="fin z_min", color="#bb3e03")
    axes[0, 1].plot(t, series["fin_max_share_pct"], label="fin z_max", color="#ee9b00")
    axes[0, 1].set_ylabel("Q share [%]")
    axes[0, 1].set_title("Fin-side symmetry")
    axes[0, 1].legend()
    axes[1, 0].plot(t, series["Nu_tube_wall"], label="tube wall", color="#005f73")
    axes[1, 0].plot(t, series["Nu_fins_wall"], label="fins wall", color="#ca6702")
    axes[1, 0].plot(t, series["Nu_total_wall"], label="total wall", color="#9b2226")
    axes[1, 0].set_ylabel("Nu")
    axes[1, 0].set_xlabel("t [s]")
    axes[1, 0].set_title("Wall-based Nusselt by patch group")
    axes[1, 0].legend()
    axes[1, 1].plot(t, series["Nu_EB"], label="Nu_EB", color="#1d4e89")
    axes[1, 1].plot(t, series["Nu_total_wall"], label="Nu_wall", color="#9b2226")
    axes[1, 1].set_ylabel("Nu")
    axes[1, 1].set_xlabel("t [s]")
    axes[1, 1].set_title("Independent Nu definitions")
    axes[1, 1].legend()
    for ax in axes.ravel():
        ax.grid(alpha=0.25)
    fig.savefig(FIG_DIR / "run008_003_heat_shares_and_nu.png", dpi=180)
    plt.close(fig)


def plot_nu_scatter(series: dict[str, np.ndarray]) -> None:
    fig, ax = plt.subplots(figsize=(6, 6), constrained_layout=True)
    ax.scatter(series["Nu_EB"], series["Nu_total_wall"], c=series["time"], cmap="viridis", s=10)
    lo = min(float(np.min(series["Nu_EB"])), float(np.min(series["Nu_total_wall"])))
    hi = max(float(np.max(series["Nu_EB"])), float(np.max(series["Nu_total_wall"])))
    ax.plot([lo, hi], [lo, hi], color="black", ls="--", lw=0.9)
    ax.set_xlabel("Nu_EB")
    ax.set_ylabel("Nu_wall")
    ax.set_title("Nu_EB vs Nu_wall")
    ax.grid(alpha=0.25)
    fig.savefig(FIG_DIR / "run008_003_nu_eb_vs_wall_scatter.png", dpi=180)
    plt.close(fig)


def write_report(summary: list[HeatSummary], lags: list[LagSummary], areas: dict[str, float]) -> None:
    values = {s.metric: s for s in summary}
    lines = [
        "# V4b_3D run008 heat-balance closure",
        "",
        f"Primary window: `{WINDOW[0]:.1f}..{WINDOW[1]:.1f} s`.",
        "",
        "## Heat-flow summary",
        "",
        f"Reference area for all reported Nu definitions: `A_hot_total = {A_HOT_TOTAL:.6f} m2`.",
        f"Patch areas are scaled from wallHeatFlux effective areas by factor `{areas['area_scale_to_reference']:.6f}` to preserve this reference area.",
        "",
        "| Metric | mean | std | min | max |",
        "|---|---:|---:|---:|---:|",
    ]
    for s in summary:
        lines.append(f"| {s.metric} | {s.mean:.6f} | {s.std:.6f} | {s.minimum:.6f} | {s.maximum:.6f} |")
    lines.extend(
        [
            "",
            "## Lag estimate",
            "",
            "| Pair | lag [s] | lag / T_shed | corr | interpretation |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for l in lags:
        lines.append(f"| {l.pair} | {l.lag_s:+.4f} | {l.lag_over_period:+.3f} | {l.correlation:.4f} | {l.interpretation} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Ratio-of-means wall-air closure is `{values['closure_ratio_of_means_pct'].mean:+.3f}%`; instantaneous closure has mean `{values['closure_pct'].mean:+.3f}%` and std `{values['closure_pct'].std:.3f}%`.",
            f"- Tube contributes `{values['tube_share_pct'].mean:.2f}%` of wall heat, fins `{values['fins_share_pct'].mean:.2f}%`.",
            f"- `Nu_total_wall = {values['Nu_total_wall'].mean:.4f}` and `Nu_EB = {values['Nu_EB'].mean:.4f}`; the independent definitions differ by `{100.0 * (values['Nu_total_wall'].mean - values['Nu_EB'].mean) / values['Nu_EB'].mean:+.3f}%`.",
            f"- Lag correlations are weak; treat transport-lag values as diagnostic, not as a robust convection-time measurement unless repeated with a longer record or a cleaner outlet signal.",
            "",
            "## Figures",
            "",
            "- `../../figures/003/run008_003_heat_balance_timeseries_closure.png`",
            "- `../../figures/003/run008_003_heat_balance_lag.png`",
            "- `../../figures/003/run008_003_heat_shares_and_nu.png`",
            "- `../../figures/003/run008_003_nu_eb_vs_wall_scatter.png`",
        ]
    )
    (DATA_DIR / "run008_003_heat_balance.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    wall = read_wall_heat_flux()
    outlet = outlet_thermal_series()
    areas = scaled_patch_areas(wall)
    series = build_heat_series(wall, outlet, areas)

    f_shed = 3.2787
    lags = [
        cross_correlation_lag(series["time"], series["Q_wall"], series["Q_air"], f_shed, "Q_wall -> Q_air"),
        cross_correlation_lag(series["time"], series["Q_wall"], series["T_out"], f_shed, "Q_wall -> T_out"),
    ]
    summary_names = [
        "Q_air",
        "Q_air_massT",
        "Q_wall",
        "Q_tube",
        "Q_fin_min",
        "Q_fin_max",
        "Q_fins",
        "closure_pct",
        "closure_ratio_of_means_pct",
        "closure_massT_pct",
        "tube_share_pct",
        "fins_share_pct",
        "fin_min_share_pct",
        "fin_max_share_pct",
        "Nu_tube_wall",
        "Nu_fin_min_wall",
        "Nu_fin_max_wall",
        "Nu_fins_wall",
        "Nu_total_wall",
        "Nu_EB",
    ]
    summary = [summarize(name, series[name]) for name in summary_names]

    rows = []
    for i, t in enumerate(series["time"]):
        rows.append({key: float(value[i]) for key, value in series.items()})
    write_csv(DATA_DIR / "run008_003_heat_balance_timeseries.csv", rows)
    write_csv(DATA_DIR / "run008_003_heat_balance_summary.csv", [asdict(s) for s in summary])
    write_csv(DATA_DIR / "run008_003_heat_balance_lags.csv", [asdict(l) for l in lags])
    (DATA_DIR / "run008_003_heat_balance.json").write_text(
        json.dumps(
            {
                "window": WINDOW,
                "areas": {
                    **areas,
                },
                "summary": [asdict(s) for s in summary],
                "lags": [asdict(l) for l in lags],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    plot_heat_timeseries(series)
    plot_lag(series["time"], series["Q_wall"], series["Q_air"], series["T_out"], lags)
    plot_shares_nu(series)
    plot_nu_scatter(series)
    write_report(summary, lags, areas)
    print((DATA_DIR / "run008_003_heat_balance.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
