from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


REPO_DIR = Path("/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9")
SRC004 = REPO_DIR / "VV_cases/presentation_data/004_x_strip_Nu_vorticity"
OUT_DIR = REPO_DIR / "VV_cases/presentation_data/005_x_strip_robustness_analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SRC004))
from build_x_strip_nu_vorticity import CASES, DX, D_REF, K_AIR, T_WALL, discover_x_range, summarize_case  # noqa: E402


PRIMARY_DX_MM = 1.0
SENSITIVITY_DX_MM = [1.0, 0.5, 0.1]
SELECTED_RE = [160.0, 175.0, 200.0]
BASELINE_RE = 150.0
STEADY_RE = [100.0, 150.0]
LAGS_MM = list(range(-6, 7))

VORTEX_METRICS = [
    ("near_wall_Qcriterion_2D_positive_nd", "near-wall Qcrit"),
    ("near_wall_lambda_ci_2D_nd", "near-wall lambda_ci"),
    ("bulk_without_tube_near_wall_Qcriterion_2D_positive_nd", "bulk-no-wall Qcrit"),
    ("bulk_without_tube_near_wall_lambda_ci_2D_nd", "bulk-no-wall lambda_ci"),
    ("wake_Qcriterion_2D_positive_nd", "wake Qcrit"),
    ("wake_lambda_ci_2D_nd", "wake lambda_ci"),
]


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(value) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out


def fmt(value: float, digits: int = 7) -> str:
    if value != value:
        return "nan"
    return f"{value:.{digits}g}"


def compute_rows_for_dx(dx_mm: float) -> list[dict]:
    xmin, xmax = discover_x_range()
    edges = np.arange(xmin, xmax + 0.5 * dx_mm / 1000.0, dx_mm / 1000.0)
    rows: list[dict] = []
    for case in CASES:
        rows.extend(summarize_case(case, edges))
    for row in rows:
        row["dx_mm"] = dx_mm
    return rows


def save_rows_for_widths() -> dict[float, list[dict]]:
    width_rows: dict[float, list[dict]] = {}
    for dx_mm in SENSITIVITY_DX_MM:
        path = OUT_DIR / f"x_strip_raw_dx{dx_mm:g}mm.csv"
        if path.exists():
            rows = read_csv(path)
        else:
            rows = compute_rows_for_dx(dx_mm)
            write_csv(rows, path)
        width_rows[dx_mm] = rows
    return width_rows


def by_re_x(rows: list[dict], value_key: str) -> tuple[list[float], np.ndarray, np.ndarray]:
    res = sorted({float(r["Re"]) for r in rows})
    xs = np.asarray(sorted({float(r["x_center_mm"]) for r in rows}), dtype=float)
    grid = np.full((len(res), len(xs)), np.nan)
    re_idx = {re: i for i, re in enumerate(res)}
    x_idx = {x: i for i, x in enumerate(xs)}
    for row in rows:
        grid[re_idx[float(row["Re"])], x_idx[float(row["x_center_mm"])]] = fnum(row[value_key])
    return res, xs, grid


def add_tube_markers(ax) -> None:
    ax.axvline(-6, color="0.35", ls="--", lw=0.8)
    ax.axvline(6, color="0.35", ls="--", lw=0.8)


def lmtd(delta_in: np.ndarray, delta_out: np.ndarray) -> np.ndarray:
    delta_in = np.maximum(delta_in, 1.0e-9)
    delta_out = np.maximum(delta_out, 1.0e-9)
    out = np.empty_like(delta_in, dtype=float)
    same = np.abs(delta_in - delta_out) < 1.0e-8
    out[same] = 0.5 * (delta_in[same] + delta_out[same])
    ratio = delta_in[~same] / delta_out[~same]
    out[~same] = (delta_in[~same] - delta_out[~same]) / np.log(ratio)
    return out


