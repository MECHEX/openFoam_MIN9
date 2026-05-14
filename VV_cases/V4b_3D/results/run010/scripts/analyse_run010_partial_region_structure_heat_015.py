from __future__ import annotations

import importlib.util
import math
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


RUN_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = RUN_DIR.parents[3]
DATA_DIR = RUN_DIR / "data" / "015_partial"
FIG_DIR = RUN_DIR / "figures" / "015_partial"

CASE_DIR = Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run010_varprops_cp")
VTK_ROOT = Path(r"\\wsl.localhost\Ubuntu-24.04\home\hexmachina\of_runs\V4b_3D_run010_varprops_cp_q_lambda2_partial48\vtk_processors")

D = 0.012
U_REF = 0.25266
T_IN = 293.15
T_HOT = 343.15
C_AIR = 1005.0
MU_AIR = 1.827e-5
PR_AIR = 0.713
K_AIR = C_AIR * MU_AIR / PR_AIR
A_HOT_TOTAL = 0.002032


def load_run008_015_module():
    path = REPO_ROOT / "VV_cases" / "V4b_3D" / "results" / "run008" / "scripts" / "analyse_run008_region_structure_heat_015.py"
    spec = importlib.util.spec_from_file_location("run008_layer015", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def lmtd(t_out: float) -> float:
    d1 = T_HOT - T_IN
    d2 = T_HOT - t_out
    return (d1 - d2) / math.log(d1 / d2)


def read_wall_heat_flux() -> dict[str, np.ndarray]:
    path = CASE_DIR / "postProcessing" / "wallHeatFlux" / "0" / "wallHeatFlux.dat"
    per_time: dict[float, dict[str, dict[str, float]]] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 6:
            per_time.setdefault(float(parts[0]), {})[parts[1]] = {"Q": float(parts[4]), "q": float(parts[5])}
    times = np.asarray(sorted(per_time), dtype=float)
    out = {"time": times}
    for patch in ["hot_tube", "hot_fin_z_min", "hot_fin_z_max"]:
        q_rate = np.asarray([per_time[t].get(patch, {}).get("Q", np.nan) for t in times])
        q_flux = np.asarray([per_time[t].get(patch, {}).get("q", np.nan) for t in times])
        out[f"Q_{patch}"] = q_rate
        out[f"Araw_{patch}"] = q_rate / q_flux
    out["Q_tube"] = out["Q_hot_tube"]
    out["Q_fin_min"] = out["Q_hot_fin_z_min"]
    out["Q_fin_max"] = out["Q_hot_fin_z_max"]
    out["Q_fins"] = out["Q_fin_min"] + out["Q_fin_max"]
    out["Q_wall"] = out["Q_tube"] + out["Q_fins"]
    return out


def patch_nfaces(boundary_text: str, name: str) -> int:
    match = re.search(rf"{re.escape(name)}\s*\{{(.*?)\}}", boundary_text, re.S)
    if not match:
        return 0
    nmatch = re.search(r"nFaces\s+(\d+)\s*;", match.group(1))
    return int(nmatch.group(1)) if nmatch else 0


def patch_values(path: Path, patch: str, n_faces: int) -> np.ndarray:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"{re.escape(patch)}\s*\{{(.*?)\n\s*\}}", text, re.S)
    if not match:
        raise RuntimeError(f"Patch {patch} not found in {path}")
    section = match.group(1)
    uniform = re.search(r"value\s+uniform\s+([0-9eE.+\-]+)", section)
    if uniform:
        return np.full(n_faces, float(uniform.group(1)))
    vals = re.search(r"value\s+nonuniform\s+List<scalar>\s+(\d+)\s*\((.*?)\)", section, re.S)
    if not vals:
        raise RuntimeError(f"Patch values not found for {patch} in {path}")
    arr = np.fromstring(vals.group(2), sep=" ")
    if len(arr) != n_faces:
        raise RuntimeError(f"Expected {n_faces} values, got {len(arr)} in {path}")
    return arr


