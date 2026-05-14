# V4b_3D run010 partial layer 015

This is a stopped-partial diagnostic based on the available `t = 2..5.935 s` run010 data.
It should be recomputed after run010 reaches `t = 10 s` before being treated as final.

## Inputs

- 48 phase-selected full-field snapshots from `data/001/run010_001_partial_48_phase_snapshot_selection.csv`
- Q/Lambda2/vorticity VTK export: `/home/hexmachina/of_runs/V4b_3D_run010_varprops_cp_q_lambda2_partial48/vtk_processors`
- wall heat flux and decomposed outlet fields from `/home/hexmachina/of_runs/V4b_3D_run010_varprops_cp`

## Heat balance over selected phases

- `Q_wall_mean = 1.77061 W`
- `Q_air_mean = 1.77256 W`
- `closure_mean = +0.2605%`
- `Nu_wall_mean = 9.66997`
- `Nu_EB_mean = 9.68796`

## Correlation screen

| region | corr(I_Lambda2*, paired Nu) | corr(I_Q*, paired Nu) | n |
|---|---:|---:|---:|
| `R_far_wake` | -0.190 | -0.316 | 48 |
| `R_fin_junction` | -0.397 | -0.773 | 48 |
| `R_fin_sweep` | -0.019 | -0.413 | 48 |
| `R_global_control` | -0.664 | -0.732 | 48 |
| `R_near_wake` | -0.309 | -0.461 | 48 |
| `R_sep` | -0.512 | 0.270 | 48 |

Interpretation: this is a stronger screen than run008_015 because it uses 48 phases instead of six,
but it is still partial because the run was stopped at `t = 5.935 s`.
