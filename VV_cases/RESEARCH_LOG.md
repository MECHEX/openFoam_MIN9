# Research Log

Chronological record of work performed in `VV_cases`.

## Entry format

Each entry should contain:

- timestamp with timezone
- study name
- work package
- actions taken
- outputs created or updated
- decisions made
- next step

---

## 2026-04-04 10:34:13 +02:00 | VV_cases | Repository organization standard

### Work package

Define a single storage convention for all V-studies before continuing with new simulations.

### Actions taken

- reviewed the current `VV_cases` structure
- confirmed that there was no shared repository-level storage standard
- confirmed that there was no repository-level operational checklist
- confirmed that there was no shared research log for all studies
- created `VV_cases/README.md`
- created `VV_cases/STORAGE_STANDARD.md`
- created `VV_cases/WORKING_CHECKLIST.md`
- created `VV_cases/RESEARCH_LOG.md`

### Outputs created

- `VV_cases/README.md`
- `VV_cases/STORAGE_STANDARD.md`
- `VV_cases/WORKING_CHECKLIST.md`
- `VV_cases/RESEARCH_LOG.md`

### Decisions made

- each study will remain separated as `V1`, `V2`, `V3`, `V4a`, `V4b`
- each archived run will use numbered folders such as `001_data_<run_slug>`
- each run folder will be split into:
  - `00_notes`
  - `01_openfoam_setup`
  - `02_raw_data`
  - `03_processed_data`
  - `04_plots`
  - `05_logs`
- old layouts will not be rewritten destructively
- future work packages must end with an update to this log

### Next step

Apply the new storage convention first to `V1_solver`, then align new `V2_confined` work to the same standard before launching more runs.

---

## 2026-04-04 10:57:16 +02:00 | V1_solver | study_v1 cleanup and repository archival

### Work package

Restructure `study_v1` to the new numbered-run layout and remove older exploratory material from the active repository root.

### Actions taken

- updated `VV_cases/V1_solver/V1Study.py` to write into:
  - `results/study_v1/runs`
  - `results/study_v1/study_summary`
  - `results/study_v1/publication`
- updated `VV_cases/V1_solver/V1PublicationPlots.py` to read from `study_summary` and write to `publication/figures`
- added a reproducible migration script:
  - `VV_cases/V1_solver/MigrateStudyV1.ps1`
- migrated legacy unnumbered V1 run folders into numbered folders:
  - `001_data_baseline_medium_Re090`
  - `002_data_baseline_medium_Re100`
  - `003_data_baseline_medium_Re110`
  - `004_data_baseline_medium_Re120`
  - `005_data_baseline_medium_Re140`
  - `006_data_baseline_medium_Re160`
  - `007_data_baseline_coarse_Re120`
  - `008_data_baseline_coarse_Re160`
  - `009_data_baseline_fine_Re120`
  - `010_data_baseline_fine_Re160`
  - `011_data_long_medium_Re120`
  - `012_data_long_medium_Re160`
  - `013_data_long_medium_Re200`
  - `014_data_long_target100k_Re160`
- copied archived OpenFOAM setup, raw `postProcessing`, and logs from `C:\openfoam-case\VV_cases\V1_solver\...` into the numbered run folders
- regenerated V1 study outputs with the new layout:
  - per-run `output.md`
  - per-run `summary.json`
  - per-run `Cl_vs_time.png`
  - study-level summary files
  - publication figures
- moved old top-level V1 pre-cleanup material to:
  - `Archiwum/VV_cases/V1_solver/study_v1_pre_cleanup`
- moved legacy exploratory directories from the repository root to:
  - `Archiwum/openFoam_MIN`
  - `Archiwum/mesh`
- added `Archiwum/README.md`
- updated references that still pointed to the old mesh location in `VV_cases/V4b_3D`

### Outputs created or updated

- `VV_cases/V1_solver/V1Study.py`
- `VV_cases/V1_solver/V1PublicationPlots.py`
- `VV_cases/V1_solver/MigrateStudyV1.ps1`
- `VV_cases/V1_solver/results/study_v1/runs/...`
- `VV_cases/V1_solver/results/study_v1/study_summary/...`
- `VV_cases/V1_solver/results/study_v1/publication/figures/...`
- `Archiwum/README.md`

### Decisions made

- `study_v1` remains the study root, but now uses the standard substructure:
  - `runs`
  - `study_summary`
  - `publication`
- each historical V1 run is now preserved as a numbered archive entry
- legacy pre-`VV_cases` material is no longer kept in the active repository root
- future V1 work should continue from the numbered-run layout, not from the old flat `study_v1` layout

### Next step

Apply the same storage convention to `V2_confined` before launching the next verification batch.

---

## 2026-04-04 11:05:43 +02:00 | V1_solver | correction of run definition and regrouping into one campaign

### Work package

Correct the repository model so that one run contains many simulations, instead of treating each simulation as a separate run.

### Actions taken

- corrected the storage convention:
  - `run = one attempt / one campaign`
  - `simulation = one case inside that run`
