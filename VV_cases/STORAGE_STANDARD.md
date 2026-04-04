# VV Cases Storage Standard

## Purpose

This document defines how simulation results are stored in the `VV_cases` part of the repository.
The goal is reproducibility, easy navigation, and a clear separation between:

- OpenFOAM setup used for the run
- raw solver output
- processed data
- plots
- human-readable notes

## Scope

This standard applies to every study directory:

- `VV_cases/V1_solver`
- `VV_cases/V2_confined`
- `VV_cases/V2_thermal`
- `VV_cases/V3_array`
- `VV_cases/V4a_2D`
- `VV_cases/V4b_3D`

## Core principle

In this repository:

- a `run` means one attempt / one computational campaign
- a run can contain many simulations
- different Reynolds numbers, meshes, or domain variants usually belong to the same run
- a new run number is created only when the whole attempt is repeated after failure, correction, or major methodological change

## What belongs where

This is the practical rule for OpenFOAM content:

- study level:
  - Python scripts
  - generators
  - plotting scripts
  - documentation
  - study-wide plans and comparisons
- run level:
  - campaign notes
  - run-wide summary tables
  - overlay plots across many simulations
  - shared assumptions for that attempt
- simulation level:
  - frozen OpenFOAM case
  - raw solver output
  - processed metrics
  - single-case plots

Important:

- `0/`, `constant/`, `system/`, `Allrun`, `caseMeta.json` belong to one simulation
- they should not be stored only once at study level if they are meant to document results
- the study may keep templates or generators, but the frozen setup used to produce a result must live with that simulation

### Example

Correct:

```text
VV_cases/
  V1_solver/
    V1Study.py
    V1PublicationPlots.py
    templates/
      base_case/
    results/
      study_v1/
        runs/
          001_data_beta05_initial_verification/
            02_simulations/
              baseline_medium_Re160/
                01_openfoam_setup/
                  0/
                  constant/
                  system/
                  Allrun
```

Not recommended:

```text
VV_cases/
  V1_solver/
    0/
    constant/
    system/
```

if those folders are supposed to document many different simulations. That would hide which setup produced which result.

If a study keeps a reusable generic case template, store it under:

- `templates/base_case/`

and not as loose `0/`, `constant/`, or `system/` folders directly in the study root.

## High-level study layout

Each study should follow this structure:

```text
VV_cases/
  Vx_name/
    templates/
      base_case/
    <study scripts and templates>
    results/
      runs/
        001_data_<run_slug>/
        002_data_<run_slug>/
        003_data_<run_slug>/
      study_summary/
      publication/
```

If a study already uses a named study root such as `results/study_v1`, then the same
structure should exist inside that study root:

```text
results/
  study_v1/
    runs/
    study_summary/
    publication/
```

## Run numbering

Each run attempt gets its own numbered folder:

- `001_data_<run_slug>`
- `002_data_<run_slug>`
- `003_data_<run_slug>`

Rules:

- The numeric prefix is global within a study and increments monotonically.
- Do not overwrite an old run folder after a failed or incomplete attempt.
- If the whole attempt must be repeated, create the next number and keep a meaningful slug.
- Example:
  - `001_data_beta05_initial_verification`
  - `002_data_beta05_inlet_fix`
  - `003_data_beta05_repeat_after_mesh_change`

This preserves history and makes failed attempts traceable.

## Required structure inside each run

Every run folder should contain the following subfolders:

```text
001_data_<run_slug>/
  00_notes/
  01_run_setup/
  02_simulations/
  03_run_summary/
  04_publication_candidates/
  05_run_logs/
```

### `00_notes`

Human-readable documentation for the run as a whole.

Recommended files:

- `run_scope.md`
- `run_decisions.md`
- `run_outcome.md`

### `01_run_setup`

Run-level setup shared by all simulations in the campaign.

Recommended contents:

- shared assumptions
- batch scripts
- parameter notes
- copied study plan if useful

This folder should not be used as the only place for case-specific `0/constant/system`.
Those belong inside each simulation when they define the actual solved case.

### `02_simulations`

One subfolder per simulation, for example:

- `baseline_medium_Re100`
- `baseline_medium_Re160`
- `long_medium_Re200`

### `03_run_summary`

Aggregated outputs for the whole run.

Recommended contents:

- `summary.csv`
- `summary.md`
- comparison tables
- overlay plots generated from all simulations in the run

### `04_publication_candidates`

