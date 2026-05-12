# V4b_3D run008 phase-averaging physical story

Phase is defined from the Hilbert analytic signal of `Cl` from layer 002. The production window `t=2..10 s` is binned into 16 shedding-phase bins.

## Key phase events

| event | phase bin | phase [deg] | value | lag from max abs(Cl) [deg] | lag [s] |
|---|---:|---:|---:|---:|---:|
| Cl_max | 12 | 281.2 | 2.58578 | +45.0 | +0.0381 |
| Cl_min | 10 | 236.2 | 2.42324 | +0.0 | +0.0000 |
| Cl_zero_down | 0 | 11.2 | 2.51482 | +135.0 | +0.1144 |
| Cl_zero_up | 3 | 78.8 | 2.51673 | -157.5 | -0.1334 |
| Q_wall_max | 13 | 303.8 | 1.4816 | +67.5 | +0.0572 |
| Q_tube_max | 10 | 236.2 | 0.362043 | +0.0 | +0.0000 |
| Q_fins_max | 13 | 303.8 | 1.11961 | +67.5 | +0.0572 |
| Nu_tube_wall_max | 5 | 123.7 | 8.45856 | -112.5 | -0.0953 |
| Nu_fins_wall_max | 5 | 123.7 | 7.66007 | -112.5 | -0.0953 |
| Nu_EB_max | 5 | 123.7 | 7.95401 | -112.5 | -0.0953 |

## Heat-transfer timing

- Reference phase for maximum `|Cl|`: `236.2 deg`.
- `Q_wall` maximum phase: `303.8 deg`, lag `+67.5 deg` / `+0.0572 s`.
- `Q_tube` maximum lag from maximum `|Cl|`: `+0.0 deg` / `+0.0000 s`.
- `Q_fins` maximum lag from maximum `|Cl|`: `+67.5 deg` / `+0.0572 s`.

Interpretation: maxima of integrated heat uptake are phase-locked to the shedding cycle, but they should be read relative to the local Nu maps because tube and fins redistribute heat-transfer intensity differently around the cycle.

## Outputs

- `run008_009_phase_global_cycle.csv`
- `run008_009_phase_events.csv`
- `run008_009_fin_phase_profiles.csv`
- `run008_009_midspan_phase_summary.csv`
- `run008_009_phase_arrays.npz`

## Figures

- `../../figures/009/run008_009_phase_global_cycle.png`
- `../../figures/009/run008_009_tube_nu_phase_grid.png`
- `../../figures/009/run008_009_fin_nu_phase_map.png`
- `../../figures/009/run008_009_midspan_wake_speed_phase_grid.png`
- `../../figures/009/run008_009_midspan_temperature_phase_grid.png`
- `../../figures/009/run008_009_phase_story_key_frames.png`