- updated `VV_cases/STORAGE_STANDARD.md`
- updated `VV_cases/WORKING_CHECKLIST.md`
- updated `VV_cases/README.md`
- updated `VV_cases/V1_solver/V1Study.py` to use:
  - one active run directory
  - simulation subfolders inside `02_simulations`
  - run-level summary output in `03_run_summary`
- updated `VV_cases/V1_solver/V1PublicationPlots.py` to save publication figures both:
  - at study level
  - at run level
- regrouped the V1 simulations under:
  - `VV_cases/V1_solver/results/study_v1/runs/001_data_beta05_initial_verification`
- moved the following simulations into that run:
  - `baseline_medium_Re090`
  - `baseline_medium_Re100`
  - `baseline_medium_Re110`
  - `baseline_medium_Re120`
  - `baseline_medium_Re140`
  - `baseline_medium_Re160`
  - `baseline_coarse_Re120`
  - `baseline_coarse_Re160`
  - `baseline_fine_Re120`
  - `baseline_fine_Re160`
  - `long_medium_Re120`
  - `long_medium_Re160`
  - `long_medium_Re200`
  - `long_target100k_Re160`
- regenerated V1 summaries and publication figures after regrouping
- moved the now-misleading one-off migration script to:
  - `Archiwum/VV_cases/V1_solver/MigrateStudyV1_per_sim_legacy.ps1`

### Outputs created or updated

- `VV_cases/STORAGE_STANDARD.md`
- `VV_cases/WORKING_CHECKLIST.md`
- `VV_cases/README.md`
- `VV_cases/V1_solver/V1Study.py`
- `VV_cases/V1_solver/V1PublicationPlots.py`
- `VV_cases/V1_solver/results/study_v1/runs/001_data_beta05_initial_verification/...`
- `VV_cases/V1_solver/results/study_v1/study_summary/...`
- `VV_cases/V1_solver/results/study_v1/publication/figures/...`

### Decisions made

- a run number now refers to a campaign, not a single simulation
- the current V1 material is interpreted as one first verification campaign
- future V1 simulations that belong to the same campaign should stay under the same run
- a new V1 run number should be created only for a truly new attempt

### Next step

Apply the same campaign-style run model to `V2_confined` before starting the next batch of confined-cylinder verification cases.

---

## 2026-04-04 11:23:55 +02:00 | VV_cases | clarification of study vs run vs simulation OpenFOAM content

### Work package

Clarify exactly where OpenFOAM case folders such as `0`, `constant`, `system`, and `Allrun` should live in the repository structure.

### Actions taken

- updated `VV_cases/STORAGE_STANDARD.md`
- added a direct explanation of:
  - study level content
  - run level content
  - simulation level content
- added an explicit rule that frozen OpenFOAM case folders belong to the simulation level
- added a concrete directory example for `V1`
- updated `VV_cases/WORKING_CHECKLIST.md` to remind us to archive `0/constant/system/Allrun` at simulation level

### Decisions made

- study level keeps scripts, generators, documentation, and study-wide summaries
- run level keeps campaign notes and run-wide summaries
- simulation level keeps the frozen OpenFOAM case and all case-specific outputs
- `0`, `constant`, `system`, `Allrun`, and similar case-defining files are treated as simulation-level artifacts unless they are purely templates

### Next step

Carry this exact distinction into `V2_confined` so the next study starts cleanly with the same storage rules.

---

## 2026-04-04 11:33:29 +02:00 | VV_cases | moving loose case folders into study templates

### Work package

Clean the study roots by moving loose OpenFOAM case folders into explicit template locations.

### Actions taken

- reviewed the `VV_cases` study roots again
- confirmed that several studies still had loose case folders directly in the study root:
  - `0`
  - `0.orig`
  - `constant`
  - `system`
  - and in some cases `Allrun`
- updated `VV_cases/STORAGE_STANDARD.md` to state explicitly that reusable generic case templates belong in:
  - `templates/base_case/`
- updated `VV_cases/WORKING_CHECKLIST.md` with the same rule
- moved loose case folders into `templates/base_case/` for:
  - `V1_solver`
  - `V2_confined`
  - `V2_thermal`
  - `V3_array`
  - `V4a_2D`
  - `V4b_3D`
- moved the matching top-level `Allrun` files into `templates/base_case/` where they belonged to the template case

### Outputs created or updated

- `VV_cases/STORAGE_STANDARD.md`
- `VV_cases/WORKING_CHECKLIST.md`
- `VV_cases/V1_solver/templates/base_case/...`
- `VV_cases/V2_confined/templates/base_case/...`
- `VV_cases/V2_thermal/templates/base_case/...`
- `VV_cases/V3_array/templates/base_case/...`
- `VV_cases/V4a_2D/templates/base_case/...`
- `VV_cases/V4b_3D/templates/base_case/...`

### Decisions made

- study roots should stay clean and contain mainly:
  - scripts
  - documentation
  - results
  - template folders
- reusable OpenFOAM base cases are treated as study-level templates
- frozen result-producing OpenFOAM cases remain simulation-level artifacts inside runs

### Next step

Use the cleaned structure as the starting point for bringing `V2_confined` into the same run-and-simulation workflow as `V1`.
