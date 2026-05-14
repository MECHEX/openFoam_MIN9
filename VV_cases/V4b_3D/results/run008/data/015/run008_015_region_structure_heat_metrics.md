# V4b_3D run008 layer 015: region-limited structure/heat/phase coupling

## Purpose

This diagnostic layer asks whether local vortical activity in physically
defined regions is more informative than global Q/Lambda2 cell counts when
paired with local heat-transfer response and the Cl shedding phase.

No new CFD was run. The layer uses the six existing layer-013 full-field
checkpoints and local Nu arrays from layers 004/005/009.

## Inputs

- Q/Lambda2/vorticity VTK export: `/home/hexmachina/of_runs/V4b_3D_run008_q_lambda2_013/vtk_processors`
- selected phases: `data/013/run008_013_selected_q_lambda2_times.csv`
- tube local Nu phase maps: `data/009/run008_009_phase_arrays.npz`
- fin local Nu phase maps: `data/009/run008_009_phase_arrays.npz`

## Region definitions

- `D = 0.012 m`, `R = 0.006 m`, `U_ref = 0.25266 m/s`
- tube centre assumed at `(0, 0, 0)` in the OpenFOAM case coordinates
- fin planes at `z = -0.006 m` and `z = +0.006 m`
- thresholds: `Q_thr = 3000.0`, `Lambda2_thr = -3000.0`

| region | physical target | paired heat region |
|---|---|---|
| `R_sep` | side shear-layer/separation shell near tube | `tube_sep` |
| `R_near_wake` | immediate wake behind tube | `tube_rear` |
| `R_fin_junction` | tube-fin junction volume | `tube_junction + fin_near_tube` |
| `R_fin_sweep` | near-fin downstream sweeping zone | `fin_downstream_sweep` |
| `R_far_wake` | downstream control region | `fin_upstream_control` |
| `R_global_control` | all cells with positive volume | global control pairing |

## Outputs

- `data/015/run008_015_region_q_lambda2_metrics.csv`
- `data/015/run008_015_region_heat_metrics.csv`
- `data/015/run008_015_region_structure_heat_merged.csv`
- `data/015/run008_015_region_structure_heat_correlations.csv`
- `figures/015/run008_015_region_structure_heat_phase.png`
- `figures/015/run008_015_region_structure_heat_phase.pdf`

## First-pass correlation screen

| region | corr(I_Lambda2*, Nu) | n |
|---|---:|---:|
| `R_far_wake` | 0.168 | 6 |
| `R_fin_junction` | -0.145 | 6 |
| `R_fin_sweep` | -0.870 | 6 |
| `R_global_control` | 0.166 | 6 |
| `R_near_wake` | -0.113 | 6 |
| `R_sep` | -0.136 | 6 |

## Interpretation

This is a six-phase diagnostic, so it should be read as a screening layer,
not as a final causal/lag analysis. It is useful if region-limited
structure metrics vary more clearly than the global control and if the
stronger correlations occur in physically paired regions, especially
`R_near_wake`, `R_sep`, or `R_fin_junction`.

The paper-grade extension would compute Q/Lambda2 for many more run008
checkpoints over `t = 2..10 s`, then evaluate lagged correlations between
regional structure metrics and local Nu/q''.

Top positive six-phase screens:

- `R_far_wake`: corr(I_Lambda2*, Nu) = `0.168`
- `R_global_control`: corr(I_Lambda2*, Nu) = `0.166`
- `R_near_wake`: corr(I_Lambda2*, Nu) = `-0.113`
