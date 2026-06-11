from __future__ import annotations

import csv
import gzip
import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9")
OUT_DIR = REPO_DIR / "VV_cases/presentation_data/007_strong_indicators/00_1_wall_local_Nu"
SOURCE_002 = REPO_DIR / "VV_cases/presentation_data/002_Nu_and_vorticity"
STAGE00_DIR = REPO_DIR / "VV_cases/presentation_data/007_strong_indicators/00_fullNu3D_xt"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SOURCE_002))
from build_stripwise_heat_figures import PATCH_FILES, polygon_area, read_vtk_polydata  # noqa: E402

sys.path.insert(0, str(STAGE00_DIR))
from build_00_fullNu3D_xt import read_plane_tbulk, safe_plane_name  # noqa: E402


CASES = [
    {"Re": 100.0, "case": "run012_re100", "path": Path("/home/hexmachina/of_runs/V4b_3D_run012_re100_production"), "regime": "steady"},
    {"Re": 150.0, "case": "run013_re150", "path": Path("/home/hexmachina/of_runs/V4b_3D_run013_re150_production"), "regime": "steady"},
    {"Re": 160.0, "case": "run015_re160", "path": Path("/home/hexmachina/of_runs/V4b_3D_run015_re160_production"), "regime": "shedding"},
    {"Re": 175.0, "case": "run014_re175", "path": Path("/home/hexmachina/of_runs/V4b_3D_run014_re175_production"), "regime": "shedding"},
    {"Re": 200.0, "case": "run008_re200", "path": Path("/home/hexmachina/of_runs/V4b_3D_run008"), "regime": "production shedding"},
]

D_REF_M = 0.012
K_AIR_W_MK = 0.028
DX_M = 0.001
T_EPS = 1.0e-9

PATCH_LABELS = {
    "hot_tube.vtk": ("tube", "hot_tube"),
    "hot_fin_z_min.vtk": ("fins", "hot_fin_z_min"),
    "hot_fin_z_max.vtk": ("fins", "hot_fin_z_max"),
}


def numeric_time_dirs(base: Path) -> list[tuple[float, str]]:
    vals: list[tuple[float, str]] = []
    if not base.exists():
        return vals
    for p in base.iterdir():
        if not p.is_dir():
            continue
        try:
            vals.append((float(p.name), p.name))
        except ValueError:
            continue
    return sorted(vals, key=lambda item: item[0])


def selected_full_field_times(case: dict) -> list[str]:
    surface = {round(t, 10): name for t, name in numeric_time_dirs(case["path"] / "postProcessing/hot_tube_surface")}
    times: list[tuple[float, str]] = []
    for t, name in numeric_time_dirs(case["path"] / "processor0"):
        key = round(t, 10)
        field_dir = case["path"] / "processor0" / name
        if 8.0 <= t <= 10.0 and key in surface and all((field_dir / f).exists() for f in ["U", "T", "rho"]):
            times.append((t, surface[key]))
    return [name for _, name in sorted(times)]


