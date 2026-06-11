# 002_Nu_and_vorticity

Presentation figures relating heat transfer to vortex presence/intensity.

## Figure 1

`fig01_Qwall_vs_ClRMS.png`

- x-axis: late-window `Cl_rms`, used as a global vortex-shedding intensity metric.
- y-axis: integrated wall heat transfer `Q_wall = Q_tube + Q_fins` from `wallHeatFlux`.
- points: completed production-geometry cases Re=100, 150, 160, 175, 200.
- Re=155 is excluded until the run is fully post-processed.

## Figure 2

`fig02_heat_partition_steady_vs_shedding.png`

- stacked bars: heat-transfer partition between tube and fins.
- black line: `Cl_rms`, showing vortex intensity on the same cases.
- comparison highlights transition from steady/pre-Hopf cases to shedding/post-Hopf cases.

## Figure 3

`fig03_Q_components_and_ClRMS_vs_Re.png`

- left panel: `Q_total`, `Q_tube`, and `Q_fins` as functions of Reynolds number.
- right panel: `Cl_rms` as a compact vortex-intensity/onset indicator.
- shaded band: current onset bracket between steady Re=150 and shedding Re=160.

## Figure 4

`fig04_stripwise_Q_profiles_by_Re.png`

- integrates `wallHeatFlux` directly on hot tube and fin VTK surfaces.
- strips are 1 mm wide in streamwise `x`, using polygon centroid assignment.
- each curve is averaged over the late-time analysis window for that Re.

## Figure 5

`fig05_stripwise_delta_Re200_minus_Re150.png`

- local stripwise difference between production shedding Re=200 and steady Re=150.
- highlights where the globally smooth Q(Re) trend has local spatial structure.

## Figures 6-9

`fig06_local_excess_over_global_gain.png`

- compares local strip gain against global gain, so it suppresses the trivial effect that larger Re gives larger total Q.

`fig07_Q_excess_over_steady_model.png`

- subtracts a local linear extrapolation based on steady Re=100 and Re=150.

`fig08_local_share_delta_vs_Re150.png`

- shows whether each strip takes a larger or smaller share of total heat transfer than in the Re=150 baseline.

`fig09_local_dQdRe_by_interval.png`

- estimates local sensitivity over Re intervals 100-150, 150-160, and 160-200.

## Important note

Figures use `Q_wall` directly from integrated `wallHeatFlux`. This is good for mechanism
and presentation-level interpretation, but publication-grade comparison should also use
the final accepted `Nu`/thermal normalization workflow for each Re.
