# V4b_3D partial timestep sensitivity: maxCo=0.8 vs maxCo=0.4

`run006a` was intentionally stopped before the full target `t = 6 s`; therefore this is a partial check, not the final `t = 3..6 s` timestep-sensitivity result.

## Primary Available Window

| Run | maxCo | window | Cd_mean | Cl_mean | Cl_rms | f_shed | St | T_out | Nu_EB |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| run004b | 0.8 | t = 0.5..2.6 s | 3.362091 | 2.513970 | 0.190678 | 3.2459 | 0.15416 | 305.602 +/- 1.046 | 7.7252 +/- 0.7075 |
| run006a | 0.4 | t = 0.5..2.6 s | 3.362270 | 2.513552 | 0.190056 | 3.2436 | 0.15405 | 305.598 +/- 1.046 | 7.7226 +/- 0.7070 |

Differences for `run006a` versus matched `run004b`:

| Quantity | Difference |
|---|---:|
| Cd_mean | +0.01% |
| Cl_rms | -0.33% |
| St | -0.07% |
| T_out | -0.004 K |
| Nu_EB | -0.03% |

## All Windows

| Window | Cd diff | Cl_rms diff | St diff | T_out diff | Nu_EB diff |
|---|---:|---:|---:|---:|---:|
| t = 0.5..2.6 s | +0.01% | -0.33% | -0.07% | -0.004 K | -0.03% |
| t = 1..2.6 s | +0.00% | -0.33% | +0.02% | -0.004 K | -0.04% |
| t = 1.5..2.6 s | +0.00% | -0.22% | -0.04% | -0.004 K | -0.04% |

## Interpretation

The partial `maxCo=0.4` result tracks the `maxCo=0.8` reference very closely for force statistics, shedding frequency, and EB+LMTD heat transfer over the available common windows. Because the run was stopped before the intended `t = 3..6 s` averaging window, this should be reported as an indicative partial timestep check rather than a final timestep-independence proof.
