# Stage 5: full-3D publication-grade analysis gap

The current 005 analysis is stronger than the exploratory 004 analysis, but it is still based on:

- surface-integrated `Q` and `A` from hot tube/fins,
- midspan `z=0` sampled-plane proxies for `T_bulk`, `Q_2D`, `lambda_ci`, and `omega_z`,
- x-strip binning of sampled VTK data.

What is complete now:

- tube/fins heat-transfer separation on full hot surfaces;
- absolute `Delta_Q` and `Delta_Nu` relative to Re150;
- renamed `relative_local_sensitivity_vs_Re150` to avoid overclaiming enhancement;
- energetic shares `Q_strip/Q_total`;
- spatial-lag correlation instead of zero-lag-only Pearson;
- tests without hotspot strips and without tube zone;
- strip-width sensitivity for 1.0, 0.5, and 0.1 mm;
- DeltaT-definition sensitivity for LMTD proxy, Tin reference, and constant DeltaT.

What is still required for publication-grade full 3D:

Update 2026-06-09:

- A first full-volume 3D x-strip analysis was completed in `../006_full3D_x_strip_1mm`.
- It computes OpenFOAM `Q` and `vorticity` in the 3D fluid volume and averages/integrates them over 1 mm x-strips.
- It also separates tube-near-wall, wake, and bulk-no-tube-wall regions using 3D cell centroids.
- Heat transfer remains joined from full hot-surface `wallHeatFlux` integration.
- The remaining publication-grade gap is exact mass-flow `T_bulk(x)` on y-z cutting planes and optional threshold/window sensitivity.

1. Full `y-z` cross-section mass-flow temperature:
   `T_bulk(x) = integral(rho Ux T dA) / integral(rho Ux dA)`.

2. Full 3D volume-band vortex metrics:
   integrate `Qcriterion`, `lambda2`, `lambda_ci`, or `omega` over x-bands in the fluid volume,
   not only on `z=0`.

3. Fin near-wall structure metrics:
   current near-wall metrics cover the tube annulus on `z=0`, not fin wall layers.

4. Threshold sensitivity:
   repeat vortex metrics with alternative thresholds for positive `Qcriterion`/negative `lambda2`.

5. Time-window and phase sensitivity:
   repeat metrics over multiple late windows and, for shedding cases, separate phase-averaged and RMS fields.

Recommended wording:

The current 005 dataset supports a conference/defense-level mechanism argument:
local heat-transfer sensitivity is spatially redistributed after onset, and zero-lag correlation is insufficient
because vortex/shear proxies are spatially shifted relative to thermal response.

For journal-level quantitative claims, use full 3D `T_bulk(x)` and volume-integrated vortex metrics.
