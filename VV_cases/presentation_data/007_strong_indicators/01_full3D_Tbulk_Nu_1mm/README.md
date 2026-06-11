# 01_full3D_Tbulk_Nu_1mm

Stage 01 builds a stronger local thermal dependent variable for later coherence and EPOD analysis.

Inputs:

- `../../006_full3D_x_strip_1mm/full3D_x_strip_1mm_merged_with_heat.csv`
- `../../005_x_strip_robustness_analysis/x_strip_enriched_dx1mm.csv`

Main definition:

`Nu_3D_Tbulk_lmtd = Q_strip * D / (A_strip * k * DeltaT_3D_lmtd)`

where `Q_strip` and `A_strip` come from full hot tube/fins wall surfaces, while `DeltaT_3D_lmtd` is estimated from the full-3D convective bulk-temperature proxy in each 1 mm x-strip.

Important limitation:

This is stronger than the earlier midspan/LMTD proxy, but it is still based on a 3D strip-wise bulk-temperature proxy. Exact publication-grade `T_bulk(x,t)` should later be computed on y-z cutting planes.

Outputs:

- `stage01_full3D_Tbulk_Nu_1mm.csv`
- `stage01_summary_global_indicators.csv`
- `fig01_Tbulk3D_and_DeltaT_profiles`
- `fig02_Nu3D_profiles_and_proxy_comparison`
- `fig03_DeltaNu_DeltaQ_relative_sensitivity_3D`
- `fig04_tube_fins_Nu3D_and_Q_profiles`
