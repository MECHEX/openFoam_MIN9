# V4b_3D run010 layer 017

Lag scan with cyclic-shift surrogates using the currently available incomplete run010 data.

## Inputs

- time window: `2.000..7.520 s`
- uniform vortex/heat grid: `277` samples at `dt = 0.020 s`
- lag range: `+-T_shed = +-0.3080 s`
- cyclic-shift surrogates: `1000`
- region intensities computed from decomposed OpenFOAM `Q` and `Lambda2` fields

## Heat balance on the analysis grid

- `Q_wall_mean = 1.76956 W`
- `Q_air_mean = 1.7676 W`
- `closure_mean = +0.4789%`
- `Nu_wall_mean = 9.65838`
- `Nu_EB_mean = 9.65495`

## I_Lambda2* -> Nu hypothesis pairs

| pair | rho_star | tau_star_s | tau_over_T_shed | surrogate_p95_absrho | surrogate_p99_absrho | empirical_p | tau_phase_s | tau_conv_s_assumed | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R_sep -> Nu_tube_wall | -0.514 | 0.16 | 0.5195 | 0.3904 | 0.3965 | 0.000999 | 0.05682 | 0.03557 | significant but lag > T_shed/2 |
| R_near_wake -> Nu_tube_wall | 0.8394 | -0.08 | -0.2597 | 0.6887 | 0.6927 | 0.000999 | 0.1114 | 0.07115 | significant but wrong-direction/zero-lag |
| R_fin_junction -> Nu_wall | -0.6248 | -0.14 | -0.4545 | 0.5314 | 0.601 | 0.000999 | 0.06835 | 0.02372 | significant but wrong-direction/zero-lag |
| R_fin_sweep -> Nu_fins_wall | 0.7453 | 0.22 | 0.7143 | 0.7204 | 0.7379 | 0.000999 | 0.1458 | 0.07905 | significant but lag > T_shed/2 |
| R_far_wake -> Nu_fins_wall | 0.2972 | 0.16 | 0.5195 | 0.2465 | 0.2565 | 0.000999 | -0.1094 | 0.1581 | significant but lag > T_shed/2 |

## Strongest associations across all screened signals

| pair | structure_signal | response_signal | rho_star | tau_star_s | empirical_p | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| R_near_wake -> Nu_tube_wall | I_Lambda2* | Nu | 0.8394 | -0.08 | 0.000999 | significant but wrong-direction/zero-lag |
| R_fin_sweep -> Nu_fins_wall | I_Q* | Nu | -0.7853 | 0.02 | 0.000999 | confirmed p<0.01 |
| R_fin_junction -> Nu_wall | I_Q* | Nu | -0.7804 | 0.16 | 0.000999 | significant but lag > T_shed/2 |
| R_fin_sweep -> Nu_fins_wall | I_Lambda2* | Nu | 0.7453 | 0.22 | 0.000999 | significant but lag > T_shed/2 |
| R_sep -> Nu_tube_wall | I_Q* | Nu | 0.744 | 0.28 | 0.000999 | significant but lag > T_shed/2 |
| R_fin_sweep -> Nu_fins_wall | I_Q* | Q | 0.6799 | -0.2 | 0.000999 | significant but wrong-direction/zero-lag |
| R_near_wake -> Nu_tube_wall | I_Q* | Nu | 0.6607 | 0.24 | 0.000999 | significant but lag > T_shed/2 |
| R_fin_junction -> Nu_wall | I_Lambda2* | Nu | -0.6248 | -0.14 | 0.000999 | significant but wrong-direction/zero-lag |
| R_fin_sweep -> Nu_fins_wall | I_Lambda2* | Q | 0.5723 | -0.08 | 0.000999 | significant but wrong-direction/zero-lag |
| R_far_wake -> Nu_fins_wall | I_Q* | Nu | -0.5432 | 0.28 | 0.000999 | significant but lag > T_shed/2 |
| R_sep -> Nu_tube_wall | I_Lambda2* | Nu | -0.514 | 0.16 | 0.000999 | significant but lag > T_shed/2 |
| R_far_wake -> Nu_fins_wall | I_Q* | Q | -0.4913 | -0.16 | 0.000999 | significant but wrong-direction/zero-lag |

## Interpretation

This is a stronger diagnostic than layer 016 because it uses a uniform time series instead of 48 phase-selected samples.
A positive `tau_star_s` means that the regional structure metric leads the heat response.
Pairs marked as confirmed pass the cyclic-shift surrogate threshold and have a positive lag within the expected convection-time range.
Because run010 is still incomplete, repeat this layer after the solver reaches `t = 10 s` before using it as a final paper-grade claim.
