# 004_x_strip_Nu_vorticity

Local x-strip Nusselt and vorticity-proxy analysis.

## Method

- Strips are 1 mm wide along the streamwise `x` direction.
- `Q_strip` and `A_strip` are integrated directly from hot tube and hot fin VTK surfaces.
- `alpha_strip = Q_strip / (A_strip * deltaT_lm_proxy)`.
- `Nu_strip_proxy = alpha_strip * D / k_air`.
- Constants used: `D = 0.012 m`, `T_wall = 343.15 K`, `k_air = 0.028 W/(m K)`.
- `deltaT_lm_proxy` is based on midspan `T_bulk` proxy from the `z=0` sampled plane, weighted by positive `Ux`.
- Vorticity proxy is `mean(|omega_z|) * D / U_ref`, computed on the same `z=0` sampled plane.
- Regional metrics separate near-wall and wake mechanisms:
  near-wall uses a tube annulus from `R` to `R + 0.0015 m`;
  wake uses `x >= R` and excludes that near-wall annulus.
- `bulk_without_tube_near_wall` uses the whole midspan plane over the full x-domain,
  but removes the tube near-wall annulus.

## Important Limitation

This is a presentation/mechanism metric, not yet a full publication-grade local Nu.
For strict validation, `T_bulk(x_left)` and `T_bulk(x_right)` should be computed from full
`y-z` cross-sections using mass-flow weighting. Here they are approximated from the midspan plane.

## Figures

`fig01_x_strip_Nu_profiles_by_Re.png`: local strip Nusselt profiles.

`fig02_x_strip_vorticity_profiles_by_Re.png`: local vorticity/mixing proxy profiles.

`fig03_x_strip_Nu_excess_over_global_gain.png`: local Nu excess after removing mean Nu scaling.

`fig04_x_strip_Nu_excess_and_vorticity_overlay.png`: z-scored overlay of Nu excess and vorticity proxy.

`fig05_scatter_vorticity_vs_Nu_excess.png`: stripwise correlation between vorticity proxy and Nu excess.

`fig06_x_strip_Q_reference_profiles_by_Re.png`: original Q profiles for reference.

`fig07_x_strip_Qcriterion2D_profiles_by_Re.png`: one positive `Q_2D` criterion number per x-strip.

`fig08_x_strip_lambda_ci_profiles_by_Re.png`: one 2D swirling-strength number per x-strip.

`fig09_x_strip_near_wall_omega_profiles_by_Re.png`: near-wall shear/rotation separated from wake.

`fig10_x_strip_wake_Qcriterion2D_profiles_by_Re.png`: wake-only positive `Q_2D` proxy.

`fig11_x_strip_wake_lambda_ci_profiles_by_Re.png`: wake-only 2D swirling strength.

`fig12_x_strip_near_wall_Qcriterion2D_profiles_by_Re.png`: near-wall positive `Q_2D` around the tube.

`fig13_x_strip_near_wall_lambda_ci_profiles_by_Re.png`: near-wall 2D swirling strength around the tube.

`fig14_x_strip_bulk_no_near_wall_Qcriterion2D_profiles_by_Re.png`: full x-domain midspan positive `Q_2D` after removing tube near-wall region.

`fig15_x_strip_bulk_no_near_wall_lambda_ci_profiles_by_Re.png`: full x-domain midspan swirling strength after removing tube near-wall region.

`fig16`-`fig19`: direct Nu-excess comparison with inner/bulk vortex proxies after removing tube near-wall region.

`fig20`-`fig23`: direct Nu-excess comparison with tube near-wall vortex/shear proxies.

`x_strip_vorticity_Nu_correlation.csv`: Pearson correlations between Nu excess and each vortex proxy.
