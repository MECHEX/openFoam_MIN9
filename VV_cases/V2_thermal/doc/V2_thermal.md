# V2 Thermal Verification

## Objective

V2 is the thermal verification track for forced convection around a heated circular cylinder.
The active sub-study is `V2a`, whose goal is to reproduce reference Nusselt numbers for
an unconfined heated cylinder under constant wall temperature conditions.

The current objective is two-stage:

1. stabilize the numerical architecture for the thermal solver
2. run the Reynolds-number matrix and compare `Nu` against the reference correlations and DNS data

## Reference literature

The current V2a reference set in the repository is:

- Lange et al. (1998), correlation used in `V2AStudy.py`
- Bharti et al. (2007), reference `Nu` values where available

The governing benchmark assumption is forced convection with:

- constant wall temperature
- constant properties
- `g = 0`

## Geometry

### Current V2a geometry

- cylinder diameter: `D = 12 mm`
- 2D span used for coefficient normalization: `Lz = 10 mm`
- cylinder center at `(0, 0)`
- quasi-unconfined domain intended for Level A validation

The active V2a document describes the accepted physical problem, not every earlier debug
case stored in the repository.

## Boundary conditions

### Thermal boundary conditions

- inlet temperature: `T_in = 293.15 K`
- cylinder temperature: constant wall temperature
- top and bottom boundaries: adiabatic
- outlet: advective/open behaviour for temperature

### Flow boundary conditions

- inlet: uniform velocity corresponding to the selected Reynolds number
- outlet: pressure reference at outlet
- cylinder: no-slip
- front/back: `empty`

### Gravity

- `g = (0 0 0)`

The V2a benchmark is therefore pure forced convection, even though the chosen solver
architecture can support buoyancy terms.

## Numerical setup

### Accepted solver architecture

The accepted architecture for V2a is now:

- solver: `buoyantBoussinesqPimpleFoam`

The previous `buoyantPimpleFoam` path is considered deprecated for V2a because it caused
structural startup problems for this forced-convection inlet/outlet configuration.

### Material model

The accepted property model is Boussinesq-style incompressible transport:

- `nu = 1.516e-5 m^2/s`
- `beta = 3.412e-3 K^-1`
- `TRef = 293.15 K`
- `Pr = 0.713`
- `Prt = 0.9`

### Active smoke-test settings

The latest successful smoke-test was performed with:

- `endTime = 0.02 s`
- fixed `deltaT`
- reduced function objects
- focus on startup stability rather than production statistics

These are smoke-test settings only. Production settings still need to be restored before
the full Reynolds-number campaign is launched.

## Mesh and mesh-independence study

### Current status

The mesh-independence study for V2a has not yet been formalized.
At the moment the work has focused on solver stabilization.

### Practical current mesh notes

- the mesh is generated with `blockMesh` and `snappyHexMesh`
- very fine near-wall cells made `GAMG` unattractive in the thermal solver tests
- one diagnostic variant without boundary-layer extrusion was tested during debugging

This no-layer diagnostic was useful for identifying that the original crash source was not
the layer addition itself.

## Convergence and monitored quantities

### Current monitored quantities

- pressure equation behaviour
- temperature equation behaviour
- continuity error
- Courant number
- later target quantities:
  - `Nu`
  - `Cd`
  - `Cl`
  - `St` only where relevant for flow regime classification

### Nusselt-number extraction

For the Boussinesq architecture, `wallHeatFlux` is no longer the preferred path.
The intended extraction route is:

- wall-normal temperature gradient on the cylinder surface
- area-averaged projection `grad(T) · n` over the `cylinder` patch
- `Nu = D * <grad(T)·n>_cylinder / (T_wall - T_inf)`

The earlier shortcut based on `mag(grad(T))` was rejected as non-physical because it
mixes tangential components into the wall heat-transfer metric.

This definition is now directly consistent with the reference papers:

- in [Bharti_2007.pdf](c:\Users\kik\My%20Drive\Politechnika%20Krakowska\Grants\2025_07_Miniatura_9_ver2\Realizacja\Art\Bharti_2007.pdf), Eq. (11)-(12) define local and surface-averaged Nusselt number from the wall heat-transfer coefficient / wall-normal thermal gradient for the cylinder surface
- in [Lange_1998.pdf](c:\Users\kik\My%20Drive\Politechnika%20Krakowska\Grants\2025_07_Miniatura_9_ver2\Realizacja\Art\Lange_1998.pdf), Sec. 2.2 defines the wall heat flux, heat-transfer coefficient, and the mean Nusselt number averaged over the whole cylinder perimeter

