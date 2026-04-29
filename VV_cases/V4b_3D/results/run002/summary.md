# V4b_3D run002 — summary

## Setup

| Parameter | Value |
|---|---|
| Date | 2026-04-26 |
| Re | 100 |
| Ri | 1.26 (mixed convection) |
| Mesh | snappyHexMesh level-3 |
| Cells | 1,840,178 |
| Lin/D | 2.0 |
| Lout/D | 5.0 |
| bg cell xy | 1.0 mm |
| Refine tube | level-3 |
| BL layers tube | 0 (no explicit BL; y+≈0.5) |
| BL layers fin | 6, first layer 30 µm |
| Solver | buoyantBoussinesqPimpleFoam |
| t_end | 2.9 s |
| t_avg_start | 2.0 s |
| Wall time | ~45 h (8 cores; swapping episodes) |

## Mesh quality

| Metric | Value |
|---|---|
| Max non-orthogonality | 57.11° |
| Avg non-orthogonality | 4.51° |
| Max skewness | 1.057 |
| Max aspect ratio | 33.4 |
| Small-determinant cells | 0 |
| Concave cells | 34,825 |

## Flow results

| Quantity | Value | Notes |
|---|---|---|
| Regime | **STEADY** | No vortex shedding at Re=100 |
| Cd_mean | 3.9974 | High due to β=0.375 blockage |
| Cl_rms | 0 | — |
| St | N/A | Steady flow |
| dp_mean | N/A | — |
| T_out | 313.306 K | |
| T_min | 293.15 K | No T undershoot (unlike run001) |
| T_max | 343.15 K | |

## Heat transfer results

| Method | Nu_tube | Nu_fin_zmin | Nu_fin_zmax | Nu_total |
|---|---|---|---|---|
| **EB+LMTD** (preferred) | — | — | — | **6.955** |
| snGrad | 4.06 | 4.90 | 4.90 | 4.28 |

- Q_total = 1.1792 W
- A_tube_meshed = 4.84×10⁻⁴ m² (+7% vs analytical π·D·Lz — snappy lvl-3 artifact; does not affect Nu_EB)
- snGrad tube scatter: IQR [2661–29141 K/m], 9.2% outliers excluded (no BL → unreliable for tube)
- snGrad fin scatter: IQR [6879–22033 K/m], 2.0% outliers excluded (reliable)

## Comparison vs run001 (mesh convergence)

| Quantity | run001 | run002 | Δ |
|---|---|---|---|
| Cells | 337,184 | 1,840,178 | +5.5× |
| Nu_EB | 7.054 | 6.955 | **−1.4%** → CONVERGED |
| Cd_mean | 4.000 | 3.997 | **−0.07%** → CONVERGED |
| T_out | 313.281 K | 313.306 K | +0.025 K |

## Wake structure

- Near-wake (1D–2D downstream): Ux 10–20% sensitivity vs run001 — requires lvl-3 mesh for local accuracy
- Far-wake: <1% difference → converged
- No wake shedding detected

## Open items

- Circumferential Nu profile on cylinder (circ_Nu_profile_ok = no)
- A_tube_meshed artefact: check whether snappy lvl-3 overestimates tube area and whether patchAverage is consistent
- Re=200 not yet run

## External data

`C:\openfoam-case\VV_cases\V4b_3D_run002\` (Windows)
`/home/kik/of_runs/V4b_3D_run002/` (WSL, full field data)
