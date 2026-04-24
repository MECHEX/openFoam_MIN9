# 001_data_v2a_level_a_unconfined_debug

## Purpose

First V2a stabilization campaign for the unconfined heated-cylinder benchmark.
This run records the early debug branch that was used to diagnose startup failures
before the accepted Boussinesq architecture was adopted.

## Scope

- one run containing the baseline `Re10` case and two targeted debug branches
- focus on solver startup and equation-path isolation
- no literature-grade `Nu` extraction yet

## Interpretation

This run should be read as a compact debug archive, not as the final accepted
production dataset for V2a.

The canonical accepted study description lives in:

- `VV_cases/V2_thermal/doc/V2_thermal.md`

## Simulation matrix

| case | role | status | key outcome |
|---|---|---|---|
| `Re10` | baseline input case | input-only | original baseline prepared, no compact output record stored here |
| `Re10_debug_serial` | serial diagnostic without function objects | completed | crash remained after removing function objects |
| `Re10_debug_serial_nolayers` | serial diagnostic without layer extrusion | completed | crash remained after removing layers |

## Main conclusion from run 001

- the original compressible startup path was too fragile for this benchmark
- removing function objects did not remove the crash
- removing boundary-layer extrusion did not remove the crash
- this run therefore served to justify the later solver-architecture change

## Next step

Keep this run as historical debug evidence and continue the active V2a workflow
from the accepted Boussinesq-based architecture described in the canonical study doc.
