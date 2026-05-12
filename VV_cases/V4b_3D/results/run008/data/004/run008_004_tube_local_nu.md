# V4b_3D run008 local tube Nu

Primary window: `2.0..10.0 s`, samples `1601`.
Definition: `Nu(theta,z,t) = q''(theta,z,t) D / (k LMTD(t))`; `LMTD(t)` comes from reconstructed outlet `T`.
Phase reference: `Cl` analytic signal from layer `002`.

## Summary

| Metric | Value |
|---|---:|
| n_times | 1601.000000 |
| n_theta_bins | 96.000000 |
| n_z_bins | 30.000000 |
| Nu_mean_area_proxy | 8.588057 |
| Nu_rms_area_proxy | 0.097830 |
| A1_mean | 0.025266 |
| A1_max | 0.062989 |
| A2_mean | 0.021483 |
| A2_max | 0.059636 |
| asym_abs_mean | 0.290857 |
| asym_abs_max | 1.325308 |
| theta_profile_max_deg | 155.625000 |
| theta_profile_min_deg | 35.625000 |
| upper_lower_asym_corr_with_Cl_zero_lag | 0.900067 |
| upper_lower_asym_best_lag_s_positive_asym_lags_Cl | -0.005000 |
| upper_lower_asym_best_lag_corr | 0.922201 |

## Interpretation

- Mean local tube Nu proxy is `8.588`; peak z-averaged Nu occurs near `theta = 155.6 deg`.
- First-harmonic local modulation is modest on average (`A1_mean = 0.025`) but localized peaks reach `A1_max = 0.063`.
- Second-harmonic modulation is comparable in places (`A2_max = 0.060`), consistent with the strong `2*f_shed` component seen in forces.
- Mean angular asymmetry magnitude is `0.291` Nu, with local extrema up to `1.325` Nu.
- Global upper-lower Nu asymmetry has zero-lag correlation `+0.900` with `Cl`; best short-lag correlation is `+0.922` at `-0.005 s`.

## Figures

- `../../figures/004/run008_004_tube_nu_maps_mean_rms_harmonics.png`
- `../../figures/004/run008_004_tube_nu_phase_asymmetry_maps.png`
- `../../figures/004/run008_004_tube_phase_averaged_nu_maps.png`
- `../../figures/004/run008_004_tube_nu_theta_profiles_asymmetry.png`
- `../../figures/004/run008_004_tube_nu_z_characteristic_angles.png`
- `../../figures/004/run008_004_tube_asymmetry_vs_cl.png`