Run-level figures and tables that may later be promoted to study-level or manuscript-level outputs.

### `05_run_logs`

Batch-level helper logs if they exist.

## Required structure inside each simulation

Each simulation inside a run should contain the following subfolders:

```text
02_simulations/
  <simulation_slug>/
    00_notes/
    01_openfoam_setup/
    02_raw_data/
    03_processed_data/
    04_plots/
    05_logs/
```

### Simulation-level `00_notes`

Human-readable documentation for one simulation.

Required files:

- `input.md`
  What was intended before launch: geometry, mesh, Reynolds number, target quantity, assumptions.
- `output.md`
  What happened after the run: result quality, regime, issues, comparison to reference, next action.

Optional files:

- `decision.md`
- `comparison.md`

### Simulation-level `01_openfoam_setup`

Snapshot of the exact OpenFOAM case used to produce that simulation.

Recommended contents:

- `0/`
- `constant/`
- `system/`
- `Allrun`
- `caseMeta.json`
- helper dictionaries such as `setExprFieldsDict`

Rule:

- This folder is a frozen copy of the setup used for that simulation.
- Do not treat it as a live working directory after the simulation is archived.
- If a simulation has a unique `0`, `constant`, `system`, or `Allrun`, store them here.

### Simulation-level `02_raw_data`

Direct outputs copied from the working OpenFOAM case.

Recommended contents:

- `postProcessing/`
- time directories if they are being archived
- copied mesh reports
- exported coefficient files

Rule:

- Keep these files as raw as possible.
- Avoid mixing hand-edited spreadsheets or manually cleaned files here.

### Simulation-level `03_processed_data`

Derived machine-readable outputs.

Recommended contents:

- `summary.json`
- extracted tables used in papers or reports
- processed coefficient files if needed

Rule:

- This is where processed metrics belong.
- If a value appears in a plot or a table, its generating data should exist here first.

### Simulation-level `04_plots`

Figures generated from the processed data of that simulation.

Recommended contents:

- `Cl_vs_time.png`
- `Cd_vs_time.png`
- single-case diagnostic figures

Rule:

- Keep only output graphics here, not the scripts that generate them.

### Simulation-level `05_logs`

Execution logs and utility logs for that simulation.

Recommended contents:

- `blockMesh.log`
- `snappyHexMesh.log`
- `checkMesh.log`
- `pimpleFoam.log`
- helper-script logs

Rule:

- Logs stay separate from raw field data and separate from human notes.

## Study-level summary folders

At the study level, keep:

```text
results/
  runs/
  study_summary/
  publication/
```

### `study_summary`

Cross-run summaries for the whole study.

Recommended contents:

- run index
- cross-run comparison tables
- current study plan
- study-wide summary files when needed

### `publication`

Selected polished outputs intended for reporting or paper writing.

Recommended contents:

- final figures
- tables exported for manuscripts
- short text snippets if needed

## Naming recommendations

Use short, stable slugs.

Run examples:

- `beta05_initial_verification`
- `beta05_inlet_fix`
- `beta0375_campaign_01`

Simulation examples:

- `baseline_medium_Re160`
- `long_medium_Re200`
- `b030_medium_Re095`

Avoid:

- spaces
- Polish diacritics
- long free-form descriptions in folder names

## Recommended workflow

For each new run:

1. Reserve the next numbered run folder.
2. Describe the run scope in `00_notes`.
3. Create or update simulation subfolders inside `02_simulations`.
4. For each simulation:
   - write `00_notes/input.md`
   - run the case in the working directory
   - copy the frozen setup to `01_openfoam_setup`
   - copy raw solver outputs to `02_raw_data`
   - generate processed metrics into `03_processed_data`
   - save figures into `04_plots`
   - write `00_notes/output.md`
5. Build run-level summaries in `03_run_summary`.
6. Save polished figures for that run in `04_publication_candidates`.
7. Update `study_summary` if the run changes the study-level picture.
8. Append the action to `VV_cases/RESEARCH_LOG.md`.

## Migration policy for existing studies

Existing study folders may still use the older layout, for example:

- `V1_solver/results/study_v1/...`

Migration rule:

- Do not rewrite history destructively.
- Keep old results readable.
- Migrate gradually by regrouping simulations under campaign-style runs.

## Decision for this repository

From this point forward:

- new work should follow this storage standard
- one run may contain many simulations
- old work should be migrated only when it materially helps the study
- every completed work package must be logged in `VV_cases/RESEARCH_LOG.md`
