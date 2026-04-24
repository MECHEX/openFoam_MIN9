# 002_data_v2a_boussinesq_validation

## Purpose

First production-oriented V2a run built on the accepted Boussinesq architecture.
This run supersedes the earlier debug-only compressible branch.

## Accepted architecture

- solver: `buoyantBoussinesqPimpleFoam`
- gravity: `g = (0 0 0)`
- regime: pure forced convection
- physical model: incompressible Boussinesq transport

## Simulation matrix

| case | Re | regime | endTime [s] | role |
|---|---:|---|---:|---|
| Re10 | 10 | steady | 100.0 | first smoke-test |
| Re10_long100s | 10 | steady | 100.0 | planned |
| Re20 | 20 | steady | 100.0 | planned |
| Re40 | 40 | steady | 100.0 | planned |
| Re100 | 100 | unsteady | 25.0 | planned |
| Re200 | 200 | unsteady | 15.0 | planned |

## Next step

- run `Re10` first as the production smoke-test for run 002
- then continue with `Re20` and `Re40` before the unsteady cases