def enrich_rows(rows: list[dict]) -> list[dict]:
    res, xs, nu = by_re_x(rows, "Nu_strip_proxy")
    _, _, q_total = by_re_x(rows, "Q_total_strip_W")
    _, _, q_tube = by_re_x(rows, "Q_tube_strip_W")
    _, _, q_fins = by_re_x(rows, "Q_fins_strip_W")
    _, _, a_tube = by_re_x(rows, "A_tube_strip_m2")
    _, _, a_fins = by_re_x(rows, "A_fins_strip_m2")
    _, _, dt_lm = by_re_x(rows, "deltaT_lm_proxy_K")
    _, _, t_in = by_re_x(rows, "T_bulk_in_proxy_K")
    _, _, t_out = by_re_x(rows, "T_bulk_out_proxy_K")
    re_idx = {re: i for i, re in enumerate(res)}

    dt_tin = T_WALL - t_in
    dt_const = np.full_like(dt_lm, 50.0)
    nu_tube = np.divide(q_tube * D_REF, a_tube * dt_lm * K_AIR, out=np.full_like(q_tube, np.nan), where=a_tube > 0)
    nu_fins = np.divide(q_fins * D_REF, a_fins * dt_lm * K_AIR, out=np.full_like(q_fins, np.nan), where=a_fins > 0)
    nu_tin = np.divide(q_total * D_REF, (a_tube + a_fins) * dt_tin * K_AIR, out=np.full_like(q_total, np.nan), where=(a_tube + a_fins) > 0)
    nu_const_dt = np.divide(q_total * D_REF, (a_tube + a_fins) * dt_const * K_AIR, out=np.full_like(q_total, np.nan), where=(a_tube + a_fins) > 0)

    q_total_global = {re: float(np.nansum(q_total[re_idx[re], :])) for re in res}
    nu_mean = {re: float(np.nanmean(nu[re_idx[re], :])) for re in res}
    i_base = re_idx[BASELINE_RE]
    enriched = []
    for row in rows:
        re = float(row["Re"])
        x = float(row["x_center_mm"])
        i = re_idx[re]
        j = int(np.where(np.isclose(xs, x))[0][0])
        local_gain = nu[i, j] / nu[i_base, j]
        mean_gain = nu_mean[re] / nu_mean[BASELINE_RE]
        out = dict(row)
        out["relative_local_sensitivity_vs_Re150"] = local_gain / mean_gain - 1.0
        out["Delta_Nu_vs_Re150"] = nu[i, j] - nu[i_base, j]
        out["Delta_Q_vs_Re150_W"] = q_total[i, j] - q_total[i_base, j]
        out["Delta_Q_tube_vs_Re150_W"] = q_tube[i, j] - q_tube[i_base, j]
        out["Delta_Q_fins_vs_Re150_W"] = q_fins[i, j] - q_fins[i_base, j]
        out["Q_strip_share_of_total"] = q_total[i, j] / q_total_global[re]
        out["Q_tube_share_of_total"] = q_tube[i, j] / q_total_global[re]
        out["Q_fins_share_of_total"] = q_fins[i, j] / q_total_global[re]
        out["Nu_tube_strip_proxy"] = nu_tube[i, j]
        out["Nu_fins_strip_proxy"] = nu_fins[i, j]
        out["Nu_Tin_reference_proxy"] = nu_tin[i, j]
        out["Nu_constant_deltaT50_proxy"] = nu_const_dt[i, j]
        enriched.append(out)
    return enriched


def plot_stage1_profiles(rows: list[dict]) -> None:
    res, xs, rel = by_re_x(rows, "relative_local_sensitivity_vs_Re150")
    _, _, dnu = by_re_x(rows, "Delta_Nu_vs_Re150")
    _, _, dq = by_re_x(rows, "Delta_Q_vs_Re150_W")
    _, _, share = by_re_x(rows, "Q_strip_share_of_total")
    re_idx = {re: i for i, re in enumerate(res)}

    def plot_metric(grid, ylabel, title, filename, zero=True):
        fig, ax = plt.subplots(figsize=(10.4, 4.8))
        cmap = plt.get_cmap("magma")
        selected = [re for re in SELECTED_RE if re in re_idx]
        for k, re in enumerate(selected):
            ax.plot(xs, grid[re_idx[re], :], lw=2.0, color=cmap(k / max(1, len(selected) - 1)), label=f"Re {re:g}")
        if zero:
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

    plot_metric(rel, "relative local sensitivity vs Re150 [-]", "Local sensitivity relative to mean Nu gain, not direct enhancement", "fig01_relative_local_sensitivity_vs_Re150")
    plot_metric(dnu, "Delta Nu vs Re150 [-]", "Absolute local Nusselt change relative to Re150", "fig02_delta_Nu_vs_Re150")
    plot_metric(dq, "Delta Q vs Re150 [W]", "Absolute local heat-transfer change relative to Re150", "fig03_delta_Q_vs_Re150")
    plot_metric(share, "Q_strip / Q_total [-]", "Energetic importance of each x-strip", "fig04_Q_strip_share_of_total", zero=False)


