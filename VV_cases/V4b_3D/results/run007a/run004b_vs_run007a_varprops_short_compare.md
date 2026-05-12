# V4b_3D short variable-property comparison

`run007a` completed to `t = 2 s`. This is an early-window physics sensitivity check, not the final production averaging window.

| Run | model | window | Cd_mean | Cl_mean | Cl_rms | f_shed | St | T_out | Nu_EB |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| run004b | Boussinesq_const | t = 0.5..2 s | 3.361209 | 2.510763 | 0.176698 | 3.2538 | 0.15453 | 305.615 +/- 0.974 | 7.7331 +/- 0.6558 |
| run007a | incompressiblePerfectGas_sutherland | t = 0.5..2 s | 3.473619 | 2.522958 | 0.178979 | 3.2441 | 0.15407 | 308.934 +/- 0.990 | 10.2249 +/- 0.7272 |

Differences for `run007a` versus matched `run004b`:

| Quantity | Difference |
|---|---:|
| Cd_mean | +3.34% |
| Cl_rms | +1.29% |
| St | -0.30% |
| T_out | +3.319 K |
| Q_total | +26.57% |
| Nu_EB | +32.22% |

Interpretation: the vortex-shedding regime is nearly unchanged, but variable air properties raise drag and heat-transfer metrics in the short matched window. A full `t = 3..6 s` variable-property run is needed before treating the magnitude as final.
