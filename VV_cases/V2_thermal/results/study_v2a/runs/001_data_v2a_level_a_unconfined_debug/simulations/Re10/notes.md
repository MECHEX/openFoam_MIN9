# Re10

## Case role

Baseline V2a input case for the unconfined heated-cylinder benchmark.
In this compact repository layout it is preserved mainly as the starting point
for the later debug branches.

## Physical setup

- benchmark type: forced convection around a heated cylinder
- Reynolds number: `Re = 10`
- inlet velocity: `U_in = 0.012632 m/s`
- inlet temperature: `T_in = 293.15 K`
- cylinder temperature: `T_w = 303.15 K`
- Prandtl number: `Pr = 0.713`

## Domain

- cylinder diameter: `D = 0.012 m`
- upstream length: `15D`
- downstream length: `30D`
- domain height: `20D`

## Intended outputs

- mean Nusselt number `Nu`
- drag coefficient `Cd` for monitoring
- flow-regime information only if needed later

## Repository note

This compact note stores the accepted baseline description only.
Detailed OpenFOAM raw artifacts are intentionally not mirrored inside the active repository.
