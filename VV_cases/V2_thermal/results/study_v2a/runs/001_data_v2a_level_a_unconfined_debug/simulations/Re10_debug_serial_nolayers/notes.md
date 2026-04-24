# Re10_debug_serial_nolayers

## Case role

Second controlled diagnostic branch derived from `Re10_debug_serial`.
Its purpose was to test whether the startup failure was caused by layer extrusion
or very small near-wall cells.

## Simplifications applied

- serial run only
- no function objects
- regenerated mesh with `addLayers false`
- short startup horizon only

## Outcome

The no-layer mesh generated successfully, but the solver still failed at the first
time step after completing the `rho`, `U`, and `h` equations.

## Interpretation

- layer extrusion was not the primary cause
- the startup failure survived both:
  - removal of function objects
  - removal of layer extrusion
- the remaining suspect was the pressure or thermo startup path itself

## Repository note

This compact note stores the accepted conclusion from the no-layer diagnostic branch.
