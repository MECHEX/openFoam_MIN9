# V4b_3D short maxCo=1.0 smoke test

`run006b` completed to `t = 2 s`. This is a speed/safety smoke test, not the final production averaging window.

| Run | maxCo | window | Cd_mean | Cl_mean | Cl_rms | f_shed | St | T_out | Nu_EB |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| run004b | 0.8 | t = 0.5..2 s | 3.361209 | 2.510763 | 0.176698 | 3.2538 | 0.15453 | 305.615 +/- 0.974 | 7.7331 +/- 0.6558 |
| run006b | 1 | t = 0.5..2 s | 3.361220 | 2.510802 | 0.176971 | 3.2561 | 0.15464 | 305.616 +/- 0.975 | 7.7339 +/- 0.6562 |

Differences for `run006b` versus matched `run004b`:

| Quantity | Difference |
|---|---:|
| Cd_mean | +0.00% |
| Cl_rms | +0.15% |
| St | +0.07% |
| T_out | +0.001 K |
| Nu_EB | +0.01% |

Interpretation: `maxCo=1.0` completed cleanly and matches the `maxCo=0.8` reference extremely closely over the early common window. This supports stability/speed viability for short checks, but `maxCo=0.8` remains the more conservative production default.
