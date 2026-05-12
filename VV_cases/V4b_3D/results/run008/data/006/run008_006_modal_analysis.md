# V4b_3D run008 POD/SPOD/DMD

Primary window: `2.0..10.0 s`, snapshots `401`, midspan points `13524`.
POD sets: `U`, `T`, and RMS-scaled joint `U+T`.

## Summary

| Metric | Value |
|---|---:|
| n_snapshots | 401.000000 |
| n_points | 13524.000000 |
| U_mode1_energy_pct | 40.696607 |
| U_mode2_energy_pct | 40.522935 |
| T_mode1_energy_pct | 39.703996 |
| T_mode2_energy_pct | 38.273113 |
| joint_mode1_energy_pct | 40.220773 |
| joint_mode2_energy_pct | 39.757562 |
| U_pair12_share_of_first8 | 0.874521 |
| T_pair12_share_of_first8 | 0.840013 |
| DMD_near_f_shed_hz | 3.357668 |
| DMD_near_2f_shed_hz | 6.569508 |
| joint_scale_U_rms | 0.066797 |
| joint_scale_T_rms | 2.707150 |

## Strongest POD-signal correlations

| POD set | mode | signal | corr |
|---|---:|---|---:|
| T | 1 | Cl | -0.9865 |
| U+T | 1 | Cl | -0.9781 |
| U | 1 | Cd | -0.8503 |
| U+T | 1 | Cd | -0.8500 |
| T | 1 | Cd | -0.8097 |
| U | 2 | Cl | -0.7928 |
| T | 5 | Q_wall | -0.6754 |
| U+T | 5 | Q_wall | -0.6230 |

## Interpretation

- U POD mode 1/2 carry `40.70%` and `40.52%`; their paired phase portrait should be inspected as the shedding-pair candidate.
- T POD is more concentrated: mode 1/2 carry `39.70%` and `38.27%`.
- DMD finds sanity-check frequencies near `3.358 Hz` and `6.570 Hz`.
- EPOD maps are regression fields conditioned on Cl, Q_wall, and Nu_tube; SPOD-like maps are single-frequency coherent amplitudes at f_shed and 2*f_shed.

## Figures

- `../../figures/006/run008_006_pod_energy.png`
- `../../figures/006/run008_006_pod_phase_portraits.png`
- `../../figures/006/run008_006_pod_mode_maps.png`
- `../../figures/006/run008_006_pod_signal_correlations.png`
- `../../figures/006/run008_006_epod_spod_maps.png`
- `../../figures/006/run008_006_dmd_sanity_modes.png`