def outlet_at_time(time_s: float) -> dict[str, float]:
    name = f"{time_s:g}"
    mdot = 0.0
    mt = 0.0
    for proc in sorted(CASE_DIR.glob("processor*"), key=lambda p: int(p.name.replace("processor", ""))):
        boundary = (proc / "constant" / "polyMesh" / "boundary").read_text(encoding="utf-8", errors="replace")
        n_faces = patch_nfaces(boundary, "outlet")
        if n_faces <= 0:
            continue
        t_path = proc / name / "T"
        phi_path = proc / name / "phi"
        if not t_path.exists() or not phi_path.exists():
            continue
        temp = patch_values(t_path, "outlet", n_faces)
        phi = patch_values(phi_path, "outlet", n_faces)
        weights = np.maximum(phi, 0.0)
        mdot += float(np.sum(weights))
        mt += float(np.sum(weights * temp))
    if mdot <= 0:
        return {"T_out": np.nan, "m_dot": np.nan, "Q_air": np.nan, "LMTD": np.nan, "Nu_EB": np.nan}
    t_out = mt / mdot
    q_air = mdot * C_AIR * (t_out - T_IN)
    l_val = lmtd(t_out)
    nu_eb = (q_air / (A_HOT_TOTAL * l_val)) * D / K_AIR
    return {"T_out": t_out, "m_dot": mdot, "Q_air": q_air, "LMTD": l_val, "Nu_EB": nu_eb}


def heat_table(selected: pd.DataFrame) -> pd.DataFrame:
    wall = read_wall_heat_flux()
    times = wall["time"]
    raw_areas = {
        "tube": float(np.nanmean(wall["Araw_hot_tube"][(times >= 2.0) & (times <= selected["time_s"].max())])),
        "fin_min": float(np.nanmean(wall["Araw_hot_fin_z_min"][(times >= 2.0) & (times <= selected["time_s"].max())])),
        "fin_max": float(np.nanmean(wall["Araw_hot_fin_z_max"][(times >= 2.0) & (times <= selected["time_s"].max())])),
    }
    scale = A_HOT_TOTAL / sum(raw_areas.values())
    areas = {k: v * scale for k, v in raw_areas.items()}

    rows = []
    for row in selected.itertuples(index=False):
        t = float(row.time_s)
        q_tube = float(np.interp(t, times, wall["Q_tube"]))
        q_fins = float(np.interp(t, times, wall["Q_fins"]))
        q_wall = float(np.interp(t, times, wall["Q_wall"]))
        out = outlet_at_time(t)
        l_val = out["LMTD"]
        nu_tube = (q_tube / (areas["tube"] * l_val)) * D / K_AIR
        nu_fins = (q_fins / ((areas["fin_min"] + areas["fin_max"]) * l_val)) * D / K_AIR
        nu_wall = (q_wall / A_HOT_TOTAL / l_val) * D / K_AIR
        rows.append(
            {
                "phase_index": row.phase_index,
                "time_s": t,
                "phase_deg": float(row.actual_phase_deg),
                "Q_tube": q_tube,
                "Q_fins": q_fins,
                "Q_wall": q_wall,
                "Q_air": out["Q_air"],
                "closure_pct": 100.0 * (q_wall - out["Q_air"]) / out["Q_air"],
                "Nu_tube_wall": nu_tube,
                "Nu_fins_wall": nu_fins,
                "Nu_wall": nu_wall,
                "Nu_EB": out["Nu_EB"],
                "T_out": out["T_out"],
            }
        )
    return pd.DataFrame(rows)


def paired_heat_for_region(heat: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "R_sep": ("Nu_tube_wall", "Q_tube"),
        "R_near_wake": ("Nu_tube_wall", "Q_tube"),
        "R_fin_junction": ("Nu_wall", "Q_wall"),
        "R_fin_sweep": ("Nu_fins_wall", "Q_fins"),
        "R_far_wake": ("Nu_fins_wall", "Q_fins"),
        "R_global_control": ("Nu_wall", "Q_wall"),
    }
    rows = []
    for hrow in heat.itertuples(index=False):
        for region, (nu_col, q_col) in mapping.items():
            rows.append(
                {
                    "phase_index": hrow.phase_index,
                    "time_s": hrow.time_s,
                    "phase_deg": hrow.phase_deg,
                    "region": region,
                    "paired_Nu": getattr(hrow, nu_col),
                    "paired_Q": getattr(hrow, q_col),
                    "paired_metric": f"{nu_col}+{q_col}",
                }
            )
    return pd.DataFrame(rows)


