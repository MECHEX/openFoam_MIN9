"""Layer 015: region-limited Q/Lambda2 metrics linked to local Nu and Cl phase.

This is a diagnostic layer built from existing run008 data. It does not run
OpenFOAM. It reads the six layer-013 Q/Lambda2 VTK checkpoints, computes
region-limited vortex-activity metrics, and pairs them with phase-matched local
Nusselt metrics from layers 004/005/009.
"""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


RUN_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = RUN_DIR / "data" / "015"
FIG_DIR = RUN_DIR / "figures" / "015"

VTK_ROOT_CANDIDATES = [
    Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run008_q_lambda2_013\vtk_processors"),
    Path(r"\\wsl$\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run008_q_lambda2_013\vtk_processors"),
    Path("/home/hexmachina/of_runs/V4b_3D_run008_q_lambda2_013/vtk_processors"),
]

D = 0.012
R_TUBE = D / 2.0
U_REF = 0.25266
XC = 0.0
YC = 0.0
Z_MIN = -0.006
Z_MAX = 0.006

Q_THR = 3000.0
L2_THR = 3000.0


@dataclass(frozen=True)
class VtkGrid:
    points: np.ndarray
    cells: list[np.ndarray]
    cell_types: np.ndarray
    cell_data: dict[str, np.ndarray]


def find_vtk_root() -> Path:
    for path in VTK_ROOT_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Cannot find layer-013 VTK root")


def line_end(buf: bytes, start: int) -> int:
    end = buf.find(b"\n", start)
    if end < 0:
        raise ValueError("Malformed VTK file: missing newline")
    return end + 1


def parse_header_line(buf: bytes, token: bytes) -> tuple[int, list[str]]:
    idx = buf.find(token)
    if idx < 0:
        raise ValueError(f"Missing VTK token {token!r}")
    end = line_end(buf, idx)
    return end, buf[idx:end].decode("ascii", errors="replace").split()


def read_legacy_vtk(path: Path) -> VtkGrid:
    buf = path.read_bytes()

    points_data_start, parts = parse_header_line(buf, b"POINTS")
    n_points = int(parts[1])
    points = np.frombuffer(buf, dtype=">f4", count=n_points * 3, offset=points_data_start).astype(np.float64)
    points = points.reshape(n_points, 3)

    cells_header_start = points_data_start + n_points * 3 * 4
    cells_idx = buf.find(b"CELLS", cells_header_start)
    cells_data_start = line_end(buf, cells_idx)
    cells_parts = buf[cells_idx:cells_data_start].decode("ascii", errors="replace").split()
    n_cells = int(cells_parts[1])
    cells_size = int(cells_parts[2])
    raw_cells = np.frombuffer(buf, dtype=">i4", count=cells_size, offset=cells_data_start)
    cells: list[np.ndarray] = []
    pos = 0
    for _ in range(n_cells):
        n = int(raw_cells[pos])
        cells.append(raw_cells[pos + 1 : pos + 1 + n].astype(np.int64))
        pos += n + 1

    type_idx = buf.find(b"CELL_TYPES", cells_data_start + cells_size * 4)
    type_data_start = line_end(buf, type_idx)
    cell_types = np.frombuffer(buf, dtype=">i4", count=n_cells, offset=type_data_start).astype(np.int32)

    cell_data_idx = buf.find(b"CELL_DATA", type_data_start + n_cells * 4)
    point_data_idx = buf.find(b"POINT_DATA", cell_data_idx)
    if cell_data_idx < 0 or point_data_idx < 0:
        raise ValueError(f"Missing CELL_DATA/POINT_DATA in {path}")
    cell_chunk = buf[cell_data_idx:point_data_idx]

    cell_data: dict[str, np.ndarray] = {}
    pattern = re.compile(rb"([A-Za-z_][A-Za-z0-9_]*) ([1-9]) ([0-9]+) (float|int)\n")
    for match in pattern.finditer(cell_chunk):
        name = match.group(1).decode("ascii")
        n_comp = int(match.group(2))
        n_vals = int(match.group(3))
        dtype_name = match.group(4).decode("ascii")
        start = cell_data_idx + match.end()
        if n_vals != n_cells:
            continue
        if dtype_name == "float":
            arr = np.frombuffer(buf, dtype=">f4", count=n_vals * n_comp, offset=start).astype(np.float64)
        else:
            arr = np.frombuffer(buf, dtype=">i4", count=n_vals * n_comp, offset=start)
        if n_comp > 1:
            arr = arr.reshape(n_vals, n_comp)
        cell_data[name] = arr

    return VtkGrid(points=points, cells=cells, cell_types=cell_types, cell_data=cell_data)


