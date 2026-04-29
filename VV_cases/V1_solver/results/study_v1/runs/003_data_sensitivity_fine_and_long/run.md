# V1 run 003 — sensitivity study: fine mesh and long domain

## Purpose

Test whether the β=0.50 onset bracket Re_crit ∈ (130, 135) determined in run002 changes when:
- **fine mesh** is used (~123k cells vs ~44k medium), and
- **long domain** (L_out=40D vs 20D) is used.

All 4 cases target β=0.50, Re=130 or Re=135 (the two sides of the run002 onset bracket).

Reference: Sahin & Owens (2004), Re_crit=124.09, St_crit=0.3393 for β=0.50.

## Cases planned

| case | mesh | downstream_D | Re | purpose |
|---|---|---:|---:|---|
| b050_fine_Re130 | fine (~123k) | 20D | 130 | fine-mesh lower bound |
| b050_fine_Re135 | fine (~123k) | 20D | 135 | fine-mesh upper bound |
| b050_long_Re130 | medium, 40D | 40D | 130 | long-domain lower bound |
| b050_long_Re135 | medium, 40D | 40D | 135 | long-domain upper bound |

## Execution status

| case | ran | t_reached [s] | t_end [s] | notes |
|---|---|---:|---:|---|
| b050_fine_Re130 | **yes** | 5.1 | 15.0 | stopped early (34% complete); STEADY result |
| b050_fine_Re135 | no | — | 15.0 | setup only, solver never started |
| b050_long_Re130 | no | — | 15.0 | setup only, solver never started |
| b050_long_Re135 | no | — | 15.0 | setup only, solver never started |

## Result: b050_fine_Re130 (only completed case)

- **Regime: STEADY** (Cl_rms=0.0013, noise-level oscillation)
- Cd_mean = 2.833 (averaged over t=3–5.1s)
- Cl_rms = 0.0013 (effectively zero; no shedding detected)
- Mesh: 123,502 cells; max non-ortho=61.5°; max skewness=0.36
- Simulation stopped at t=5.1s (endTime=15s); shedding at St≈0.34 would give T≈0.32s → ~16 periods completed, sufficient to assess regime

## Key finding

At Re=130 with fine mesh, the flow is **STEADY** — same result as the medium mesh at Re=120–140 in run001. The run002 bracket onset (Re=130 periodic with medium mesh in bracket study) may be near the mesh-dependent onset boundary. The 3 remaining cases (fine Re135, long Re130, long Re135) were not run; the study is **INCOMPLETE**.

## Open items

- Run b050_fine_Re135 to confirm upper bound with fine mesh
- Run b050_long_Re130 and b050_long_Re135 for domain sensitivity
- If b050_fine_Re135 is also STEADY → Re_crit(fine) > 135, which would shift the bracket above run002 estimate

## External data location

`C:\openfoam-case\VV_cases\V1_solver_run003\`
