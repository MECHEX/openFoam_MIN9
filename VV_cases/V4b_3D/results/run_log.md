# V4b_3D Run Log

| Run | Date | Re | Mesh | Status | Cd_mean | Cl_rms | St | T_out [K] | Nu_EB | Notes |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---|
| run001 | 2026-04-22 | 100 | medium/lvl-2 | STEADY | 4.00 | 0 | N/A | 313.281 | 7.054 | baseline Re=100; global Cd/Nu converged vs run002 |
| run002 | 2026-04-26 | 100 | lvl-3 | STEADY | 3.9974 | 0 | N/A | 313.306 | 6.955 | mesh sensitivity; Cd -0.07% and Nu_EB -1.4% vs run001 |
| run003 | 2026-04-29 | 200 | medium/lvl-2 | PERIODIC | 3.161 | 0.187 | 0.1484 | 305.26 | 7.476 | solver stopped at t=6.505/10.0 s; f_shed=3.125 Hz; Min9 label not found |
| run004b | 2026-05-06 | 200 | BL lvl-2 Lout=8D | PERIODIC | 3.361 | 0.184 | 0.1552 | 305.682 | 7.778 | controlled outlet candidate; completed to t=6 s; 8D differs from 5D but matches 16D |
| run004c | 2026-05-06 | 200 | BL lvl-2 Lout=16D | PERIODIC | 3.361 | 0.182 | 0.1546 | 305.720 | 7.803 | outlet check; 16D ~= 8D; outlet sensitivity closed and Lout=8D accepted |
| run005 | 2026-05-07 | 200 | BL lvl-2 Lin=4D | PERIODIC | 3.359 | 0.185 | 0.1552 | 305.680 | 7.776 | inlet check; Lin=4D ~= Lin=2D; inlet sensitivity closed and Lin=2D accepted |
| run006a | 2026-05-07 | 200 | BL lvl-2 maxCo=0.4 | PARTIAL | 3.362 | 0.190 | 0.1541 | 305.598 | 7.723 | stopped at t~2.616 s; partial 0.5..2.6 s check matches run004b closely; not final t=3..6 s proof |
| run006b | 2026-05-08 | 200 | BL lvl-2 maxCo=1.0 | SHORT | 3.361 | 0.177 | 0.1546 | 305.616 | 7.734 | completed to t=2 s; short maxCo=1.0 smoke test matches run004b closely; maxCo=0.8 remains production default |
| run007a | 2026-05-08 | 200 | BL lvl-2 varProps | SHORT | 3.474 | 0.179 | 0.1541 | 308.934 | 10.225 | completed to t=2 s; incompressiblePerfectGas+Sutherland vs run004b over 0.5..2 s: Cd +3.34%, St -0.30%, Nu +32.22%; extend to t=6 before final production conclusion |
| run007c | 2026-05-08 | 200 | BL lvl-2 Cp-scale const | SHORT | 3.361 | 0.177 | N/A | 305.594 | 7.731 | completed to t=2 s; eConst+Boussinesq with capacity 1005; force matches run004b; Q_air=1.462W, Q_wall=1.482W, wall-air closure +1.4%; Nu_wall_case=7.822; confirms apparent Nu jump is mainly Cv/Cp/k consistency |
| run008 | 2026-05-09 | 200 | BL lvl-2 production | ANALYZED | 3.361 | 0.176 | 0.1543 | 305.668 | 7.770 | completed to t=10 s on 20 ranks from run007c; ClockTime=50909s; production window t=2..10s; Q_air=1.471W Q_wall=1.481W closure +0.706%; POD modes 1+2 capture 80.29%; local tube/fin Nu maps and Cl-Nu coherence figures generated |

## run003 Note

For run003, the correct Strouhal number uses the canonical V4b tube diameter D = 12 mm:

`St = f D / U = 3.125 * 0.012 / 0.25267 = 0.1484`.

The earlier St=0.099 estimate should not be used for V4b_3D run003 because it used the wrong characteristic length.

## Domain-Sensitivity Decision

The accepted production-domain candidate after the completed domain checks is
`Lin=2D`, `Lout=8D`. `Lout=16D` matched `Lout=8D` for `Cd`, `St`, and `Nu_EB`,
and `Lin=4D` matched `Lin=2D` for the same metrics.
