# Re10_debug_serial

## Case role

First controlled diagnostic branch derived from the baseline `Re10` case.
This branch isolated solver startup by stripping away non-essential monitoring.

## Simplifications applied

- serial run only
- no MPI decomposition
- no `forceCoeffs`
- no `wallHeatFlux`
- no `solverInfo`
- short startup horizon from `t = 0`

## Outcome

The startup crash still occurred at the first time step after the solver completed
the `rho`, `U`, and `h` equations.

## Interpretation

- function objects were not the primary cause
- the failure was deeper than post-processing or monitoring setup
- this result justified moving the investigation toward the pressure and thermo path

## Repository note

This note preserves the diagnostic conclusion only.
The active repository no longer mirrors the full raw log tree for this historical debug case.