def discover_edges() -> np.ndarray:
    xs: list[float] = []
    for case in CASES:
        times = selected_full_field_times(case)
        if not times:
            continue
        time = times[len(times) // 2]
        for group in PATCH_FILES.values():
            for tpl in group:
                f = case["path"] / "postProcessing" / tpl.format(time=time)
                if f.exists():
                    pts, _, _ = read_vtk_polydata(f)
                    xs.extend([float(pts[:, 0].min()), float(pts[:, 0].max())])
    left = math.floor(min(xs) / DX_M) * DX_M
    right = math.ceil(max(xs) / DX_M) * DX_M
    return np.arange(left, right + 0.5 * DX_M, DX_M)


def tbulk_profile(case_dir: Path, time_name: str, edges: np.ndarray) -> np.ndarray:
    out = []
    for x_m in edges:
        f = case_dir / "postProcessing" / safe_plane_name(float(x_m)) / time_name / "cutPlane.vtk"
        if not f.exists():
            raise FileNotFoundError(f)
        out.append(read_plane_tbulk(f)["T_bulk_yz_plane_K"])
    return np.asarray(out, dtype=float)


def local_rows_for_surface(
    case: dict,
    time_name: str,
    vtk_path: Path,
    edges: np.ndarray,
    tbulk_edges: np.ndarray,
):
    points, polygons, fields = read_vtk_polydata(vtk_path)
    q = fields["wallHeatFlux"]
    wall_t = fields.get("T")
    patch_group, patch_name = PATCH_LABELS.get(vtk_path.name, ("unknown", vtk_path.stem))
    for face_id, poly in enumerate(polygons):
        idx = np.asarray(poly, dtype=int)
        verts = points[idx]
        centroid = verts.mean(axis=0)
        area = polygon_area(verts)
        if area <= 0:
            continue
        x = float(centroid[0])
        t_bulk = float(np.interp(x, edges, tbulk_edges))
        t_wall = float(wall_t[idx].mean()) if wall_t is not None else 343.15
        delta_t = max(t_wall - t_bulk, T_EPS)
        q_wall = float(q[idx].mean())
        nu = q_wall * D_REF_M / (K_AIR_W_MK * delta_t)
        yield {
            "Re": case["Re"],
            "case": case["case"],
            "regime": case["regime"],
            "time_s": float(time_name),
            "patch_group": patch_group,
            "patch_name": patch_name,
            "face_id": face_id,
            "x_m": x,
            "y_m": float(centroid[1]),
            "z_m": float(centroid[2]),
            "area_m2": area,
            "q_wall_W_m2": q_wall,
            "T_wall_local_K": t_wall,
            "T_bulk_yz_local_K": t_bulk,
            "DeltaT_local_K": delta_t,
            "Nu_wall_local": nu,
        }


def update_stats(stats: dict, row: dict, edges: np.ndarray) -> None:
    x = row["x_m"]
    b = int(np.searchsorted(edges, x, side="right") - 1)
    if b < 0 or b >= len(edges) - 1:
        return
    x_center_mm = 0.5 * (edges[b] + edges[b + 1]) * 1000.0
    keys = [
        (row["Re"], row["case"], row["regime"], row["time_s"], "all", "all", x_center_mm),
        (row["Re"], row["case"], row["regime"], row["time_s"], row["patch_group"], row["patch_group"], x_center_mm),
        (row["Re"], row["case"], row["regime"], row["time_s"], row["patch_group"], row["patch_name"], x_center_mm),
    ]
    for key in keys:
        s = stats[key]
        a = row["area_m2"]
        q_int = row["q_wall_W_m2"] * a
        s["area_sum"] += a
        s["Q_sum"] += q_int
        s["Nu_area_sum"] += row["Nu_wall_local"] * a
        s["Nu2_area_sum"] += row["Nu_wall_local"] ** 2 * a
        s["q_area_sum"] += row["q_wall_W_m2"] * a
        s["n_faces"] += 1


def stats_to_frame(stats: dict) -> pd.DataFrame:
    rows = []
    for key, s in stats.items():
        re, case, regime, time_s, patch_group, patch_name, x_center_mm = key
        area = s["area_sum"]
        nu_mean = s["Nu_area_sum"] / area if area > 0 else np.nan
        nu2_mean = s["Nu2_area_sum"] / area if area > 0 else np.nan
        rows.append(
            {
                "Re": re,
                "case": case,
                "regime": regime,
                "time_s": time_s,
                "patch_group": patch_group,
                "patch_name": patch_name,
                "x_center_mm": x_center_mm,
                "area_m2": area,
                "Q_W": s["Q_sum"],
                "q_wall_area_mean_W_m2": s["q_area_sum"] / area if area > 0 else np.nan,
                "Nu_wall_area_mean": nu_mean,
                "Nu_wall_area_std": math.sqrt(max(nu2_mean - nu_mean**2, 0.0)) if area > 0 else np.nan,
                "n_faces": s["n_faces"],
            }
        )
    return pd.DataFrame(rows)


def make_figures(strip: pd.DataFrame) -> None:
    avg = (
        strip.groupby(["Re", "patch_group", "x_center_mm"], as_index=False)
        .agg(
            Nu_wall_area_mean_tavg=("Nu_wall_area_mean", "mean"),
            Nu_wall_area_std_time=("Nu_wall_area_mean", "std"),
            Q_W_tavg=("Q_W", "mean"),
        )
    )
    avg.to_csv(OUT_DIR / "wall_local_Nu_strip_time_averaged.csv", index=False)

    fig, axes = plt.subplots(3, 1, figsize=(10.5, 9.0), sharex=True)
    for patch_group, ax in zip(["all", "tube", "fins"], axes):
        sub_patch = avg[avg["patch_group"] == patch_group]
        for re, sub in sub_patch.groupby("Re"):
            ax.plot(sub["x_center_mm"], sub["Nu_wall_area_mean_tavg"], lw=2.0, label=f"Re {re:g}")
        ax.axvline(-6, color="0.35", ls="--", lw=0.8)
        ax.axvline(6, color="0.35", ls="--", lw=0.8)
        ax.set_ylabel(f"{patch_group}\nNu local")
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False, ncol=5)
    axes[-1].set_xlabel("x position [mm]")
    fig.suptitle("0.1 local wall Nu: area-weighted mean from wall polygons")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig01_wall_local_Nu_profiles_by_patch.png", dpi=240)
    fig.savefig(OUT_DIR / "fig01_wall_local_Nu_profiles_by_patch.pdf")
    plt.close(fig)

    amp = (
        strip[strip["patch_group"] == "all"]
        .groupby(["Re", "x_center_mm"], as_index=False)
        .agg(
            Nu_time_std=("Nu_wall_area_mean", "std"),
            Nu_time_mean=("Nu_wall_area_mean", "mean"),
        )
    )
    amp["Nu_cv_percent"] = 100.0 * amp["Nu_time_std"] / amp["Nu_time_mean"].abs()
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 7.0), sharex=True)
    for re, sub in amp.groupby("Re"):
        axes[0].plot(sub["x_center_mm"], sub["Nu_time_std"], marker="o", lw=1.8, label=f"Re {re:g}")
        axes[1].plot(sub["x_center_mm"], sub["Nu_cv_percent"], marker="o", lw=1.8, label=f"Re {re:g}")
    for ax in axes:
        ax.axvline(-6, color="0.35", ls="--", lw=0.8)
        ax.axvline(6, color="0.35", ls="--", lw=0.8)
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False, ncol=5)
    axes[0].set_ylabel("std_t(Nu local)")
    axes[1].set_ylabel("std/mean Nu [%]")
    axes[1].set_xlabel("x position [mm]")
    fig.suptitle("0.1 local wall Nu temporal modulation")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig02_wall_local_Nu_temporal_amplitude.png", dpi=240)
    fig.savefig(OUT_DIR / "fig02_wall_local_Nu_temporal_amplitude.pdf")
    plt.close(fig)


