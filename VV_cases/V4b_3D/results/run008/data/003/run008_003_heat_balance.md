# V4b_3D run008 heat-balance closure

Primary window: `2.0..10.0 s`.

## Heat-flow summary

Reference area for all reported Nu definitions: `A_hot_total = 0.002032 m2`.
Patch areas are scaled from wallHeatFlux effective areas by factor `1.017157` to preserve this reference area.

| Metric | mean | std | min | max |
|---|---:|---:|---:|---:|
| Q_air | 1.470276 | 0.065605 | 1.264041 | 1.645439 |
| Q_air_massT | 1.473448 | 0.079669 | 1.214971 | 1.672485 |
| Q_wall | 1.480659 | 0.002746 | 1.475781 | 1.487595 |
| Q_tube | 0.361770 | 0.001012 | 0.359853 | 0.364449 |
| Q_fin_min | 0.560369 | 0.001160 | 0.557525 | 0.564654 |
| Q_fin_max | 0.558520 | 0.001485 | 0.556152 | 0.562347 |
| Q_fins | 1.118888 | 0.002067 | 1.115387 | 1.124762 |
| closure_pct | 0.913527 | 4.660770 | -10.036187 | 17.118854 |
| closure_ratio_of_means_pct | 0.706213 | 0.000000 | 0.706213 | 0.706213 |
| closure_massT_pct | 0.792536 | 5.628379 | -11.611288 | 21.632258 |
| tube_share_pct | 24.433060 | 0.044011 | 24.337409 | 24.567861 |
| fins_share_pct | 75.566940 | 0.044011 | 75.432139 | 75.662591 |
| fin_min_share_pct | 37.845945 | 0.067980 | 37.718927 | 38.047155 |
| fin_max_share_pct | 37.720995 | 0.052953 | 37.588116 | 37.851246 |
| Nu_tube_wall | 8.434408 | 0.060597 | 8.243016 | 8.607445 |
| Nu_fin_min_wall | 7.648288 | 0.061117 | 7.448601 | 7.814870 |
| Nu_fin_max_wall | 7.623032 | 0.059653 | 7.436505 | 7.765723 |
| Nu_fins_wall | 7.635660 | 0.059288 | 7.442553 | 7.789370 |
| Nu_total_wall | 7.816521 | 0.059077 | 7.623802 | 7.974607 |
| Nu_EB | 7.766842 | 0.401601 | 6.521058 | 8.864239 |

## Lag estimate

| Pair | lag [s] | lag / T_shed | corr | interpretation |
|---|---:|---:|---:|---|
| Q_wall -> Q_air | +1.6600 | +5.443 | 0.1507 | positive lag means the second signal lags the first |
| Q_wall -> T_out | +1.6600 | +5.443 | 0.1519 | positive lag means the second signal lags the first |

## Interpretation

- Ratio-of-means wall-air closure is `+0.706%`; instantaneous closure has mean `+0.914%` and std `4.661%`.
- Tube contributes `24.43%` of wall heat, fins `75.57%`.
- `Nu_total_wall = 7.8165` and `Nu_EB = 7.7668`; the independent definitions differ by `+0.640%`.
- Lag correlations are weak; treat transport-lag values as diagnostic, not as a robust convection-time measurement unless repeated with a longer record or a cleaner outlet signal.

## Figures

- `../../figures/003/run008_003_heat_balance_timeseries_closure.png`
- `../../figures/003/run008_003_heat_balance_lag.png`
- `../../figures/003/run008_003_heat_shares_and_nu.png`
- `../../figures/003/run008_003_nu_eb_vs_wall_scatter.png`