def plot_tube_fins(rows: list[dict]) -> None:
    res, xs, nu_tube = by_re_x(rows, "Nu_tube_strip_proxy")
    _, _, nu_fins = by_re_x(rows, "Nu_fins_strip_proxy")
    _, _, q_tube = by_re_x(rows, "Q_tube_strip_W")
    _, _, q_fins = by_re_x(rows, "Q_fins_strip_W")
    re_idx = {re: i for i, re in enumerate(res)}
    selected = [re for re in SELECTED_RE if re in re_idx]
    cmap = plt.get_cmap("viridis")
    fig, axes = plt.subplots(2, 2, figsize=(12.0, 8.5), sharex=True)
    configs = [
        (axes[0, 0], nu_tube, "Nu_tube_strip_proxy [-]", "Tube-only strip Nu proxy"),
        (axes[0, 1], nu_fins, "Nu_fins_strip_proxy [-]", "Fins-only strip Nu proxy"),
        (axes[1, 0], q_tube, "Q_tube_strip [W]", "Tube-only heat transfer"),
        (axes[1, 1], q_fins, "Q_fins_strip [W]", "Fins-only heat transfer"),
    ]
    for ax, grid, ylabel, title in configs:
        for k, re in enumerate(selected):
            ax.plot(xs, grid[re_idx[re], :], lw=1.9, color=cmap(k / max(1, len(selected) - 1)), label=f"Re {re:g}")
        add_tube_markers(ax)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
    axes[0, 1].legend(frameon=False)
    axes[1, 0].set_xlabel("x position from tube center [mm]")
    axes[1, 1].set_xlabel("x position from tube center [mm]")
    fig.suptitle("Tube and fins separated: avoiding mixed-boundary strip interpretation", y=0.995)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig05_tube_fins_separated_profiles.png", dpi=220)
    fig.savefig(OUT_DIR / "fig05_tube_fins_separated_profiles.pdf")
    plt.close(fig)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    valid = np.isfinite(a) & np.isfinite(b)
    if valid.sum() < 3:
        return float("nan")
    if np.nanstd(a[valid]) < 1.0e-14 or np.nanstd(b[valid]) < 1.0e-14:
        return float("nan")
    return float(np.corrcoef(a[valid], b[valid])[0, 1])


def lagged_corr(metric: np.ndarray, target: np.ndarray, lags_bins: list[int], mask: np.ndarray) -> list[float]:
    out = []
    for lag in lags_bins:
        if lag < 0:
            m = metric[-lag:]
            t = target[: lag if lag != 0 else None]
            mk = mask[-lag:] & mask[: lag if lag != 0 else None]
        elif lag > 0:
            m = metric[:-lag]
            t = target[lag:]
            mk = mask[:-lag] & mask[lag:]
        else:
            m = metric
            t = target
            mk = mask
        out.append(corr(m[mk], t[mk]))
    return out


