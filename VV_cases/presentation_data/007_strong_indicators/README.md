# 007_strong_indicators

Publication/defense-oriented indicator pipeline.

Status:

- `00_fullNu3D_xt`: completed; builds time-resolved 1 mm strip `Nu_3D(x,t)` from full hot-surface `wallHeatFlux` and full y-z plane `T_bulk(x,t)`.
- `00_1_wall_local_Nu`: completed; implements layer 0.1 as local wall-polygon `Nu_wall(s,t)` on tube and fins before strip averaging.
- `01_full3D_Tbulk_Nu_1mm`: started first; builds the stronger thermal dependent variable for 1 mm x-strips.
- `02_frequency_coherence_phase`: completed as an exploratory frequency/phase stage using `Cl(t)` and selected local `Nu_3D(x,t)` strips.
- `03_EPOD_velocity_to_Nu`: completed as a midspan-velocity POD / local full-surface `Nu_3D(x,t)` coupling analysis.

Planned next folders:

- `04_scalar_indicator_table`: compact scalar indicators per Re/case.
