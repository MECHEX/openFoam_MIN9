# Wall-Heat-Flux Tendency Budget PoC

Case: `V4b_3D run008`

## What this PoC computes

This is a near-wall first-cell estimate, not the final publication-grade
normal-derivative budget. For each selected hot-wall face we use:

- direct local `q''(t)` from the OpenFOAM `wallHeatFlux` boundary field,
- owner-cell `T`, `U`, and `grad(T)`,
- face-to-owner normal distance `d_n`,
- the constant-property `run008` conductivity `k = Cp * mu / Pr`.

The local first-cell closure used here is:

- `q''_model ~= k (T_wall - T_P) / d_n`
- `P_q_model = d q''_model / dt ~= -(k/d_n) dT_P/dt`
- `P_adv_est ~= (k/d_n) (u . grad T)_P`
- `P_diff_est ~= -(k/d_n) (dT_P/dt + (u . grad T)_P)`

The most honest comparison quantity is therefore the direct boundary-field tendency
`P_q_direct = d q''/dt` together with the residual closure
`P_q_direct - (P_adv_est + P_diff_est)`.

## Region inventory

- analysed faces: `12532`
- analysed regions: `fin_control, fin_near_tube, fin_sweep, tube_junction, tube_rear, tube_separation`

## RMS summary

| region | n_faces | q_mean [W/m2] | RMS(P_q) | RMS(P_adv) | RMS(P_diff) | RMS(closure) | corr(P_q,P_adv) | corr(P_q,P_diff) | dominant | q_model MAE [%q] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| `fin_control` | 600 | 1238.98 | 0.15 | 40.61 | 40.54 | 0.00 | 0.445 | -0.442 | advective | 0.00 |
| `fin_near_tube` | 1644 | 569.36 | 0.69 | 0.76 | 1.17 | 0.00 | -0.310 | 0.790 | diffusive | 0.00 |
| `fin_sweep` | 1704 | 371.84 | 15.64 | 15.84 | 23.77 | 0.00 | -0.140 | 0.751 | diffusive | 0.00 |
| `tube_junction` | 3920 | 714.56 | 3.87 | 0.30 | 3.79 | 0.28 | -0.001 | 0.995 | diffusive | 25.73 |
| `tube_rear` | 2024 | 226.38 | 43.01 | 5.22 | 43.53 | 0.00 | -0.041 | 0.993 | diffusive | 0.00 |
| `tube_separation` | 2640 | 1068.49 | 2.65 | 1.80 | 2.99 | 0.61 | -0.047 | 0.765 | diffusive | 6.57 |

## First reading

- strongest direct tendency RMS region: `tube_rear`
- weakest direct tendency RMS region: `fin_control`
- `tube_*` regions indicate tube-wall production zones.
- `fin_*` regions indicate fin-wall production zones aggregated over both fin sides.

## Limits

- This is not yet the exact wall-normal derivative form `k d_n(u.gradT) - k alpha d_n(laplacianT)`.
- `P_diff_est` is obtained from the first-cell energy balance, not from an independently differentiated wall-normal Laplacian.
- The closure column tells us how far the first-cell estimate is from the direct `wallHeatFlux` tendency.
- A publication-grade extension should repeat this with explicit near-wall gradient reconstruction and grid/time sensitivity of the budget itself.

## Figures

- `figures/run008_budget_phase_regions.png`
- `figures/run008_budget_rms_summary.png`

Figure title candidate:

`Local wall-heat-flux tendency budget: where the wall gradient is produced, not where vortices are visible.`