def tet_volume(a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray) -> float:
    return abs(float(np.dot(np.cross(b - a, c - a), d - a))) / 6.0


def cell_volume(points: np.ndarray, ids: np.ndarray, cell_type: int) -> float:
    p = points[ids]
    if cell_type == 10 and len(ids) == 4:  # tetra
        return tet_volume(p[0], p[1], p[2], p[3])
    if cell_type == 12 and len(ids) == 8:  # hexahedron, VTK order
        tets = [(0, 1, 3, 4), (1, 2, 3, 6), (1, 3, 4, 6), (1, 5, 4, 6), (3, 7, 4, 6)]
        return sum(tet_volume(p[a], p[b], p[c], p[d]) for a, b, c, d in tets)
    if cell_type == 14 and len(ids) == 5:  # pyramid
        return tet_volume(p[0], p[1], p[2], p[4]) + tet_volume(p[0], p[2], p[3], p[4])
    # Conservative fallback for rare unexpected types: zero weight instead of
    # inventing geometry. The report records the covered volume.
    return 0.0


def processor_metrics(path: Path) -> pd.DataFrame:
    grid = read_legacy_vtk(path)
    centers = np.asarray([grid.points[ids].mean(axis=0) for ids in grid.cells])
    volumes = np.asarray([cell_volume(grid.points, ids, int(ct)) for ids, ct in zip(grid.cells, grid.cell_types)])

    x = centers[:, 0] - XC
    y = centers[:, 1] - YC
    z = centers[:, 2]
    r = np.sqrt(x * x + y * y)
    d_tube = r - R_TUBE
    d_fin = np.minimum(np.abs(z - Z_MIN), np.abs(z - Z_MAX))

    q = np.asarray(grid.cell_data["Q"], dtype=float)
    l2 = np.asarray(grid.cell_data["Lambda2"], dtype=float)

    # Side band excludes the front/rear stagnation zones by requiring |y| to be
    # substantial relative to the tube radius.
    masks = {
        "R_sep": (d_tube > 0.0) & (d_tube < 0.25 * D) & (np.abs(y) > 0.35 * D) & (np.abs(y) < 1.05 * D),
        "R_near_wake": (x > 0.25 * D) & (x < 2.5 * D) & (np.abs(y) < 1.0 * D),
        "R_fin_junction": (d_tube > 0.0) & (d_tube < 0.35 * D) & (d_fin < 0.20 * D),
        "R_fin_sweep": (d_fin < 0.15 * D) & (x > -0.5 * D) & (x < 3.0 * D),
        "R_far_wake": (x > 3.0 * D) & (x < 6.0 * D) & (np.abs(y) < 1.5 * D),
        "R_global_control": volumes > 0,
    }

    rows = []
    for region, mask in masks.items():
        mask = mask & (volumes > 0)
        if not np.any(mask):
            rows.append({"region": region, "volume": 0.0, "I_Q": np.nan, "I_Lambda2": np.nan, "Q_volume_fraction": np.nan, "Lambda2_volume_fraction": np.nan})
            continue
        vr = float(np.sum(volumes[mask]))
        iq = float(np.sum(np.maximum(q[mask] - Q_THR, 0.0) * volumes[mask]) / vr)
        il2 = float(np.sum(np.maximum(-l2[mask] - L2_THR, 0.0) * volumes[mask]) / vr)
        qfrac = float(np.sum((q[mask] > Q_THR) * volumes[mask]) / vr)
        l2frac = float(np.sum((l2[mask] < -L2_THR) * volumes[mask]) / vr)
        rows.append({"region": region, "volume": vr, "I_Q": iq, "I_Lambda2": il2, "Q_volume_fraction": qfrac, "Lambda2_volume_fraction": l2frac})
    return pd.DataFrame(rows)


