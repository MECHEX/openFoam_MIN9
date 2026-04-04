# Working Checklist

Read this file before starting a new block of work in `VV_cases`.

## Before starting

1. Identify the target study:
   - `V1_solver`
   - `V2_confined`
   - `V2_thermal`
   - `V3_array`
   - `V4a_2D`
   - `V4b_3D`
2. Read `VV_cases/STORAGE_STANDARD.md`.
3. Decide whether the task is:
   - setup change
   - new run
   - rerun after failure
   - new simulation inside an existing run
   - post-processing only
   - plotting only
4. Reserve the next run folder name in the form:
   - `NNN_data_<run_slug>`
5. Decide which simulations belong to that run.
6. Write or update the run note and simulation `input.md` files before launching.
7. Check whether the simulation has its own `0/constant/system/Allrun`.
   If yes, archive them at simulation level, not only at run or study level.
8. If the study keeps a reusable generic template case, store it in `templates/base_case/`, not loose in the study root.

## During the work

1. Keep the working OpenFOAM case separate from the archived run folder.
2. Do not overwrite old numbered runs.
3. If a single simulation changes inside the same campaign, keep it under the same run.
4. If the whole campaign must be repeated after failure or major correction, create a new run number.
5. Keep run-level and simulation-level outputs separate.

## After the work package

1. Freeze the exact setup used for each simulation in `01_openfoam_setup`.
2. Save raw solver output in `02_raw_data`.
3. Save extracted metrics in `03_processed_data`.
4. Save figures in `04_plots`.
5. Write simulation `00_notes/output.md`.
6. Update run-level summary files.
7. Update study-level summary files if relevant.
8. Append a timestamped entry to `VV_cases/RESEARCH_LOG.md`.

## Minimum questions to answer before leaving the task

- What was changed?
- What run was updated?
- Which simulations were added or changed?
- Where are the raw results?
- Where are the processed results?
- What should happen next?

## Non-negotiable rule

No substantial simulation or post-processing task is considered complete until the
corresponding entry is written to `VV_cases/RESEARCH_LOG.md`.
