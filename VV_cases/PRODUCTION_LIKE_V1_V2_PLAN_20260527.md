# Production-Like V1/V2 Plan

Date: 2026-05-27

## Goal

Replace the current benchmark-style reruns of `V1` and `V2` with
`production-like` cases that keep the same OpenFOAM 13 `foamRun -solver fluid`
path as `V4b_3D` and move the domain/mesh setup as close as reasonably
possible to the accepted production family.

## What Changes

### Shared target for both studies

- solver: `foamRun -solver fluid`
- thermophysics: `heRhoThermo + eConst + Boussinesq + sensibleInternalEnergy`
- transport: constant `mu`, `Pr`
- pressure convention: dynamic `p` and `p_rgh`
- front/back treatment: thin 3D, not 2D `empty`
- domain family: align with `V4b` production box
  - upstream length about `2D`
  - downstream length about `8D`
- mesh family: align with `V4b`
  - blockMesh backbone similar to `V4b`
  - local cylinder/wake refinement similar to `V4b`
  - comparable near-body and wake cell density

### V1 production-like objective

- Keep the `V1` verification question:
  confinement/onset/shedding behavior.
- Change the computational setting:
  from literature-style long channel to `V4b`-like compact production box.
- Expected output:
  not a pure literature verification anymore, but a solver+mesh consistency
  bridge from classical `V1` physics to production numerics.

### V2 production-like objective

- Keep the `V2` thermal validation question:
  cylinder heat-transfer behavior across low/moderate `Re`.
- Change the computational setting:
  from the old O-grid benchmark mesh to a `V4b`-like Cartesian/snappy family.
- Expected output:
  not a pure benchmark O-grid validation anymore, but a production-like
  thermal consistency study on the final solver/mesh family.

## Recommended Case Design

### Track A: minimal defensible

- `V1`
  - Use one `beta` close to project geometry relevance, e.g. `beta=0.375` or
    `0.50`
  - Run `2-3` Reynolds numbers around the expected transition window
- `V2`
  - Run `Re = 10, 40, 100`
- Purpose:
  fast bridge evidence before presentation

### Track B: strong presentation set

- `V1`
  - `beta = 0.375, 0.50`
  - `2` Reynolds numbers per `beta`, one below and one above transition
- `V2`
  - `Re = 10, 20, 40, 60, 100`
- Purpose:
  enough data for plots showing old benchmark vs production-like rerun

## Implementation Plan

### Step 1. Freeze current benchmark reruns

- stop current `V1` and `V2` background runs
- keep existing scripts/results as archival baseline

### Step 2. Build a shared production-like mesh template

- derive a reusable template from `V4b_3D`
- use:
  - `Lin = 2D`
  - `Lout = 8D`
  - thin 3D span comparable to `V4b`
  - local refinement around cylinder and wake
- define `coarse`, `medium`, `fine` variants if needed

### Step 3. Create new V1 production-like study

- new script:
  `VV_cases/V1_solver/_code/V1ProductionLikeStudy.py`
- geometry:
  confined cylinder, but inside the compact `V4b`-like box
- observables:
  `Cd`, `Cl_rms`, `St`, regime classification
- comparison plots:
  - old benchmark V1 vs new production-like V1
  - production-like V1 vs Sahin/Owens only as a contextual reference

### Step 4. Create new V2 production-like study

- new script:
  `VV_cases/V2_thermal/_code/V2ProductionLikeStudy.py`
- geometry:
  heated cylinder only, but meshed with the same family logic as `V4b`
- observables:
  `Nu`, `Cd`, `St`, temperature bounds, thermal sanity checks
- comparison plots:
  - old O-grid V2 vs new production-like V2
  - new production-like V2 vs Lange/Bharti references

### Step 5. Sanity and mesh checks

- run `checkMesh` on all variants
- compare:
  - cell count
  - non-orthogonality
  - near-cylinder density
  - wake density
- confirm no residual `empty`-patch artifacts

### Step 6. Short execution campaign

- start with one smoke case for `V1` and one for `V2`
- then launch the shortened matrix only after:
  - stable startup
  - clean patch fields
  - analyzers reading the new outputs correctly

### Step 7. Presentation outputs

- summary tables:
  - old benchmark
  - new production-like
  - reference
- figures:
  - `V1`: `Cl(t)`, `St` comparison, `Cd` comparison
  - `V2`: `Nu(t)`, `Nu old vs new`, `Nu vs reference`
- one slide explicitly stating:
  benchmark verification/validation and production-like bridge are separate

## Key Interpretation Rule

After this change, `V1` and `V2` should be presented as
`production-like consistency reruns`, not as the canonical benchmark studies.
The old benchmark campaigns remain the clean verification/validation layer;
the new reruns become the bridge to final production numerics.

## Immediate Next Actions

1. Create the shared `V4b`-like mesh/domain helper.
2. Implement one smoke `V1` production-like case.
3. Implement one smoke `V2` production-like case.
4. Verify analyzers and plotting.
5. Launch the shortened presentation matrix.