def aggregate_vortex_metrics(vtk_root: Path, selected: pd.DataFrame) -> pd.DataFrame:
    all_rows = []
    for _, row in selected.iterrows():
        time_s = f"{float(row['selected_time_s']):g}"
        files = sorted(vtk_root.glob(f"processor*/VTK/processor*_{time_s}.vtk"))
        if len(files) != 20:
            raise RuntimeError(f"Expected 20 processor VTK files for t={time_s}, found {len(files)}")
        partial = []
        for path in files:
            partial.append(processor_metrics(path))
        df = pd.concat(partial, ignore_index=True)
        grouped = []
        for region, g in df.groupby("region"):
            vol = g["volume"].to_numpy(float)
            total = float(np.sum(vol))
            out = {
                "label": row["label"],
                "time_s": float(row["selected_time_s"]),
                "phase_deg": float(row["selected_phase_deg"]),
                "region": region,
                "volume_m3": total,
            }
            for col in ["I_Q", "I_Lambda2", "Q_volume_fraction", "Lambda2_volume_fraction"]:
                vals = g[col].to_numpy(float)
                ok = np.isfinite(vals) & (vol > 0)
                out[col] = float(np.sum(vals[ok] * vol[ok]) / np.sum(vol[ok])) if np.any(ok) else np.nan
            out["I_Q_star"] = out["I_Q"] * D * D / (U_REF * U_REF)
            out["I_Lambda2_star"] = out["I_Lambda2"] * D * D / (U_REF * U_REF)
            grouped.append(out)
        all_rows.extend(grouped)
        print(f"processed {row['label']} t={time_s}")
    return pd.DataFrame(all_rows)


def circular_phase_distance_deg(a: np.ndarray, b: float) -> np.ndarray:
    return np.abs((a - b + 180.0) % 360.0 - 180.0)


def mean_or_nan(values: np.ndarray) -> float:
    return float(np.nanmean(values)) if np.any(np.isfinite(values)) else np.nan


