# V4b_3D run008 local fin Nu

Primary window: `2.0..10.0 s`, samples `1601`.
Definition: `Nu_local(x,t) = q''(x,t) D / (k LMTD(t))`; x-profiles are point-averaged over each fin surface.
Phase and coupling reference: `Cl` from layer `002`.

## Summary

| Metric | Value |
|---|---:|
| n_times | 1601.000000 |
| n_x_bins | 80.000000 |
| n_valid_x_bins_z_min | 61.000000 |
| n_valid_x_bins_z_max | 61.000000 |
| Nu_mean_z_min | 4.566922 |
| Nu_mean_z_max | 4.541200 |
| Nu_rms_z_min_mean | 0.048238 |
| Nu_rms_z_max_mean | 0.049844 |
| A1_z_min_mean | 0.013569 |
| A1_z_max_mean | 0.013023 |
| A2_z_min_mean | 0.009504 |
| A2_z_max_mean | 0.011093 |
| mean_abs_antisymmetric_Nu | 0.014799 |
| mean_fin_pair_corr | 0.857934 |
| mean_coherence_z_min | 0.605514 |
| mean_coherence_z_max | 0.613258 |
| active_fraction_z_min | 0.508197 |
| active_fraction_z_max | 0.491803 |
| median_lag_z_min_s | -0.075000 |
| median_lag_z_max_s | -0.075000 |
| phase1_z_max_minus_z_min_deg | -3.326004 |
| median_lag_z_max_minus_z_min_s | 0.000000 |

## Interpretation

- Mean fin Nu is nearly symmetric: z_min `4.567`, z_max `4.541`.
- Mean absolute antisymmetric component is `0.0148` Nu and the mean fin-pair time correlation is `0.858`.
- Cl-coupled zones occupy `50.8%` of x bins on z_min and `49.2%` on z_max using coherence >= 0.5 and above-median A1.
- Median lag estimates are `-0.0750 s` for z_min and `-0.0750 s` for z_max; median z_max-z_min lag difference is `+0.0000 s`.
- Mean `A1` phase difference z_max-z_min is `-3.33 deg`, so the two fin surfaces are nearly in phase for the Cl-coupled component.

## Figures

- `../../figures/005/run008_005_fin_nu_x_profiles.png`
- `../../figures/005/run008_005_fin_phase_coherence_lag.png`
- `../../figures/005/run008_005_fin_nu_xt_maps.png`
- `../../figures/005/run008_005_fin_active_coupled_zones.png`
