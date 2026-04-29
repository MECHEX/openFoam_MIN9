# V4b_3D Run Log

| Run | Date | Re | Mesh | Status | Cd_mean | Cl_rms | St | T_out [K] | Nu_EB | Notes |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---|
| run001 | 2026-04-22 | 100 | medium/lvl-2 | STEADY | 4.00 | 0 | N/A | 313.281 | 7.054 | baseline Re=100; global Cd/Nu converged vs run002 |
| run002 | 2026-04-26 | 100 | lvl-3 | STEADY | 3.9974 | 0 | N/A | 313.306 | 6.955 | mesh sensitivity; Cd -0.07% and Nu_EB -1.4% vs run001 |
| run003 | 2026-04-29 | 200 | medium/lvl-2 | PERIODIC | 3.161 | 0.187 | 0.1484 | 305.26 | 7.476 | solver stopped at t=6.505/10.0 s; f_shed=3.125 Hz; Min9 label not found |

## run003 Note

For run003, the correct Strouhal number uses the canonical V4b tube diameter D = 12 mm:

`St = f D / U = 3.125 * 0.012 / 0.25267 = 0.1484`.

The earlier St=0.099 estimate should not be used for V4b_3D run003 because it used the wrong characteristic length.
