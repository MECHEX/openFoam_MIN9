# 006_full3D_x_strip_1mm

Full-3D x-strip analysis using 1 mm streamwise strips.

What is full 3D here:

- OpenFOAM `Q` and `vorticity` fields are computed from the 3D volume solution.
- Metrics are integrated/averaged over all fluid cells assigned to each 1 mm x-strip.
- Tube-near-wall, wake, and bulk-no-tube-wall regions are separated using 3D cell centroids.
- Heat-transfer metrics are joined from the existing full hot-surface `wallHeatFlux` integration in 005.

Important limitation:

- `T_bulk_3D_Ux_volume_weighted_K` is a 3D convective volume-weighted proxy, not an exact y-z cross-section mass-flow integral.
- Exact publication-grade `T_bulk(x)` still needs sampled y-z cutting planes or face-based integration.

Times used:

- `run012_re100`: 8, 8.96, 10
- `run013_re150`: 8, 8.96, 10
- `run015_re160`: 8, 8.96, 10
- `run014_re175`: 8, 8.96, 10
- `run008_re200`: 8, 8.96, 10

Main outputs:

- `full3D_x_strip_1mm_time_resolved.csv`
- `full3D_x_strip_1mm_time_averaged.csv`
- `full3D_x_strip_1mm_merged_with_heat.csv`
- `full3D_spatial_lag_correlations.csv`
- `full3D_best_spatial_lags.csv`
- `fig01_full3D_x_strip_profiles`
- `fig02_Nu_sensitivity_vs_full3D_bulk_Qcriterion`
- `fig03_full3D_spatial_lag_correlations`
