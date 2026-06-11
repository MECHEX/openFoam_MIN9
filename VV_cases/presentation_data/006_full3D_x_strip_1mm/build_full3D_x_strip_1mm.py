from __future__ import annotations

import csv
import math
import os
import shutil
import subprocess
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9")
OUT_DIR = REPO_DIR / "VV_cases/presentation_data/006_full3D_x_strip_1mm"
HEAT_005 = REPO_DIR / "VV_cases/presentation_data/005_x_strip_robustness_analysis/x_strip_enriched_dx1mm.csv"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CASES = [
    {"Re": 100.0, "case": "run012_re100", "path": Path("/home/hexmachina/of_runs/V4b_3D_run012_re100_production"), "window": (8.0, 10.0), "regime": "steady"},
    {"Re": 150.0, "case": "run013_re150", "path": Path("/home/hexmachina/of_runs/V4b_3D_run013_re150_production"), "window": (8.0, 10.0), "regime": "steady"},
    {"Re": 160.0, "case": "run015_re160", "path": Path("/home/hexmachina/of_runs/V4b_3D_run015_re160_production"), "window": (8.0, 10.0), "regime": "shedding"},
    {"Re": 175.0, "case": "run014_re175", "path": Path("/home/hexmachina/of_runs/V4b_3D_run014_re175_production"), "window": (8.0, 10.0), "regime": "shedding"},
    {"Re": 200.0, "case": "run008_re200", "path": Path("/home/hexmachina/of_runs/V4b_3D_run008"), "window": (8.0, 10.0), "regime": "production shedding"},
]

DX_M = 0.001
D_REF = 0.012
R_REF = 0.5 * D_REF
NEAR_WALL_THICKNESS = 0.0015
SELECTED_RE = [160.0, 175.0, 200.0]
BASELINE_RE = 150.0
N_TIMES_PER_CASE = 3


def run_bash(command: str, cwd: Path | None = None) -> None:
    full = f"source /opt/openfoam13/etc/bashrc; {command}"
    subprocess.run(["bash", "-lc", full], cwd=str(cwd) if cwd else None, check=True)


def numeric_time_dirs(case_dir: Path) -> list[tuple[float, str]]:
    times = []
    for p in case_dir.iterdir():
        if not p.is_dir():
            continue
        try:
            times.append((float(p.name), p.name))
        except ValueError:
            pass
    return sorted(times, key=lambda item: item[0])


def select_times(case: dict) -> list[float]:
    t0, t1 = case["window"]
    times = [
        t
        for t, name in numeric_time_dirs(case["path"] / "processor0")
        if t0 <= t <= t1
        and (case["path"] / "processor0" / name / "U").exists()
        and (case["path"] / "processor0" / name / "T").exists()
    ]
    if not times:
        times = [t for t, name in numeric_time_dirs(case["path"]) if t0 <= t <= t1 and (case["path"] / name / "U").exists()]
    if len(times) <= N_TIMES_PER_CASE:
        return times
    idx = np.linspace(0, len(times) - 1, N_TIMES_PER_CASE).round().astype(int)
    return [times[i] for i in idx]


def n_processors(case_dir: Path) -> int:
    return len([p for p in case_dir.iterdir() if p.is_dir() and p.name.startswith("processor")])


def cleanup_vtk(case_dir: Path) -> None:
    vtk = case_dir / "VTK"
    if vtk.exists():
        shutil.rmtree(vtk)
    for proc in case_dir.glob("processor*/VTK"):
        shutil.rmtree(proc, ignore_errors=True)


