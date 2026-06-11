# 00_1_wall_local_Nu

This folder implements layer `0.1`: local instantaneous wall Nusselt number on hot tube and fin surfaces.

Definition:

`Nu_wall_local(s,t) = q''_w(s,t) * D_ref / [k_air * (T_wall(s,t) - T_bulk_yz(x_s,t))]`

where:

- `s` is a hot-wall polygon centroid on tube or fins.
- `q''_w` comes directly from OpenFOAM `wallHeatFlux` on the hot surfaces.
- `T_wall(s,t)` comes from the wall-surface `T` field.
- `T_bulk_yz(x_s,t)` is interpolated from full y-z cut-plane mass-flow bulk temperature.
- `D_ref = 0.012 m`, `k_air = 0.028 W/(m K)`.

What this improves compared with earlier stage `00_fullNu3D_xt`:

- Stage 00 produced one area-integrated `Nu_3D(x,t)` per 1 mm strip.
- This stage produces local wall-polygon `Nu_wall_local(s,t)` before strip averaging.
- Strip values here are area-weighted summaries of local wall Nu, not the starting point.

Current sampling:

- full local rows written: `1823640`
- available full-field times per Re: `{100.0: 26, 150.0: 26, 160.0: 26, 175.0: 26, 200.0: 26}`

Outputs:

- `wall_local_Nu_time_resolved.csv.gz`: full local wall-polygon dataset.
- `wall_local_Nu_strip_stats.csv`: area-weighted strip/patch/time statistics.
- `wall_local_Nu_strip_time_averaged.csv`: time-averaged strip profiles.
- `fig01_wall_local_Nu_profiles_by_patch`: all/tube/fins local-Nu profiles.
- `fig02_wall_local_Nu_temporal_amplitude`: temporal modulation of local wall Nu.

Important limitation:

The wall field is local on the available hot-surface mesh, but temporal resolution is still limited by available full volume fields: currently 26 snapshots per Re over 8-10 s. More snapshots are needed for publication-grade coherence/SPOD.