def stage2_lag_analysis(rows: list[dict], dx_mm: float = PRIMARY_DX_MM) -> list[dict]:
    res, xs, target = by_re_x(rows, "relative_local_sensitivity_vs_Re150")
    re_idx = {re: i for i, re in enumerate(res)}
    lag_bins = [int(round(lag / dx_mm)) for lag in LAGS_MM]
    masks = {
        "full": np.ones_like(xs, dtype=bool),
        "without_x_pm5p5": (~np.isclose(xs, -5.5, atol=0.51 * dx_mm)) & (~np.isclose(xs, 5.5, atol=0.51 * dx_mm)),
        "without_tube_zone": (xs < -6.0) | (xs > 6.0),
    }
    rows_out = []
    for metric_key, metric_label in VORTEX_METRICS:
        _, _, metric_grid = by_re_x(rows, metric_key)
        for re in [r for r in SELECTED_RE if r in re_idx]:
            for mask_name, mask in masks.items():
                vals = lagged_corr(metric_grid[re_idx[re], :], target[re_idx[re], :], lag_bins, mask)
                for lag_mm, value in zip(LAGS_MM, vals):
                    rows_out.append(
                        {
                            "Re": re,
                            "metric": metric_key,
                            "metric_label": metric_label,
                            "mask": mask_name,
                            "lag_mm": lag_mm,
                            "corr": value,
                        }
                    )
    write_csv(rows_out, OUT_DIR / "stage2_spatial_lag_correlations.csv")
    plot_lag_panels(rows_out)
    return rows_out


def plot_lag_panels(lag_rows: list[dict]) -> None:
    selected_metrics = [
        "near_wall_Qcriterion_2D_positive_nd",
        "bulk_without_tube_near_wall_Qcriterion_2D_positive_nd",
        "wake_Qcriterion_2D_positive_nd",
    ]
    for mask in ["full", "without_x_pm5p5", "without_tube_zone"]:
        fig, axes = plt.subplots(3, 1, figsize=(10.4, 9.0), sharex=True)
        for ax, metric in zip(axes, selected_metrics):
            sub_metric = [r for r in lag_rows if r["metric"] == metric and r["mask"] == mask]
            for re in SELECTED_RE:
                sub = [r for r in sub_metric if float(r["Re"]) == re]
                if not sub:
                    continue
                x = [float(r["lag_mm"]) for r in sub]
                y = [fnum(r["corr"]) for r in sub]
                ax.plot(x, y, marker="o", lw=1.7, label=f"Re {re:g}")
            ax.axhline(0, color="0.2", lw=0.8)
            ax.axvline(0, color="0.35", ls="--", lw=0.8)
            ax.set_ylabel("corr")
            ax.set_title(metric.replace("_", " "))
            ax.grid(True, alpha=0.25)
            ax.legend(frameon=False, ncol=3)
        axes[-1].set_xlabel("spatial lag: corr[M(x), sensitivity(x+lag)] [mm]")
        fig.suptitle(f"Spatial-offset correlation, mask={mask}", y=0.995)
        fig.tight_layout()
        fig.savefig(OUT_DIR / f"fig06_spatial_lag_correlation_{mask}.png", dpi=220)
        fig.savefig(OUT_DIR / f"fig06_spatial_lag_correlation_{mask}.pdf")
        plt.close(fig)


def best_lag_table(lag_rows: list[dict]) -> list[dict]:
    out = []
    keys = sorted({(r["Re"], r["metric"], r["mask"]) for r in lag_rows}, key=lambda x: (float(x[0]), x[1], x[2]))
    for re, metric, mask in keys:
        sub = [r for r in lag_rows if r["Re"] == re and r["metric"] == metric and r["mask"] == mask]
        vals = [(float(r["lag_mm"]), fnum(r["corr"])) for r in sub if fnum(r["corr"]) == fnum(r["corr"])]
        if not vals:
            continue
        lag, value = max(vals, key=lambda p: abs(p[1]))
        out.append({"Re": re, "metric": metric, "mask": mask, "best_abs_corr_lag_mm": lag, "best_abs_corr": value})
    write_csv(out, OUT_DIR / "stage2_best_spatial_lags.csv")
    return out