def ensure_vtk(case: dict, time_value: float) -> list[Path]:
    case_dir = case["path"]
    nproc = n_processors(case_dir)
    if nproc <= 0:
        raise RuntimeError(f"No processor directories in {case_dir}")
    cleanup_vtk(case_dir)
    time_s = f"{time_value:g}"
    mpi = f"mpirun -np {nproc} --oversubscribe --allow-run-as-root"
    run_bash(f"cd {case_dir}; {mpi} postProcess -parallel -funcs '(Q vorticity)' -time {time_s}", cwd=case_dir)
    run_bash(
        f"cd {case_dir}; {mpi} foamToVTK -parallel -time {time_s} -fields '(U T rho Q vorticity)' -noPointValues -ascii",
        cwd=case_dir,
    )
    files = sorted(case_dir.glob("processor*/VTK/processor*_*.vtk"))
    if not files:
        raise RuntimeError(f"No internal processor VTK files after export for {case['case']} time {time_s}")
    return files


def read_legacy_vtk(path: Path) -> tuple[np.ndarray, list[list[int]], list[int], dict[str, np.ndarray]]:
    tokens = path.read_text(errors="ignore").split()
    i = tokens.index("POINTS")
    n_points = int(tokens[i + 1])
    start = i + 3
    vals = np.asarray([float(v) for v in tokens[start : start + 3 * n_points]], dtype=float)
    points = vals.reshape(n_points, 3)

    i = tokens.index("CELLS")
    n_cells = int(tokens[i + 1])
    total = int(tokens[i + 2])
    raw = tokens[i + 3 : i + 3 + total]
    cells: list[list[int]] = []
    j = 0
    for _ in range(n_cells):
        m = int(raw[j])
        cells.append([int(v) for v in raw[j + 1 : j + 1 + m]])
        j += m + 1

    i = tokens.index("CELL_TYPES")
    n_types = int(tokens[i + 1])
    cell_types = [int(v) for v in tokens[i + 2 : i + 2 + n_types]]
    if n_types != n_cells:
        raise RuntimeError(f"Cell type count mismatch in {path}")

    fields: dict[str, np.ndarray] = {}
    i = tokens.index("CELL_DATA") + 2
    while i < len(tokens):
        key = tokens[i]
        if key == "FIELD":
            n_fields = int(tokens[i + 2])
            i += 3
            for _ in range(n_fields):
                name = tokens[i]
                ncomp = int(tokens[i + 1])
                ntuples = int(tokens[i + 2])
                start = i + 4
                arr = np.asarray([float(v) for v in tokens[start : start + ncomp * ntuples]], dtype=float)
                fields[name] = arr.reshape(ntuples, ncomp)[:, 0] if ncomp == 1 else arr.reshape(ntuples, ncomp)
                i = start + ncomp * ntuples
        elif key == "SCALARS":
            name = tokens[i + 1]
            ncomp = 1
            next_token = tokens[i + 3]
            if next_token != "LOOKUP_TABLE":
                try:
                    ncomp = int(next_token)
                    i += 1
                except ValueError:
                    ncomp = 1
            if tokens[i + 3] == "LOOKUP_TABLE":
                start = i + 5
            else:
                start = i + 4
            arr = np.asarray([float(v) for v in tokens[start : start + n_cells * ncomp]], dtype=float)
            fields[name] = arr.reshape(n_cells, ncomp)[:, 0] if ncomp == 1 else arr.reshape(n_cells, ncomp)
            i = start + n_cells * ncomp
        elif key == "VECTORS":
            name = tokens[i + 1]
            start = i + 3
            arr = np.asarray([float(v) for v in tokens[start : start + 3 * n_cells]], dtype=float).reshape(n_cells, 3)
            fields[name] = arr
            i = start + 3 * n_cells
        else:
            i += 1
    return points, cells, cell_types, fields


FACES = {
    10: [[0, 2, 1], [0, 1, 3], [1, 2, 3], [2, 0, 3]],  # tetra
    12: [[0, 4, 7, 3], [1, 2, 6, 5], [0, 1, 5, 4], [3, 7, 6, 2], [0, 3, 2, 1], [4, 5, 6, 7]],  # hex
    14: [[0, 3, 2, 1], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]],  # pyramid
}


