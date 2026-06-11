from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


OUT_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/presentation_data/002_Nu_and_vorticity")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CASES = [
    {"Re": 100, "case": "run012_re100", "path": Path("/home/hexmachina/of_runs/V4b_3D_run012_re100_production"), "window": (8.0, 10.0), "regime": "steady"},
    {"Re": 150, "case": "run013_re150", "path": Path("/home/hexmachina/of_runs/V4b_3D_run013_re150_production"), "window": (8.0, 10.0), "regime": "steady"},
    {"Re": 160, "case": "run015_re160", "path": Path("/home/hexmachina/of_runs/V4b_3D_run015_re160_production"), "window": (8.0, 10.0), "regime": "shedding"},
    {"Re": 175, "case": "run014_re175", "path": Path("/home/hexmachina/of_runs/V4b_3D_run014_re175_production"), "window": (8.0, 10.0), "regime": "shedding"},
    {"Re": 200, "case": "run008_re200", "path": Path("/home/hexmachina/of_runs/V4b_3D_run008"), "window": (8.0, 10.0), "regime": "production shedding"},
]

PATCH_FILES = {
    "tube": ["hot_tube_surface/{time}/hot_tube.vtk"],
    "fins": ["hot_fin_surface/{time}/hot_fin_z_min.vtk", "hot_fin_surface/{time}/hot_fin_z_max.vtk"],
}

DX = 0.001
TIME_STRIDE = 10


def read_vtk_polydata(path: Path) -> tuple[np.ndarray, list[list[int]], dict[str, np.ndarray]]:
    lines = path.read_text(errors="ignore").splitlines()
    i = 0
    points = None
    polygons: list[list[int]] = []
    fields: dict[str, np.ndarray] = {}
    while i < len(lines):
        parts = lines[i].split()
        if not parts:
            i += 1
            continue
        if parts[0] == "POINTS":
            n = int(parts[1])
            vals: list[float] = []
            i += 1
            while len(vals) < 3 * n:
                vals.extend(float(x) for x in lines[i].split())
                i += 1
            points = np.asarray(vals, dtype=float).reshape(n, 3)
            continue
        if parts[0] == "POLYGONS":
            n_poly = int(parts[1])
            raw: list[int] = []
            i += 1
            while len(polygons) < n_poly:
                raw.extend(int(float(x)) for x in lines[i].split())
                j = 0
                while j < len(raw) and len(polygons) < n_poly:
                    nverts = raw[j]
                    if j + 1 + nverts > len(raw):
                        break
                    polygons.append(raw[j + 1 : j + 1 + nverts])
                    j += 1 + nverts
                raw = raw[j:]
                i += 1
            continue
        if parts[0] == "FIELD" and parts[1] == "attributes":
            n_fields = int(parts[2])
            i += 1
            for _ in range(n_fields):
                header = lines[i].split()
                name = header[0]
                n_comp = int(header[1])
                n_tuple = int(header[2])
                count = n_comp * n_tuple
                vals = []
                i += 1
                while len(vals) < count:
                    vals.extend(float(x) for x in lines[i].split())
                    i += 1
                arr = np.asarray(vals, dtype=float)
                if n_comp > 1:
                    arr = arr.reshape(n_tuple, n_comp)
                fields[name] = arr
            continue
        i += 1
    if points is None:
        raise ValueError(f"No POINTS in {path}")
    return points, polygons, fields


def polygon_area(vertices: np.ndarray) -> float:
    if len(vertices) < 3:
        return 0.0
    origin = vertices[0]
    area = 0.0
    for i in range(1, len(vertices) - 1):
        area += 0.5 * np.linalg.norm(np.cross(vertices[i] - origin, vertices[i + 1] - origin))
    return float(area)


def time_dirs(case_dir: Path, surface_dir: str, t0: float, t1: float) -> list[str]:
    base = case_dir / "postProcessing" / surface_dir
    vals = []
    for p in base.iterdir():
        if not p.is_dir():
            continue
        try:
            t = float(p.name)
        except ValueError:
            continue
        if t0 <= t <= t1:
            vals.append((t, p.name))
    vals.sort()
    return [name for _, name in vals[::TIME_STRIDE]]