## Current case matrix

The currently planned V2a Reynolds-number matrix is:

| case | Re | expected regime | target end time [s] | status |
|---|---:|---|---:|---|
| Re10 | 10 | steady | 100.0 | smoke-test passed in Boussinesq architecture; next run should target `Nu(t)` plateau |
| Re20 | 20 | steady | 100.0 | pending |
| Re40 | 40 | steady | 100.0 | pending |
| Re100 | 100 | unsteady | 25.0 | pending |
| Re200 | 200 | unsteady | 15.0 | pending |

The active production-oriented run has now been prepared as:

- `results/study_v2a/runs/002_data_v2a_boussinesq_validation`

and the corresponding working cases were generated in:

- `C:\openfoam-case\VV_cases\V2_thermal_run002`

For the steady cases (`Re10`, `Re20`, `Re40`), the active plan is now to write results
every `1 s` up to `100 s` so that `Nu(t)` can be assessed for thermal convergence rather
than inferred from a single late snapshot.

## Current results

### Latest accepted diagnostic result

The current best diagnostic dataset is the stopped `Re10_long100s` run in the active
run-002 Boussinesq branch.

Post-processing of the saved parallel fields gives:

- `Nu(t)` reconstructed up to about `47.0 s`
- mean `Nu` over the second half of the run: `6.8857`
- mean `Nu` over the last `10 s`: `6.0189`
- reference values:
  - `Nu_Lange = 1.8101`
  - `Nu_Bharti = 1.8623`
- transient spectral peak from `Cl` tail: `St_peak = 0.0659`

Interpretation:

- the solver architecture is stable and the accepted `Nu` definition is now implemented
  consistently with Bharti and Lange
- the current thermal solution is still far above the literature benchmark
- therefore this run is still diagnostic, not validated
- the extracted `St` is not physically comparable to literature for `Re = 10`, where a
  steady regime is expected

The current comparison assets are stored in:

- [literature_comparison.md](c:\Users\kik\My%20Drive\Politechnika%20Krakowska\Researches\Repositories\openFoam\VV_cases\V2_thermal\results\study_v2a\runs\002_data_v2a_boussinesq_validation\literature_comparison.md)
- [literature_comparison_Re10_long100s.md](c:\Users\kik\My%20Drive\Politechnika%20Krakowska\Researches\Repositories\openFoam\VV_cases\V2_thermal\results\study_v2a\runs\002_data_v2a_boussinesq_validation\literature_comparison_Re10_long100s.md)
- [Re10_long100s_Nu_vs_time.png](c:\Users\kik\My%20Drive\Politechnika%20Krakowska\Researches\Repositories\openFoam\VV_cases\V2_thermal\results\study_v2a\runs\002_data_v2a_boussinesq_validation\plots\Re10_long100s_Nu_vs_time.png)

This is sufficient to confirm that the solver architecture and the accepted `Nu`
definition are now viable. It is not yet sufficient for final literature comparison.
because only one non-zero thermal snapshot is available and the case is still in startup
transient.

The compact run archive currently stored in:

- `results/study_v2a/runs/001_data_v2a_level_a_unconfined_debug`

contains only the earlier pre-switch debug cases in note form.
It should therefore be treated as historical debug evidence, not as the accepted
production Reynolds matrix for V2a.

## Comparison with literature

No final literature comparison table should be treated as accepted yet for V2a.

At this stage:

- the reference literature targets are defined
- the solver architecture has been corrected
- the production Reynolds-number matrix has not yet been completed

Therefore the next comparison table should only be generated after:

1. production controls are restored
2. `Nu` extraction is implemented in the new architecture
3. `Re10`, `Re20`, and `Re40` are completed successfully

## Recommended reference setup

The current recommended next-step setup for V2a is:

- `buoyantBoussinesqPimpleFoam`
- active Boussinesq transport model in `transportProperties`
- clean run-002 generator in `_code/V2AStudy.py`
- `Re10` as the first production confirmation case of run 002
- then `Re20` and `Re40`

## Figures used in this document

Selected figures should be stored in:

- [figs](./figs)

At the current stage this folder is reserved for:

- geometry figure
- future `Nu vs Re` comparison figure
- future residual or startup-stability figure if needed for the manuscript