def triangle_volume_from_centroid(c: np.ndarray, a: np.ndarray, b: np.ndarray, d: np.ndarray) -> float:
    return abs(float(np.dot(a - c, np.cross(b - c, d - c)))) / 6.0


def cell_volume(verts: np.ndarray, cell_type: int) -> float:
    faces = FACES.get(cell_type)
    if faces is None:
        return float("nan")
    c = verts.mean(axis=0)
    volume = 0.0
    for face in faces:
        face_pts = verts[np.asarray(face, dtype=int)]
        for k in range(1, len(face_pts) - 1):
            volume += triangle_volume_from_centroid(c, face_pts[0], face_pts[k], face_pts[k + 1])
    return volume


def discover_edges_from_heat() -> np.ndarray:
    heat = pd.read_csv(HEAT_005)
    left = heat["x_left_mm"].min() / 1000.0
    right = heat["x_right_mm"].max() / 1000.0
    return np.arange(left, right + 0.5 * DX_M, DX_M)


def summarize_vtk_files(case: dict, time_value: float, vtk_files: list[Path], edges: np.ndarray) -> list[dict]:
    n = len(edges) - 1
    vol = np.zeros(n)
    rho_ux_v = np.zeros(n)
    rho_ux_t_v = np.zeros(n)
    qpos_v = np.zeros(n)
    qpos_int = np.zeros(n)
    omega_v = np.zeros(n)
    omega_int = np.zeros(n)
    near_vol = np.zeros(n)
    near_qpos_v = np.zeros(n)
    near_omega_v = np.zeros(n)
    bulk_vol = np.zeros(n)
    bulk_qpos_v = np.zeros(n)
    bulk_omega_v = np.zeros(n)
    wake_vol = np.zeros(n)
    wake_qpos_v = np.zeros(n)
    wake_omega_v = np.zeros(n)
    cell_type_counter: Counter[int] = Counter()

    for path in vtk_files:
        points, cells, cell_types, fields = read_legacy_vtk(path)
        q = fields["Q"]
        vort = fields["vorticity"]
        vel = fields["U"]
        temp = fields["T"]
        rho = fields.get("rho", np.ones(len(cells)))
        omega_mag = np.linalg.norm(vort, axis=1)

        for idx, (cell, ctype) in enumerate(zip(cells, cell_types)):
            verts = points[np.asarray(cell, dtype=int)]
            center = verts.mean(axis=0)
            b = int(np.searchsorted(edges, center[0], side="right") - 1)
            if b < 0 or b >= n:
                continue
            v = cell_volume(verts, ctype)
            if not np.isfinite(v) or v <= 0:
                continue
            cell_type_counter[ctype] += 1
            qpos = max(float(q[idx]), 0.0)
            om = float(omega_mag[idx])
            ux = max(float(vel[idx, 0]), 0.0)
            r = float(np.hypot(center[0], center[1]))
            is_near = (R_REF * 0.98) <= r <= (R_REF + NEAR_WALL_THICKNESS)
            is_wake = center[0] >= R_REF and r > (R_REF + NEAR_WALL_THICKNESS)

            vol[b] += v
            conv = float(rho[idx]) * ux * v
            rho_ux_v[b] += conv
            rho_ux_t_v[b] += conv * float(temp[idx])
            qpos_v[b] += qpos * v
            qpos_int[b] += qpos * v
            omega_v[b] += om * v
            omega_int[b] += om * v

            if is_near:
                near_vol[b] += v
                near_qpos_v[b] += qpos * v
                near_omega_v[b] += om * v
            else:
                bulk_vol[b] += v
                bulk_qpos_v[b] += qpos * v
                bulk_omega_v[b] += om * v
            if is_wake:
                wake_vol[b] += v
                wake_qpos_v[b] += qpos * v
                wake_omega_v[b] += om * v

    rows = []
    for i in range(n):
        rows.append(
            {
                "Re": case["Re"],
                "case": case["case"],
                "regime": case["regime"],
                "time": time_value,
                "x_left_mm": edges[i] * 1000.0,
                "x_right_mm": edges[i + 1] * 1000.0,
                "x_center_mm": 0.5 * (edges[i] + edges[i + 1]) * 1000.0,
                "fluid_volume_m3": vol[i],
                "T_bulk_3D_Ux_volume_weighted_K": rho_ux_t_v[i] / rho_ux_v[i] if rho_ux_v[i] > 0 else np.nan,
                "Qcriterion_positive_3D_volume_mean_1_s2": qpos_v[i] / vol[i] if vol[i] > 0 else np.nan,
                "Qcriterion_positive_3D_volume_integral_m3_s2": qpos_int[i],
                "omega_mag_3D_volume_mean_1_s": omega_v[i] / vol[i] if vol[i] > 0 else np.nan,
                "omega_mag_3D_volume_integral_m3_s": omega_int[i],
                "near_tube_wall_volume_m3": near_vol[i],
                "near_tube_wall_Qcriterion_positive_3D_mean_1_s2": near_qpos_v[i] / near_vol[i] if near_vol[i] > 0 else np.nan,
                "near_tube_wall_omega_mag_3D_mean_1_s": near_omega_v[i] / near_vol[i] if near_vol[i] > 0 else np.nan,
                "bulk_no_tube_wall_volume_m3": bulk_vol[i],
                "bulk_no_tube_wall_Qcriterion_positive_3D_mean_1_s2": bulk_qpos_v[i] / bulk_vol[i] if bulk_vol[i] > 0 else np.nan,
                "bulk_no_tube_wall_omega_mag_3D_mean_1_s": bulk_omega_v[i] / bulk_vol[i] if bulk_vol[i] > 0 else np.nan,
                "wake_volume_m3": wake_vol[i],
                "wake_Qcriterion_positive_3D_mean_1_s2": wake_qpos_v[i] / wake_vol[i] if wake_vol[i] > 0 else np.nan,
                "wake_omega_mag_3D_mean_1_s": wake_omega_v[i] / wake_vol[i] if wake_vol[i] > 0 else np.nan,
                "cell_types": ";".join(f"{k}:{v}" for k, v in sorted(cell_type_counter.items())),
            }
        )
    return rows