def strip_integral_for_vtk(path: Path, edges: np.ndarray) -> np.ndarray:
    points, polygons, fields = read_vtk_polydata(path)
    q = fields["wallHeatFlux"]
    out = np.zeros(len(edges) - 1)
    for poly in polygons:
        idx = np.asarray(poly, dtype=int)
        verts = points[idx]
        x_centroid = float(verts[:, 0].mean())
        bin_idx = int(np.searchsorted(edges, x_centroid, side="right") - 1)
        if bin_idx < 0 or bin_idx >= len(out):
            continue
        area = polygon_area(verts)
        q_mean = float(q[idx].mean())
        out[bin_idx] += q_mean * area
    return out


def discover_x_range() -> tuple[float, float]:
    xs = []
    for case in CASES:
        t0, t1 = case["window"]
        for surf in ["hot_tube_surface", "hot_fin_surface"]:
            names = time_dirs(case["path"], surf, t0, t1)
            if not names:
                continue
            time = names[len(names) // 2]
            files = [case["path"] / "postProcessing" / tpl.format(time=time) for group in PATCH_FILES.values() for tpl in group]
            for f in files:
                if f.exists():
                    pts, _, _ = read_vtk_polydata(f)
                    xs.extend([float(pts[:, 0].min()), float(pts[:, 0].max())])
    xmin = np.floor(min(xs) / DX) * DX
    xmax = np.ceil(max(xs) / DX) * DX
    return float(xmin), float(xmax)


def summarize_case(case: dict, edges: np.ndarray) -> list[dict]:
    t0, t1 = case["window"]
    tube_acc = []
    fins_acc = []
    names = time_dirs(case["path"], "hot_tube_surface", t0, t1)
    for time in names:
        tube = np.zeros(len(edges) - 1)
        fins = np.zeros(len(edges) - 1)
        for tpl in PATCH_FILES["tube"]:
            f = case["path"] / "postProcessing" / tpl.format(time=time)
            if f.exists():
                tube += strip_integral_for_vtk(f, edges)
        for tpl in PATCH_FILES["fins"]:
            f = case["path"] / "postProcessing" / tpl.format(time=time)
            if f.exists():
                fins += strip_integral_for_vtk(f, edges)
        tube_acc.append(tube)
        fins_acc.append(fins)
    tube_mean = np.vstack(tube_acc).mean(axis=0)
    fins_mean = np.vstack(fins_acc).mean(axis=0)
    rows = []
    for i in range(len(edges) - 1):
        rows.append(
            {
                "Re": case["Re"],
                "case": case["case"],
                "regime": case["regime"],
                "x_left_mm": edges[i] * 1000,
                "x_right_mm": edges[i + 1] * 1000,
                "x_center_mm": 0.5 * (edges[i] + edges[i + 1]) * 1000,
                "Q_tube_strip_W": tube_mean[i],
                "Q_fins_strip_W": fins_mean[i],
                "Q_total_strip_W": tube_mean[i] + fins_mean[i],
                "n_times_used": len(names),
            }
        )
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def rows_to_grid(rows: list[dict], metric: str) -> tuple[list[float], np.ndarray, np.ndarray]:
    res = sorted({float(r["Re"]) for r in rows})
    xs = np.asarray(sorted({float(r["x_center_mm"]) for r in rows}), dtype=float)
    grid = np.full((len(res), len(xs)), np.nan)
    re_idx = {re: i for i, re in enumerate(res)}
    x_idx = {x: i for i, x in enumerate(xs)}
    for r in rows:
        grid[re_idx[float(r["Re"])], x_idx[float(r["x_center_mm"])]] = float(r[metric])
    return res, xs, grid


def add_tube_markers(ax) -> None:
    ax.axvline(-6, color="0.35", ls="--", lw=0.8)
    ax.axvline(6, color="0.35", ls="--", lw=0.8)


def save_metric_plot(
    xs: np.ndarray,
    series: dict[float | str, np.ndarray],
    ylabel: str,
    title: str,
    filename: str,
    zero_line: bool = True,
) -> None:
    fig, ax = plt.subplots(figsize=(10.4, 4.8))
    cmap = plt.get_cmap("magma")
    for i, (label, values) in enumerate(series.items()):
        color = cmap(i / max(1, len(series) - 1))
        ax.plot(xs, values, lw=2.0, color=color, label=f"Re {label}" if isinstance(label, float) else str(label))
    if zero_line:
        ax.axhline(0, color="0.2", lw=0.8)
    add_tube_markers(ax)
    ax.set_xlabel("x position from tube center [mm], 1 mm strips")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"{filename}.png", dpi=220)
    fig.savefig(OUT_DIR / f"{filename}.pdf")
    plt.close(fig)