def write_readme(local_rows_count: int, strip: pd.DataFrame) -> None:
    n_times = strip.groupby("Re")["time_s"].nunique().to_dict()
    text = f"""# 00_1_wall_local_Nu

This folder implements layer `0.1`: local instantaneous wall Nusselt number on hot tube and fin surfaces.

Definition:

`Nu_wall_local(s,t) = q''_w(s,t) * D_ref / [k_air * (T_wall(s,t) - T_bulk_yz(x_s,t))]`

where:

- `s` is a hot-wall polygon centroid on tube or fins.
- `q''_w` comes directly from OpenFOAM `wallHeatFlux` on the hot surfaces.
- `T_wall(s,t)` comes from the wall-surface `T` field.
- `T_bulk_yz(x_s,t)` is interpolated from full y-z cut-plane mass-flow bulk temperature.
- `D_ref = {D_REF_M:g} m`, `k_air = {K_AIR_W_MK:g} W/(m K)`.

What this improves compared with earlier stage `00_fullNu3D_xt`:

- Stage 00 produced one area-integrated `Nu_3D(x,t)` per 1 mm strip.
- This stage produces local wall-polygon `Nu_wall_local(s,t)` before strip averaging.
- Strip values here are area-weighted summaries of local wall Nu, not the starting point.

Current sampling:

- full local rows written: `{local_rows_count}`
- available full-field times per Re: `{n_times}`

Outputs:

- `wall_local_Nu_time_resolved.csv.gz`: full local wall-polygon dataset.
- `wall_local_Nu_strip_stats.csv`: area-weighted strip/patch/time statistics.
- `wall_local_Nu_strip_time_averaged.csv`: time-averaged strip profiles.
- `fig01_wall_local_Nu_profiles_by_patch`: all/tube/fins local-Nu profiles.
- `fig02_wall_local_Nu_temporal_amplitude`: temporal modulation of local wall Nu.

Important limitation:

The wall field is local on the available hot-surface mesh, but temporal resolution is still limited by available full volume fields: currently 26 snapshots per Re over 8-10 s. More snapshots are needed for publication-grade coherence/SPOD.
"""
    (OUT_DIR / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    edges = discover_edges()
    local_path = OUT_DIR / "wall_local_Nu_time_resolved.csv.gz"
    fieldnames = [
        "Re",
        "case",
        "regime",
        "time_s",
        "patch_group",
        "patch_name",
        "face_id",
        "x_m",
        "y_m",
        "z_m",
        "area_m2",
        "q_wall_W_m2",
        "T_wall_local_K",
        "T_bulk_yz_local_K",
        "DeltaT_local_K",
        "Nu_wall_local",
    ]
    stats = defaultdict(lambda: defaultdict(float))
    n_rows = 0
    with gzip.open(local_path, "wt", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for case in CASES:
            times = selected_full_field_times(case)
            print(f"{case['case']}: {len(times)} times")
            for time_name in times:
                tb = tbulk_profile(case["path"], time_name, edges)
                for group in PATCH_FILES.values():
                    for tpl in group:
                        vtk_path = case["path"] / "postProcessing" / tpl.format(time=time_name)
                        if not vtk_path.exists():
                            continue
                        for row in local_rows_for_surface(case, time_name, vtk_path, edges, tb):
                            writer.writerow(row)
                            update_stats(stats, row, edges)
                            n_rows += 1
    strip = stats_to_frame(stats)
    strip.to_csv(OUT_DIR / "wall_local_Nu_strip_stats.csv", index=False)
    make_figures(strip)
    write_readme(n_rows, strip)
    print(f"Wrote {n_rows} local wall Nu rows to {local_path}")


if __name__ == "__main__":
    main()