def write_rows(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def average_time_rows(rows: list[dict]) -> list[dict]:
    df = pd.DataFrame(rows)
    group_cols = ["Re", "case", "regime", "x_left_mm", "x_right_mm", "x_center_mm"]
    numeric = [c for c in df.columns if c not in group_cols + ["time", "cell_types"]]
    out = df.groupby(group_cols, as_index=False)[numeric].mean()
    out["n_3D_times_used"] = df.groupby(group_cols)["time"].nunique().to_numpy()
    return out.to_dict("records")


def merge_with_heat(rows: list[dict]) -> pd.DataFrame:
    full = pd.DataFrame(rows)
    heat = pd.read_csv(HEAT_005)
    full["Re"] = pd.to_numeric(full["Re"], errors="coerce")
    heat["Re"] = pd.to_numeric(heat["Re"], errors="coerce")
    full["x_center_mm"] = pd.to_numeric(full["x_center_mm"], errors="coerce")
    heat["x_center_mm"] = pd.to_numeric(heat["x_center_mm"], errors="coerce")
    full["x_key_mm"] = full["x_center_mm"].round(6)
    heat["x_key_mm"] = heat["x_center_mm"].round(6)
    keep = [
        "Re",
        "x_key_mm",
        "Nu_strip_proxy",
        "relative_local_sensitivity_vs_Re150",
        "Delta_Nu_vs_Re150",
        "Delta_Q_vs_Re150_W",
        "Q_strip_share_of_total",
        "Q_total_strip_W",
        "Q_tube_strip_W",
        "Q_fins_strip_W",
    ]
    merged = full.merge(heat[keep], on=["Re", "x_key_mm"], how="left")
    merged = merged.drop(columns=["x_key_mm"])
    for metric in [
        "Qcriterion_positive_3D_volume_mean_1_s2",
        "omega_mag_3D_volume_mean_1_s",
        "near_tube_wall_Qcriterion_positive_3D_mean_1_s2",
        "near_tube_wall_omega_mag_3D_mean_1_s",
        "bulk_no_tube_wall_Qcriterion_positive_3D_mean_1_s2",
        "bulk_no_tube_wall_omega_mag_3D_mean_1_s",
        "wake_Qcriterion_positive_3D_mean_1_s2",
        "wake_omega_mag_3D_mean_1_s",
    ]:
        merged[metric] = pd.to_numeric(merged[metric], errors="coerce")
        merged[f"{metric}_nd"] = merged[metric] * (D_REF / (merged["Re"] * 0.028 / D_REF)) ** 2
    return merged


def add_tube(ax) -> None:
    ax.axvline(-6, color="0.25", ls="--", lw=0.9)
    ax.axvline(6, color="0.25", ls="--", lw=0.9)
    ax.axvspan(-6, 6, color="0.7", alpha=0.08, lw=0)


def plot_profiles(df: pd.DataFrame) -> None:
    colors = {160.0: "#31588a", 175.0: "#b35806", 200.0: "#8b1a1a"}
    fig, axes = plt.subplots(2, 2, figsize=(13.0, 8.2), sharex=True)
    configs = [
        ("Qcriterion_positive_3D_volume_mean_1_s2", "3D mean positive Q [1/s2]", "Full-volume Qcriterion+"),
        ("omega_mag_3D_volume_mean_1_s", "3D mean |omega| [1/s]", "Full-volume vorticity magnitude"),
        ("bulk_no_tube_wall_Qcriterion_positive_3D_mean_1_s2", "bulk-no-wall Q+ [1/s2]", "3D bulk-no-tube-wall Qcriterion+"),
        ("T_bulk_3D_Ux_volume_weighted_K", "T bulk proxy [K]", "3D Ux-volume-weighted bulk temperature proxy"),
    ]
    for ax, (col, ylabel, title) in zip(axes.ravel(), configs):
        for re in SELECTED_RE:
            sub = df[df["Re"].eq(re)].sort_values("x_center_mm")
            ax.plot(sub["x_center_mm"], sub[col], lw=1.9, color=colors[re], label=f"Re {int(re)}")
        add_tube(ax)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
    axes[0, 0].legend(frameon=False, ncols=3)
    axes[1, 0].set_xlabel("x from tube center [mm], 1 mm strips")
    axes[1, 1].set_xlabel("x from tube center [mm], 1 mm strips")
    fig.suptitle("Full-3D x-strip vortex and temperature metrics", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig01_full3D_x_strip_profiles.png", dpi=240)
    fig.savefig(OUT_DIR / "fig01_full3D_x_strip_profiles.pdf")
    plt.close(fig)


def plot_overlay(df: pd.DataFrame) -> None:
    colors = {160.0: "#31588a", 175.0: "#b35806", 200.0: "#8b1a1a"}
    fig, axes = plt.subplots(3, 1, figsize=(11.5, 9.0), sharex=True)
    for ax, re in zip(axes, SELECTED_RE):
        sub = df[df["Re"].eq(re)].sort_values("x_center_mm")
        x = sub["x_center_mm"].to_numpy()
        sensitivity = sub["relative_local_sensitivity_vs_Re150"].to_numpy()
        q3d = sub["bulk_no_tube_wall_Qcriterion_positive_3D_mean_1_s2"].to_numpy()
        q3d_norm = q3d / np.nanmax(q3d) if np.nanmax(q3d) > 0 else q3d
        ax.plot(x, sensitivity, lw=2.0, color=colors[re], label="relative local sensitivity")
        ax.plot(x, q3d_norm, lw=1.8, color="0.15", ls="--", label="3D bulk-no-wall Q+ normalized")
        ax.axhline(0, color="0.2", lw=0.8)
        add_tube(ax)
        ax.set_ylabel(f"Re {int(re)}")
        ax.grid(True, alpha=0.25)
    axes[0].legend(frameon=False, ncols=2)
    axes[-1].set_xlabel("x from tube center [mm], 1 mm strips")
    fig.suptitle("Nu sensitivity compared with full-3D bulk vortex metric", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig02_Nu_sensitivity_vs_full3D_bulk_Qcriterion.png", dpi=240)
    fig.savefig(OUT_DIR / "fig02_Nu_sensitivity_vs_full3D_bulk_Qcriterion.pdf")
    plt.close(fig)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    valid = np.isfinite(a) & np.isfinite(b)
    if valid.sum() < 3:
        return float("nan")
    if np.nanstd(a[valid]) < 1e-14 or np.nanstd(b[valid]) < 1e-14:
        return float("nan")
    return float(np.corrcoef(a[valid], b[valid])[0, 1])


def spatial_lag(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    metrics = [
        "Qcriterion_positive_3D_volume_mean_1_s2",
        "omega_mag_3D_volume_mean_1_s",
        "bulk_no_tube_wall_Qcriterion_positive_3D_mean_1_s2",
        "bulk_no_tube_wall_omega_mag_3D_mean_1_s",
        "near_tube_wall_Qcriterion_positive_3D_mean_1_s2",
        "near_tube_wall_omega_mag_3D_mean_1_s",
    ]
    for re in SELECTED_RE:
        sub = df[df["Re"].eq(re)].sort_values("x_center_mm")
        target = sub["relative_local_sensitivity_vs_Re150"].to_numpy()
        x = sub["x_center_mm"].to_numpy()
        masks = {
            "full": np.isfinite(target),
            "without_x_pm5p5": np.isfinite(target) & ~(np.isclose(x, -5.5) | np.isclose(x, 5.5)),
            "without_tube_zone": np.isfinite(target) & ~((-6 <= x) & (x <= 6)),
        }
        for metric in metrics:
            m = sub[metric].to_numpy()
            for mask_name, mask in masks.items():
                for lag in range(-6, 7):
                    if lag < 0:
                        aa = m[-lag:]
                        bb = target[:lag]
                        mk = mask[-lag:] & mask[:lag]
                    elif lag > 0:
                        aa = m[:-lag]
                        bb = target[lag:]
                        mk = mask[:-lag] & mask[lag:]
                    else:
                        aa = m
                        bb = target
                        mk = mask
                    rows.append({"Re": re, "metric": metric, "mask": mask_name, "lag_mm": lag, "corr": corr(aa[mk], bb[mk])})
    out = pd.DataFrame(rows)
    out.to_csv(OUT_DIR / "full3D_spatial_lag_correlations.csv", index=False)
    best = out.dropna().copy()
    best["abs_corr"] = best["corr"].abs()
    best = best.sort_values("abs_corr", ascending=False).groupby(["Re", "metric", "mask"], as_index=False).first()
    best.to_csv(OUT_DIR / "full3D_best_spatial_lags.csv", index=False)
    return out


def plot_lags(lags: pd.DataFrame) -> None:
    metrics = [
        ("bulk_no_tube_wall_Qcriterion_positive_3D_mean_1_s2", "3D bulk-no-wall Q+"),
        ("bulk_no_tube_wall_omega_mag_3D_mean_1_s", "3D bulk-no-wall |omega|"),
        ("near_tube_wall_Qcriterion_positive_3D_mean_1_s2", "3D near-tube-wall Q+"),
    ]
    colors = {160.0: "#31588a", 175.0: "#b35806", 200.0: "#8b1a1a"}
    fig, axes = plt.subplots(1, 3, figsize=(14.0, 4.4), sharey=True)
    for ax, (metric, title) in zip(axes, metrics):
        for re in SELECTED_RE:
            sub = lags[(lags["metric"].eq(metric)) & (lags["mask"].eq("full")) & (lags["Re"].eq(re))]
            ax.plot(sub["lag_mm"], sub["corr"], marker="o", lw=1.8, color=colors[re], label=f"Re {int(re)}")
        ax.axhline(0, color="0.2", lw=0.8)
        ax.axvline(0, color="0.2", lw=0.8)
        ax.set_title(title)
        ax.set_xlabel("spatial lag [mm]")
        ax.grid(True, alpha=0.25)
    axes[0].set_ylabel("corr(metric(x), sensitivity(x+lag))")
    axes[0].legend(frameon=False)
    fig.suptitle("Full-3D spatial-lag correlations against Nu sensitivity", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig03_full3D_spatial_lag_correlations.png", dpi=240)
    fig.savefig(OUT_DIR / "fig03_full3D_spatial_lag_correlations.pdf")
    plt.close(fig)


def write_readme(times_by_case: dict[str, list[float]]) -> None:
    lines = [
        "# 006_full3D_x_strip_1mm",
        "",
        "Full-3D x-strip analysis using 1 mm streamwise strips.",
        "",
        "What is full 3D here:",
        "",
        "- OpenFOAM `Q` and `vorticity` fields are computed from the 3D volume solution.",
        "- Metrics are integrated/averaged over all fluid cells assigned to each 1 mm x-strip.",
        "- Tube-near-wall, wake, and bulk-no-tube-wall regions are separated using 3D cell centroids.",
        "- Heat-transfer metrics are joined from the existing full hot-surface `wallHeatFlux` integration in 005.",
        "",
        "Important limitation:",
        "",
        "- `T_bulk_3D_Ux_volume_weighted_K` is a 3D convective volume-weighted proxy, not an exact y-z cross-section mass-flow integral.",
        "- Exact publication-grade `T_bulk(x)` still needs sampled y-z cutting planes or face-based integration.",
        "",
        "Times used:",
        "",
    ]
    for case, times in times_by_case.items():
        lines.append(f"- `{case}`: {', '.join(f'{t:g}' for t in times)}")
    lines.extend(
        [
            "",
            "Main outputs:",
            "",
            "- `full3D_x_strip_1mm_time_resolved.csv`",
            "- `full3D_x_strip_1mm_time_averaged.csv`",
            "- `full3D_x_strip_1mm_merged_with_heat.csv`",
            "- `full3D_spatial_lag_correlations.csv`",
            "- `full3D_best_spatial_lags.csv`",
            "- `fig01_full3D_x_strip_profiles`",
            "- `fig02_Nu_sensitivity_vs_full3D_bulk_Qcriterion`",
            "- `fig03_full3D_spatial_lag_correlations`",
        ]
    )
    (OUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    edges = discover_edges_from_heat()
    all_rows: list[dict] = []
    times_by_case: dict[str, list[float]] = {}
    for case in CASES:
        times = select_times(case)
        times_by_case[case["case"]] = times
        print(f"{case['case']}: times {times}", flush=True)
        for t in times:
            print(f"  post-processing/exporting t={t:g}", flush=True)
            vtk_files = ensure_vtk(case, t)
            print(f"  parsing {len(vtk_files)} processor VTK files", flush=True)
            all_rows.extend(summarize_vtk_files(case, t, vtk_files, edges))
    write_rows(all_rows, OUT_DIR / "full3D_x_strip_1mm_time_resolved.csv")
    avg_rows = average_time_rows(all_rows)
    write_rows(avg_rows, OUT_DIR / "full3D_x_strip_1mm_time_averaged.csv")
    merged = merge_with_heat(avg_rows)
    merged.to_csv(OUT_DIR / "full3D_x_strip_1mm_merged_with_heat.csv", index=False)
    plot_profiles(merged)
    plot_overlay(merged)
    lags = spatial_lag(merged)
    plot_lags(lags)
    write_readme(times_by_case)
    print(f"Done: {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