def main() -> None:
    xmin, xmax = discover_x_range()
    edges = np.arange(xmin, xmax + 0.5 * DX, DX)
    rows: list[dict] = []
    for case in CASES:
        rows.extend(summarize_case(case, edges))
    write_csv(rows, OUT_DIR / "stripwise_1mm_heat_by_Re.csv")

    fig, axes = plt.subplots(3, 1, figsize=(10.6, 10.2), sharex=True)
    cmap = plt.get_cmap("viridis")
    res = sorted({r["Re"] for r in rows})
    colors = {re: cmap(i / max(1, len(res) - 1)) for i, re in enumerate(res)}
    metrics = [
        ("Q_total_strip_W", "Q_total per 1 mm strip [W]"),
        ("Q_tube_strip_W", "Q_tube per 1 mm strip [W]"),
        ("Q_fins_strip_W", "Q_fins per 1 mm strip [W]"),
    ]
    for ax, (metric, ylabel) in zip(axes, metrics):
        for re in res:
            sub = [r for r in rows if r["Re"] == re]
            x = [r["x_center_mm"] for r in sub]
            y = [r[metric] for r in sub]
            ax.plot(x, y, lw=1.9, color=colors[re], label=f"Re {re}")
        ax.axvline(-6, color="0.35", ls="--", lw=0.8)
        ax.axvline(6, color="0.35", ls="--", lw=0.8)
        ax.text(-5.8, ax.get_ylim()[1] * 0.88, "tube", fontsize=8, color="0.25")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.25)
    axes[0].legend(ncol=5, frameon=False, loc="upper right")
    axes[-1].set_xlabel("x position from tube center [mm], 1 mm strips")
    fig.suptitle("Stripwise heat transfer along hot tube and fins", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig04_stripwise_Q_profiles_by_Re.png", dpi=220)
    fig.savefig(OUT_DIR / "fig04_stripwise_Q_profiles_by_Re.pdf")
    plt.close(fig)

    pivot = {}
    for r in rows:
        if r["Re"] in (150, 200):
            pivot.setdefault((r["x_center_mm"], r["Re"]), r)
    diff_rows = []
    for r in [rr for rr in rows if rr["Re"] == 150]:
        r200 = pivot.get((r["x_center_mm"], 200))
        if not r200:
            continue
        diff_rows.append(
            {
                "x_center_mm": r["x_center_mm"],
                "dQ_total_Re200_minus_Re150_W": r200["Q_total_strip_W"] - r["Q_total_strip_W"],
                "dQ_tube_Re200_minus_Re150_W": r200["Q_tube_strip_W"] - r["Q_tube_strip_W"],
                "dQ_fins_Re200_minus_Re150_W": r200["Q_fins_strip_W"] - r["Q_fins_strip_W"],
            }
        )
    write_csv(diff_rows, OUT_DIR / "stripwise_1mm_delta_Re200_minus_Re150.csv")

    fig, ax = plt.subplots(figsize=(10.4, 4.8))
    x = [r["x_center_mm"] for r in diff_rows]
    ax.plot(x, [r["dQ_total_Re200_minus_Re150_W"] for r in diff_rows], color="#1f5f8b", lw=2.2, label="Delta Q_total")
    ax.plot(x, [r["dQ_tube_Re200_minus_Re150_W"] for r in diff_rows], color="#e07a5f", lw=1.8, label="Delta Q_tube")
    ax.plot(x, [r["dQ_fins_Re200_minus_Re150_W"] for r in diff_rows], color="#3d84a8", lw=1.8, label="Delta Q_fins")
    ax.axhline(0, color="0.2", lw=0.8)
    ax.axvline(-6, color="0.35", ls="--", lw=0.8)
    ax.axvline(6, color="0.35", ls="--", lw=0.8)
    ax.set_xlabel("x position from tube center [mm], 1 mm strips")
    ax.set_ylabel("Delta Q strip [W], Re200 - Re150")
    ax.set_title("Where shedding changes heat transfer locally")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig05_stripwise_delta_Re200_minus_Re150.png", dpi=220)
    fig.savefig(OUT_DIR / "fig05_stripwise_delta_Re200_minus_Re150.pdf")
    plt.close(fig)

    res, xs_grid, q_total = rows_to_grid(rows, "Q_total_strip_W")
    _, _, q_tube = rows_to_grid(rows, "Q_tube_strip_W")
    _, _, q_fins = rows_to_grid(rows, "Q_fins_strip_W")
    re_idx = {re: i for i, re in enumerate(res)}
    q_parts = {
        "total": q_total,
        "tube": q_tube,
        "fins": q_fins,
    }

    q_global = {re: float(np.nansum(q_total[re_idx[re], :])) for re in res}
    i100 = re_idx[100.0]
    i150 = re_idx[150.0]
    derived_rows = []
    for re in res:
        i_re = re_idx[re]
        global_gain = q_global[re] / q_global[150.0]
        for j, x_mm in enumerate(xs_grid):
            q150 = q_total[i150, j]
            q100 = q_total[i100, j]
            q_actual = q_total[i_re, j]
            local_gain = q_actual / q150 if abs(q150) > 1e-14 else np.nan
            expected_steady = q100 + (q150 - q100) * ((re - 100.0) / 50.0)
            local_share = q_actual / q_global[re] if abs(q_global[re]) > 1e-14 else np.nan
            share_150 = q150 / q_global[150.0] if abs(q_global[150.0]) > 1e-14 else np.nan
            derived_rows.append(
                {
                    "Re": re,
                    "x_center_mm": x_mm,
                    "Q_total_strip_W": q_actual,
                    "Q_global_total_W": q_global[re],
                    "global_gain_vs_Re150": global_gain,
                    "local_gain_vs_Re150": local_gain,
                    "local_excess_over_global_gain": (local_gain / global_gain - 1.0) if abs(global_gain) > 1e-14 else np.nan,
                    "Q_expected_from_Re100_Re150_linear_W": expected_steady,
                    "Q_excess_over_steady_linear_W": q_actual - expected_steady,
                    "local_share_of_global_Q": local_share,
                    "local_share_delta_vs_Re150": local_share - share_150,
                }
            )
    write_csv(derived_rows, OUT_DIR / "stripwise_1mm_derived_metrics.csv")

    selected_res = [re for re in (160.0, 175.0, 200.0) if re in re_idx]
    save_metric_plot(
        xs_grid,
        {re: np.asarray([r["local_excess_over_global_gain"] for r in derived_rows if r["Re"] == re]) for re in selected_res},
        "local gain / global gain - 1 [-]",
        "Local heat-transfer amplification after removing global Re scaling",
        "fig06_local_excess_over_global_gain",
    )
    save_metric_plot(
        xs_grid,
        {re: np.asarray([r["Q_excess_over_steady_linear_W"] for r in derived_rows if r["Re"] == re]) for re in selected_res},
        "Q_actual - Q_linear(100,150) per strip [W]",
        "Local heat-transfer excess over steady Re100-Re150 trend",
        "fig07_Q_excess_over_steady_model",
    )
    save_metric_plot(
        xs_grid,
        {re: np.asarray([r["local_share_delta_vs_Re150"] for r in derived_rows if r["Re"] == re]) for re in selected_res},
        "delta local share of global Q vs Re150 [-]",
        "Where heat transfer is redistributed relative to Re150",
        "fig08_local_share_delta_vs_Re150",
    )

    intervals = [
        (100.0, 150.0, "steady 100-150"),
        (150.0, 160.0, "onset 150-160"),
        (160.0, 200.0, "post-onset 160-200"),
    ]
    slope_rows = []
    fig, axes = plt.subplots(3, 1, figsize=(10.6, 10.0), sharex=True)
    part_colors = {"total": "#1f5f8b", "tube": "#e07a5f", "fins": "#3d84a8"}
    for ax, (re_a, re_b, label) in zip(axes, intervals):
        if re_a not in re_idx or re_b not in re_idx:
            continue
        for part, grid in q_parts.items():
            slope = (grid[re_idx[re_b], :] - grid[re_idx[re_a], :]) / (re_b - re_a)
            ax.plot(xs_grid, slope, lw=1.9, color=part_colors[part], label=f"dQ_{part}/dRe")
            for x_mm, value in zip(xs_grid, slope):
                slope_rows.append(
                    {
                        "interval": label,
                        "Re_from": re_a,
                        "Re_to": re_b,
                        "x_center_mm": x_mm,
                        f"dQ_{part}_dRe_W_per_Re": value,
                    }
                )
        ax.axhline(0, color="0.2", lw=0.8)
        add_tube_markers(ax)
        ax.set_ylabel("dQ/dRe [W/Re]")
        ax.set_title(label)
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False, ncol=3, loc="upper right")
    axes[-1].set_xlabel("x position from tube center [mm], 1 mm strips")
    fig.suptitle("Local heat-transfer sensitivity by Reynolds-number interval", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig09_local_dQdRe_by_interval.png", dpi=220)
    fig.savefig(OUT_DIR / "fig09_local_dQdRe_by_interval.pdf")
    plt.close(fig)

    # Make one compact CSV row per x/interval with all three components.
    compact_slope_rows = []
    for re_a, re_b, label in intervals:
        if re_a not in re_idx or re_b not in re_idx:
            continue
        slopes = {
            part: (grid[re_idx[re_b], :] - grid[re_idx[re_a], :]) / (re_b - re_a)
            for part, grid in q_parts.items()
        }
        for j, x_mm in enumerate(xs_grid):
            compact_slope_rows.append(
                {
                    "interval": label,
                    "Re_from": re_a,
                    "Re_to": re_b,
                    "x_center_mm": x_mm,
                    "dQ_total_dRe_W_per_Re": slopes["total"][j],
                    "dQ_tube_dRe_W_per_Re": slopes["tube"][j],
                    "dQ_fins_dRe_W_per_Re": slopes["fins"][j],
                }
            )
    write_csv(compact_slope_rows, OUT_DIR / "stripwise_1mm_local_slopes.csv")

    readme = OUT_DIR / "README.md"
    readme.write_text(
        """# 002_Nu_and_vorticity

Presentation figures relating heat transfer to vortex presence/intensity.

## Figure 1

`fig01_Qwall_vs_ClRMS.png`

- x-axis: late-window `Cl_rms`, used as a global vortex-shedding intensity metric.
- y-axis: integrated wall heat transfer `Q_wall = Q_tube + Q_fins` from `wallHeatFlux`.
- points: completed production-geometry cases Re=100, 150, 160, 175, 200.
- Re=155 is excluded until the run is fully post-processed.

## Figure 2

`fig02_heat_partition_steady_vs_shedding.png`

- stacked bars: heat-transfer partition between tube and fins.
- black line: `Cl_rms`, showing vortex intensity on the same cases.
- comparison highlights transition from steady/pre-Hopf cases to shedding/post-Hopf cases.

## Figure 3

`fig03_Q_components_and_ClRMS_vs_Re.png`

- left panel: `Q_total`, `Q_tube`, and `Q_fins` as functions of Reynolds number.
- right panel: `Cl_rms` as a compact vortex-intensity/onset indicator.
- shaded band: current onset bracket between steady Re=150 and shedding Re=160.

## Figure 4

`fig04_stripwise_Q_profiles_by_Re.png`

- integrates `wallHeatFlux` directly on hot tube and fin VTK surfaces.
- strips are 1 mm wide in streamwise `x`, using polygon centroid assignment.
- each curve is averaged over the late-time analysis window for that Re.

## Figure 5

`fig05_stripwise_delta_Re200_minus_Re150.png`

- local stripwise difference between production shedding Re=200 and steady Re=150.
- highlights where the globally smooth Q(Re) trend has local spatial structure.

## Figures 6-9

`fig06_local_excess_over_global_gain.png`

- compares local strip gain against global gain, so it suppresses the trivial effect that larger Re gives larger total Q.

`fig07_Q_excess_over_steady_model.png`

- subtracts a local linear extrapolation based on steady Re=100 and Re=150.

`fig08_local_share_delta_vs_Re150.png`

- shows whether each strip takes a larger or smaller share of total heat transfer than in the Re=150 baseline.

`fig09_local_dQdRe_by_interval.png`

- estimates local sensitivity over Re intervals 100-150, 150-160, and 160-200.

## Important note

Figures use `Q_wall` directly from integrated `wallHeatFlux`. This is good for mechanism
and presentation-level interpretation, but publication-grade comparison should also use
the final accepted `Nu`/thermal normalization workflow for each Re.
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
