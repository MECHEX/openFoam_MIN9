# 003_data_heated_channel_solver_check

## Purpose

Diagnostic recovery run for V2 thermal verification after the cylinder case produced a non-physical temperature field.

This run deliberately removes the snappy cylinder mesh from the problem:

- geometry: 2D plane channel from `blockMesh`
- thermal problem: uniform wall temperature on both walls
- solver architecture: `buoyantBoussinesqPimpleFoam` with `g = 0`
- scalar convection check: `div(phi,T) Gauss vanLeer`
- reference target: fully developed plane-channel UWT `Nu ~= 7.541`
- default diagnostic Re is `Re_Dh = 100` to keep a finite outlet wall-bulk temperature difference

## Critique driving this run

- The current `Re10_long100s` cylinder result has a non-physical `T` field and must not be used as a validation result.
- The cylinder result mixes at least three issues: scalar boundedness, `Nu` extraction, and snappy wall-normal mesh quality.
- This channel check isolates the solver/scheme/extraction path before investing in a structured O-grid cylinder mesh.

## Simulation matrix

| simulation | Re_Dh | target | status |
|---|---:|---:|---|
| plane_channel_Re100_UWT | 100 | Nu ~= 7.541 | analyzed to t=40.001 s |

## Result

- The diagnostic channel field stayed bounded: `T_min = 293.1744 K`, `T_max = 303.1500 K`, with `0.00%` cells below inlet temperature and `0.00%` cells above wall temperature.
- Local station comparison at `x/D_h = 12.083`: `Nu = 7.5643` vs analytic UWT `Nu = 7.5410`, error `+0.31%`.
- The outlet itself is thermally saturated (`T_w - T_bulk ~= 0`), so outlet-only Nu is intentionally not used for the comparison.
- The profile and table are stored in `summary.md`, `summary.csv`, `Nu_profile.csv`, and `plots/V2_channel_Re100_Nu_profile.png`.

## Planned interpretation

- Since `T` stays bounded and local downstream `Nu` matches the analytic value, the solver/scheme path is acceptable for the simple orthogonal benchmark and the cylinder problem should move to O-grid meshing.
- If `T` overshoots here too, the scalar transport setup is still wrong independently of the cylinder mesh.
- A preliminary `Re_Dh = 10` channel sanity run stayed bounded but saturated the outlet to `T_wall`, making outlet-local Nu ill-conditioned; the Nu diagnostic therefore uses `Re_Dh = 100`.