def processor_id(path: Path) -> int:
    return int(path.parent.parent.name.replace("processor", ""))


def build_region_cache(run008_layer, vtk_root: Path, first_time: float) -> dict[int, dict[str, object]]:
    time_name = f"{first_time:g}"
    files = sorted(vtk_root.glob(f"processor*/VTK/processor*_{time_name}.vtk"), key=processor_id)
    if len(files) != 20:
        raise RuntimeError(f"Expected 20 processor files for cache time {time_name}, found {len(files)}")

    cache: dict[int, dict[str, object]] = {}
    for path in files:
        grid = run008_layer.read_legacy_vtk(path)
        centers = np.asarray([grid.points[ids].mean(axis=0) for ids in grid.cells])
        volumes = np.asarray(
            [run008_layer.cell_volume(grid.points, ids, int(ct)) for ids, ct in zip(grid.cells, grid.cell_types)]
        )

        x = centers[:, 0]
        y = centers[:, 1]
        z = centers[:, 2]
        r = np.sqrt(x * x + y * y)
        d_tube = r - D / 2.0
        d_fin = np.minimum(np.abs(z + 0.006), np.abs(z - 0.006))
        masks = {
            "R_sep": (d_tube > 0.0) & (d_tube < 0.25 * D) & (np.abs(y) > 0.35 * D) & (np.abs(y) < 1.05 * D),
            "R_near_wake": (x > 0.25 * D) & (x < 2.5 * D) & (np.abs(y) < 1.0 * D),
            "R_fin_junction": (d_tube > 0.0) & (d_tube < 0.35 * D) & (d_fin < 0.20 * D),
            "R_fin_sweep": (d_fin < 0.15 * D) & (x > -0.5 * D) & (x < 3.0 * D),
            "R_far_wake": (x > 3.0 * D) & (x < 6.0 * D) & (np.abs(y) < 1.5 * D),
            "R_global_control": volumes > 0,
        }
        masks = {key: mask & (volumes > 0) for key, mask in masks.items()}
        cache[processor_id(path)] = {"volumes": volumes, "masks": masks}
    return cache


def aggregate_vortex_metrics_fast(run008_layer, vtk_root: Path, selected: pd.DataFrame) -> pd.DataFrame:
    cache = build_region_cache(run008_layer, vtk_root, float(selected.iloc[0]["selected_time_s"]))
    rows = []
    for row in selected.itertuples(index=False):
        time_s = float(row.selected_time_s)
        time_name = f"{time_s:g}"
        files = sorted(vtk_root.glob(f"processor*/VTK/processor*_{time_name}.vtk"), key=processor_id)
        if len(files) != 20:
            raise RuntimeError(f"Expected 20 VTK files for t={time_name}, found {len(files)}")

        accum: dict[str, dict[str, float]] = {}
        for path in files:
            grid = run008_layer.read_legacy_vtk(path)
            proc_cache = cache[processor_id(path)]
            volumes = proc_cache["volumes"]
            q = np.asarray(grid.cell_data["Q"], dtype=float)
            l2 = np.asarray(grid.cell_data["Lambda2"], dtype=float)
            for region, mask in proc_cache["masks"].items():
                vr = float(np.sum(volumes[mask]))
                if vr <= 0:
                    continue
                rec = accum.setdefault(region, {"volume": 0.0, "IQ_num": 0.0, "IL2_num": 0.0, "Qfrac_num": 0.0, "L2frac_num": 0.0})
                rec["volume"] += vr
                rec["IQ_num"] += float(np.sum(np.maximum(q[mask] - run008_layer.Q_THR, 0.0) * volumes[mask]))
                rec["IL2_num"] += float(np.sum(np.maximum(-l2[mask] - run008_layer.L2_THR, 0.0) * volumes[mask]))
                rec["Qfrac_num"] += float(np.sum((q[mask] > run008_layer.Q_THR) * volumes[mask]))
                rec["L2frac_num"] += float(np.sum((l2[mask] < -run008_layer.L2_THR) * volumes[mask]))

        for region, rec in accum.items():
            vol = rec["volume"]
            iq = rec["IQ_num"] / vol
            il2 = rec["IL2_num"] / vol
            rows.append(
                {
                    "label": row.label,
                    "time_s": time_s,
                    "phase_deg": float(row.selected_phase_deg),
                    "region": region,
                    "volume_m3": vol,
                    "I_Q": iq,
                    "I_Lambda2": il2,
                    "Q_volume_fraction": rec["Qfrac_num"] / vol,
                    "Lambda2_volume_fraction": rec["L2frac_num"] / vol,
                    "I_Q_star": iq * D * D / (U_REF * U_REF),
                    "I_Lambda2_star": il2 * D * D / (U_REF * U_REF),
                }
            )
        print(f"processed {row.label} t={time_name}", flush=True)
    return pd.DataFrame(rows)


