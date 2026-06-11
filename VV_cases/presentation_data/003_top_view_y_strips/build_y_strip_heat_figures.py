from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


REPO_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9")
SOURCE_DIR = REPO_DIR / "VV_cases/presentation_data/002_Nu_and_vorticity"
OUT_DIR = REPO_DIR / "VV_cases/presentation_data/003_top_view_y_strips"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SOURCE_DIR))
from build_stripwise_heat_figures import CASES, DX, PATCH_FILES, polygon_area, read_vtk_polydata, time_dirs  # noqa: E402


AXIS_INDEX = 1
AXIS_NAME = "y"
AXIS_LABEL = "y position from tube center [mm], 1 mm top-view strips"


def discover_axis_range() -> tuple[float, float]:
    coords = []
    for case in CASES:
        t0, t1 = case["window"]
        for surf in ["hot_tube_surface", "hot_fin_surface"]:
            names = time_dirs(case["path"], surf, t0, t1)
            if not names:
                continue
            time = names[len(names) // 2]
            files = [
                case["path"] / "postProcessing" / tpl.format(time=time)
                for group in PATCH_FILES.values()
                for tpl in group
            ]
            for f in files:
                if f.exists():
                    pts, _, _ = read_vtk_polydata(f)
                    coords.extend([float(pts[:, AXIS_INDEX].min()), float(pts[:, AXIS_INDEX].max())])
    cmin = np.floor(min(coords) / DX) * DX
    cmax = np.ceil(max(coords) / DX) * DX
    return float(cmin), float(cmax)


def strip_integral_for_vtk(path: Path, edges: np.ndarray) -> np.ndarray:
    points, polygons, fields = read_vtk_polydata(path)
    q = fields["wallHeatFlux"]
    out = np.zeros(len(edges) - 1)
    for poly in polygons:
        idx = np.asarray(poly, dtype=int)
        verts = points[idx]
        centroid_coord = float(verts[:, AXIS_INDEX].mean())
        bin_idx = int(np.searchsorted(edges, centroid_coord, side="right") - 1)
        if bin_idx < 0 or bin_idx >= len(out):
            continue
        out[bin_idx] += float(q[idx].mean()) * polygon_area(verts)
    return out


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
        center = 0.5 * (edges[i] + edges[i + 1]) * 1000
        rows.append(
            {
                "Re": case["Re"],
                "case": case["case"],
                "regime": case["regime"],
                f"{AXIS_NAME}_left_mm": edges[i] * 1000,
                f"{AXIS_NAME}_right_mm": edges[i + 1] * 1000,
                f"{AXIS_NAME}_center_mm": center,
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
    coords = np.asarray(sorted({float(r[f"{AXIS_NAME}_center_mm"]) for r in rows}), dtype=float)
    grid = np.full((len(res), len(coords)), np.nan)
    re_idx = {re: i for i, re in enumerate(res)}
    coord_idx = {coord: i for i, coord in enumerate(coords)}
    for r in rows:
        grid[re_idx[float(r["Re"])], coord_idx[float(r[f"{AXIS_NAME}_center_mm"])]] = float(r[metric])
    return res, coords, grid


def add_tube_markers(ax) -> None:
    ax.axvline(-6, color="0.35", ls="--", lw=0.8)
    ax.axvline(0, color="0.45", ls=":", lw=0.8)
    ax.axvline(6, color="0.35", ls="--", lw=0.8)


def save_metric_plot(
    coords: np.ndarray,
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
        legend = f"Re {label:g}" if isinstance(label, float) else str(label)
        ax.plot(coords, values, lw=2.0, color=color, label=legend)
    if zero_line:
        ax.axhline(0, color="0.2", lw=0.8)
    add_tube_markers(ax)
    ax.set_xlabel(AXIS_LABEL)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"{filename}.png", dpi=220)
    fig.savefig(OUT_DIR / f"{filename}.pdf")
    plt.close(fig)


def build_derived_rows(rows: list[dict]) -> tuple[list[dict], list[dict], list[float], np.ndarray, dict[str, np.ndarray]]:
    res, coords, q_total = rows_to_grid(rows, "Q_total_strip_W")
    _, _, q_tube = rows_to_grid(rows, "Q_tube_strip_W")
    _, _, q_fins = rows_to_grid(rows, "Q_fins_strip_W")
    re_idx = {re: i for i, re in enumerate(res)}
    q_parts = {"total": q_total, "tube": q_tube, "fins": q_fins}
    q_global = {re: float(np.nansum(q_total[re_idx[re], :])) for re in res}

    i100 = re_idx[100.0]
    i150 = re_idx[150.0]
    derived_rows = []
    for re in res:
        i_re = re_idx[re]
        global_gain = q_global[re] / q_global[150.0]
        for j, coord_mm in enumerate(coords):
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
                    f"{AXIS_NAME}_center_mm": coord_mm,
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

    intervals = [
        (100.0, 150.0, "steady 100-150"),
        (150.0, 160.0, "onset 150-160"),
        (160.0, 200.0, "post-onset 160-200"),
    ]
    slope_rows = []
    for re_a, re_b, label in intervals:
        if re_a not in re_idx or re_b not in re_idx:
            continue
        slopes = {
            part: (grid[re_idx[re_b], :] - grid[re_idx[re_a], :]) / (re_b - re_a)
            for part, grid in q_parts.items()
        }
        for j, coord_mm in enumerate(coords):
            slope_rows.append(
                {
                    "interval": label,
                    "Re_from": re_a,
                    "Re_to": re_b,
                    f"{AXIS_NAME}_center_mm": coord_mm,
                    "dQ_total_dRe_W_per_Re": slopes["total"][j],
                    "dQ_tube_dRe_W_per_Re": slopes["tube"][j],
                    "dQ_fins_dRe_W_per_Re": slopes["fins"][j],
                }
            )
    return derived_rows, slope_rows, res, coords, q_parts


def main() -> None:
    cmin, cmax = discover_axis_range()
    edges = np.arange(cmin, cmax + 0.5 * DX, DX)
    rows: list[dict] = []
    for case in CASES:
        rows.extend(summarize_case(case, edges))
    write_csv(rows, OUT_DIR / "y_strip_1mm_heat_by_Re.csv")

    fig, axes = plt.subplots(3, 1, figsize=(10.6, 10.2), sharex=True)
    cmap = plt.get_cmap("viridis")
    res = sorted({r["Re"] for r in rows})
    colors = {re: cmap(i / max(1, len(res) - 1)) for i, re in enumerate(res)}
    metrics = [
        ("Q_total_strip_W", "Q_total per 1 mm y-strip [W]"),
        ("Q_tube_strip_W", "Q_tube per 1 mm y-strip [W]"),
        ("Q_fins_strip_W", "Q_fins per 1 mm y-strip [W]"),
    ]
    for ax, (metric, ylabel) in zip(axes, metrics):
        for re in res:
            sub = [r for r in rows if r["Re"] == re]
            coord = [r[f"{AXIS_NAME}_center_mm"] for r in sub]
            val = [r[metric] for r in sub]
            ax.plot(coord, val, lw=1.9, color=colors[re], label=f"Re {re}")
        add_tube_markers(ax)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.25)
    axes[0].legend(ncol=5, frameon=False, loc="upper right")
    axes[-1].set_xlabel(AXIS_LABEL)
    fig.suptitle("Top-view y-strip heat transfer across hot tube and fins", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig01_y_strip_Q_profiles_by_Re.png", dpi=220)
    fig.savefig(OUT_DIR / "fig01_y_strip_Q_profiles_by_Re.pdf")
    plt.close(fig)

    derived_rows, slope_rows, res_float, coords, q_parts = build_derived_rows(rows)
    write_csv(derived_rows, OUT_DIR / "y_strip_1mm_derived_metrics.csv")
    write_csv(slope_rows, OUT_DIR / "y_strip_1mm_local_slopes.csv")

    re_idx = {re: i for i, re in enumerate(res_float)}
    selected_res = [re for re in (160.0, 175.0, 200.0) if re in re_idx]
    save_metric_plot(
        coords,
        {re: np.asarray([r["local_excess_over_global_gain"] for r in derived_rows if r["Re"] == re]) for re in selected_res},
        "local gain / global gain - 1 [-]",
        "Top-view local amplification after removing global Re scaling",
        "fig02_y_local_excess_over_global_gain",
    )
    save_metric_plot(
        coords,
        {re: np.asarray([r["Q_excess_over_steady_linear_W"] for r in derived_rows if r["Re"] == re]) for re in selected_res},
        "Q_actual - Q_linear(100,150) per y-strip [W]",
        "Top-view heat-transfer excess over steady Re100-Re150 trend",
        "fig03_y_Q_excess_over_steady_model",
    )
    save_metric_plot(
        coords,
        {re: np.asarray([r["local_share_delta_vs_Re150"] for r in derived_rows if r["Re"] == re]) for re in selected_res},
        "delta local share of global Q vs Re150 [-]",
        "Top-view redistribution of heat-transfer share relative to Re150",
        "fig04_y_local_share_delta_vs_Re150",
    )

    intervals = [
        (100.0, 150.0, "steady 100-150"),
        (150.0, 160.0, "onset 150-160"),
        (160.0, 200.0, "post-onset 160-200"),
    ]
    fig, axes = plt.subplots(3, 1, figsize=(10.6, 10.0), sharex=True)
    part_colors = {"total": "#1f5f8b", "tube": "#e07a5f", "fins": "#3d84a8"}
    for ax, (re_a, re_b, label) in zip(axes, intervals):
        if re_a not in re_idx or re_b not in re_idx:
            continue
        for part, grid in q_parts.items():
            slope = (grid[re_idx[re_b], :] - grid[re_idx[re_a], :]) / (re_b - re_a)
            ax.plot(coords, slope, lw=1.9, color=part_colors[part], label=f"dQ_{part}/dRe")
        ax.axhline(0, color="0.2", lw=0.8)
        add_tube_markers(ax)
        ax.set_ylabel("dQ/dRe [W/Re]")
        ax.set_title(label)
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False, ncol=3, loc="upper right")
    axes[-1].set_xlabel(AXIS_LABEL)
    fig.suptitle("Top-view local heat-transfer sensitivity by Reynolds-number interval", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig05_y_local_dQdRe_by_interval.png", dpi=220)
    fig.savefig(OUT_DIR / "fig05_y_local_dQdRe_by_interval.pdf")
    plt.close(fig)

    (OUT_DIR / "README.md").write_text(
        """# 003_top_view_y_strips

Top-view 1 mm strip analysis of integrated wall heat transfer.

The method is the same as in `002_Nu_and_vorticity`, but each surface polygon is
assigned to a strip by its centroid `y` coordinate instead of `x`. This asks a
different question: how heat transfer is distributed across the channel/tube width
in the top-view direction.

## Figures

`fig01_y_strip_Q_profiles_by_Re.png`

- absolute `Q_total`, `Q_tube`, and `Q_fins` per 1 mm y-strip.

`fig02_y_local_excess_over_global_gain.png`

- local y-strip gain divided by global gain, minus 1. Values above 0 mean that the
  strip grows faster than the whole exchanger after removing global Re scaling.

`fig03_y_Q_excess_over_steady_model.png`

- difference from a local linear steady trend fitted between Re=100 and Re=150.

`fig04_y_local_share_delta_vs_Re150.png`

- redistribution of each y-strip's share of total heat transfer relative to Re=150.

`fig05_y_local_dQdRe_by_interval.png`

- local heat-transfer sensitivity over Re intervals 100-150, 150-160, and 160-200.

Dashed vertical lines mark approximate tube radius bounds at y = +/-6 mm; the dotted
line marks the tube centerline.
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
