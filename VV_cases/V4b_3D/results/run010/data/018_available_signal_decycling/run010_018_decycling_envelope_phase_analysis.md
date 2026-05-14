# V4b_3D run010 layer 018

Decycling, envelope-correlation, and harmonic phase-consistency tests on layer-017 uniform signals.

## Method

- `raw`: direct signal after linear detrending and z-score.
- `decycled_residual`: least-squares removal of `f_shed` and `2*f_shed` from both structure and heat signals, then lag scan of residuals.
- `envelope`: analytic-signal envelope lag scan, testing cycle-by-cycle amplitude modulation.
- cyclic-shift surrogates: `1000` per pair/method.
- positive lag means structure signal leads heat response.
- `rho_pos_star` tracks the strongest positive correlation; `rho_abs_star` tracks the strongest signed relation by absolute magnitude.

## I_Lambda2* -> Nu, all methods

| pair | method | rho_abs_star | tau_abs_star_s | rho_pos_star | tau_pos_star_s | sur_pos_p95 | phase_2f_minus_2phase_f_wrapped_rad | tau_phase_f_s | tau_phase_2f_s | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R_sep -> Nu_tube_wall | raw | -0.529 | 0.16 | 0.2767 | -0.04 | 0.2091 | -0.8273 | 0.05568 | 0.07596 | only signed/periodic coupling |
| R_sep -> Nu_tube_wall | decycled_residual | -0.5535 | 0.16 | 0.4002 | 0.28 | 0.3397 | -1.064 | 0.1054 | -0.02253 | only signed/periodic coupling |
| R_sep -> Nu_tube_wall | envelope | -0.2522 | -0.06 | 0.2409 | 0.02 | 0.2796 | -2.535 | -0.07523 | -0.0131 | not significant after test |
| R_near_wake -> Nu_tube_wall | raw | 0.8464 | -0.08 | 0.8464 | -0.08 | 0.7048 | 1.586 | 0.1115 | 0.07264 | only signed/periodic coupling |
| R_near_wake -> Nu_tube_wall | decycled_residual | 0.7309 | -0.08 | 0.7309 | -0.08 | 0.4389 | 2.764 | 0.105 | 0.03723 | only signed/periodic coupling |
| R_near_wake -> Nu_tube_wall | envelope | -0.7664 | -0.18 | 0.615 | -0.26 | 0.5641 | -2.998 | 0.02835 | -0.05218 | only signed/periodic coupling |
| R_fin_junction -> Nu_wall | raw | -0.6381 | -0.14 | 0.6361 | -0.04 | 0.4696 | 0.714 | 0.06755 | 0.05005 | only signed/periodic coupling |
| R_fin_junction -> Nu_wall | decycled_residual | -0.6045 | 0.16 | 0.5722 | 0.28 | 0.3128 | -0.6663 | 0.06293 | -0.07474 | only signed/periodic coupling |
| R_fin_junction -> Nu_wall | envelope | 0.6525 | 0.3 | 0.6525 | 0.3 | 0.5269 | -0.07921 | 0.002345 | 0.004286 | only signed/periodic coupling |
| R_fin_sweep -> Nu_fins_wall | raw | 0.7753 | 0.22 | 0.7753 | 0.22 | 0.7551 | 0.4964 | 0.1122 | -0.05397 | only signed/periodic coupling |
| R_fin_sweep -> Nu_fins_wall | decycled_residual | 0.7009 | -0.24 | 0.7009 | -0.24 | 0.465 | -2.31 | 0.1389 | 0.04151 | only signed/periodic coupling |
| R_fin_sweep -> Nu_fins_wall | envelope | 0.6798 | -0.08 | 0.6798 | -0.08 | 0.6442 | -0.8677 | 0.05296 | 0.07423 | only signed/periodic coupling |
| R_far_wake -> Nu_fins_wall | raw | 0.3064 | 0.16 | 0.3064 | 0.16 | 0.2515 | 1.95 | -0.11 | -0.003744 | only signed/periodic coupling |
| R_far_wake -> Nu_fins_wall | decycled_residual | -0.3153 | 0.28 | 0.2745 | 0.16 | 0.1751 | -1.683 | -0.1036 | -0.06239 | only signed/periodic coupling |
| R_far_wake -> Nu_fins_wall | envelope | 0.2201 | 0.18 | 0.2201 | 0.18 | 0.2402 | -1.391 | 0.1095 | -0.01036 | not significant after test |