def corr_or_nan(x: pd.Series, y: pd.Series) -> float:
    a = x.to_numpy(float)
    b = y.to_numpy(float)
    ok = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[ok], b[ok])[0, 1]) if np.sum(ok) >= 3 else np.nan


def make_figure(vortex: pd.DataFrame, heat: pd.DataFrame, merged: pd.DataFrame) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    regions = ["R_sep", "R_near_wake", "R_fin_junction", "R_fin_sweep", "R_far_wake", "R_global_control"]
    colors = dict(zip(regions, ["#d95f02", "#1b9e77", "#7570b3", "#e7298a", "#666666", "#222222"]))
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)

    ax = axes[0, 0]
    for region in regions:
        g = vortex[vortex["region"] == region].sort_values("phase_deg")
        ax.plot(g["phase_deg"], g["I_Lambda2_star"], marker="o", ms=3, lw=1, label=region, color=colors[region])
    ax.set_xlabel("Cl phase [deg]")
    ax.set_ylabel(r"$I_{\lambda_2}^*$")
    ax.set_title("A. Region-limited Lambda2 intensity")
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    for col, label in [("Nu_wall", "Nu wall"), ("Nu_tube_wall", "Nu tube"), ("Nu_fins_wall", "Nu fins"), ("Nu_EB", "Nu EB")]:
        ax.plot(heat["phase_deg"], heat[col], marker="s", ms=3, lw=1, label=label)
    ax.set_xlabel("Cl phase [deg]")
    ax.set_ylabel("Nu")
    ax.set_title("B. Phase heat-transfer response")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    ax.plot(heat["phase_deg"], heat["Q_wall"], marker="o", ms=3, label="Q_wall")
    ax.plot(heat["phase_deg"], heat["Q_air"], marker="o", ms=3, label="Q_air")
    ax2 = ax.twinx()
    ax2.plot(heat["phase_deg"], heat["closure_pct"], color="#6a3d9a", lw=1, label="closure")
    ax.set_xlabel("Cl phase [deg]")
    ax.set_ylabel("Q [W]")
    ax2.set_ylabel("closure [%]")
    ax.set_title("C. Wall-air heat balance at selected phases")
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, fontsize=8)

    ax = axes[1, 1]
    for region in regions:
        g = merged[merged["region"] == region]
        ax.scatter(g["I_Lambda2_star"], g["paired_Nu"], s=20, label=region, color=colors[region])
        r = corr_or_nan(g["I_Lambda2_star"], g["paired_Nu"])
        if np.isfinite(r):
            ax.text(g["I_Lambda2_star"].median(), g["paired_Nu"].median(), f"{r:.2f}", fontsize=8, color=colors[region])
    ax.set_xlabel(r"$I_{\lambda_2}^*$")
    ax.set_ylabel("paired Nu")
    ax.set_title("D. Structure/heat pairing, 48 partial phases")
    ax.legend(fontsize=8)

    fig.suptitle("run010 partial layer 015: 48-phase region-limited structure/heat diagnostic", fontsize=14)
    fig.savefig(FIG_DIR / "run010_015_partial_region_structure_heat_phase.png", dpi=220)
    fig.savefig(FIG_DIR / "run010_015_partial_region_structure_heat_phase.pdf")
    plt.close(fig)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    selected = pd.read_csv(RUN_DIR / "data" / "001" / "run010_001_partial_48_phase_snapshot_selection.csv")
    selected_for_vortex = selected.rename(
        columns={"time_s": "selected_time_s", "actual_phase_deg": "selected_phase_deg"}
    )
    selected_for_vortex["label"] = selected_for_vortex["phase_index"].map(lambda i: f"phase_{int(i):02d}")

    run008_layer = load_run008_015_module()
    vortex = aggregate_vortex_metrics_fast(run008_layer, VTK_ROOT, selected_for_vortex)
    vortex["phase_index"] = vortex["label"].str.extract(r"(\d+)").astype(int)
    heat = heat_table(selected)
    paired = paired_heat_for_region(heat)
    merged = vortex.merge(paired, on=["phase_index", "time_s", "phase_deg", "region"], how="left")

    vortex.to_csv(DATA_DIR / "run010_015_partial_region_q_lambda2_metrics.csv", index=False, float_format="%.10g")
    heat.to_csv(DATA_DIR / "run010_015_partial_heat_metrics.csv", index=False, float_format="%.10g")
    merged.to_csv(DATA_DIR / "run010_015_partial_region_structure_heat_merged.csv", index=False, float_format="%.10g")

    corr_rows = []
    for region, g in merged.groupby("region"):
        corr_rows.append(
            {
                "region": region,
                "corr_I_Lambda2_star_paired_Nu": corr_or_nan(g["I_Lambda2_star"], g["paired_Nu"]),
                "corr_I_Q_star_paired_Nu": corr_or_nan(g["I_Q_star"], g["paired_Nu"]),
                "corr_I_Lambda2_star_paired_Q": corr_or_nan(g["I_Lambda2_star"], g["paired_Q"]),
                "n": len(g),
            }
        )
    corr = pd.DataFrame(corr_rows).sort_values("region")
    corr.to_csv(DATA_DIR / "run010_015_partial_region_structure_heat_correlations.csv", index=False, float_format="%.10g")
    pivot = vortex.pivot_table(index=["phase_index", "time_s", "phase_deg"], columns="region", values="I_Lambda2_star").reset_index()
    pivot.to_csv(DATA_DIR / "run010_015_partial_phase_region_lambda2_pivot.csv", index=False, float_format="%.10g")
    make_figure(vortex, heat, merged)

    summary = [
        "# V4b_3D run010 partial layer 015",
        "",
        "This is a stopped-partial diagnostic based on the available `t = 2..5.935 s` run010 data.",
        "It should be recomputed after run010 reaches `t = 10 s` before being treated as final.",
        "",
        "## Inputs",
        "",
        "- 48 phase-selected full-field snapshots from `data/001/run010_001_partial_48_phase_snapshot_selection.csv`",
        "- Q/Lambda2/vorticity VTK export: `/home/hexmachina/of_runs/V4b_3D_run010_varprops_cp_q_lambda2_partial48/vtk_processors`",
        "- wall heat flux and decomposed outlet fields from `/home/hexmachina/of_runs/V4b_3D_run010_varprops_cp`",
        "",
        "## Heat balance over selected phases",
        "",
        f"- `Q_wall_mean = {heat['Q_wall'].mean():.6g} W`",
        f"- `Q_air_mean = {heat['Q_air'].mean():.6g} W`",
        f"- `closure_mean = {heat['closure_pct'].mean():+.4f}%`",
        f"- `Nu_wall_mean = {heat['Nu_wall'].mean():.6g}`",
        f"- `Nu_EB_mean = {heat['Nu_EB'].mean():.6g}`",
        "",
        "## Correlation screen",
        "",
        "| region | corr(I_Lambda2*, paired Nu) | corr(I_Q*, paired Nu) | n |",
        "|---|---:|---:|---:|",
    ]
    for row in corr.itertuples(index=False):
        summary.append(f"| `{row.region}` | {row.corr_I_Lambda2_star_paired_Nu:.3f} | {row.corr_I_Q_star_paired_Nu:.3f} | {row.n} |")
    summary += [
        "",
        "Interpretation: this is a stronger screen than run008_015 because it uses 48 phases instead of six,",
        "but it is still partial because the run was stopped at `t = 5.935 s`.",
        "",
    ]
    (DATA_DIR / "run010_015_partial_region_structure_heat_metrics.md").write_text("\n".join(summary), encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
