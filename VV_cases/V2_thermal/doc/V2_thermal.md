# V2 Thermal Verification

## Objective

V2 is the thermal verification track for forced convection around a heated circular cylinder.
The active sub-study is `V2a`, whose goal is to reproduce reference Nusselt numbers for
an unconfined heated cylinder under constant wall temperature conditions.

The original snappy-mesh thermal path was rejected after solver and Nu-definition debugging. The current accepted validation path is the structured O-grid cylinder matrix in `results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation`.

The current objective is now to use that validated O-grid chain as the thermal reference for V4b-style heat-transfer post-processing, and to keep the earlier snappy/Boussinesq attempts as historical diagnostics only.

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

### Accepted validation run

The accepted V2a validation run is:

```text
results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation
```

It replaced the earlier unstable snappy-mesh branch and uses a structured O-grid around the heated cylinder. The earlier `run001` and `run002` branches remain useful debugging history, but they should not be cited as accepted thermal validation.

## Mesh and mesh-independence study

### Current status

The accepted validation mesh for `run004` is a structured O-grid with `10,240` cells in the archived result table. It is not a full mesh-independence study, but it is sufficiently clean for the current purpose: checking the solver, wall-normal Nu extraction, bounded temperature field, and Reynolds-number trend against the reference data.

### Practical current mesh notes

- the accepted validation branch uses a structured O-grid cylinder mesh
- the older snappyHexMesh/no-layer cases are historical diagnostics
- the O-grid branch avoids the near-wall ambiguity that made the first thermal validation attempt unreliable

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
- area-averaged projection `grad(T) . n` over the `cylinder` patch
- `Nu = D * <grad(T).n>_cylinder / (T_wall - T_inf)`

The earlier shortcut based on `mag(grad(T))` was rejected as non-physical because it
mixes tangential components into the wall heat-transfer metric.

This definition is now directly consistent with the reference papers:

- in [Bharti_2007.pdf](c:\Users\kik\My%20Drive\Politechnika%20Krakowska\Grants\2025_07_Miniatura_9_ver2\Realizacja\Art\Bharti_2007.pdf), Eq. (11)-(12) define local and surface-averaged Nusselt number from the wall heat-transfer coefficient / wall-normal thermal gradient for the cylinder surface
- in [Lange_1998.pdf](c:\Users\kik\My%20Drive\Politechnika%20Krakowska\Grants\2025_07_Miniatura_9_ver2\Realizacja\Art\Lange_1998.pdf), Sec. 2.2 defines the wall heat flux, heat-transfer coefficient, and the mean Nusselt number averaged over the whole cylinder perimeter

## Current case matrix

The accepted O-grid validation matrix is:

| case | Re | latest time [s] | Nu | reference Nu | error [%] | status |
|---|---:|---:|---:|---:|---:|---|
| `Re10_ogrid` | 10 | 99.994 | 1.88065 | 1.86230 | 0.985 | candidate |
| `Re20_ogrid` | 20 | 100.000 | 2.48293 | 2.46530 | 0.715 | candidate |
| `Re40_ogrid` | 40 | 100.000 | 3.30454 | 3.28250 | 0.671 | candidate |
| `Re45_ogrid` | 45 | 119.999 | 3.47356 | 3.46566 | 0.228 | candidate |
| `Re60_ogrid` | 60 | 79.800 | 3.97777 | 3.97516 | 0.066 | candidate |
| `Re100_ogrid` | 100 | 24.513 | 5.17196 | 5.12778 | 0.862 | candidate |
| `Re200_ogrid` | 200 | 11.464 | 7.50399 | 7.42021 | 1.129 | diagnostic |

The low-Re cases form the cleanest validation set. The `Re200` O-grid result is useful as an article-range diagnostic, but it has the shortest physical record in the table and should be treated more cautiously than the low-Re steady cases.

## Current results

### Latest accepted result

The accepted result is the O-grid cylinder validation (`run004`). It gives wall-normal-gradient Nusselt numbers within about `0.07..1.13%` of the reference values over the archived `Re=10..200` matrix, with bounded temperature fields and no cylinder-surface overshoot above `T_wall`.

Key interpretation:

- the wall-normal `Nu` extraction route is now validated for a clean cylinder benchmark
- the structured O-grid branch supersedes the rejected snappy validation attempt
- the low-Re matrix (`Re10..Re60`) is especially strong for thermal verification
- `Re100` and `Re200` are useful unsteady/article-range checks, with `Re200` marked diagnostic because of its shorter record

Accepted run-level summary:

```text
results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/summary.md
```

Earlier run-002 Boussinesq/snappy results should be cited only as diagnostic history. They confirmed parts of the solver architecture, but their Nu values were not accepted for literature validation.

## Comparison with literature

The accepted O-grid comparison is now the current literature comparison for V2a. The low-Re O-grid cases agree with the reference Nu values to within about one percent, and the extended article-range dashboard is stored with the run-004 outputs.

The remaining caution is scope: this validates the thermal solver and Nu extraction on an unconfined heated-cylinder benchmark. It does not by itself validate the confined V4b fin-and-tube geometry, whose production support comes from internal heat-balance closure and campaign sensitivity checks.

## Recommended reference setup

The recommended V2a reference setup is:

- structured O-grid cylinder validation branch (`run004`)
- constant wall temperature cylinder
- pure forced convection with `g = 0`
- wall-normal-gradient Nusselt extraction on the cylinder surface
- use the accepted `run004` table for thermal solver/Nu-method validation

Future work, if needed, should formalize a mesh-independence check around the O-grid branch rather than returning to the rejected snappy validation path.

## Figures used in this document

Selected figures should be stored in:

- [figs](./figs)

Current run-level figures are stored with `run004`, including:

- `plots/V2_run004_Nu_vs_reference.png`
- `plots/V2A_Nu_Re_articles_vs_present.png`
- `plots/V2A_articles_vs_present_dashboard.png`
- per-case `Nu(t)` plots for the O-grid matrix

Only final figures explicitly cited by this canonical document should be copied into `doc/figs/`.
