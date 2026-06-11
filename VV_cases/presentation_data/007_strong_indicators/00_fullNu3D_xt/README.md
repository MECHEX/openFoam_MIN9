# 00_fullNu3D_xt

This folder contains the first time-resolved full-3D strip Nusselt dataset.

Definition used here:

`Nu_3D(x,t) = Q_strip(x,t) * D_ref / (A_strip(x,t) * k_air * DeltaT_lm_yz(x,t))`

where:

- `Q_strip(x,t)` is integrated from the full hot tube and fin `wallHeatFlux` VTK surfaces.
- `A_strip(x,t)` is the corresponding hot-surface area in each 1 mm x-strip.
- `T_bulk_left/right_yz(x,t)` is computed from full y-z cut planes as
  `integral(rho Ux T dA) / integral(rho Ux dA)`, using positive `Ux`.
- `DeltaT_lm_yz` is the logarithmic wall-to-air temperature difference between the left and right strip boundaries.

Settings:

- strip width: `1 mm`
- time window: 8-10 s for all cases
- time sampling: all available volume-field snapshots with matching hot-surface files; 26 snapshots per Re
- wall temperature: `343.15 K`
- reference diameter: `0.012 m`
- air conductivity: `0.028 W/(m K)`

Outputs:

- `fullNu3D_xt_time_resolved.csv`: main `x,t` dataset.
- `fullNu3D_xt_time_averaged_by_x.csv`: time-mean profile by strip.
- `fullNu3D_xt_summary_by_Re.csv`: scalar summary by Reynolds number.
- `fig01_Nu3D_xt_profiles_time_mean`: x-profiles with temporal standard deviation.
- `fig02_Nu3D_xt_time_traces_selected_strips`: selected time traces.
- `fig03_Nu3D_xt_heatmap_Re*`: x-time heatmaps for shedding cases.

Important note:

Tube/fins split columns use the same local y-z bulk temperature for a strip. This is physically defensible for air-side local Nu, but it is not a separate wall-temperature field for tube and fins.