def stage3_width_sensitivity(enriched_by_width: dict[float, list[dict]]) -> list[dict]:
    out = []
    for dx_mm, rows in enriched_by_width.items():
        lag_rows = stage2_lag_analysis(rows, dx_mm=dx_mm)
        best = best_lag_table(lag_rows)
        res, xs, rel = by_re_x(rows, "relative_local_sensitivity_vs_Re150")
        re_idx = {re: i for i, re in enumerate(res)}
        for re in [r for r in SELECTED_RE if r in re_idx]:
            y = rel[re_idx[re], :]
            j = int(np.nanargmax(y))
            out.append(
                {
                    "dx_mm": dx_mm,
                    "Re": re,
                    "peak_relative_sensitivity_x_mm": xs[j],
                    "peak_relative_sensitivity": y[j],
                }
            )
        for row in best:
            if row["metric"] in (
                "bulk_without_tube_near_wall_Qcriterion_2D_positive_nd",
                "near_wall_Qcriterion_2D_positive_nd",
                "wake_Qcriterion_2D_positive_nd",
            ) and row["mask"] == "full":
                out.append({"dx_mm": dx_mm, **row})
    write_csv(out, OUT_DIR / "stage3_strip_width_sensitivity.csv")
    plot_width_sensitivity(out)
    return out


def plot_width_sensitivity(rows: list[dict]) -> None:
    peak_rows = [r for r in rows if "peak_relative_sensitivity_x_mm" in r]
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    for re in SELECTED_RE:
        sub = [r for r in peak_rows if float(r["Re"]) == re]
        ax.plot([fnum(r["dx_mm"]) for r in sub], [fnum(r["peak_relative_sensitivity_x_mm"]) for r in sub], marker="o", label=f"Re {re:g}")
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.axhline(5.5, color="0.35", ls="--", lw=0.8)
    ax.set_xlabel("strip width dx [mm]")
    ax.set_ylabel("x of peak relative sensitivity [mm]")
    ax.set_title("Strip-width sensitivity of the apparent hotspot location")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig07_strip_width_hotspot_sensitivity.png", dpi=220)
    fig.savefig(OUT_DIR / "fig07_strip_width_hotspot_sensitivity.pdf")
    plt.close(fig)


def stage4_delta_t_variants(rows: list[dict]) -> None:
    res, xs, nu_lmtd = by_re_x(rows, "Nu_strip_proxy")
    _, _, nu_tin = by_re_x(rows, "Nu_Tin_reference_proxy")
    _, _, nu_const = by_re_x(rows, "Nu_constant_deltaT50_proxy")
    re_idx = {re: i for i, re in enumerate(res)}
    selected = [re for re in SELECTED_RE if re in re_idx]
    for re in selected:
        fig, ax = plt.subplots(figsize=(10.4, 4.8))
        ax.plot(xs, nu_lmtd[re_idx[re], :], lw=2.0, label="LMTD midspan proxy")
        ax.plot(xs, nu_tin[re_idx[re], :], lw=1.8, label="Tin reference")
        ax.plot(xs, nu_const[re_idx[re], :], lw=1.8, label="constant DeltaT=50K")
        add_tube_markers(ax)
        ax.set_xlabel("x position from tube center [mm]")
        ax.set_ylabel("Nu proxy [-]")
        ax.set_title(f"DeltaT-definition sensitivity for Re {re:g}")
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(OUT_DIR / f"fig08_deltaT_definition_sensitivity_Re{int(re)}.png", dpi=220)
        fig.savefig(OUT_DIR / f"fig08_deltaT_definition_sensitivity_Re{int(re)}.pdf")
        plt.close(fig)