def heat_metrics(selected: pd.DataFrame) -> pd.DataFrame:
    tube = np.load(RUN_DIR / "data" / "009" / "run008_009_phase_arrays.npz")
    phase_deg = tube["phase_deg"]
    theta = tube["theta_centers"]
    theta_deg = (np.degrees(theta) + 360.0) % 360.0
    z = tube["z_centers"]
    tube_phase = tube["tube_nu_phase"]
    fin_x = tube["fin_x"]
    fin_min = tube["fin_z_min_phase"]
    fin_max = tube["fin_z_max_phase"]

    z_near_fin = np.minimum(np.abs(z - Z_MIN), np.abs(z - Z_MAX)) < 0.20 * D
    z_all = np.ones_like(z, dtype=bool)

    tube_masks = {
        "tube_sep": ((theta_deg > 55) & (theta_deg < 125)) | ((theta_deg > 235) & (theta_deg < 305)),
        "tube_rear": (theta_deg < 60) | (theta_deg > 300),
        "tube_front": (theta_deg > 135) & (theta_deg < 225),
    }

    fin_masks = {
        "fin_near_tube": np.abs(fin_x) < 0.5 * D,
        "fin_downstream_sweep": (fin_x > 0.0) & (fin_x < np.nanmax(fin_x)),
        "fin_upstream_control": (fin_x < -0.5 * D),
    }

    region_to_surfaces = {
        "R_sep": ["tube_sep"],
        "R_near_wake": ["tube_rear"],
        "R_fin_junction": ["tube_junction", "fin_near_tube"],
        "R_fin_sweep": ["fin_downstream_sweep"],
        "R_far_wake": ["fin_upstream_control"],
        "R_global_control": ["tube_rear", "fin_downstream_sweep"],
    }

    rows = []
    for _, row in selected.iterrows():
        idx = int(np.argmin(circular_phase_distance_deg(phase_deg, float(row["selected_phase_deg"]))))
        phase_bin = float(phase_deg[idx])
        tube_map = tube_phase[idx]
        fin_pair = np.nanmean(np.stack([fin_min[idx], fin_max[idx]]), axis=0)
        for region, surfaces in region_to_surfaces.items():
            vals = []
            names = []
            for surface in surfaces:
                if surface == "tube_junction":
                    mask = np.outer(z_near_fin, np.ones_like(theta, dtype=bool))
                    vals.append(mean_or_nan(tube_map[mask]))
                elif surface.startswith("tube_"):
                    tmask = tube_masks[surface]
                    zmask = z_all
                    mask = np.outer(zmask, tmask)
                    vals.append(mean_or_nan(tube_map[mask]))
                else:
                    fmask = fin_masks[surface]
                    vals.append(mean_or_nan(fin_pair[fmask]))
                names.append(surface)
            rows.append(
                {
                    "label": row["label"],
                    "time_s": float(row["selected_time_s"]),
                    "phase_deg": float(row["selected_phase_deg"]),
                    "phase_bin_deg": phase_bin,
                    "region": region,
                    "surface_region": "+".join(names),
                    "Nu_mean": mean_or_nan(np.asarray(vals, dtype=float)),
                    "Nu_components": ";".join(f"{name}:{val:.6g}" for name, val in zip(names, vals)),
                }
            )
    return pd.DataFrame(rows)


def write_csv(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, index=False, float_format="%.10g")


