# 005_x_strip_robustness_analysis

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
- `fig09_dx0p5mm_core_profiles` and `fig09_dx0p1mm_core_profiles`: direct 0.5 mm and 0.1 mm strip profiles for relative sensitivity, Delta Nu, Delta Q, and strip heat share.
- `fig10_dx0p5mm_tube_fins_profiles` and `fig10_dx0p1mm_tube_fins_profiles`: direct 0.5 mm and 0.1 mm tube/fins separated profiles.

Strip-width interpretation:

- 0.5 mm profiles are useful as a robustness check against the primary 1 mm strips.
- 0.1 mm profiles are intentionally shown, but should be treated as an over-refined post-processing stress test; many zero/spike patterns come from surface/sample discretization rather than smooth physical variation.

Core CSV outputs:

- `x_strip_enriched_dx1mm.csv`: primary enriched local dataset.
- `stage2_spatial_lag_correlations.csv`: all lag correlations.
- `stage2_best_spatial_lags.csv`: best lag summary.
- `stage3_strip_width_sensitivity.csv`: strip-width robustness.
- `STAGE5_full3D_publication_gap_report.md`: what remains for publication-grade full 3D.
