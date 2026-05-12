# V4b_3D run004 - planned outlet-sensitivity setup

## Status

Prepared only. This run is intended as the first `V4b_3D` outlet-sensitivity check with a longer downstream domain than the current baseline `Lout = 5D`.

## Planned Setup

| Parameter | Value |
|---|---|
| Parent reference | `run003` |
| Purpose | isolate outlet-length influence on wake, `St`, `Cd`, `dp`, and `T_out` |
| Re | 200 |
| Mesh family | medium / lvl-2, same family as `run001` and `run003` |
| Lin/D | 2.0 |
| Lout/D | 8.0 by default in the prep script |
| Lout [mm] | 96.00 |
| Lx [mm] | 147.71 |
| Solver | `buoyantBoussinesqPimpleFoam` |
| Runtime goal | same order as `run003`, but only after fresh remeshing |

## Comparison Target

Primary comparison is against `run003`, which used:

- `Re = 200`
- medium / lvl-2 mesh
- `Lin = 2D`
- `Lout = 5D`
- periodic shedding with `St = 0.1484`

The acceptance question for `run004` is not whether the flow becomes periodic, because that is already established. The question is how much the shorter baseline outlet affected:

- shedding frequency / `St`
- `Cd_mean`
- `Cl_rms`
- `pressure_drop`
- `T_out`
- `Nu_EB`

## Notes

- The preparation script is stored in `VV_cases/V4b_3D/_code/prepare_run004_re200_longer_lout.sh`.
- The script defaults to `Lout = 8D`, but it also supports `LOUT_D=10` if a stronger outlet-sensitivity check is needed.
- Because geometry changes, the mesh must be rebuilt before running the solver.
