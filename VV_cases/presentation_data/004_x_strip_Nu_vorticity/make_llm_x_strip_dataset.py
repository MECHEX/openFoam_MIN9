from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
RAW = HERE / "x_strip_1mm_Nu_vorticity.csv"
DERIVED = HERE / "x_strip_1mm_Nu_vorticity_derived.csv"
CORR = HERE / "x_strip_vorticity_Nu_correlation.csv"
OUT_MD = HERE / "LLM_x_strip_left_to_right_dataset.md"
OUT_CSV = HERE / "LLM_x_strip_left_to_right_local_data.csv"


LOCAL_COLUMNS = [
    "Re",
    "case",
    "regime",
    "x_center_mm",
    "Q_total_strip_W",
    "Q_tube_strip_W",
    "Q_fins_strip_W",
    "A_total_strip_m2",
    "deltaT_lm_proxy_K",
    "alpha_strip_W_m2K",
    "Nu_strip_proxy",
    "omega_z_abs_nd",
    "Qcriterion_2D_positive_nd",
    "lambda_ci_2D_nd",
    "near_wall_omega_z_abs_nd",
    "near_wall_Qcriterion_2D_positive_nd",
    "near_wall_lambda_ci_2D_nd",
    "wake_Qcriterion_2D_positive_nd",
    "wake_lambda_ci_2D_nd",
    "bulk_without_tube_near_wall_Qcriterion_2D_positive_nd",
    "bulk_without_tube_near_wall_lambda_ci_2D_nd",
]

DERIVED_COLUMNS = [
    "Re",
    "x_center_mm",
    "Nu_local_excess_over_global_gain",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(value: str) -> float:
    if value == "" or value.lower() == "nan":
        return float("nan")
    return float(value)


def fmt(value: float | str, digits: int = 6) -> str:
    if isinstance(value, str):
        if value == "" or value.lower() == "nan":
            return "nan"
        try:
            value = float(value)
        except ValueError:
            return value
    if value != value:
        return "nan"
    return f"{value:.{digits}g}"


def rows_to_csv_text(rows: list[dict[str, str]], columns: list[str]) -> str:
    out = [",".join(columns)]
    for row in rows:
        out.append(",".join(fmt(row.get(col, "")) for col in columns))
    return "\n".join(out)


def main() -> None:
    raw = read_csv(RAW)
    derived = read_csv(DERIVED)
    corr = read_csv(CORR)
    excess_by_key = {
        (fmt(row["Re"]), fmt(row["x_center_mm"])): row["Nu_local_excess_over_global_gain"]
        for row in derived
    }

    local_rows = []
    for row in raw:
        slim = {col: row.get(col, "") for col in LOCAL_COLUMNS}
        slim["Nu_local_excess_over_global_gain"] = excess_by_key.get(
            (fmt(row["Re"]), fmt(row["x_center_mm"])), "nan"
        )
        local_rows.append(slim)

    local_columns = LOCAL_COLUMNS + ["Nu_local_excess_over_global_gain"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=local_columns)
        writer.writeheader()
        writer.writerows(local_rows)

    summary_rows = []
    for re in sorted({row["Re"] for row in raw}, key=float):
        sub = [row for row in raw if row["Re"] == re]
        def avg(col: str) -> float:
            vals = [fnum(row[col]) for row in sub if fnum(row[col]) == fnum(row[col])]
            return sum(vals) / len(vals) if vals else float("nan")

        def total(col: str) -> float:
            vals = [fnum(row[col]) for row in sub if fnum(row[col]) == fnum(row[col])]
            return sum(vals)

        summary_rows.append(
            {
                "Re": re,
                "regime": sub[0]["regime"],
                "Q_total_sum_W": fmt(total("Q_total_strip_W")),
                "Q_tube_sum_W": fmt(total("Q_tube_strip_W")),
                "Q_fins_sum_W": fmt(total("Q_fins_strip_W")),
                "Nu_mean_proxy": fmt(avg("Nu_strip_proxy")),
                "Nu_min_proxy": fmt(min(fnum(row["Nu_strip_proxy"]) for row in sub)),
                "Nu_max_proxy": fmt(max(fnum(row["Nu_strip_proxy"]) for row in sub)),
                "omega_mean_nd": fmt(avg("omega_z_abs_nd")),
                "near_wall_omega_mean_nd": fmt(avg("near_wall_omega_z_abs_nd")),
                "wake_Qcriterion_mean_nd": fmt(avg("wake_Qcriterion_2D_positive_nd")),
                "bulk_no_wall_Qcriterion_mean_nd": fmt(
                    avg("bulk_without_tube_near_wall_Qcriterion_2D_positive_nd")
                ),
                "bulk_no_wall_lambda_ci_mean_nd": fmt(
                    avg("bulk_without_tube_near_wall_lambda_ci_2D_nd")
                ),
            }
        )

    summary_columns = list(summary_rows[0].keys())
    corr_columns = ["Re", "metric", "pearson_r_vs_Nu_excess", "n_strips"]

    md = f"""# LLM x-strip left-to-right dataset

Purpose: compact dataset for another LLM to analyze local heat-transfer and vortex/shear proxies from left to right along the exchanger.

Coordinate convention:

- `x_center_mm` is strip center position in millimeters relative to tube center.
- Negative `x` is upstream/left side.
- Tube approximate bounds are `x = -6 mm` and `x = +6 mm`.
- Strips are 1 mm wide.

Core heat-transfer definitions:

- `Q_total_strip_W = Q_tube_strip_W + Q_fins_strip_W`, integrated from wallHeatFlux on hot surfaces.
- `alpha_strip_W_m2K = Q_total_strip_W / (A_total_strip_m2 * deltaT_lm_proxy_K)`.
- `Nu_strip_proxy = alpha_strip_W_m2K * D / k_air`, with `D = 0.012 m`, `k_air = 0.028 W/(m K)`.
- `deltaT_lm_proxy_K` uses midspan `z=0` bulk-temperature proxy, not full 3D mass-flow cross-section.

Vortex/shear proxy definitions:

- `omega_z_abs_nd`: whole midspan strip mean `|omega_z| D / U_ref`.
- `Qcriterion_2D_positive_nd`: whole midspan strip mean `max(Q_2D,0) D^2 / U_ref^2`.
- `lambda_ci_2D_nd`: whole midspan strip mean 2D swirling strength `lambda_ci D / U_ref`.
- `near_wall_*`: tube near-wall annulus only, from `R` to `R + 1.5 mm`.
- `wake_*`: only downstream wake region `x >= R`, excluding tube near-wall annulus.
- `bulk_without_tube_near_wall_*`: full midspan strip over all `x`, excluding the tube near-wall annulus.

Important limitation:

- These vortex/shear proxies come from `z=0` midspan sampled planes, not full 3D volume fields.
- Near-wall values cover the tube near-wall region, not fin wall layers.
- Use these as mechanism/proxy data, not final publication-grade local Nu validation.

Suggested analysis request:

Analyze whether local `Nu_strip_proxy` and especially `Nu_local_excess_over_global_gain` are better explained by near-wall tube shear, wake vortex proxies, or bulk-without-near-wall vortex proxies. Look for spatial offsets, not only Pearson correlation, because wake structures may affect heat transfer downstream or indirectly.

## Re-level summary

```csv
{rows_to_csv_text(summary_rows, summary_columns)}
```

## Correlations with local Nu excess

```csv
{rows_to_csv_text(corr, corr_columns)}
```

## Local x-strip data

```csv
{rows_to_csv_text(local_rows, local_columns)}
```
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