def stage5_publication_gap_report() -> None:
    text = """# Stage 5: full-3D publication-grade analysis gap

The current 005 analysis is stronger than the exploratory 004 analysis, but it is still based on:

- surface-integrated `Q` and `A` from hot tube/fins,
- midspan `z=0` sampled-plane proxies for `T_bulk`, `Q_2D`, `lambda_ci`, and `omega_z`,
- x-strip binning of sampled VTK data.

What is complete now:

- tube/fins heat-transfer separation on full hot surfaces;
- absolute `Delta_Q` and `Delta_Nu` relative to Re150;
- renamed `relative_local_sensitivity_vs_Re150` to avoid overclaiming enhancement;
- energetic shares `Q_strip/Q_total`;
- spatial-lag correlation instead of zero-lag-only Pearson;
- tests without hotspot strips and without tube zone;
- strip-width sensitivity for 1.0, 0.5, and 0.1 mm;
- DeltaT-definition sensitivity for LMTD proxy, Tin reference, and constant DeltaT.

What is still required for publication-grade full 3D:

1. Full `y-z` cross-section mass-flow temperature:
   `T_bulk(x) = integral(rho Ux T dA) / integral(rho Ux dA)`.

2. Full 3D volume-band vortex metrics:
   integrate `Qcriterion`, `lambda2`, `lambda_ci`, or `omega` over x-bands in the fluid volume,
   not only on `z=0`.

3. Fin near-wall structure metrics:
   current near-wall metrics cover the tube annulus on `z=0`, not fin wall layers.

4. Threshold sensitivity:
   repeat vortex metrics with alternative thresholds for positive `Qcriterion`/negative `lambda2`.

5. Time-window and phase sensitivity:
   repeat metrics over multiple late windows and, for shedding cases, separate phase-averaged and RMS fields.

Recommended wording:

The current 005 dataset supports a conference/defense-level mechanism argument:
local heat-transfer sensitivity is spatially redistributed after onset, and zero-lag correlation is insufficient
because vortex/shear proxies are spatially shifted relative to thermal response.

For journal-level quantitative claims, use full 3D `T_bulk(x)` and volume-integrated vortex metrics.
"""
    (OUT_DIR / "STAGE5_full3D_publication_gap_report.md").write_text(text, encoding="utf-8")


def write_readme() -> None:
    readme = """# 005_x_strip_robustness_analysis

Robust x-strip analysis for conference defense and publication-oriented review.

Main correction relative to the exploratory 004 analysis:

- `Nu_local_excess_over_global_gain` is renamed and interpreted as `relative_local_sensitivity_vs_Re150`.
- It is not described as direct local heat-transfer enhancement.
- Absolute metrics `Delta_Nu`, `Delta_Q`, energetic shares, tube/fins split, spatial-lag correlations, hotspot-removal tests, strip-width sensitivity, and DeltaT-definition sensitivity are added.

Important figures:

- `fig01_relative_local_sensitivity_vs_Re150`: renamed relative sensitivity metric.
- `fig02_delta_Nu_vs_Re150`: absolute local Nu change.
- `fig03_delta_Q_vs_Re150`: absolute local heat-transfer change.
- `fig04_Q_strip_share_of_total`: energetic importance of each strip.
- `fig05_tube_fins_separated_profiles`: tube/fins separation.
- `fig06_spatial_lag_correlation_*.png`: spatial-offset correlation and robustness masks.
- `fig07_strip_width_hotspot_sensitivity`: sensitivity to 1.0, 0.5, and 0.1 mm strip widths.
- `fig08_deltaT_definition_sensitivity_Re*.png`: sensitivity to DeltaT definition.

Core CSV outputs:

- `x_strip_enriched_dx1mm.csv`: primary enriched local dataset.
- `stage2_spatial_lag_correlations.csv`: all lag correlations.
- `stage2_best_spatial_lags.csv`: best lag summary.
- `stage3_strip_width_sensitivity.csv`: strip-width robustness.
- `STAGE5_full3D_publication_gap_report.md`: what remains for publication-grade full 3D.
"""
    (OUT_DIR / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    width_rows = save_rows_for_widths()
    enriched_by_width = {}
    for dx_mm, rows in width_rows.items():
        path = OUT_DIR / f"x_strip_enriched_dx{dx_mm:g}mm.csv"
        if path.exists():
            enriched = read_csv(path)
        else:
            enriched = enrich_rows(rows)
            write_csv(enriched, path)
        enriched_by_width[dx_mm] = enriched

    primary = enriched_by_width[PRIMARY_DX_MM]
    plot_stage1_profiles(primary)
    plot_tube_fins(primary)
    lag_rows = stage2_lag_analysis(primary, dx_mm=PRIMARY_DX_MM)
    best_lag_table(lag_rows)
    stage3_width_sensitivity(enriched_by_width)
    stage4_delta_t_variants(primary)
    stage5_publication_gap_report()
    write_readme()
    print(f"Wrote robust analysis to {OUT_DIR}")


if __name__ == "__main__":
    main()
