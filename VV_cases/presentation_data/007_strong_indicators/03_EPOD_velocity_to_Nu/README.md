# 03_EPOD_velocity_to_Nu

This stage links midspan velocity structures to the full-surface local heat-transfer response.

Definition:

- Velocity side: POD of `U_x, U_y` fluctuations on the existing `midspan_z0` sampled plane.
- Thermal side: full `Nu_3D(x,t)` from stage `00_fullNu3D_xt`.
- EPOD indicator: correlation/covariance between each velocity POD temporal coefficient and each local `Nu_3D(x,t)` strip.
- Additional scalar: `R2_Nu_from_first3_velocity_modes`, the fraction of local Nu fluctuation variance explained by the first three velocity POD coefficients.

Important limitation:

This is not a full-volume 3D velocity POD. It uses the midspan plane because those data are already available at all matching full-field times. Treat it as a mechanistic indicator: which coherent velocity modes appear to drive or mirror local air-side heat-transfer response.

Outputs:

- `stage03_velocity_POD_energy.csv`
- `stage03_EPOD_mode_Nu_correlations.csv`
- `stage03_temporal_coefficients_and_selected_Nu.csv`
- `fig01_velocity_POD_energy_Re*`
- `fig02_EPOD_corr_map_Re*`
- `fig03_R2_Nu_from_velocity_modes_Re*`
- `fig04_a1_vs_selected_Nu_Re*`

Strongest mode-Nu links found:

```text
   Re  mode  x_center_mm  corr_mode_coeff_vs_Nu  R2_Nu_from_first3_velocity_modes
175.0     1         13.5               0.979954                          0.982973
175.0     1         -7.5               0.979947                          0.989889
160.0     1         -5.5              -0.979031                          0.968698
200.0     1        -10.5              -0.977499                          0.993029
150.0     1          7.5               0.976621                          0.970846
200.0     1         -9.5              -0.975459                          0.988586
160.0     1         -4.5              -0.974613                          0.982895
175.0     1         12.5               0.972899                          0.970452
```