def plot_results(merged: pd.DataFrame, heat: pd.DataFrame) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    order = ["R_sep", "R_near_wake", "R_fin_junction", "R_fin_sweep", "R_far_wake", "R_global_control"]
    colors = {
        "R_sep": "#d95f02",
        "R_near_wake": "#1b9e77",
        "R_fin_junction": "#7570b3",
        "R_fin_sweep": "#e7298a",
        "R_far_wake": "#666666",
        "R_global_control": "#222222",
    }

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    ax = axes[0, 0]
    # Schematic in x-y plane.
    theta = np.linspace(0, 2 * np.pi, 300)
    ax.plot(R_TUBE * np.cos(theta) * 1000, R_TUBE * np.sin(theta) * 1000, color="black", lw=1.5)
    rects = [
        ("R_near_wake", 0.25 * D, -1.0 * D, 2.25 * D, 2.0 * D),
        ("R_far_wake", 3.0 * D, -1.5 * D, 3.0 * D, 3.0 * D),
    ]
    for name, x0, y0, w, h in rects:
        ax.add_patch(plt.Rectangle((x0 * 1000, y0 * 1000), w * 1000, h * 1000, fill=False, ec=colors[name], lw=2, label=name))
    ax.add_patch(plt.Rectangle((-0.5 * D * 1000, -16), 3.5 * D * 1000, 32, fill=False, ec=colors["R_fin_sweep"], lw=2, ls="--", label="R_fin_sweep x-window"))
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x relative to tube centre [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_title("A. Region definitions, x-y projection")
    ax.legend(fontsize=8, loc="upper right")

    ax = axes[0, 1]
    for region in order:
        g = merged[merged["region"] == region].sort_values("phase_deg")
        if g.empty:
            continue
        ax.plot(g["phase_deg"], g["I_Lambda2_star"], marker="o", color=colors[region], label=region)
    ax.set_xlabel("Cl phase [deg]")
    ax.set_ylabel(r"$I_{\lambda_2}^* = I_{\lambda_2}D^2/U_{ref}^2$")
    ax.set_title("B. Region-limited Lambda2 intensity")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    for region in order:
        g = merged[merged["region"] == region].sort_values("phase_deg")
        if g.empty:
            continue
        ax.plot(g["phase_deg"], g["Nu_mean"], marker="s", color=colors[region], label=region)
    ax.set_xlabel("Cl phase [deg]")
    ax.set_ylabel("phase-matched local Nu")
    ax.set_title("C. Paired local heat-transfer response")

    ax = axes[1, 1]
    for region in ["R_sep", "R_near_wake", "R_fin_junction", "R_fin_sweep", "R_far_wake"]:
        g = merged[merged["region"] == region]
        if g.empty:
            continue
        ax.scatter(g["I_Lambda2_star"], g["Nu_mean"], color=colors[region], label=region, s=45)
        if len(g) >= 3:
            x = g["I_Lambda2_star"].to_numpy(float)
            y = g["Nu_mean"].to_numpy(float)
            ok = np.isfinite(x) & np.isfinite(y)
            if np.sum(ok) >= 3:
                r = np.corrcoef(x[ok], y[ok])[0, 1]
                ax.text(x[ok][-1], y[ok][-1], f"r={r:.2f}", fontsize=8, color=colors[region])
    ax.set_xlabel(r"$I_{\lambda_2}^*$")
    ax.set_ylabel("local Nu")
    ax.set_title("D. Six-phase structure/heat pairing")
    ax.legend(fontsize=8)

    fig.suptitle("run008 layer 015: region-limited vortical activity, local Nu, and Cl phase", fontsize=14)
    fig.savefig(FIG_DIR / "run008_015_region_structure_heat_phase.png", dpi=220)
    fig.savefig(FIG_DIR / "run008_015_region_structure_heat_phase.pdf")
    plt.close(fig)


def write_report(vortex: pd.DataFrame, heat: pd.DataFrame, merged: pd.DataFrame) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    corr_rows = []
    for region, g in merged.groupby("region"):
        x = g["I_Lambda2_star"].to_numpy(float)
        y = g["Nu_mean"].to_numpy(float)
        ok = np.isfinite(x) & np.isfinite(y)
        corr = float(np.corrcoef(x[ok], y[ok])[0, 1]) if np.sum(ok) >= 3 else np.nan
        corr_rows.append({"region": region, "corr_I_Lambda2_star_Nu": corr, "n": int(np.sum(ok))})
    corr_df = pd.DataFrame(corr_rows).sort_values("region")
    corr_df.to_csv(DATA_DIR / "run008_015_region_structure_heat_correlations.csv", index=False, float_format="%.6g")

    key = merged.pivot_table(index=["label", "phase_deg"], columns="region", values="I_Lambda2_star").reset_index()
    key.to_csv(DATA_DIR / "run008_015_phase_region_lambda2_pivot.csv", index=False, float_format="%.6g")

    top_corr = corr_df.sort_values("corr_I_Lambda2_star_Nu", ascending=False).head(3)
    lines = [
        "# V4b_3D run008 layer 015: region-limited structure/heat/phase coupling",
        "",
        "## Purpose",
        "",
        "This diagnostic layer asks whether local vortical activity in physically",
        "defined regions is more informative than global Q/Lambda2 cell counts when",
        "paired with local heat-transfer response and the Cl shedding phase.",
        "",
        "No new CFD was run. The layer uses the six existing layer-013 full-field",
        "checkpoints and local Nu arrays from layers 004/005/009.",
        "",
        "## Inputs",
        "",
        "- Q/Lambda2/vorticity VTK export: `/home/hexmachina/of_runs/V4b_3D_run008_q_lambda2_013/vtk_processors`",
        "- selected phases: `data/013/run008_013_selected_q_lambda2_times.csv`",
        "- tube local Nu phase maps: `data/009/run008_009_phase_arrays.npz`",
        "- fin local Nu phase maps: `data/009/run008_009_phase_arrays.npz`",
        "",
        "## Region definitions",
        "",
        f"- `D = {D} m`, `R = {R_TUBE} m`, `U_ref = {U_REF} m/s`",
        "- tube centre assumed at `(0, 0, 0)` in the OpenFOAM case coordinates",
        "- fin planes at `z = -0.006 m` and `z = +0.006 m`",
        f"- thresholds: `Q_thr = {Q_THR}`, `Lambda2_thr = -{L2_THR}`",
        "",
        "| region | physical target | paired heat region |",
        "|---|---|---|",
        "| `R_sep` | side shear-layer/separation shell near tube | `tube_sep` |",
        "| `R_near_wake` | immediate wake behind tube | `tube_rear` |",
        "| `R_fin_junction` | tube-fin junction volume | `tube_junction + fin_near_tube` |",
        "| `R_fin_sweep` | near-fin downstream sweeping zone | `fin_downstream_sweep` |",
        "| `R_far_wake` | downstream control region | `fin_upstream_control` |",
        "| `R_global_control` | all cells with positive volume | global control pairing |",
        "",
        "## Outputs",
        "",
        "- `data/015/run008_015_region_q_lambda2_metrics.csv`",
        "- `data/015/run008_015_region_heat_metrics.csv`",
        "- `data/015/run008_015_region_structure_heat_merged.csv`",
        "- `data/015/run008_015_region_structure_heat_correlations.csv`",
        "- `figures/015/run008_015_region_structure_heat_phase.png`",
        "- `figures/015/run008_015_region_structure_heat_phase.pdf`",
        "",
        "## First-pass correlation screen",
        "",
        "| region | corr(I_Lambda2*, Nu) | n |",
        "|---|---:|---:|",
    ]
    for _, row in corr_df.iterrows():
        lines.append(f"| `{row['region']}` | {row['corr_I_Lambda2_star_Nu']:.3f} | {int(row['n'])} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "This is a six-phase diagnostic, so it should be read as a screening layer,",
        "not as a final causal/lag analysis. It is useful if region-limited",
        "structure metrics vary more clearly than the global control and if the",
        "stronger correlations occur in physically paired regions, especially",
        "`R_near_wake`, `R_sep`, or `R_fin_junction`.",
        "",
        "The paper-grade extension would compute Q/Lambda2 for many more run008",
        "checkpoints over `t = 2..10 s`, then evaluate lagged correlations between",
        "regional structure metrics and local Nu/q''.",
        "",
        "Top positive six-phase screens:",
        "",
    ]
    for _, row in top_corr.iterrows():
        lines.append(f"- `{row['region']}`: corr(I_Lambda2*, Nu) = `{row['corr_I_Lambda2_star_Nu']:.3f}`")
    lines.append("")
    (DATA_DIR / "run008_015_region_structure_heat_metrics.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    selected = pd.read_csv(RUN_DIR / "data" / "013" / "run008_013_selected_q_lambda2_times.csv")
    vtk_root = find_vtk_root()

    vortex = aggregate_vortex_metrics(vtk_root, selected)
    heat = heat_metrics(selected)
    merged = vortex.merge(heat, on=["label", "time_s", "phase_deg", "region"], how="left")

    write_csv(DATA_DIR / "run008_015_region_q_lambda2_metrics.csv", vortex)
    write_csv(DATA_DIR / "run008_015_region_heat_metrics.csv", heat)
    write_csv(DATA_DIR / "run008_015_region_structure_heat_merged.csv", merged)

    metadata = {
        "vtk_root": str(vtk_root),
        "n_selected_phases": int(len(selected)),
        "regions": sorted(vortex["region"].unique().tolist()),
        "Q_thr": Q_THR,
        "Lambda2_thr_abs": L2_THR,
        "D": D,
        "U_ref": U_REF,
        "coordinate_assumption": "tube centre at (0,0,0), fin planes z=+-0.006 m",
    }
    (DATA_DIR / "run008_015_region_structure_heat_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    plot_results(merged, heat)
    write_report(vortex, heat, merged)
    print((DATA_DIR / "run008_015_region_structure_heat_metrics.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