## Strongest envelope positive correlations

| pair | structure_signal | response_signal | rho_pos_star | tau_pos_star_s | sur_pos_p95 | class |
| --- | --- | --- | --- | --- | --- | --- |
| R_sep -> Nu_tube_wall | I_Q* | Nu | 0.7535 | -0.02 | 0.5125 | only signed/periodic coupling |
| R_fin_sweep -> Nu_fins_wall | I_Lambda2* | Nu | 0.6798 | -0.08 | 0.6442 | only signed/periodic coupling |
| R_fin_junction -> Nu_wall | I_Lambda2* | Nu | 0.6525 | 0.3 | 0.5269 | only signed/periodic coupling |
| R_fin_sweep -> Nu_fins_wall | I_Q* | Nu | 0.6208 | 0.2 | 0.5483 | only signed/periodic coupling |
| R_near_wake -> Nu_tube_wall | I_Lambda2* | Nu | 0.615 | -0.26 | 0.5641 | only signed/periodic coupling |
| R_fin_junction -> Nu_wall | I_Q* | Nu | 0.5476 | 0.18 | 0.4857 | only signed/periodic coupling |
| R_near_wake -> Nu_tube_wall | I_Q* | Nu | 0.2836 | 0.26 | 0.158 | only signed/periodic coupling |
| R_sep -> Nu_tube_wall | I_Lambda2* | Nu | 0.2409 | 0.02 | 0.2796 | not significant after test |

## Strongest decycled residual signed relations

| pair | structure_signal | response_signal | rho_abs_star | tau_abs_star_s | rho_pos_star | tau_pos_star_s | sur_abs_p95 | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R_near_wake -> Nu_tube_wall | I_Lambda2* | Nu | 0.7309 | -0.08 | 0.7309 | -0.08 | 0.5856 | only signed/periodic coupling |
| R_fin_sweep -> Nu_fins_wall | I_Q* | Nu | -0.7273 | 0.18 | 0.518 | -0.02 | 0.5203 | only signed/periodic coupling |
| R_fin_sweep -> Nu_fins_wall | I_Lambda2* | Nu | 0.7009 | -0.24 | 0.7009 | -0.24 | 0.465 | only signed/periodic coupling |
| R_fin_junction -> Nu_wall | I_Q* | Nu | -0.6712 | 0.16 | 0.5186 | -0.1 | 0.4246 | only signed/periodic coupling |
| R_sep -> Nu_tube_wall | I_Q* | Nu | 0.6192 | -0.02 | 0.6192 | -0.02 | 0.4679 | only signed/periodic coupling |
| R_fin_junction -> Nu_wall | I_Lambda2* | Nu | -0.6045 | 0.16 | 0.5722 | 0.28 | 0.4786 | only signed/periodic coupling |
| R_sep -> Nu_tube_wall | I_Lambda2* | Nu | -0.5535 | 0.16 | 0.4002 | 0.28 | 0.4374 | only signed/periodic coupling |
| R_near_wake -> Nu_tube_wall | I_Q* | Nu | 0.4284 | -0.06 | 0.4284 | -0.06 | 0.447 | not significant after test |

## Interpretation

If decycled residual correlations collapse, the layer-017 coupling is mostly common shedding rhythm.
If envelope correlations remain positive and significant at positive lag, stronger cycles of vortex activity precede stronger heat-transfer cycles.
If `phase_2f_minus_2phase_f_wrapped_rad` is near zero and `tau_phase_f_s` is close to `tau_phase_2f_s`, a true time-delay interpretation is plausible.
Large phase mismatch means mode-specific phase locking rather than one convective delay.
