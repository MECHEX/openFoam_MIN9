# 002_data_sahin_owens_poiseuille_verification

## run scope

# V1 run 002 scope

## Run identifier

- `002_data_sahin_owens_poiseuille_verification`

## Purpose

This run is the second V1 verification campaign.
Its goal is a direct comparison of the confined-cylinder solver response against
Sahin and Owens (2004) using a Poiseuille inlet definition consistent with the paper.

## Why this is a new run

Run `001_data_beta05_initial_verification` used the earlier verification setup.
This new campaign changes the methodological basis of the inlet/reference definition,
so it should be tracked as a separate run and not mixed into run 001.

## Verification targets

- direct literature comparison at `beta = 0.30`
- direct literature comparison at `beta = 0.50`
- project-relevant reference geometry at `beta = 0.375`

## Working assumptions

- `Re = U_max * D / nu`
- `St = f * D / U_max`
- inlet profile: Poiseuille
- solver family: `pimpleFoam`
- this remains a V1 solver-verification task, not a thermal study

## Expected outputs

- simulation-level `input.md` and `output.md` for every case
- run-level summary table for all `beta` and `Re` points
- explicit comparison table against Sahin and Owens
- article-quality figure(s) for `St` versus literature

## Planned simulation groups

- `beta = 0.30`: points around `Re_crit = 94.56`
- `beta = 0.375`: points around interpolated transition for the project geometry
- `beta = 0.50`: points around `Re_crit = 124.09`

## Status

- run created
- documentation scaffold prepared
- simulations not launched yet

## case matrix

# V1 run 002 case matrix

- run name: 002_data_sahin_owens_poiseuille_verification
- working run root: `C:\openfoam-case\VV_cases\V1_solver_run002`

| case | beta | Re | H [mm] | Re_crit_ref | St_ref | purpose |
|---|---:|---:|---:|---:|---:|---|
| b030_medium_Re080 | 0.300 | 80 | 40.00 | 94.56 | 0.209 | beta=0.30 below Re_crit |
| b030_medium_Re090 | 0.300 | 90 | 40.00 | 94.56 | 0.209 | beta=0.30 steady bracket lower |
| b030_medium_Re095 | 0.300 | 95 | 40.00 | 94.56 | 0.209 | beta=0.30 near Re_crit |
| b030_medium_Re100 | 0.300 | 100 | 40.00 | 94.56 | 0.209 | beta=0.30 above Re_crit |
| b030_medium_Re120 | 0.300 | 120 | 40.00 | 94.56 | 0.209 | beta=0.30 well above Re_crit |
| b0375_medium_Re090 | 0.375 | 90 | 32.00 | 105.63 | 0.2579 | beta=0.375 below interpolated Re_crit |
| b0375_medium_Re105 | 0.375 | 105 | 32.00 | 105.63 | 0.2579 | beta=0.375 steady bracket lower |
| b0375_medium_Re110 | 0.375 | 110 | 32.00 | 105.63 | 0.2579 | beta=0.375 near interpolated Re_crit |
| b0375_medium_Re120 | 0.375 | 120 | 32.00 | 105.63 | 0.2579 | beta=0.375 above interpolated Re_crit |
| b0375_medium_Re135 | 0.375 | 135 | 32.00 | 105.63 | 0.2579 | beta=0.375 well above interpolated Re_crit |
| b050_medium_Re100 | 0.500 | 100 | 24.00 | 124.09 | 0.3393 | beta=0.50 below Re_crit |
| b050_medium_Re120 | 0.500 | 120 | 24.00 | 124.09 | 0.3393 | beta=0.50 steady |
| b050_medium_Re125 | 0.500 | 125 | 24.00 | 124.09 | 0.3393 | beta=0.50 steady onset test 15s |
| b050_medium_Re130 | 0.500 | 130 | 24.00 | 124.09 | 0.3393 | beta=0.50 steady onset test |
| b050_medium_Re135 | 0.500 | 135 | 24.00 | 124.09 | 0.3393 | beta=0.50 bracket midpoint test 15s |
| b050_medium_Re140 | 0.500 | 140 | 24.00 | 124.09 | 0.3393 | beta=0.50 periodic |
| b050_medium_Re150 | 0.500 | 150 | 24.00 | 124.09 | 0.3393 | beta=0.50 well above Re_crit |
| b060_medium_Re120 | 0.600 | 120 | 20.00 | 117.19 | 0.4073 | beta=0.60 steady onset test 15s |
| b060_medium_Re125 | 0.600 | 125 | 20.00 | 117.19 | 0.4073 | beta=0.60 bracket lower test 15s |
| b060_medium_Re135 | 0.600 | 135 | 20.00 | 117.19 | 0.4073 | beta=0.60 periodic above Re_crit |

## comparison plan

# Comparison plan for run 002

## Reference

- Sahin, M. and Owens, R.G. (2004), *Physics of Fluids* 16, 1305-1320

## Comparison strategy

We will separate the comparison into three bands:

1. `beta = 0.30`
   Direct literature verification against the paper values.
2. `beta = 0.375`
   Project geometry reference point.
   This point is not a direct table match and will be treated as an interpolated or project-specific comparison.
3. `beta = 0.50`
   Direct literature verification against the paper values.

## Primary quantities

- flow regime: steady / periodic
- shedding frequency `f`
- Strouhal number `St`
- mean drag coefficient `Cd_mean`

## Secondary checks

- sensitivity to mesh level if needed
- sensitivity to simulation horizon if the periodic state appears late

## Acceptance logic

- the direct literature points are `beta = 0.30` and `beta = 0.50`
- agreement should be judged first on the onset/absence of periodic shedding near the critical range
- then on `St`
- `beta = 0.375` is not a pass/fail literature point; it is the bridge to the project geometry

## Planned reporting

- run-level table with columns:
  - case
  - beta
  - Re
  - mesh
  - regime
  - `Cd_mean`
  - `f`
  - `St_sim`
  - `St_ref`
  - delta `%`
- one clean manuscript plot showing our `St` versus Sahin and Owens for the direct-comparison betas

## runtime locations

# Runtime locations

- working run root: `C:\openfoam-case\VV_cases\V1_solver_run002`
- archive run dir: `C:\Users\kik\My Drive\Politechnika Krakowska\Researches\Repositories\openFoam\VV_cases\V1_solver\results\study_v1\runs\002_data_sahin_owens_poiseuille_verification`
- study summary dir: `C:\Users\kik\My Drive\Politechnika Krakowska\Researches\Repositories\openFoam\VV_cases\V1_solver\results\study_v1\study_summary\002_data_sahin_owens_poiseuille_verification`
