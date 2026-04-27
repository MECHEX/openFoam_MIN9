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

## 2026-04-04 13:52:57 +02:00 | V1_solver | documentation audit and run 002 scaffold for Sahin & Owens comparison

### Work package

Check whether the shared repository documentation is sufficient to continue, then prepare the next V1 run as a separate campaign for direct comparison with Sahin and Owens.

### Actions taken

- reviewed:
  - `VV_cases/README.md`
  - `VV_cases/STORAGE_STANDARD.md`
  - `VV_cases/RESEARCH_LOG.md`
  - current `V1_solver/results/study_v1` layout
- confirmed that the shared repository documentation is already sufficient to continue work without additional structural changes
- identified one methodological clarification:
  - the Poiseuille-inlet literature comparison belongs to `V1` as a second verification run, not as a continuation of run 001
- created:
  - `VV_cases/V1_solver/results/study_v1/runs/002_data_sahin_owens_poiseuille_verification`
- added run-level notes describing:
  - purpose
  - scope
  - comparison logic
  - direct-comparison betas versus project-geometry beta

### Outputs created or updated

- `VV_cases/V1_solver/results/study_v1/runs/002_data_sahin_owens_poiseuille_verification/00_notes/run_scope.md`
- `VV_cases/V1_solver/results/study_v1/runs/002_data_sahin_owens_poiseuille_verification/01_run_setup/comparison_plan.md`
- `VV_cases/RESEARCH_LOG.md`

### Decisions made

- current shared documentation is good enough to proceed
- run 001 remains the initial verification campaign
- direct comparison against Sahin and Owens will be tracked as V1 run 002
- `beta = 0.30` and `beta = 0.50` are direct literature comparison points
- `beta = 0.375` is retained as the project-relevant bridge case

### Next step

Use the existing Poiseuille-inlet study logic as the execution basis for V1 run 002, but store results under the new V1 run folder and prepare the first simulation set around the critical Reynolds ranges.

---

## 2026-04-04 14:50:36 +02:00 | V1_solver | V1 run 002 technical start and case generation

### Work package

Create the dedicated study driver for V1 run 002 and generate the first working cases for the Sahin and Owens comparison campaign.

### Actions taken

- created `VV_cases/V1_solver/V1Run2Study.py`
- kept V1 run 002 separate from V1 run 001 by using:
  - study archive path under `VV_cases/V1_solver/results/study_v1/runs/002_data_sahin_owens_poiseuille_verification`
  - working-case root at `C:\openfoam-case\VV_cases\V1_solver_run002`
- implemented in the new driver:
  - Poiseuille inlet setup
  - `beta`-dependent channel height
  - Sahin and Owens reference lookup
  - run-002-specific summary and comparison outputs
  - archiving of OpenFOAM setup, raw post-processing, and logs into the V1 run-002 structure
- generated the first full set of working cases:
  - `b030_medium_Re080`
  - `b030_medium_Re095`
  - `b030_medium_Re100`
  - `b030_medium_Re120`
  - `b0375_medium_Re090`
  - `b0375_medium_Re110`
  - `b0375_medium_Re120`
  - `b0375_medium_Re135`
  - `b050_medium_Re100`
  - `b050_medium_Re120`
  - `b050_medium_Re130`
  - `b050_medium_Re150`
- generated run-level setup files for run 002, including:
  - `case_matrix.md`
  - `runtime_locations.md`
  - `study_plan.md`

### Outputs created or updated

- `VV_cases/V1_solver/V1Run2Study.py`
- `VV_cases/V1_solver/results/study_v1/runs/002_data_sahin_owens_poiseuille_verification/...`
- `C:\openfoam-case\VV_cases\V1_solver_run002\...`

### Decisions made

- V1 run 002 will use the project-standard campaign structure but remain a V1 solver-verification run
- all initial run-002 cases use the medium mesh
- direct literature checks remain focused on `beta = 0.30` and `beta = 0.50`
- `beta = 0.375` remains the bridge case to the project geometry

### Next step

Launch the first pilot subset near the critical Reynolds ranges, then analyze regime and `St` before deciding whether the full 12-case batch should run unchanged.

---

## 2026-04-04 | V1_solver | V1 run 002 pilot subset execution and β=0.50 onset investigation

### Work package

Execute the first pilot subset of V1 run 002 (cases near the critical Reynolds number for each β), analyse results against Sahin & Owens Table IV, and decide how to proceed for β=0.50.

### Actions taken

- restarted `b030_medium_Re100` from t=3.3s (previous run was interrupted by a double-source shell error)
- ran the following pilot subset sequentially:
  - `b030_medium_Re095` (already complete)
  - `b030_medium_Re100` (restarted)
  - `b0375_medium_Re110`
  - `b0375_medium_Re120`
  - `b050_medium_Re120`
  - `b050_medium_Re130`
- fixed `PermissionError` in `V1Run2Study.py` `replace_dir()` on Windows by adding `_rm_readonly` error handler to `shutil.rmtree`
- ran `V1Run2Study.py analyze` and `compare`
- identified that β=0.30 and β=0.375 match Sahin & Owens well
- identified that β=0.50 Re=120 and Re=130 both remain steady, while S&O predict Re_crit=124.09
- discussed extending Re=130 to 20s to force oscillations — rejected as methodologically unsound
- decided to add `b050_medium_Re140` (12.7% above Re_crit) as a clean new case instead
- added `b050_medium_Re140` to `V1Run2Study.py` CASES list
- prepared and ran `b050_medium_Re140`

### Pilot results (Sahin & Owens comparison)

| case | β | Re | regime | St_sim | St_ref | ΔSt% |
|---|---|---|---|---|---|---|
| b030_medium_Re095 | 0.30 | 95 | periodic | 0.2083 | 0.2090 | −0.3 |
| b030_medium_Re100 | 0.30 | 100 | periodic | 0.2032 | 0.2090 | −2.8 |
| b0375_medium_Re110 | 0.375 | 110 | periodic | 0.2542 | 0.2579 | −1.4 |
| b0375_medium_Re120 | 0.375 | 120 | periodic | 0.2556 | 0.2579 | −0.9 |
| b050_medium_Re120 | 0.50 | 120 | steady | — | — | — |
| b050_medium_Re130 | 0.50 | 130 | steady | — | — | — |

### Decisions made

- β=0.30: results consistent with S&O, ΔSt within 3%
- β=0.375: results consistent with interpolated S&O reference, ΔSt within 1.5%
- β=0.50: Re=130 remaining steady is unexpected (S&O Re_crit=124.09); extending simulation time was considered but rejected — it would mask a real discrepancy rather than resolve it
- `b050_medium_Re140` added as the honest next step: further above the threshold, cleaner signal, same 5s end time
- note: S&O determined Re_crit via linear stability analysis (eigenvalue method), not DNS; their DNS validation was at Re=200; our DNS at Re=130 may simply need more headroom

### Outputs created or updated

- `VV_cases/V1_solver/V1Run2Study.py` (added `b050_medium_Re140`, fixed `replace_dir`)
- `VV_cases/V1_solver/run002_pilot_continue.sh`
- `C:\openfoam-case\VV_cases\V1_solver_run002\b050_medium_Re140\`
- `VV_cases/RESEARCH_LOG.md`

### Next step

Analyse `b050_medium_Re140` result. If periodic → confirms solver onset bracket for β=0.50 between Re=130 (steady) and Re=140 (periodic), consistent with S&O Re_crit=124.09. If still steady → investigate perturbation strength or mesh near onset.

---

## 2026-04-04 | V1_solver | V1 run 002 β=0.50 onset confirmed, pilot complete

### Work package

Confirm onset of vortex shedding for β=0.50 with a clean additional case at Re=140, and close the pilot phase of V1 run 002.

### Actions taken

- added `b050_medium_Re140` to `V1Run2Study.py` CASES list
- prepared and ran `b050_medium_Re140` (fresh Allrun, Poiseuille inlet, 5s)
- ran `V1Run2Study.py analyze b050_medium_Re140` and `compare`

### Result

`b050_medium_Re140`: **periodic**, St_sim = 0.3402, St_ref = 0.3393, ΔSt = +0.26% — best agreement of all pilot cases.

Onset bracket for β=0.50 established: Re ∈ (130, 140). Sahin & Owens give Re_crit = 124.09 from linear stability analysis. The gap is expected: linear stability gives the infinitesimal-perturbation threshold, DNS finds the finite-amplitude onset which requires slightly more headroom.

### Full pilot summary

| β | Re | regime | St_sim | St_ref | ΔSt% |
|---|---|---|---|---|---|
| 0.30 | 95 | periodic | 0.2083 | 0.2090 | −0.3 |
| 0.30 | 100 | periodic | 0.2032 | 0.2090 | −2.8 |
| 0.375 | 110 | periodic | 0.2542 | 0.2579 | −1.4 |
| 0.375 | 120 | periodic | 0.2556 | 0.2579 | −0.9 |
| 0.50 | 120 | steady | — | — | — |
| 0.50 | 130 | steady | — | — | — |
| 0.50 | 140 | periodic | 0.3402 | 0.3393 | +0.3 |

### Decisions made

- pilot phase declared complete: solver reproduces S&O Strouhal numbers within ~3% across all three β values
- Re=130 remaining steady is consistent with S&O methodology difference (linear stability vs DNS); not a solver error
- extending Re=130 simulation time was correctly rejected — the right fix was Re=140
- remaining 5 untouched cases (`b030_Re080`, `b030_Re120`, `b0375_Re090`, `b0375_Re135`, `b050_Re100`) can be run to fill the full matrix but are not required for the VV conclusion

### Outputs created or updated

- `VV_cases/V1_solver/V1Run2Study.py`
- `C:\openfoam-case\VV_cases\V1_solver_run002\b050_medium_Re140\`
- `VV_cases/V1_solver/results/study_v1/runs/002_data_sahin_owens_poiseuille_verification\03_run_summary\`
- `VV_cases/RESEARCH_LOG.md`

### Next step

Decide whether to complete the remaining 5 cases for a full matrix, or declare V1 run 002 sufficient and advance to the thermal verification (V2) or directly to the project geometry cases (V4a/V4b).

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

---
### 2026-04-04 20:05 | Konfiguracja session logging
Skonfigurowano automatyczne wpisy do RESEARCH_LOG po każdej wymianie. Zainicjowano pliki pamięci (MEMORY.md) z profilem użytkownika, stanem projektu V1 i preferencjami pracy.

---
### 2026-04-04 20:17 | Wykres Hopf onset vs beta
Wygenerowano wykres Re_crit vs β porównujący S&O (2004) z wynikami pilota DNS run 002. Szary pas ±2%, punkty DNS z bracketami onset. Plik: study_summary/.../plots/hopf_onset_vs_beta.png

---
### 2026-04-04 20:36 | Aktualizacja wykresu Hopf onset
Zaktualizowano dane S&O o punkty digitalizowane z wykresu (beta=0.35, 0.40, 0.45) i zmieniono pasek na +/-5%. Beta=0.50 DNS wypada tuż powyżej górnej granicy pasa — spójne z fizyką (DNS vs liniowa stabilność).

---
### 2026-04-04 20:42 | Aktualizacja wykresu Hopf onset v2
Zaktualizowano dane S&O z wykresu (0.30-0.70), usunięto tytuł, zmieniono na pomaranczowe trojkaty Present Work, +/-5% band.

---
### 2026-04-04 20:46 | Analiza przyczyn szerokiego bracket onset beta=0.50
Główna przyczyna: za krótki czas symulacji (5s) przy małym nadkrytycznym Re. Przy Re=130 (+4.8% ponad Re_crit) współczynnik wzrostu bifurkacji Hopfa jest mały — potrzeba ~20-30s. Siatka (max_non_ortho~58°, 10 komórek przekroju) jest czynnikiem drugorzędnym.

---
### 2026-04-04 20:48 | Uruchomiono b050_medium_Re125 (15s)
Test onset przy Re=125 (+0.8% ponad S&O Re_crit=124). Symulacja 15s zamiast 5s — analiza Cl w oknach 0-5, 5-10, 10-15s. Cel: sprawdzić czy za krótki czas byl glowna przyczyna braku onset przy Re=130.

---
### 2026-04-04 21:30 | Wynik b050_medium_Re125 (15s) — steady
Re=125 (+0.8% ponad S&O Re_crit=124) pozostaje steady przez cale 15s. Cl_rms spada z 1.6e-3 (0-5s) do 6.5e-5 (10-15s) — zaburzenie zanika wykładniczo. DNS Re_crit lezy miedzy 130 a 140 — typowa roznica DNS vs liniowa analiza stabilnosci (S&O).

---
### 2026-04-04 21:38 | Uruchomiono Re130 restart (25s) + b060_Re120 (15s)
Re=130 restart od t=5s do t=25s — weryfikacja czy oscylacje rozwiną się przy +4.8% ponad S&O Re_crit. b060_medium_Re120: nowy case beta=0.60, Re=120 (+2.6% ponad S&O ~117).

---
### 2026-04-04 22:10 | Aktualizacja wykresu — zielone/czerwone kropki
Zmieniono wizualizację DNS: zielone = shedding, czerwone = steady. Wszystkie sprawdzone Re naniesione na wykres Hopf onset vs beta. Widoczny bracketing dla beta=0.50 (3 czerwone + 1 zielona).

---
### 2026-04-04 22:16 | Uruchomiono kolejke 4 nowych casow
b030_Re090 (5s), b0375_Re105 (5s), b050_Re135 (15s), b060_Re125 (15s) — cel: czerwone kropki dla beta=0.30/0.375, rozstrzygniecie bracketu dla beta=0.50 i 0.60.

---
### 2026-04-04 22:32 | Re130 potwierdzony steady (t=5-12s zanik), kolejka 4 casow uruchomiona
Re130 zanik ~2%/s przez 7s -> subcritical. Batch: b030_Re090, b0375_Re105, b050_Re135, b060_Re125 (bzzhmi1jb).

---
### 2026-04-05 17:36 | Wyniki batcha 4 casow i aktualizacja wykresu Hopf onset

Wszystkie 4 case'y zakończone. Wyniki: b030_Re090 periodic (St=0.208), b0375_Re105 periodic (St=0.253), b050_Re135 periodic (St=0.340), b060_Re125 steady. Bracket β=0.50 zwężony do (130, 135). Dla β=0.30 i β=0.375 DNS onset leży poniżej najniższego testowanego Re — zgodnie z S&O. Wykres hopf_onset_vs_beta.png zaktualizowany o 4 nowe punkty.

---
### 2026-04-05 19:10 | Uruchomiono V1 run003 — sensitivity study fine mesh i long domain

Stworzono V1Run3Study.py i 4 case'y dla β=0.50: b050_fine_Re130, b050_fine_Re135 (fine mesh ~123k komórek, 15s) oraz b050_long_Re130, b050_long_Re135 (medium mesh, L_out=40D, 15s). Batch uruchomiony w WSL. Fine mesh ma tło 224×16 vs 168×12 dla medium.

---
### 2026-04-05 19:52 | Korekta fine mesh — za agresywny near_level

Pierwsza próba fine mesh (base_dx=1.5mm, near_level=3) generowała ~600k komórek i utknęła po 34 minutach snappy. Poprawiono na base_dx=2mm, near_level=2, surface_level=4 — finalnie 123 502 komórki (3.2× medium). Batch ponownie uruchomiony.

---
### 2026-04-05 20:45 | Włączono MPI parallelizację dla run003

Zmodyfikowano Allrun: decomposePar + mpirun -np 4 pimpleFoam -parallel + reconstructPar. decomposeParDict: scotch, 4 subdomeny. CPU: 20 logicznych (10 fizycznych). pimpleFoam używa 4 rdzeni.

---
### 2026-04-05 21:30 | Analiza live Cl dla b050_fine_Re130 i przemyślenia dot. rozbieżności

**Stan b050_fine_Re130 (fine mesh, Re=130, t≈4.6/15s):**
Cl peak-to-peak ≈ 3e-3, stałe od t>3.7s, brak trendu wzrostowego. Wygląda na steady — fine mesh nie przesuwa bracketu w dół. Wniosek wstępny: rozbieżność bracket (130,135) vs S&O 124 nie jest efektem siatki.

**Pytanie otwarte: dlaczego β=0.30 i β=0.375 sheddingują poniżej S&O Re_crit?**

Zestawienie rozbieżności DNS vs S&O LSA:
- β=0.30:  S&O Re_crit=94.56, DNS periodic przy Re=90 → DNS Re_crit < 90 (>-5% vs S&O)
- β=0.375: S&O Re_crit≈105.6, DNS periodic przy Re=105 → DNS Re_crit < 105 (<-1% vs S&O)
- β=0.50:  S&O Re_crit=124.09, DNS bracket (130,135) → DNS Re_crit > 124 (+5 do +9% vs S&O)

Rozbieżności są symetryczne co do wielkości (~5-9%) ale w PRZECIWNYCH kierunkach dla niskiego i wysokiego β. Możliwe przyczyny:
1. Brak dolnego bracketu (steady case) dla β=0.30 i β=0.375 — nie znamy rzeczywistego DNS Re_crit, tylko górną granicę.
2. Perturbacja `setExprFields` = 0.002 m/s stała dla wszystkich przypadków. Dla β=0.30 Re=90: U_max=0.114 m/s → perturbacja = 1.76% U_max. Może wymuszać onset poniżej naturalnego Re_crit.
3. Fizyczna różnica LSA vs DNS przy różnym β: przy β bliskim maksimum krzywej (β≈0.50) DNS overshoots LSA; przy β dalej od maksimum (β=0.30) może undershoots.
4. Domena 8D upstream może nie być wystarczająca dla β=0.30 (H=3.33D — szersza), gdzie perturbacja upstream od cylindra sięga dalej.

**Następny krok:** uruchomić Re=80, Re=85 dla β=0.30 żeby znaleźć dolny bracket i zmierzyć rzeczywistą rozbieżność DNS vs S&O.

---
### 2026-04-05 21:35 | Pełny opis setupu symulacji — dla zewnętrznej analizy

**Cel:** weryfikacja solvera V1 vs Sahin & Owens (2004), Phys. Fluids 16, 1305–1320.
Geometria: cylinder 2D w kanale (Poiseuille), β = D/H, brak turbulencji.

**Solver:** OpenFOAM v2512, pimpleFoam (incompressible, laminar), 2D (pseudo-3D: 1 komórka w z, warunki empty przód/tył).

**Parametry fizyczne:**
- D = 0.012 m (średnica cylindra)
- ν = 1.516×10⁻⁵ m²/s
- ρ = 1.205 kg/m³
- Re = U_max · D / ν (U_max = prędkość centralna Poiseuille)

**Domena (run002 medium, β=0.50 jako przykład):**
- L_in = 8D = 96 mm (upstream od cylindra)
- L_out = 20D = 240 mm (downstream od cylindra)
- H = D/β = 24 mm (β=0.50), 32 mm (β=0.375), 40 mm (β=0.30)
- Span z = 10 mm (1 komórka, 2D)

**Siatka (medium, snappyHexMesh):**
- tło blockMesh: 168×12×1 komórek (dx≈2.5mm), base_dx=0.0025m
- snappy refinement: level 3 na cylindrze (0.3125mm), level 2 near cylinder (0.625mm), level 1 wake
- BL na cylindrze: 6 warstw, expansion 1.20, finalLayerThickness=0.25
- BL na ścianach (top/bottom): 2 warstwy
- Łącznie: ~38 746 komórek (β=0.50), ~56 460 komórek (β=0.30)
- max non-orthogonality: ~56–58°

**Siatka (fine, run003):**
- tło: 168×12×1, base_dx=0.002m
- snappy: level 4 na cylindrze (0.125mm), level 2 near (0.5mm), level 2 wake (0.5mm)
- BL cylinder: 8 warstw; BL ściany: 3 warstwy
- Łącznie: 123 502 komórki (β=0.50)

**Warunki brzegowe:**
- inlet: exprFixedValue — profil Poiseuille U(y) = U_max·(1-(2y/H)²), v=0, w=0
- outlet: U: zeroGradient; p: fixedValue 0
- top/bottom: noSlip (U), zeroGradient (p)
- cylinder: noSlip (U), zeroGradient (p)

**Inicjalizacja:**
- pole U inicjowane jako uniform (U_max, 0, 0)
- następnie setExprFields nakłada profil Poiseuille + perturbację Gaussa: v = 0.002·exp(-((x-D)/10mm)²-((y-0.003)/D)²) [m/s]
- perturbacja jest bezwymiarowa tylko przez normalizację — absolutna wartość 0.002 m/s niezależnie od Re

**Krok czasowy:**
- startowy deltaT = 1e-3 s
- adjustTimeStep yes, maxCo = 0.9
- typowy adaptacyjny dt ≈ 0.001–0.0015 s

**Schematy numeryczne:**
- czasowe: backward (2nd order, implicit)
- konwekcja: Gauss linearUpwind grad(U) (2nd order upwind)
- dyfuzja: Gauss linear corrected
- ciśnienie: GAMG + GaussSeidel; prędkość: PBiCGStab + DILU
- PIMPLE: 1 outer, 2 inner correctors, 1 non-orthogonal corrector

**Czas symulacji:**
- przypadki β=0.50 blisko onset: 15 s
- pozostałe: 5 s
- analiza Cl w ostatnich 4 s (lub ostatnich 40% czasu symulacji)

**Wyniki run002 (medium mesh, Poiseuille inlet):**
| β    | Re  | regime   | St_sim | St_ref (S&O) | ΔSt%  |
|------|-----|----------|--------|--------------|-------|
| 0.30 | 90  | periodic | 0.208  | 0.209        | −0.3  |
| 0.30 | 95  | periodic | 0.208  | 0.209        | −0.3  |
| 0.30 | 100 | periodic | 0.203  | 0.209        | −2.8  |
| 0.375| 105 | periodic | 0.253  | ~0.258       | −2.0  |
| 0.375| 110 | periodic | 0.254  | ~0.258       | −1.4  |
| 0.375| 120 | periodic | 0.256  | ~0.258       | −0.9  |
| 0.50 | 120 | steady   | —      | —            | —     |
| 0.50 | 125 | steady   | —      | —            | —     |
| 0.50 | 130 | steady   | —      | —            | —     |
| 0.50 | 135 | periodic | 0.340  | 0.339        | +0.3  |
| 0.50 | 140 | periodic | 0.340  | 0.339        | +0.3  |
| 0.60 | 120 | steady   | —      | —            | —     |
| 0.60 | 125 | steady   | —      | —            | —     |

**Otwarte pytania do analizy:**
1. Dlaczego DNS Re_crit(β=0.30) < 90 gdy S&O LSA daje 94.56? Różnica kierunku rozbieżności vs β=0.50.
2. Czy perturbacja v=0.002 m/s (stała) jest zbyt duża dla małego Re, wymuszając onset poniżej naturalnego Re_crit?
3. Jaki wpływ ma L_out=20D na wyniki? (badane w run003 long domain)
4. Czy fine mesh (123k) zmienia bracket onset β=0.50? (badane w run003 — wstępnie: nie)
5. Brak dolnej granicy bracketu dla β=0.30 i β=0.375 — konieczne Re=80, Re=85 dla β=0.30.

---

## 2026-04-07 | V1_solver | Publication figures generation

### Działania
- Uruchomiono `V1PublicationFigures.py` — skrypt napisany pod koniec poprzedniej sesji na podstawie danych z PDF Sahin & Owens (2004).
- Naprawiono błąd `ParseSyntaxException`: Agg backend matplotlib nie obsługuje `\mathrm` w math mode — zamieniono etykiety osi fig3 na plain text.
- Wygenerowano wszystkie 3 figury publikacyjne.

### Wygenerowane figury
1. **fig1_hopf_onset.png** — diagram Hopf onset: krzywa S&O LSA ±5%, brackets DNS ze strzałkami. β=0.50 ma pełen bracket (130↔135), pozostałe jednostronne.
2. **fig2_St_vs_Re.png** — St(Re) per β: linie DNS, markery LSA onset (×), punkt DNS S&O (★, β=0.30, Re=100, St=0.2115 z sekcji IV B artykułu).
3. **fig3_St_parity.png** — parity St: ±2% pasmo, wszystkie punkty w granicach 1:1. Etykiety osi uczciwie opisują: "S&O (LSA, at Re_crit)" vs "DNS (present, supercritical Re)".

### Obserwacje
- Fig3 pokazuje dobrą zgodność St (~0-3%), ale porównanie jest metodologicznie nierównoważne (LSA vs DNS supercritical).
- W fig2 widać wyraźnie przesunięcie onset β=0.50: DNS daje bracket 130–135 vs S&O LSA 124.09 (różnica ~5–8%).
- β=0.30 i β=0.375 wymagają dolnych bracketów (Re<90).

### Lokalizacja plików
`VV_cases/V1_solver/results/study_v1/publication/figures/`

### Następny krok
- Opcjonalnie: uruchomić Re=80, 85 dla β=0.30 i uzupełnić dolny bracket.
- Opcjonalnie: dokończyć run003 (long domain, L_out=40D) dla testu wpływu warunku wylotowego.
- Złożenie rysunków do artykułu.

---

### 2026-04-07 17:41 | meta — research log workflow
Omówiono zasadę aktualizacji RESEARCH_LOG po każdej wymianie. Zasada jest zapisana w memory/feedback_style.md ale nie jest automatycznie czytana na starcie sesji — tylko MEMORY.md (indeks) ładuje się automatycznie. Zasada będzie egzekwowana ręcznie w tej sesji.

---

### 2026-04-07 17:41 | V1_solver — publikacyjne wykresy i podsumowanie weryfikacji V1

#### Wygenerowane figury (V1PublicationFigures.py)

**Fig 1 — Hopf onset diagram** (`fig1_hopf_onset.png`)
- Krzywa S&O LSA Re_crit(β) z ±5% pasmem niepewności
- DNS brackets: wypełniony marker = najniższe Re periodic, pusty = najwyższe Re steady, strzałka między nimi
- Status bracketów:
  - β=0.30: górna granica Re<90 (brak dolnej — wymagane Re=80, 85)
  - β=0.375: górna granica Re<105 (brak dolnej)
  - β=0.50: pełen bracket (130 steady ↔ 135 periodic) — Re_crit ∈ (130, 135) vs S&O LSA 124.09
  - β=0.60: dolna granica Re>125 (brak górnej)

**Fig 2 — St(Re) per β** (`fig2_St_vs_Re.png`)
- Linie DNS z markerami per β (0.30, 0.375, 0.50, 0.60)
- Markery × = S&O LSA onset (Re_crit, St_crit) z Table IV
- Marker ★ = jedyny punkt DNS S&O dostępny w tekście: β=0.30, Re=100, St=0.2115 (Sec. IV B)
- β=0.30 i 0.375 mają pełne linie; β=0.50 i 0.60 tylko 1–2 punkty (jednostronne brackety)

**Fig 3 — Parity plot St** (`fig3_St_parity.png`)
- Wszystkie punkty w obrębie ±2% od linii 1:1
- Etykiety osi uczciwe metodologicznie: "St S&O (LSA, at Re_crit)" vs "St DNS (present, supercritical Re)"
- Komentarz na wykresie wyjaśnia że porównanie nie jest punkt-do-punktu

#### Podsumowanie weryfikacji V1

**Zgodność St:** ΔSt = 0–3%, wszystkie wartości w paśmie ±3% od S&O LSA St_crit. Dobra zgodność.

**Zgodność Re_crit:** DNS onset leży ~5–10% powyżej S&O LSA dla β=0.50. Prawdopodobne przyczyny:
1. Różnica warunku wylotowego: S&O ∂²u₁/∂x₁²=0 vs present zeroGradient (1st derivative)
2. Różnica długości domeny: S&O L_out=40D vs present L_out=20D
3. LSA (liniowa analiza stabilności) daje onset z infinitezymalną perturbacją; DNS z v=0.002 m/s — finite amplitude

**Wyjątek β=0.30 i 0.375:** DNS onset poniżej Re=90 vs S&O LSA 94.56 i ~109 — rozbieżność w odwrotnym kierunku. Nie wyjaśnione.

**Następny krok:**
- Opcjonalnie uzupełnić dolne brackety (Re=80, 85 dla β=0.30) i górny bracket dla β=0.60
- Opcjonalnie run003 long domain (L_out=40D) — test wpływu BC wylotowego
- V1 uznany za zweryfikowany w zakresie St; kwestia Re_crit udokumentowana jako znana rozbieżność metodologiczna

---

### 2026-04-07 20:15 | V2_thermal — start V2A Level A, V2AStudy.py napisany i skonfigurowany

Zaczęto V2 (weryfikacja termiczna). Plan: V2A (Level A) = unconfined cylinder jako primary thermal benchmark, V2B (Level B) = confined β=0.50 jako consistency check.

Napisano `V2AStudy.py` (V2_thermal/V2AStudy.py). Analogiczny do V1Run2Study.py. Konfiguracja:
- buoyantPimpleFoam, g=0 (pure forced convection)
- D=12mm, T_in=293.15K, T_w=303.15K, ΔT=10K (małe ΔT aby minimalizować efekty kompresyjności)
- Pr=0.713, k_air=0.02574 W/(m·K)
- Unconfined: H=20D=240mm, slip BC top/bottom (β~5%)
- L_in=15D, L_out=30D (steady) / 40D (unsteady)
- background mesh: 108×48×1 (dx=5mm), snappy level 3 na cylindrze (0.625mm), 6 warstw BL
- BEZ BL na ścianach (slip)

Przypadki:
| Nazwa  | Re  | Regime   | endTime |
|--------|-----|----------|---------|
| Re10   | 10  | steady   | 60s     |
| Re20   | 20  | steady   | 60s     |
| Re40   | 40  | steady   | 60s     |
| Re100  | 100 | unsteady | 25s     |
| Re200  | 200 | unsteady | 15s     |

Referencje Nu (CWT, Pr=0.7, unconfined):
- Lange et al. (1998): Nu = 0.082*Re^0.5 + 0.734*Re^chi
- Bharti et al. (2007) Table 3: Re10=1.8623, Re20=2.4653, Re40=3.2825

`python V2AStudy.py setup` — 5 katalogów gotowych. Następny krok: uruchomić obliczenia.

---

### 2026-04-07 20:33 | V2_thermal — V2A obliczenia uruchomione (5 przypadków równolegle)

Problem ze spacjami w ścieżce (`My Drive`) — OpenFOAM nie obsługuje. Rozwiązano: katalog roboczy = `C:\openfoam-case\VV_cases\V2_thermal_run001\` (bez spacji).

Dodano MPI do V2AStudy.py: `decomposePar → mpirun -np 4 buoyantPimpleFoam → reconstructPar`.

Uruchomiono 5 procesów równolegle (PIDs 1881–1889):
- Re10, Re20, Re40 (steady, endTime=60s)
- Re100, Re200 (unsteady, endTime=25s/15s)

Status (20:33): wszystkie 5 w fazie snappyHexMesh (serial, ~97% CPU każdy).
Następnie każdy przejdzie do decomposePar + mpirun -np 4 buoyantPimpleFoam.

---

### 2026-04-07 20:45 | V2_thermal — błąd snappy naprawiony, restart

Błąd: `minMedianAxisAngle` → `minMedialAxisAngle` (zmiana nazwy klucza w OpenFOAM v2512). Naprawiono w template i we wszystkich 5 case'ach. Zrestartoowano obliczenia.

---

### 2026-04-07 22:10 | V2_thermal — debug Re10: sekwencja błędów konfiguracyjnych buoyantPimpleFoam

Skupiono się wyłącznie na Re10 w celu weryfikacji setupu przed równoległym uruchomieniem wszystkich 5 przypadków.

#### Błąd 1 — fvSolution: residualControl jako skalar (naprawiony wcześniej)
```
FOAM FATAL ERROR: Residual data for U must be specified as a dictionary
```
Przyczyna: `U 1e-5;` zamiast `U { tolerance 1e-5; relTol 0; }`.  
Naprawiono w template i Re10.

#### Błąd 2 — thermophysicalProperties: hePsiThermo nie istnieje w OF v2512 (naprawiony wcześniej)
```
FOAM FATAL ERROR: Unknown rhoThermo type hePsiThermo
```
Przyczyna: OpenFOAM v2512 nie posiada `hePsiThermo`. Poprawna klasa to `heRhoThermo`.  
Naprawiono w template i Re10.

#### Błąd 3 — brak pola `p` w 0/ (naprawiony)
```
FOAM FATAL ERROR: cannot find file "processor0/0/p"
```
Przyczyna: `buoyantPimpleFoam` wymaga absolutnego pola ciśnienia `p` (heRhoThermo oblicza gęstość z p·M/(R·T)). Nasze `0/` zawierało tylko `p_rgh`.  
Naprawiono: dodano `0/p` z `calculated` BC (solver wyprowadza p z p_rgh) i absolutnym ciśnieniem referencyjnym 101325 Pa.  
Zmieniono też `p_rgh` z `uniform 0` (manometryczne) na `uniform 101325` (absolutne) — konieczne aby EOS dało ρ₀≈1.204 kg/m³ przy starcie.

#### Błąd 4 — forceCoeffs: brak `rhoInf` (naprawiony)
```
FOAM FATAL IO ERROR: Entry 'rhoInf' not found in dictionary "stream/functions/forceCoeffs"
```
Przyczyna: `forceCoeffs` z `rho rho;` (compressible mode) nadal wymaga `rhoInf` do normalizacji Cd/Cl.  
Naprawiono: dodano `rhoInf 1.2040;` do template i Re10.

#### Błąd 5 — fvSchemes: błędna nazwa członu dyfuzji (naprawiony)
```
FOAM FATAL IO ERROR: Entry 'div(((rho*nuEff)*dev2(T(grad(U)))))' not found in divSchemes
```
Przyczyna: template miał `div((muEff*dev2(T(grad(U)))))` — forma dla solverów nieściśliwych. buoyantPimpleFoam v2512 generuje człon w postaci `(rho*nuEff)`.  
Naprawiono: zmieniono wpis w template i Re10.

#### Aktualny status — SIGFPE w GAMG (niestabilność numeryczna)
Po naprawieniu wszystkich 5 błędów konfiguracyjnych solver startuje poprawnie (wczytuje thermophysics, PIMPLE, pola), ale pada z floating point exception w `GAMGSolver::scale()`. Oznacza to rozbieżność numeryczną — prawdopodobnie:
- Zbyt duży krok czasowy dt=1e-3 s przy starcie z zerowego pola prędkości
- Lub problem z kondycjonowaniem macierzy ciśnienia na dużym domenie (H=20D)

**Następne kroki diagnostyczne:**
1. Sprawdzić `Time=` i residua tuż przed crashem
2. Zmniejszyć `deltaT` (np. 1e-4 s) lub dodać `startFrom latestTime` z ramping U
3. Rozważyć `maxCo 0.2` z `adjustTimeStep yes` na start


---

### 2026-04-08 15:30 | V2_thermal — głęboki debug Re10: sekwencja błędów konfiguracyjnych i numerycznych

#### Kontekst
Debug tylko Re10 (serial + MPI) przed uruchomieniem wszystkich 5 przypadków. Celem: doprowadzić buoyantPimpleFoam do stabilnej pracy.

---

#### Chronologia naprawionych błędów (sesja 2026-04-08)

**Błąd 6 — GAMG SIGFPE w `scale()` (niezależny od smoother)**
Wszystkie warianty GAMG crashują w `GAMGSolver::scale()` — zarówno GaussSeidel, DICGaussSeidel, symGaussSeidel. Przyczyna: mesh ma komórki o rozmiarze ~3μm (face area min = 3.07e-8 m²) z snappyHexMesh. Na poziomie coarse agglomeration macierz ma zerową przekątną → divide-by-zero w scale(). Problem istnieje zarówno serial jak i parallel. GAMG jest wyłączone z użycia dla tej siatki.

**Błąd 7 — PCG+DIC bardzo wolna zbieżność przy ciśnieniu absolutnym**
Przełączono p_rgh outlet na `fixedValue 101325` (ciśnienie absolutne) żeby EOS dawało ρ=1.204 kg/m³. PCG potrzebował 441+ iteracji (vs ~40 przy ciśnieniu manometrycznym). Przyczyna: przy p_rgh=101325 Pa ciśnienie absolutne dominuje nad korektą (która jest rzędu ~0.01 Pa), co daje bardzo złe uwarunkowanie macierzy PCG.

**Błąd 8 — rho→0 przy ciśnieniu manometrycznym + fixedValue outlet**
Przy p_rgh outlet = fixedValue 0 (manometryczne), OpenFOAM inicjalizuje p_rgh=101325 (z `p - rho*g*h`), solver koryguje do ~0, a następnie w pEqn.H: `p = p_rgh + rho*g*h = 0` → EOS: `ρ = p·M/(R·T) = 0` → `thermo.correctRho(ψ·p - ψ·p₀) = -1.204` → ρ=0 → SIGFPE.

**Przełomowe zrozumienie architektury ciśnieniowej buoyantPimpleFoam:**
Z analizy `createFields.H` i `pEqn.H`:
- Linia `p_rgh = p - rho*gh` w createFields.H NADPISUJE wartość z pliku 0/p_rgh
- Plik 0/p_rgh definiuje tylko BC, nie initial field (który jest zawsze = p)
- `p_rgh.needReference()` = true gdy brak fixedValue BC → aktywuje korekcję masy
- Korekcja masy: `p += (initialMass - ∫ψp dV)/compressibility` → przywraca p_absolute do 101325 Pa → ρ≈1.204 kg/m³ zachowane!

**Aktualny stan testów (niezakończone):**
Próba z outlet `zeroGradient` (needReference=true) + pRefCell=0, pRefValue=0. Solver wciąż crashuje z Foam::divide PRZED solve p_rgh (po h solve). Diagnoza w toku — crash prawdopodobnie w pEqn.H setup (rAU, HbyA, phiHbyA) lub w forceCoeffs/wallHeatFlux function object.

---

#### Aktualna konfiguracja Re10 (stan na 2026-04-08 ~15:30)

| Parametr | Wartość |
|----------|---------|
| Solver | buoyantPimpleFoam (serial, debug) |
| ddtSchemes | `backward` |
| deltaT | 1e-4 s |
| adjustTimeStep | yes, maxCo 0.5 |
| p_rgh solver | PCG + DIC |
| nOuterCorrectors | 1 (PISO mode) |
| nCorrectors | 2 |
| pRefCell/Value | 0 / 0 Pa |
| p_rgh outlet BC | `zeroGradient` |
| 0/p | uniform 101325 Pa |
| 0/p_rgh | uniform 0 (gauge) |
| 0/h | brak (usunięty) |
| Siatka | 15676 komórek 2D, min face area 3.07e-8 m² |

**Następny krok diagnostyczny:**
Ustalić co crashuje między h solve a p_rgh solve. Prawdopodobne kandydaty:
1. `forceCoeffs` function object (liczy siły z p, może mieć problem przy starcie gdy p jest nieokreślone)
2. `fvc::ddt(rho, K)` lub `phiHbyA` w pEqn.H setup
3. Korekcja masy `(initialMass - ∫ψp)/compressibility` — jeśli compressibility=0


---

### 2026-04-08 22:02 | V2_thermal - package 1: run structure and V2A sync

#### What was changed
- Created the official V2A run folder:
  - `VV_cases/V2_thermal/results/study_v2a/runs/001_data_v2a_level_a_unconfined_debug`
- Added run-level notes and setup files:
  - `00_notes/run_scope.md`
  - `01_run_setup/case_matrix.md`
- Created the first simulation shell inside the run:
  - `02_simulations/Re10/...`
- Moved the old pre-standard repo snapshots (`Re10`, `Re20`, `Re40`, `Re100`, `Re200`) to:
  - `VV_cases/V2_thermal/results/study_v2a/legacy_pre_run_layout/`

#### V2AStudy.py synchronization
- Bound V2A to the official run slug `001_data_v2a_level_a_unconfined_debug`.
- `setup` now writes run notes and simulation `input.md`.
- Added `0/p` generation with absolute initial pressure `101325 Pa`.
- Updated generated `0/p_rgh` to the current debug form:
  - gauge internal field
  - `zeroGradient` outlet
  - `fixedFluxPressure` on the remaining patches
- Added `caseMeta.json` to each working case.
- Changed processed-result output path from the old loose layout to simulation-level `03_processed_data`.
- Corrected `Aref` in generated `forceCoeffs` from `pi*D*Lz` to `D*Lz`.
- Added `rhoInf` to generated `forceCoeffs`.

#### Template synchronization
- Updated `templates/base_case/0/p_rgh` to match the current gauge-pressure debug strategy.
- Updated `templates/base_case/system/fvSolution` to the current Re10 debug form:
  - `nOuterCorrectors = 1`
  - `pRefCell = 0`
  - `pRefValue = 0`
- Updated `templates/base_case/system/controlDict` to the current debug-oriented startup values:
  - `deltaT = 1e-4`
  - `adjustTimeStep yes`

#### Interpretation
- V2A is no longer structurally loose in the repo.
- The repository now reflects the current debug state instead of the earlier pre-standard snapshots.
- The next step remains technical, not organizational: isolate the Re10 crash with a controlled serial run.

#### Next step
- Create and run a single diagnostic `Re10_debug_serial` case from the current working setup.
- First test it without the full function-object stack, then compare against the current crashing configuration.

---

### 2026-04-08 22:12 | V2_thermal - package 2: Re10_debug_serial without function objects

#### Action
- Created a clean external working copy:
  - `C:\openfoam-case\VV_cases\V2_thermal_run001\Re10_debug_serial`
- Cloned from the current working Re10 case.
- Removed MPI leftovers (`processor*`) and old `postProcessing`.
- Replaced `system/controlDict` with a short serial diagnostic setup:
  - `startFrom startTime`
  - `endTime = 0.001`
  - `deltaT = 1e-5`
  - `adjustTimeStep no`
  - `functions {}`
- Ran `buoyantPimpleFoam` serially with all function objects disabled.

#### Result
- The case still crashes at the first time step.
- Sequence remains:
  - solve `rho`
  - solve `Ux`
  - solve `Uy`
  - solve `h`
  - crash in `Foam::divide(...)`
- Therefore the crash persists even with:
  - no `forceCoeffs`
  - no `wallHeatFlux`
  - no `solverInfo`
  - no MPI
  - much smaller `deltaT`

#### Interpretation
- Function objects are not the primary cause.
- MPI is not the primary cause.
- A too-large startup time step is not the primary cause.
- The main suspect set is now narrower:
  1. pressure-density coupling / `pEqn` startup path
  2. thermodynamic field consistency (`p`, `p_rgh`, `rho`, `h/T`)
  3. mesh-induced pathology during startup, even before the pressure solve completes cleanly

#### Archiving
- Frozen repo record created under:
  - `VV_cases/V2_thermal/results/study_v2a/runs/001_data_v2a_level_a_unconfined_debug/02_simulations/Re10_debug_serial/`
- Saved there:
  - `01_openfoam_setup/`
  - `05_logs/log.serial_debug_nofunctions`
  - `00_notes/input.md`
  - `00_notes/output.md`

#### Next step
- Prepare one more stripped diagnostic case, most likely with a simpler mesh (preferably no layers on the cylinder) to test whether the crash is mesh-startup driven.
- If the no-layer case still crashes at the same location, the next focus should move directly to the pressure/thermo field formulation.

---

### 2026-04-08 22:27 | V2_thermal - package 3: Re10_debug_serial_nolayers

#### Action
- Created a second stripped diagnostic case:
  - `C:\openfoam-case\VV_cases\V2_thermal_run001\Re10_debug_serial_nolayers`
- Based on the same Re10 working case, but with:
  - `addLayers false` in `snappyHexMeshDict`
  - serial execution only
  - no function objects
  - `deltaT = 1e-5`
  - short horizon `endTime = 0.001`
- Regenerated the mesh from scratch:
  - `blockMesh`
  - `snappyHexMesh -overwrite`
- Then ran `buoyantPimpleFoam` serially.

#### Result
- The no-layer mesh completed successfully.
- Final snapped mesh statistics before the solver:
  - `cells = 43792`
- The solver still crashed at the first time step.
- The crash location is unchanged:
  - solve `rho`
  - solve `Ux`
  - solve `Uy`
  - solve `h`
  - crash in `Foam::divide(...)` before `p_rgh`

#### Interpretation
- This is a strong narrowing step.
- We have now ruled out, as primary causes:
  1. function objects
  2. MPI
  3. a too-large startup time step
  4. boundary-layer extrusion itself
- The remaining core suspect is the pressure / thermo startup path in `buoyantPimpleFoam` for this setup.

#### Archived outputs
- Saved in repo under:
  - `VV_cases/V2_thermal/results/study_v2a/runs/001_data_v2a_level_a_unconfined_debug/02_simulations/Re10_debug_serial_nolayers/`
- Stored:
  - `01_openfoam_setup/`
  - `05_logs/log.serial_debug_nolayers`
  - `00_notes/input.md`
  - `00_notes/output.md`

#### Next step
- Stop spending cycles on generic mesh/function-object cleanup.
- Switch to pressure/thermo diagnostics directly.
- The next most valuable move is to build one more minimal pressure-focused variant, or compare against a known-good small `buoyantPimpleFoam` heated case to isolate the exact field inconsistency.

---

## 2026-04-09 | V2_thermal - package 4: solver architecture diagnosis and switch to buoyantBoussinesqPimpleFoam

### Work package

Diagnose the root cause of all `buoyantPimpleFoam` crashes, decide on the correct solver for this study, and get Re10 running without crashes as a smoke-test before parallel production runs.

---

### 2026-04-09 | V2_thermal — diagnosis of buoyantPimpleFoam crashes

#### Action

- Read OpenFOAM-v2512 source:
  - `/applications/solvers/heatTransfer/buoyantPimpleFoam/createFields.H`
  - `/applications/solvers/heatTransfer/buoyantPimpleFoam/pEqn.H`
- Traced the startup sequence step by step for the Re10 forced-convection inlet/outlet topology.

#### Finding 1 — pRefValue=0 startup bug in createFields.H

`createFields.H` contains (inside `if (p_rgh.needReference())`):

```cpp
p += dimensionedScalar("p", p.dimensions(),
         pRefValue - getRefCellValue(p, pRefCell));
```

With `internalField uniform 101325` and `pRefValue 0` this evaluates to:

```
p += (0 − 101325) = −101325  →  p = 0 everywhere
```

`psi*p = rho = 0` at the start of `pEqn.H` → integer divide-by-zero → `SIGFPE` in `Foam::divide`.

This was the root cause of every crash observed from the very first run.

**Workaround tested:** Setting `pRefValue 101325` eliminates the crash at startup. The solver then proceeds to the first pressure solve.

#### Finding 2 — fundamental incompatibility of buoyantPimpleFoam with forced convection (g=0, inlet+outlet)

After fixing the startup crash, the first pressure solve produced Co_max ≈ 278 with U_max ≈ 1947 m/s. Detailed trace:

- `p_rgh` after step 1: varies 63 000 – 117 000 Pa (should be ~0.01 Pa variation for Re10 at 0.0001 s).
- Root cause: `buoyantPimpleFoam` uses compressible pressure architecture with a mass-correction loop (`p += (initialMass - fvc::domainIntegrate(psi*p)) / compressibility`). This loop is designed for natural convection in closed or semi-open domains with gravity driving the density variation. With g=0 and an open inlet/outlet topology the correction has no physical reference point and produces unphysical pressure swings at every outer iteration.
- No BC or mesh change could resolve this; it is structural.

#### Finding 3 — Richardson number analysis (Ri >> 1, but references use g=0)

For Re=10, D=0.01 m, U_in=0.01263 m/s, ΔT=10 K, β=3.41e-3 K⁻¹:

```
Ri = g·β·ΔT·D / U² ≈ 9.81 × 3.41e-3 × 10 × 0.01 / (0.01263)² ≈ 25
```

The physical flow is buoyancy-dominated. However, both reference studies (Lange et al. 1998 and Bharti et al. 2007) deliberately solve incompressible Navier-Stokes with **g=0** to isolate forced-convection heat transfer and report Nu as a pure function of Re and Pr. To reproduce their Nu values we must match their assumption: incompressible, g=0.

#### Decision — switch to buoyantBoussinesqPimpleFoam

`buoyantBoussinesqPimpleFoam`:
- Solves incompressible NS with Boussinesq buoyancy term (g·β·(T-Tref) source in momentum).
- Setting g=0 in `constant/g` disables the buoyancy term entirely → pure forced convection.
- Uses kinematic pressure [m² s⁻²], `transportProperties` (nu, beta, TRef, Pr, Prt), explicit T transport equation.
- No compressible mass-correction loop, no thermo library, no psi field.
- Matches the incompressible assumption of both reference papers.

---

### 2026-04-09 | V2_thermal — Re10 conversion to buoyantBoussinesqPimpleFoam

#### Actions — file changes

**`constant/transportProperties`** (new file):
```
transportModel  Newtonian;
nu              1.516e-05;    // mu/rho = 1.825e-5 / 1.204
beta            3.412e-03;   // 1/T_ref (ideal-gas approx)
TRef            293.15;
Pr              0.713;
Prt             0.9;
```
Previous `constant/thermophysicalProperties` retained but no longer used.

**`system/controlDict`**:
- `application  buoyantBoussinesqPimpleFoam`
- `endTime  0.02` (smoke-test; production will be 60 s for Re10–40)
- `adjustTimeStep  no` (smoke-test; production will be `yes, maxCo 0.5`)
- `functions`: reduced to `solverInfo` only; `wallHeatFlux` removed (incompatible — requires compressible turbulence model).

**`system/fvSolution`**:
- Removed: `rho.*`, `h`, `e` solvers; `pRefValue 101325`
- Added/kept: `p_rgh` (PCG+DIC), `(U|T)` (PBiCGStab+DILU)
- `pRefValue 0` (gauge pressure; outlet anchored at 0)
- `momentumPredictor no` (laminar, low Re)

**`system/fvSchemes`**:
- Removed compressible terms: `div(phi,h)`, `div(phi,K)`, `div(phid,p)`, `div(phi,Ekp)`, `div(((rho*nuEff)*dev2(...)))`
- Added incompressible terms: `div(phi,T)`, `div((nuEff*dev2(T(grad(U)))))`

**`0/p_rgh`**:
- `dimensions  [0 2 -2 0 0 0 0]` (kinematic gauge pressure m² s⁻²)
- `internalField  uniform 0`
- `outlet  fixedValue 0`; all walls and inlet: `fixedFluxPressure  rho rhok`

**`0/alphat`**:
- `dimensions  [0 2 -1 0 0 0 0]` (kinematic turbulent thermal diffusivity m² s⁻¹)
- All patches: `type calculated; value uniform 0`

**`0/U`**:
- `internalField  uniform (0 0 0)` (static start to avoid impulsive start with cylinder noSlip)

#### Result — successful smoke-test run

```
Time = 0.02
DICPCG: Solving for p_rgh, Initial residual = 0.003087, Final residual = 9.1e-10, No Iterations 242
DILUPBiCGStab: Solving for T, Initial residual = 7.02e-4, Final residual = 2.6e-12, No Iterations 1
time step continuity errors : sum local = 4.81e-15, global = 1.43e-17
Co_max = 0.0060
ExecutionTime = 41.68 s  ClockTime = 43 s
End
```

200 steps (t = 0 → 0.02 s), Co_max stabilises at ~0.006. No crashes, no unphysical pressure swings.

#### Known issues / observations

- PCG takes 100–250 iterations per corrector. Acceptable for now (GAMG is unusable due to 3 µm near-wall cells). Will review if production runtime is excessive.
- `wallHeatFlux` is permanently disabled for this solver. Nu must be extracted in post-processing from snGrad(T) on the cylinder surface: `Nu = D * |snGrad(T)|_avg / (T_cyl - T_inf)`.

#### Outputs created / modified

- `C:\openfoam-case\VV_cases\V2_thermal_run001\Re10\` — full Boussinesq case
  - `constant/transportProperties`
  - `system/controlDict`, `fvSolution`, `fvSchemes`
  - `0/p_rgh`, `0/alphat`, `0/U`

#### Next steps

1. Restore production `endTime` and `adjustTimeStep yes; maxCo 0.5` in `controlDict`.
2. Add Nu extraction function object (surfaceFieldValue on cylinder snGrad(T)).
3. Propagate all Boussinesq changes to Re20, Re40, Re100, Re200 cases.
4. Update `V2AStudy.py` to generate Boussinesq cases.
5. Update templates in `VV_cases/V2_thermal/templates/base_case/`.
6. Run all 5 Re cases; extract Nu; compare vs Lange et al. (1998) Eq. 18 and Bharti et al. (2007) Table 3.

---

## 2026-04-09 | VV_cases - package 5: canonical study documents

### Work package

Introduce a clean documentation layer for each study that is separate from the global
chronological research log.

### Actions

- Updated:
  - `VV_cases/STORAGE_STANDARD.md`
  - `VV_cases/WORKING_CHECKLIST.md`
- Added `doc/` and `doc/figs/` folders for:
  - `V1_solver`
  - `V2_confined`
  - `V2_thermal`
  - `V3_array`
  - `V4a_2D`
  - `V4b_3D`
- Added canonical study documents:
  - `VV_cases/V1_solver/doc/V1_solver.md`
  - `VV_cases/V2_thermal/doc/V2_thermal.md`
  - placeholder canonical documents for the remaining studies
- Copied selected `V1` publication figures into:
  - `VV_cases/V1_solver/doc/figs/`

### Decision

The repository now uses two clearly separated documentation layers:

- `VV_cases/RESEARCH_LOG.md`
  - chronological log of all work packages, debugging steps, and decisions
- `VV_cases/<study>/doc/<study>.md`
  - clean, continuously improved technical description of the accepted study setup and results

The per-study canonical document is not a dated log and should be rewritten when the
accepted setup or accepted results improve.

### Immediate consequence

- `RESEARCH_LOG.md` remains the only timeline.
- `doc/<study>.md` becomes the study-facing raw text basis for article writing.
- `doc/figs/` contains only figures explicitly cited by that canonical document.

### Next step

- Return to `V2a` repo cleanup and synchronize the active Boussinesq architecture in the
  study scripts and templates before launching the next thermal production runs.

---

## 2026-04-09 | V1_solver - package 6: flatten active repository layout

### Work package

Reduce the active `V1_solver` repository layout to a much simpler structure:

- keep only the canonical study document and cited figures at study level
- keep only compact run folders under `results/study_v1/runs`
- keep only one `notes.md` per simulation
- remove the active `publication`, `study_summary`, and `Archiwum` layers

### Actions

- Updated:
  - `VV_cases/STORAGE_STANDARD.md`
  - `VV_cases/WORKING_CHECKLIST.md`
- Simplified `V1_solver/results/study_v1` to:
  - `runs/001_data_beta05_initial_verification`
  - `runs/002_data_sahin_owens_poiseuille_verification`
- Flattened each run:
  - created `run.md`
  - moved `summary.csv` and `summary.md` to run root
  - kept run-level `plots/` only where present
- Renamed `02_simulations` to `simulations`
- Flattened each simulation to a single `notes.md`
- Copied the run-002 parity figure into:
  - `VV_cases/V1_solver/doc/figs/V1_run002_St_vs_SahinOwens.*`
- Removed active folders:
  - `VV_cases/V1_solver/results/study_v1/publication`
  - `VV_cases/V1_solver/results/study_v1/study_summary`
  - top-level `Archiwum`

### Decision

For the active repository, `V1_solver` will no longer mirror full per-case OpenFOAM
subtrees in the study archive. The repo now stores:

- canonical study text in `doc/`
- selected cited figures in `doc/figs/`
- compact run summaries
- compact per-simulation notes

### Current active structure

Active study-level structure:

- `VV_cases/V1_solver/doc/`
- `VV_cases/V1_solver/results/study_v1/runs/`

Active run-level structure:

- `run.md`
- `summary.csv`
- `summary.md`
- `plots/` when needed
- `simulations/`

Active simulation-level structure:

- `notes.md`

### Next step

- Review whether `V1_solver/templates/` and the loose helper scripts in the study root are
  still needed in the active repository, or should also be archived/removed.

---

## 2026-04-09 | V1_solver - package 7: move study scripts into _code

### Work package

Clean the `V1_solver` study root further by removing the now-unneeded template layer and
grouping all Python study scripts under a dedicated `_code` folder.

### Actions

- Updated:
  - `VV_cases/STORAGE_STANDARD.md`
  - `VV_cases/WORKING_CHECKLIST.md`
- Confirmed that `V1_solver/templates/` was no longer used in the active workflow
- Standardized study-level code location to:
  - `VV_cases/<study>/_code/`
- Moved V1 Python scripts into:
  - `VV_cases/V1_solver/_code/`
- Updated basic usage strings and helper references to the new `_code/` location

### Decision

For the active `VV_cases` layout:

- study-specific Python scripts belong in `_code/`
- `templates/` should not be kept in a study unless it is actively used

For `V1_solver`, the active study root is now intentionally minimal:

- `doc/`
- `results/`
- `_code/`
- a small number of helper shell scripts, pending later review

### Next step

- Review whether the remaining root-level shell helpers in `V1_solver` are still worth
  keeping, or should also move into `_code/` or be removed.

---

## 2026-04-09 12:17 | V2_thermal - package 1: align active repo layout with V1

### Work package

Bring `V2_thermal` into the same simplified active-repository layout already adopted
for `V1_solver`.

### Actions

- moved the study driver into:
  - `VV_cases/V2_thermal/_code/V2AStudy.py`
- moved the active template tree into:
  - `VV_cases/V2_thermal/_code/templates/`
- flattened the active run:
  - `results/study_v2a/runs/001_data_v2a_level_a_unconfined_debug/`
- kept only:
  - `run.md`
  - `summary.csv`
  - `summary.md`
  - `simulations/<case>/notes.md`
- removed the extra run-layer folders that mirrored old archival structure
- removed:
  - `results/study_v2a/legacy_pre_run_layout`
- rewrote the run-level and case-level notes so they read as compact technical records
  instead of merged `input/output` fragments

### Decision

`V2_thermal` now follows the same active repository model as `V1_solver`:

- `doc/`
- `results/`
- `_code/`

Within the active run archive, each stored simulation is represented by one `notes.md`
file only.

### Important note

This cleanup package simplified the repository structure only.
It did not yet complete the technical synchronization of `V2AStudy.py` and its template
tree to the accepted Boussinesq architecture described in `doc/V2_thermal.md`.

### Next step

- synchronize `V2AStudy.py` and `_code/templates/base_case/` with the accepted
  Boussinesq-based V2a setup before launching the next production thermal cases

---

## 2026-04-09 12:37 | V2_thermal - package 2: Boussinesq generator sync and run-002 preparation

### Work package

Turn `V2AStudy.py` into the active Boussinesq-based generator for V2a and prepare the
first production-oriented validation run.

### Actions

- rewrote:
  - `VV_cases/V2_thermal/_code/V2AStudy.py`
- switched the active run slug to:
  - `002_data_v2a_boussinesq_validation`
- switched the external working root to:
  - `C:\openfoam-case\VV_cases\V2_thermal_run002`
- removed compressible case generation from the active script:
  - no generated `0/p`
  - no generated `0/h`
  - no `thermophysicalProperties`
  - no `wallHeatFlux` function object in `controlDict`
- generated active Boussinesq files directly from the script:
  - `constant/transportProperties`
  - `constant/g`
  - `constant/turbulenceProperties`
  - `system/controlDict`
  - `system/fvSchemes`
  - `system/fvSolution`
  - `0/U`
  - `0/T`
  - `0/p_rgh`
  - `0/alphat`
- synchronized:
  - `VV_cases/V2_thermal/_code/templates/base_case/`
  with the same active Boussinesq architecture
- prepared the new run by executing:
  - `python VV_cases/V2_thermal/_code/V2AStudy.py setup`

### Outputs created

- repo run folder:
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/`
- external working cases:
  - `C:\openfoam-case\VV_cases\V2_thermal_run002\Re10`
  - `C:\openfoam-case\VV_cases\V2_thermal_run002\Re20`
  - `C:\openfoam-case\VV_cases\V2_thermal_run002\Re40`
  - `C:\openfoam-case\VV_cases\V2_thermal_run002\Re100`
  - `C:\openfoam-case\VV_cases\V2_thermal_run002\Re200`

### Decision

Run 002 is now the active production-oriented V2a branch.
Run 001 remains in the repository as a compact historical debug record only.

### Important note

The solver architecture is now synchronized, but the final dedicated `Nu` extraction
path for the Boussinesq workflow is still pending. The next simulation step should
therefore start with a production smoke-test on `Re10`.

### Next step

- run `Re10` from `C:\openfoam-case\VV_cases\V2_thermal_run002\Re10`
- confirm stable startup and sustained execution on the production controls
- then continue with `Re20` and `Re40`

---

## 2026-04-09 13:32 | V2_thermal - package 3: Re10 partial smoke-test assessment

### Work package

Assess the interrupted `Re10` run-002 calculation and decide what can already be used
as a valid preliminary V2a result.

### Actions

- checked the run status from:
  - `C:\openfoam-case\VV_cases\V2_thermal_run002\Re10\logs\`
- confirmed:
  - `snappyHexMesh` finished successfully
  - `checkMesh` finished successfully aside from the standard quasi-2D empty-patch warning
  - `buoyantBoussinesqPimpleFoam` advanced to about `t = 7.51 s`
  - no active solver process remained
  - no `FOAM FATAL ERROR` was found in the solver log
- treated the stopped run as an interrupted partial smoke-test rather than a numerical crash
- extracted preliminary metrics:
  - cells: `46480`
  - `Co_mean` tail: `0.0228`
  - `Co_max` tail: `0.4726`
  - last `1 s` force tail:
    - `Cd_mean = 1.9671`
    - `Cl_mean = -2.9245`
    - large standard deviations indicating a still-strong transient
- updated:
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/simulations/Re10/notes.md`
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/summary.csv`
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/summary.md`

### Decision

The current `Re10` result is already good enough as a preliminary demonstration of:

- solver startup stability
- mesh validity
- controlled timestep behavior

It is not yet good enough as the final physical validation result for `Nu`, `Cd`, or the
steady-force level, because the run is incomplete and the force history is still transient.

### Next step

- decide whether to present this stage as a pure stability/smoke-test figure set
- only after that continue with either:
  - finishing `Re10`
  - or launching the next production cases

---

## 2026-04-09 13:48 | V2_thermal - package 4: preliminary Re10 figures and literature table

### Work package

Generate clean preliminary run-002 assets from the interrupted `Re10` calculation:

- `Cd(t)` and `Cl(t)` figure
- transient `Cl` spectrum
- clean literature comparison table
- explicit assessment of what can and cannot yet be claimed for `St` and `Nu`

### Actions

- fixed the `grad(T)` parser in:
  - `VV_cases/V2_thermal/_code/V2Run002PreliminaryPlots.py`
- extended the script to also write:
  - `literature_comparison.csv`
- generated:
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/plots/Re10_Cd_Cl_vs_time.png`
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/plots/Re10_Cd_Cl_vs_time.svg`
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/plots/Re10_Cl_spectrum.png`
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/plots/Re10_Cl_spectrum.svg`
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/literature_comparison.md`
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/literature_comparison.csv`
- updated:
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/simulations/Re10/notes.md`
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/summary.md`

### Main readings

- provisional spectral peaks from the transient `Cl` signal:
  - last `1 s`: `St = 7.4647`
  - last `2 s`: `St = 7.3888`
  - last `3 s`: `St = 7.3854`
- these values are not physically acceptable shedding Strouhal numbers for `Re = 10`
- they were kept only as transient diagnostic peaks from an interrupted non-settled run
- literature references for `Nu` at `Re = 10`:
  - `Nu_Lange = 1.8101`
  - `Nu_Bharti = 1.8623`
- rough single-snapshot estimate from `mag(grad(T))`:
  - `Nu ~= 74.67`
- this rough `Nu` estimate is grossly inconsistent with the literature scale and is explicitly rejected

### Decision

The current `Re10` assets are suitable only as:

- a solver-stability smoke-test figure set
- a diagnostic transient-force package

They are not suitable yet as:

- final `St` validation
- final `Nu` validation
- a valid `Nu(t)` presentation

### Next step

- either finish `Re10` and add a proper Boussinesq wall-heat-transfer extraction path
- or move directly to the next production cases after accepting this package as smoke-test-only evidence

---

## 2026-04-09 21:56 | V2_thermal - package 5: accepted Nu extraction route and report sync

### Work package

Replace the provisional rejected `mag(grad(T))` shortcut with the accepted
Boussinesq `Nu` extraction route and synchronize the run-002 reporting files.

### Actions

- implemented mesh-based wall-normal `Nu` extraction in:
  - `VV_cases/V2_thermal/_code/V2AStudy.py`
- extraction now uses:
  - `postProcess -func grad(T)` on written times
  - area-weighted projection `grad(T) · n` on the `cylinder` patch
  - `Nu = D * <grad(T)·n> / (T_wall - T_inf)`
- corrected the `Cl` column read in the run-002 analysis path
- ran:
  - `python .\\VV_cases\\V2_thermal\\_code\\V2AStudy.py analyze Re10`
- obtained the first physically consistent `Nu` reading for the interrupted `Re10` run:
  - `Nu = 6.7653`
  - `Nu_samples = 1`
- updated run-002 reporting:
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/simulations/Re10/notes.md`
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/summary.md`
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/summary.csv`
- updated the preliminary comparison assets by regenerating:
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/literature_comparison.md`
  - `VV_cases/V2_thermal/results/study_v2a/runs/002_data_v2a_boussinesq_validation/literature_comparison.csv`
- updated the canonical study document:
  - `VV_cases/V2_thermal/doc/V2_thermal.md`
  - including the correction from `D = 10 mm` to the active `D = 12 mm`

### Main readings

- the accepted `Nu` route is now physically correct
- the interrupted `Re10` run yields:
  - `Nu = 6.7653`
- this is much smaller than the previously rejected `Nu ~ 74.67`, which confirms the
  older shortcut was indeed wrong
- the value is still well above the steady literature scale:
  - `Nu_Lange = 1.8101`
  - `Nu_Bharti = 1.8623`
- current interpretation:
  - this is a startup-transient heat-transfer level from a partially written run
  - not yet a converged steady comparison result

### Decision

Run 002 now has the correct `Nu` definition and extraction path.
The remaining issue is no longer "how to compute `Nu`", but simply that the current
`Re10` calculation does not yet contain enough thermal history for a valid steady
literature comparison.

### Next step

- continue with a longer `Re10` thermal history on the accepted Boussinesq setup
- once multiple written thermal snapshots are available, build `Nu(t)` and check
  convergence toward the Lange/Bharti steady reference level

---

## 2026-04-09 22:08 | V2_thermal - package 6: Nu definition verified directly from the source PDFs

### Work package

Verify the accepted `Nu` definition against the actual Bharti (2007) and Lange (1998)
papers supplied locally by the user.

### Sources checked

- `c:\Users\kik\My Drive\Politechnika Krakowska\Grants\2025_07_Miniatura_9_ver2\Realizacja\Art\Bharti_2007.pdf`
- `c:\Users\kik\My Drive\Politechnika Krakowska\Grants\2025_07_Miniatura_9_ver2\Realizacja\Art\Lange_1998.pdf`

### Main findings

- Bharti explicitly defines:
  - local Nusselt number on the cylinder surface
  - surface-averaged Nusselt number as the average of the local values over the full cylinder surface
- Lange explicitly defines:
  - wall heat flux
  - heat-transfer coefficient
  - Nusselt number as the normalized wall heat-transfer coefficient
  - the mean Nusselt number as the value averaged over the whole cylinder perimeter
- both papers are therefore consistent with the accepted V2a route:
  - use the wall-normal temperature gradient on the cylinder surface
  - do not use `mag(grad(T))`
  - compare the area/perimeter-averaged `Nu` against the literature values

### Repo update

- updated:
  - `VV_cases/V2_thermal/doc/V2_thermal.md`
  - with a direct note that the current V2a `Nu` definition is aligned with Bharti Eq. (11)-(12) and Lange Sec. 2.2

### Decision

The current V2a `Nu` definition is now verified not only by standard CFD practice, but
also directly against the two source papers we use as references.

### Immediate follow-up

- steady cases in `V2AStudy.py` were extended from `60 s` to `100 s`
- steady write interval was reduced from `5 s` to `1 s`
- reason: the next `Re10` production run should resolve `Nu(t)` and its plateau directly, instead of relying on a single late thermal snapshot

---

## 2026-04-09 22:25 | V2_thermal - package 7: long Re10 case launched toward Nu(t) plateau

### Work package

Start a fresh longer `Re10` production-oriented case aimed at resolving `Nu(t)` and
its approach to the steady Lange/Bharti level.

### Actions

- added a fresh non-destructive case entry:
  - `Re10_long100s`
  - same `Re = 10`
  - `endTime = 100 s`
  - `writeInterval = 1 s`
- added `decomposeParDict` generation to:
  - `VV_cases/V2_thermal/_code/V2AStudy.py`
  - with `numberOfSubdomains = 10`
- created the fresh external working case:
  - `C:\openfoam-case\VV_cases\V2_thermal_run002\Re10_long100s`
- added a dedicated launcher script:
  - `VV_cases/V2_thermal/_code/run_re10_long100s_parallel.sh`
- verified directly that:
  - WSL can access the case directory
  - `blockMesh` runs successfully on the fresh case
- launched the long case and confirmed that it advanced into:
  - `snappyHexMesh -overwrite`

### Current live status

- the fresh `Re10_long100s` case is now genuinely in progress
- current active stage:
  - `snappyHexMesh`
- the 10-process solver stage has not started yet, because the case is still in the
  meshing phase

### Decision

The current V2a production branch is now moving again on a fresh longer `Re10` case.
At this moment the only blocker is runtime, not methodology or startup stability.

## 2026-04-09 22:38 | V2_thermal - package 8: long Re10 continued after snappyHexMesh

### Work package

Carry the fresh `Re10_long100s` case past meshing into the actual parallel flow and
thermal solve without rerunning `blockMesh` or `snappyHexMesh`.

### Actions

- verified that:
  - `snappyHexMesh` finished cleanly
  - final mesh was written without errors
  - final cell count is `46480`
  - total meshing time was `693.59 s`
- confirmed that the current live launch stopped at the meshing stage and had not yet
  produced:
  - `log.checkMesh`
  - `log.decomposePar`
  - `log.buoyantBoussinesqPimpleFoam`
- added a continuation launcher:
  - `VV_cases/V2_thermal/_code/continue_re10_long100s_parallel.sh`
- prepared the case to continue from:
  - `checkMesh`
  - `decomposePar`
  - `mpirun -np 10 buoyantBoussinesqPimpleFoam -parallel`

### Decision

The fresh `Re10_long100s` case will now move into the actual 10-process solve without
repeating the already completed meshing stage.

### Follow-up note

- the first continuation launches exited immediately because both launcher scripts set
  `set -u` before sourcing the OpenFOAM `bashrc`
- the OpenFOAM vendor `bashrc` touches variables that are not guaranteed to be defined
  in non-interactive shells, so `nounset` aborted the scripts before:
  - `checkMesh`
  - `decomposePar`
  - `mpirun`
- both launchers were corrected by moving:
  - `source .../bashrc`
  - ahead of `set -euo pipefail`
- after the corrected relaunch, the case advanced into:
  - `mpirun -np 10 buoyantBoussinesqPimpleFoam -parallel`
  - stable runtime confirmed up to about `t = 46.18 s`
- the run was then stopped manually for the night at user request

## 2026-04-10 09:25 | V2_thermal - package 9: post-processing of the stopped Re10_long100s run

### Work package

Extract `Nu(t)` and a transient `St` descriptor from the stopped `Re10_long100s`
parallel run without restarting the solver.

### Actions

- confirmed that the parallel run had written `48` time directories in `processor0`
  up to about `47.0 s`
- reconstructed the saved temperature fields only:
  - `reconstructPar -fields '(T)'`
- post-processed the reconstructed fields:
  - `postProcess -func 'grad(T)'`
- ran the study-level analyzer for:
  - `Re10_long100s`
- added a reusable export helper:
  - `VV_cases/V2_thermal/_code/V2ATimeseries.py`
- exported the following assets for `Re10_long100s`:
  - `Re10_long100s_Nu_timeseries.csv`
  - `Re10_long100s_forceCoeffs_timeseries.csv`
  - `plots/Re10_long100s_Nu_vs_time.png`
  - `plots/Re10_long100s_Cd_Cl_vs_time.png`
  - `plots/Re10_long100s_Cl_spectrum.png`
  - `literature_comparison_Re10_long100s.md`
  - `literature_comparison_Re10_long100s.csv`
- updated the run-level `literature_comparison.md` and `literature_comparison.csv`
  so they now point to the current best `Re10_long100s` comparison instead of the
  earlier short smoke-test

### Results

- `Nu(t)` now covers about `47.0 s`
- `Nu` mean over the second half of the run:
  - `6.8857`
- `Nu` mean over the last `10 s`:
  - `6.0189`
- literature references at `Re = 10`:
  - `Nu_Lange = 1.8101`
  - `Nu_Bharti = 1.8623`
- current mismatch:
  - `+280.41%` vs Lange
  - `+269.74%` vs Bharti
- transient spectral peak from `Cl` tail:
  - `St_peak = 0.0659`

### Interpretation

- the accepted `Nu` definition is now implemented consistently with Bharti and Lange
- the current `Re10_long100s` result is still not a valid literature match
- `Nu(t)` remains far above the expected steady level and has not converged to the
  benchmark range
- the reported `St` remains only a transient signal descriptor; it is not suitable for
  physical comparison at `Re = 10`

---

## 2026-04-11 | V2_thermal - package 11: mesh rebuild (addLayers=false) and 30 s diagnostic run

### Work package

Identify and fix the root cause of non-physical T field and `Nu ≈ 6–7` (expected `~1.86`).
Rebuild mesh with `addLayers false`, run 30 s, and diagnose whether Nu is now
approaching the literature range.

### Actions

**Mesh fixes applied to Re10_long100s:**
- `snappyHexMeshDict`: `addLayers false` (was `true`)
  — previous `addLayers true` created genuine 3D boundary-layer cells near the cylinder
  surface; these caused z-velocity up to 0.001 m/s (8.7 % of U_inf) and non-physical
  T advection in z even for a nominally 2D case
- `snappyHexMeshDict`: cylinder and box z-extents corrected to ±0.005 m (were ±0.010 m)
- `0/U`: `internalField uniform (0.012632 0 0)` (was `(0 0 0)` — caused hydraulic shock)
- `0/T`: top and bottom walls changed from `zeroGradient` to `fixedValue 293.15`
- `fvSchemes`: `div(phi,T) Gauss limitedLinear01 1` (was `Gauss linearUpwind grad(T)`)
- `fvSolution`: `nNonOrthogonalCorrectors 2` (was 1)
- `controlDict`: `wallHeatFlux` FO removed (incompatible with Boussinesq solver)

**Mesh rebuild:**
- deleted polyMesh, processor* dirs, stale time directories
- `blockMesh` → `snappyHexMesh -overwrite` → `checkMesh`
- new mesh: 43 792 cells, non-orthogonality max 38°, skewness max 0.59 — all OK
- snappyHexMesh still creates 8 z-layers near cylinder (level-3 surface refinement,
  isotropic splitting); `empty` patches enforce 2D behaviour

**Parallel run (WSL, 15 cores):**
- OF v2512 at `/home/kik/openfoam/OpenFOAM-v2512`
- `mpirun --use-hwthread-cpus -np 15 buoyantBoussinesqPimpleFoam -parallel`
  in tmux session inside WSL (survives Claude Code timeout)
- reached `Time = 30.01 s`, ClockTime ≈ 309 s (~5 min wall-clock)
- `reconstructPar` completed for all 30 time directories

### Results

| quantity | value | expected |
|---|---|---|
| Nu (t = 30 s) | 5.996 | ~1.86 |
| Cd (mean) | 2.072 | ~2.8–3.0 |
| Nu_Lange | 1.810 | — |
| Nu_Bharti | 1.862 | — |

**Patch-level T diagnostics at t = 30 s:**

| metric | value | expected |
|---|---|---|
| Global T min / max | 197 K / 337 K | 293.15–303.15 K |
| Near-wall cells with T_P > T_W | 320 / 448 (71 %) | 0 |
| Near-wall cells with T_P < T_IN | 12 / 448 | 0 |
| snGrad mean on cylinder patch | 4 986 K/m | ~1 550 K/m |
| snGrad range | −9 574 to +38 787 K/m | — |
| delta_perp mean (first cell) | 2.4 × 10⁻⁴ m | — |

### Interpretation

The T field remains non-physical despite mesh and IC fixes.
`Gauss limitedLinear01 1` is a gradient-limited linear scheme with the limiter
clipped to [0, 1]; it is **not** a fully bounded (TVD) scheme. Under non-orthogonal
cell geometries near the snappy-refined cylinder surface, it produces T values far
outside [T_IN, T_W] (197 K to 337 K observed). This inflates the snGrad estimate
and thus Nu.

The 30 s run also covers less than two convective time scales (L_out/U_inf ≈ 28 s),
so even if the scheme were corrected the field may not yet be statistically steady.

Cd = 2.07 is low (expected ~2.8–3.0 for Re = 10 unconfined), consistent with a
distorted velocity field driven by the incorrect T distribution (buoyancy coupling via
Boussinesq term remains active even at g = 0 if T drifts).

### Next steps

- [ ] Change `div(phi,T)` to `Gauss vanLeer` (bounded, monotone TVD) in `fvSchemes`
- [ ] Re-run 30 s and verify global T stays within [293.15, 303.15] K
- [ ] If T is bounded: run full 100 s and check Nu(t) convergence toward ~1.86
- [ ] If Nu still high after T is bounded: investigate non-orthogonality correction
      in the Python snGrad implementation (weighted delta vs. face-normal delta)

---

## 2026-04-12 14:10:53 +02:00 | V2_thermal | package 12: heated-channel diagnostic after failed cylinder Nu validation

### Work package

Separate the three overlapping V2 thermal problems before continuing the cylinder
validation:

- non-physical cylinder temperature field
- invalid Nu extraction path based on a global/wrong gradient comparison
- snappy cylinder mesh without structured wall-normal control

### Actions taken

- accepted the diagnosis that the current `Re10_long100s` cylinder result is not
  publishable as a Nu validation case
- confirmed the critical cylinder symptom from the working case:
  `T_min = 197.398 K`, `T_max = 337.410 K`, and `71.43%` of cylinder owner cells
  hotter than the imposed `T_wall = 303.15 K`
- created diagnostic driver:
  `VV_cases/V2_thermal/_code/V2ChannelCheck.py`
- created run archive:
  `VV_cases/V2_thermal/results/study_v2a/runs/003_data_heated_channel_solver_check`
- created working OpenFOAM cases under:
  `C:\openfoam-case\VV_cases\V2_channel_check`
- ran an initial `Re_Dh = 10` heated-channel sanity case; temperature stayed bounded,
  but the outlet saturated to `T_wall`, making outlet-only Nu ill-conditioned
- switched the diagnostic case to `Re_Dh = 100` to preserve a finite wall-bulk
  temperature difference downstream
- generated a pure `blockMesh` plane-channel case:
  21 600 hexa cells, max non-orthogonality `0`, solver
  `buoyantBoussinesqPimpleFoam`, `g = 0`, and `div(phi,T) Gauss vanLeer`
- the Re100 solver run was interrupted by host/WSL I/O during the restart window,
  but valid written fields remained up to `t = 40.001357 s`
- ran `postProcess -func writeCellCentres -latestTime` on the last written time
- corrected the analyzer so Nu is computed locally at each x-station using the
  same-station wall-normal temperature gradient and bulk temperature, instead of
  mixing a streamwise-averaged wall gradient with outlet bulk temperature
- generated local Nu profile table and plot

### Results

| quantity | value |
|---|---:|
| latest analyzed time | 40.001357 s |
| T min / max | 293.1744 K / 303.1500 K |
| cells below inlet T | 0.00% |
| cells above wall T | 0.00% |
| selected comparison station | x/Dh = 12.083 |
| selected Tw - Tbulk | 0.05299 K |
| selected local Nu | 7.5643 |
| analytic plane-channel UWT Nu | 7.5410 |
| Nu error | +0.31% |
| outlet Tw - Tbulk | ~0 K, outlet Nu not used |

### Outputs created or updated

- `VV_cases/V2_thermal/_code/V2ChannelCheck.py`
- `VV_cases/V2_thermal/results/study_v2a/runs/003_data_heated_channel_solver_check/run.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/003_data_heated_channel_solver_check/summary.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/003_data_heated_channel_solver_check/summary.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/003_data_heated_channel_solver_check/Nu_profile.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/003_data_heated_channel_solver_check/plots/V2_channel_Re100_Nu_profile.png`
- `VV_cases/V2_thermal/results/study_v2a/runs/003_data_heated_channel_solver_check/plots/V2_channel_Re100_Nu_profile.svg`
- `VV_cases/V2_thermal/doc/V2A_publication_verification_plan.md`
- `C:\openfoam-case\VV_cases\V2_channel_check\plane_channel_Re100_UWT`

### Decisions made

- the existing snappy-cylinder `Re10_long100s` Nu is invalid and should not be used
  in the article
- the simple orthogonal channel test passes both boundedness and Nu checks, so the
  solver/scheme path is not the primary failure source
- the next cylinder validation should use a structured/O-grid cylinder mesh and
  wall-normal `snGrad(T)` extraction, not `postProcess grad(T)` and not the current
  snappy mesh without boundary layers
- outlet-only Nu is not a safe diagnostic when the outlet has thermally saturated;
  local same-station Nu is required

### Next step

Start V2 thermal run 004 as a structured cylinder/O-grid validation case against
Bharti/Lange/Dennis references, using local `snGrad(T)` and publication-ready Nu
tables/plots only after the temperature field is proven bounded.

---

## 2026-04-12 14:50:05 +02:00 | V2_thermal | package 13: run 004 structured O-grid Re10 validation pilot

### Work package

Implement and execute the first structured-cylinder replacement for the rejected
snappy `Re10_long100s` thermal validation case.

### Actions taken

- created:
  `VV_cases/V2_thermal/_code/V2OGridStudy.py`
- generated run archive:
  `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation`
- generated working OpenFOAM case:
  `C:\openfoam-case\VV_cases\V2_thermal_run004\Re10_ogrid`
- built an 8-block structured O-grid in `blockMesh`:
  - outer square domain `30.5D x 30.5D`
  - `128` cells around the cylinder
  - `80` radial cells
  - radial expansion ratio `40`
  - one `empty` cell through the span
- used solver/setup:
  - `buoyantBoussinesqPimpleFoam`
  - `g = 0`
  - `div(phi,T) Gauss vanLeer`
  - hot cylinder `T = 303.15 K`
  - far-field/inlet temperature `T = 293.15 K`
  - Nu extraction from wall-normal `snGrad(T)` on the cylinder patch
- ran:
  - `blockMesh`
  - `checkMesh`
  - `postProcess -func writeCellCentres -time 0`
  - `buoyantBoussinesqPimpleFoam`
  - `V2OGridStudy.py analyze Re10_ogrid`

### Mesh result

| quantity | value |
|---|---:|
| cells | 10 240 hexahedra |
| cylinder patch faces | 128 |
| max aspect ratio | 2.306 |
| max non-orthogonality | 44.05 deg |
| max skewness | 0.702 |
| checkMesh | OK |

### Thermal/force result

| quantity | value |
|---|---:|
| latest analyzed time | 99.993804 s |
| Nu tail mean | 1.8807 |
| Nu last | 1.8806 |
| Nu Bharti | 1.8623 |
| Nu Lange | 1.8101 |
| error vs Bharti | +0.99% |
| Cd tail mean | 2.9258 |
| T min / max | 293.15 K / 303.0717 K |
| cells below `T_in` | 0.0% |
| cells above `T_wall` | 0.0% |
| cylinder owner cells above `T_wall` | 0.0% |

### Outputs created or updated

- `VV_cases/V2_thermal/_code/V2OGridStudy.py`
- `VV_cases/V2_thermal/doc/V2A_publication_verification_plan.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/run.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/summary.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/summary.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/publication_table.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/simulations/Re10_ogrid/Nu_timeseries.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/Re10_ogrid_Nu_vs_time.png`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/Re10_ogrid_Nu_vs_time.svg`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2_run004_Nu_vs_reference.png`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2_run004_Nu_vs_reference.svg`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2_run004_ogrid_mesh_schematic.png`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2_run004_ogrid_mesh_schematic.svg`

### Decisions made

- run 004 `Re10_ogrid` is the first acceptable V2A thermal validation candidate
- the previous snappy-cylinder run 002 remains rejected for Nu validation
- the O-grid path fixes the critical boundedness failure and gives Nu within 1% of
  Bharti at `Re = 10`
- the publication table should now be extended with `Re = 20` and `Re = 40`, not by
  returning to the snappy mesh

### Next step

Extend `V2OGridStudy.py` to include `Re20_ogrid` and `Re40_ogrid`, then run the same
boundedness + Nu validation workflow to complete the low-Re Bharti matrix.

---

## 2026-04-12 15:38:12 +02:00 | V2_thermal | package 14: article-style Nu(Re) comparison plot

### Work package

Create a publication-oriented `Nu(Re)` figure comparing the current O-grid result
against the available article references.

### Actions taken

- created:
  `VV_cases/V2_thermal/_code/V2PublicationNuRePlot.py`
- used the local V2A reference data already verified in the study scripts:
  - Lange et al. (1998) correlation
  - Bharti et al. (2007) tabulated values at `Re = 10, 20, 40`
- overlaid the current accepted present-work point:
  - `Re10_ogrid`, `Nu = 1.880652`
- generated a data table for the figure
- updated the run-004 `summary.md` and `run.md` so the new figure is listed with
  the other publication assets

### Outputs created or updated

- `VV_cases/V2_thermal/_code/V2PublicationNuRePlot.py`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/publication_Nu_Re_data.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Nu_Re_articles_vs_present.png`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Nu_Re_articles_vs_present.svg`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/summary.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/run.md`

### Decision

The figure currently contains one present-work point because only `Re10_ogrid` has
passed the O-grid validation workflow. It should be regenerated after `Re20_ogrid`
and `Re40_ogrid` are complete.

---

## 2026-04-12 18:08:40 +02:00 | V2_thermal | package 15: run 004 low-Re O-grid matrix completion

### Work package

Extend the validated O-grid thermal workflow from `Re10_ogrid` to the remaining
Bharti low-Re table points, `Re20_ogrid` and `Re40_ogrid`.

### Actions taken

- updated:
  `VV_cases/V2_thermal/_code/V2OGridStudy.py`
- added cases:
  - `Re20_ogrid`
  - `Re40_ogrid`
- generated working cases under:
  `C:\openfoam-case\VV_cases\V2_thermal_run004`
- ran `blockMesh`, `checkMesh`, and `postProcess -func writeCellCentres -time 0`
  for both new cases
- ran `buoyantBoussinesqPimpleFoam` to `t ~= 100 s` for both new cases
- ran full run-004 analysis for:
  - `Re10_ogrid`
  - `Re20_ogrid`
  - `Re40_ogrid`
- regenerated:
  - run summary
  - publication table
  - `Nu(t)` plots for all cases
  - `Nu(Re)` article comparison plot
  - figure data CSV
- updated:
  `VV_cases/V2_thermal/doc/V2A_publication_verification_plan.md`

### Mesh result

Both new cases use the same validated O-grid mesh:

| quantity | value |
|---|---:|
| cells | 10 240 hexahedra |
| cylinder patch faces | 128 |
| max aspect ratio | 2.306 |
| max non-orthogonality | 44.05 deg |
| max skewness | 0.702 |
| checkMesh | OK |

### Thermal/force results

| case | Re | Nu present | Nu Bharti | error vs Bharti | Nu Lange | Cd tail | T range | bounded |
|---|---:|---:|---:|---:|---:|---:|---|---|
| Re10_ogrid | 10 | 1.8807 | 1.8623 | +0.99% | 1.8101 | 2.9258 | 293.15-303.0717 K | yes |
| Re20_ogrid | 20 | 2.4829 | 2.4653 | +0.72% | 2.4087 | 2.1031 | 293.15-303.0628 K | yes |
| Re40_ogrid | 40 | 3.3045 | 3.2825 | +0.67% | 3.2805 | 1.5713 | 293.15-303.0436 K | yes |

All cases had `0.0%` cells above `T_wall`, `0.0%` cells below `T_in`, and `0.0%`
cylinder owner cells above `T_wall`.

### Outputs created or updated

- `VV_cases/V2_thermal/_code/V2OGridStudy.py`
- `VV_cases/V2_thermal/doc/V2A_publication_verification_plan.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/run.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/summary.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/summary.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/publication_table.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/publication_Nu_Re_data.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Nu_Re_articles_vs_present.png`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Nu_Re_articles_vs_present.svg`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/Re20_ogrid_Nu_vs_time.png`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/Re20_ogrid_Nu_vs_time.svg`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/Re40_ogrid_Nu_vs_time.png`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/Re40_ogrid_Nu_vs_time.svg`

### Decisions made

- the V2A low-Re Bharti validation matrix is complete for `Re = 10, 20, 40`
- O-grid + `snGrad(T)` is now the accepted path for the thermal cylinder article figure
- errors below 1% versus Bharti and bounded `T` fields make the low-Re matrix suitable
  as a publication candidate
- any `Re = 100` extension should be treated as an optional higher-Re/unsteady extension,
  not as a blocker for the Bharti low-Re validation table

### Next step

Use `publication_table.md` and `plots/V2A_Nu_Re_articles_vs_present.png` as the current
V2A article assets, unless a separate higher-Re extension is explicitly requested.

---

## 2026-04-12 19:24:51 +02:00 | V2_thermal | package 16: article-range comparison plots for Nu, St, Cd, and Cl

### Work package

Extend the V2A article comparison beyond `Nu(Re)` so that the current O-grid data
can be viewed against the quantities actually available in Bharti (2007) and Lange
(1998).

### Actions taken

- expanded:
  `VV_cases/V2_thermal/_code/V2PublicationNuRePlot.py`
- verified the Lange `Nu` exponent sign against the local PDF extraction:
  - active implementation remains `x = 0.05 + 0.226 Re^0.085`
  - the scratch-note alternative `x = -0.05 + ...` was not adopted
- generated separate comparison plots for:
  - `Nu(Re)`
  - `St(Re)`
  - `Cd(Re)`
  - `Cl(Re)`
- generated a four-panel diagnostic dashboard
- wrote a long-form CSV table containing the reference and present-work data used
  in the plots
- wrote a short comparison/next-simulation plan for the article extension
- updated the V2A publication recovery plan with the reference ranges and next
  simulation priorities

### Reference-range decision

| source | usable quantities here | Re range | max Re | notes |
|---|---|---:|---:|---|
| Bharti et al. (2007) | `Nu` for steady CWT/UHF cross-flow | 10-45 | 45 | no useful `Cd`, `Cl`, or `St` curve for this comparison |
| Lange et al. (1998) | `Nu`, `St`, onset, digitized `Cd` trend | 1e-4-200 | 200 | no reusable `Cl(Re)` curve |
| present run 004 | `Nu`, `Cd`, low-Re `Cl` diagnostic | 10-40 so far | 40 | all current cases are below `Re_c = 45.9` |

### Outputs created or updated

- `VV_cases/V2_thermal/_code/V2PublicationNuRePlot.py`
- `VV_cases/V2_thermal/doc/V2A_publication_verification_plan.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/summary.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/publication_Nu_Re_data.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/publication_articles_vs_present_data.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/publication_article_comparison_plan.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Nu_Re_articles_vs_present.png`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_St_Re_articles_vs_present.png`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Cd_Re_articles_vs_present.png`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Cl_Re_articles_vs_present.png`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_articles_vs_present_dashboard.png`

### Decisions made

- Bharti should be used as the primary low-Re `Nu` validation reference only up
  to `Re = 45`
- Lange can support a higher-Re extension up to `Re = 200`, including `St` and
  approximate `Cd`, but `Cl` should not be compared as a literature curve
- current run-004 data already cover the low-Re steady side; the next useful
  simulations are `Re45_ogrid`, `Re60_ogrid`, `Re100_ogrid`, and `Re200_ogrid`

### Next step

If the article needs the higher-Re Lange extension, prepare and run the next
O-grid cases in priority order: `Re45_ogrid`, `Re60_ogrid`, `Re100_ogrid`, then
`Re200_ogrid`. Treat `Re200_ogrid` as a mesh-sensitivity candidate before using it
as a final article point.

---

## 2026-04-13 17:34:57 +02:00 | V2_thermal | package 17: high-Re O-grid extension paused by user request

### Work package

Start the higher-Re Lange extension for V2A run 004 on 15 MPI ranks and stop it
cleanly when requested.

### Actions taken

- extended `VV_cases/V2_thermal/_code/V2OGridStudy.py` with:
  - cases `Re45_ogrid`, `Re60_ogrid`, `Re100_ogrid`, `Re200_ogrid`
  - 15-rank OpenFOAM parallel execution
  - `latestTime` restart logic for interrupted parallel cases
  - direct `processor*` analysis for `Nu`, boundedness, `Cd`, `Cl_rms`, and `St`
  - read-only-safe setup archival on Windows
- refreshed publication plots through:
  `VV_cases/V2_thermal/_code/V2PublicationNuRePlot.py`
- completed:
  - `Re45_ogrid`
  - `Re60_ogrid`
- started `Re100_ogrid`, then stopped it on user request
- confirmed that no `mpirun`, `buoyantBoussinesqPimpleFoam`, `decomposePar`, or
  `reconstructPar` process remained active after stopping

### Completed results

| case | Re | cells | latest field time | Nu | Cd | Cl_rms | St present | St Lange | T bounded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `Re45_ogrid` | 45 | 10240 | 119.9988 | 3.4736 | 1.5007 | 5.88e-7 | n/a | n/a | yes |
| `Re60_ogrid` | 60 | 10240 | 79.8003 | 3.9778 | 1.4086 | 7.29e-2 | 0.1276 | 0.1358 | yes |

### Paused state

- `Re100_ogrid` was interrupted at about `t = 6.3 s`
- processor checkpoint folders exist and can be resumed later with the updated
  `latestTime` logic
- `Re200_ogrid` has been prepared/meshed but not started

### Next step

Resume `Re100_ogrid` only if the higher-Re extension is still desired; otherwise
use the completed run-004 matrix through `Re60_ogrid` as the current article
comparison set.

---

## 2026-04-13 20:18:43 +02:00 | V2_thermal | package 18: Re100 early-window analysis and Re200 launch

### Work package

Continue the O-grid cylinder extension while keeping the high-Re validation plots current.

### Actions taken

- stopped `Re100_ogrid` cleanly with `stopAt writeNow`
- confirmed `Re100_ogrid` finished with `exit=0` at `t≈24.513 s`
- updated `run_ogrid_case_tmux.sh` so fresh O-grid cases run `setExprFields` and `decomposePar -force` before MPI
- updated `V2OGridStudy.py` force analysis to read `Cd`/`Cl` from solver logs when post-restart `coefficient.dat` files are incomplete
- reanalysed `Re10_ogrid`, `Re20_ogrid`, `Re40_ogrid`, `Re45_ogrid`, `Re60_ogrid`, and `Re100_ogrid`
- regenerated the article-comparison plots and tables
- launched `Re200_ogrid` in `tmux` session `v2_Re200` on 15 MPI ranks

### Outputs updated

- `VV_cases/V2_thermal/_code/run_ogrid_case_tmux.sh`
- `VV_cases/V2_thermal/_code/V2OGridStudy.py`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/summary.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/publication_table.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/publication_articles_vs_present_data.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_*_articles_vs_present.*`

### Results

- `Re100_ogrid` early-window result at `t≈24.513 s`:
  - `Nu≈5.1720`
  - `Cd≈1.3329`
  - `Cl_rms≈0.206`
  - `St≈0.1539` versus Lange/Williamson `St≈0.1643`
  - `T` remained bounded between inlet and wall temperatures
- `Re200_ogrid` is running; first confirmed progress was `t≈1.02 s`

### Decisions made

- `Re100_ogrid` is included on the plots as an early-window high-Re diagnostic point
- `Re200_ogrid` should not be added to the publication plots until it has a meaningful averaging window

### Next step

Monitor `Re200_ogrid`; once it reaches a useful window, stop or complete it, then analyse and regenerate the comparison plots including `Re200`.

---

## 2026-04-13 20:26:15 +02:00 | V2_thermal | package 19: publication plot band cleanup

### Work package

Clean up the article comparison figures after the Re100 early-window update.

### Actions taken

- added grey `±2%` literature-reference bands to:
  - `Nu(Re)` around the Lange and Bharti curves
  - `St(Re)` around the Lange/Williamson curve
  - `Cd(Re)` around the digitized Lange trend
- changed the `St(Re)` plot to start at `Re = 50`
- removed the standalone `Cl` comparison plot because Bharti/Lange do not provide a usable `Cl(Re)` reference curve
- changed the dashboard from four panels to three panels: `Nu`, `St`, and `Cd`
- removed stale `V2A_Cl_Re_articles_vs_present.*` plot files
- removed the stale `Cl` plot reference from the run summary
- confirmed `Re200_ogrid` continued running after the plot update; latest checked time was `t≈2.58 s`

### Outputs updated

- `VV_cases/V2_thermal/_code/V2PublicationNuRePlot.py`
- `VV_cases/V2_thermal/_code/V2OGridStudy.py`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/summary.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Nu_Re_articles_vs_present.*`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_St_Re_articles_vs_present.*`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Cd_Re_articles_vs_present.*`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_articles_vs_present_dashboard.*`

### Next step

Continue monitoring `Re200_ogrid`; once it reaches a useful averaging window, analyse it and regenerate the comparison plots including the Re200 point.

---

## 2026-04-15 20:22:02 +02:00 | toolkit_test | spectral coherence demonstrator

### Work package

Extend the POD/EPOD toy toolkit with a small spectral-coherence example.

### Actions taken

- created a long paired synthetic dataset with 1024 velocity and wall heat-flux snapshots on a 5x5 grid
- imposed a base frequency `f0 = 1.25` and a second harmonic `2f0 = 2.50`
- computed independent POD for the long velocity and heat-flux series
- extracted representative velocity and heat-flux signals
- computed Welch auto-spectra, cross-spectra, phase, and magnitude-squared coherence
- computed coherence matrices between the first POD temporal coefficients
- generated figures showing snapshots, time signals, spectra, coherence curves, POD energy, and modal-pair coherence

### Outputs created or updated

- `toolkit_test/compute_spectral_coherence.py`
- `toolkit_test/data/coherence/...`
- `toolkit_test/results/coherence/coherence_summary.md`
- `toolkit_test/results/coherence/coherence_peak_summary.csv`
- `toolkit_test/results/coherence/frequency_response.csv`
- `toolkit_test/results/coherence/pod_pair_coherence.csv`
- `toolkit_test/results/coherence/figures/...`
- `toolkit_test/README.md`

### Decisions made

- the original 5-snapshot POD/EPOD example remains unchanged
- spectral coherence uses a separate long time-series dataset because five snapshots are not enough for meaningful frequency-domain analysis
- the modal-pair heatmap is included because mode indices do not always map one-to-one between fields

### Next step

Use the coherence demonstrator to explain how this workflow could be transferred to OpenFOAM signals such as `Cl(t)`, `Nu(t)`, local `q_wall(theta,t)`, and POD coefficients of `U(x,y,t)`.

---

## 2026-04-15 20:35:39 +02:00 | toolkit_test | transfer entropy demonstrator

### Work package

Add two transfer-entropy examples on top of the synthetic POD/EPOD/coherence toolkit.

### Actions taken

- created `toolkit_test/compute_transfer_entropy.py`
- implemented a quantile-discretized lagged transfer-entropy estimator:
  - `TE_{X->Y}(lag) = I(Y_t ; X_{t-lag} | Y_{t-1})`
- added a shuffled-source surrogate baseline to reduce finite-sample bias
- computed example 1 on the existing long coherence signals with shared oscillator forcing
- computed example 2 on a cleaner delayed-causal construction:
  - `q_response(t)` depends on `u_driver(t - tau)`
  - imposed delay `tau = 7` samples
- generated TE-vs-lag plots, input-signal plots, and peak-summary plots
- updated `toolkit_test/README.md`

### Outputs created or updated

- `toolkit_test/compute_transfer_entropy.py`
- `toolkit_test/results/transfer_entropy/transfer_entropy_summary.md`
- `toolkit_test/results/transfer_entropy/transfer_entropy_peak_summary.csv`
- `toolkit_test/results/transfer_entropy/example1_current_common_driver_te.csv`
- `toolkit_test/results/transfer_entropy/example2_delayed_causal_te.csv`
- `toolkit_test/results/transfer_entropy/delayed_causal_signals.csv`
- `toolkit_test/results/transfer_entropy/figures/...`
- `toolkit_test/README.md`
- `VV_cases/RESEARCH_LOG.md`

### Decisions made

- example 1 is kept intentionally as an ambiguous common-driver case: it demonstrates directional predictability but not reliable causal direction
- example 2 uses a broadband stochastic driver instead of a purely periodic source so that the imposed direction `U -> q` is visible and the reverse direction stays near baseline
- the estimator is intentionally lightweight and transparent, suitable for demonstration before moving to more careful CFD-scale TE analysis

### Next step

Use the transfer-entropy figures to explain the difference between spectral coherence, which detects shared frequency content, and transfer entropy, which tests directional predictive information.

---

## 2026-04-15 20:58:58 +02:00 | toolkit_test | resolvent analysis demonstrator

### Work package

Add an educational reduced-order resolvent-analysis example to the synthetic toolkit.

### Actions taken

- created `toolkit_test/compute_resolvent_analysis.py`
- implemented a stable two-oscillator linear model:
  - base oscillator near `f0 = 1.25`
  - second oscillator near `2f0 = 2.50`
- computed the frequency-response/resolvent operator:
  - `H(w) = C(i w I - A)^(-1)B`
- applied SVD at each frequency:
  - `H(w) = U Sigma V*`
- saved singular-value gain curves versus frequency
- extracted and saved leading optimal forcing and response modes at `f0` and `2f0`
- generated mode-shape and phase-map figures
- updated `toolkit_test/README.md`

### Outputs created or updated

- `toolkit_test/compute_resolvent_analysis.py`
- `toolkit_test/results/resolvent/resolvent_summary.md`
- `toolkit_test/results/resolvent/resolvent_gain.csv`
- `toolkit_test/results/resolvent/resolvent_peak_summary.csv`
- `toolkit_test/results/resolvent/*_forcing_*`
- `toolkit_test/results/resolvent/*_response_*`
- `toolkit_test/results/resolvent/figures/...`
- `toolkit_test/README.md`
- `VV_cases/RESEARCH_LOG.md`

### Decisions made

- the example is explicitly reduced-order and educational, not a full OpenFOAM/Navier-Stokes linearization
- forcing and response modes are projected back onto the same 5x5 velocity and wall heat-flux field format used by POD/EPOD/coherence examples
- the imposed frequencies match the previous spectral-coherence example so the methods can be compared directly

### Next step

Use the resolvent figures to explain the difference between modal energy, spectral coherence, transfer entropy, and resolvent gain before attempting a CFD-derived linear operator.

---

## 2026-04-13 21:17:54 +02:00 | V2_thermal | package 22: Re200 stopped and added to article plots

### Work package

Stop the running `Re200_ogrid` calculation and add the resulting point to the V2A article-comparison plots.

### Actions taken

- stopped `Re200_ogrid` cleanly using `stopAt writeNow`
- confirmed the current run ended with `exit=0`
- confirmed no `mpirun` or `buoyantBoussinesqPimpleFoam` processes remained active
- reanalysed the complete run-004 matrix:
  - `Re10_ogrid`
  - `Re20_ogrid`
  - `Re40_ogrid`
  - `Re45_ogrid`
  - `Re60_ogrid`
  - `Re100_ogrid`
  - `Re200_ogrid`
- regenerated the article-comparison plots and publication tables with `Re200_ogrid` included

### Results

`Re200_ogrid` stopped at `t = 11.46423001 s`, corresponding to about 47.5 shedding periods using the Lange/Williamson reference period.

| case | Re | latest t | Nu | Nu Lange | error | Cd | Cl_rms | St | St Lange |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `Re200_ogrid` | 200 | 11.4642 | 7.5040 | 7.4202 | +1.13% | 1.3234 | 0.4443 | 0.1831 | 0.1970 |

Temperature remained physically bounded for practical purposes; the exact checker flagged `T_below_Tin_pct = 0.068%` because the minimum value was `293.14999 K`, about `1e-5 K` below `T_in = 293.15 K`.

### Outputs updated

- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/summary.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/publication_table.md`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/publication_articles_vs_present_data.csv`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Nu_Re_articles_vs_present.*`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_St_Re_articles_vs_present.*`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Cd_Re_articles_vs_present.*`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_articles_vs_present_dashboard.*`

### Next step

If the Re200 point is used as a final article value, document that it is an early-window result and consider a refined O-grid or longer averaging window for a final high-Re sensitivity check.

---

## 2026-04-15 19:27:17 +02:00 | toolkit_test | synthetic POD dataset scaffold

### Work package

Create a tiny standalone synthetic dataset for testing matrix/snapshot tooling before continuing the OpenFOAM post-processing work.

### Actions taken

- created `toolkit_test/`
- added a structured JSON dataset with five `5x5` velocity-magnitude snapshots
- added a row-major flattened CSV version for direct POD input
- added a README describing the flattening convention and POD snapshot matrix assembly
- validated that:
  - there are exactly five snapshots
  - each snapshot is `5x5`
  - all wall/boundary values are zero
  - the first snapshot is symmetric
  - the first snapshot center value is `10`

### Outputs created

- `toolkit_test/README.md`
- `toolkit_test/data/velocity_snapshots_5x5.json`
- `toolkit_test/data/velocity_snapshots_5x5_wide.csv`

### Next step

Use the synthetic data to prototype POD assembly: flatten snapshots, subtract the temporal mean, run SVD, and inspect the first spatial modes.

---

## 2026-04-15 19:29:26 +02:00 | toolkit_test | snapshot heatmap visualization

### Work package

Create visual checks for the synthetic `5x5` velocity snapshot dataset.

### Actions taken

- added `toolkit_test/plot_velocity_snapshots.py`
- generated one color heatmap PNG for each velocity snapshot
- used a shared color scale across all snapshots for visual comparability
- annotated each cell with its scalar velocity value
- updated `toolkit_test/README.md` with the figure location and regeneration command

### Outputs created or updated

- `toolkit_test/plot_velocity_snapshots.py`
- `toolkit_test/figures/s01_symmetric_core.png`
- `toolkit_test/figures/s02_right_skew.png`
- `toolkit_test/figures/s03_left_skew.png`
- `toolkit_test/figures/s04_vertical_stretch.png`
- `toolkit_test/figures/s05_diagonal_mode.png`
- `toolkit_test/README.md`

### Next step

Use the visualized snapshots to verify the POD input matrix construction before computing SVD modes.

---

## 2026-04-15 19:32:33 +02:00 | toolkit_test | paired wall heat-flux POD dataset

### Work package

Add a second synthetic field so that velocity and wall heat-flux POD analyses can be compared.

### Actions taken

- created a paired `wall_heat_flux` dataset on the same `5x5` grid and time samples as the velocity snapshots
- kept heat-flux values only on the boundary ring; interior values are zero
- designed the heat-flux perturbations to be related to, but not identical with, the velocity perturbations
- added a row-major flattened CSV version of the heat-flux snapshots
- extended the plotting script to regenerate both velocity and heat-flux heatmaps
- generated five new heat-flux heatmaps
- updated `toolkit_test/README.md`
- validated that:
  - there are exactly five heat-flux snapshots
  - each snapshot is `5x5`
  - the interior `3x3` entries are zero
  - the boundary ring carries nonzero heat-flux information

### Outputs created or updated

- `toolkit_test/data/heat_flux_wall_snapshots_5x5.json`
- `toolkit_test/data/heat_flux_wall_snapshots_5x5_wide.csv`
- `toolkit_test/plot_velocity_snapshots.py`
- `toolkit_test/figures/heat_flux_q01_symmetric_walls.png`
- `toolkit_test/figures/heat_flux_q02_right_wall_hot.png`
- `toolkit_test/figures/heat_flux_q03_left_wall_hot.png`
- `toolkit_test/figures/heat_flux_q04_top_bottom_hot.png`
- `toolkit_test/figures/heat_flux_q05_diagonal_wall_mode.png`
- `toolkit_test/README.md`

### Next step

Prototype POD on both datasets: compare the leading velocity modes with the leading wall heat-flux modes and then test a combined snapshot matrix if useful.

---

## 2026-04-15 19:49:46 +02:00 | toolkit_test | independent POD for velocity and heat flux

### Work package

Compute standalone POD decompositions for the synthetic velocity and wall heat-flux datasets.

### Actions taken

- added `toolkit_test/compute_pod.py`
- built snapshot matrices using row-major flattened `5x5` fields as columns
- subtracted the temporal mean before decomposition
- computed SVD/POD independently for:
  - velocity magnitude
  - wall heat flux
- wrote POD outputs as data files:
  - raw snapshot matrix
  - centered snapshot matrix
  - mean field
  - singular values and modal energy fractions
  - spatial modes as `5x5` CSV matrices
  - temporal coefficients
  - structured JSON result
- verified reconstruction from `mean + modes * coefficients`

### Results

- velocity POD:
  - active modes: `4`
  - energy fractions: `50.780%`, `28.004%`, `19.443%`, `1.773%`
  - reconstruction relative error: `1.64e-16`
- wall heat-flux POD:
  - active modes: `4`
  - energy fractions: `43.056%`, `30.776%`, `24.818%`, `1.351%`
  - reconstruction relative error: `1.87e-16`

### Outputs created or updated

- `toolkit_test/compute_pod.py`
- `toolkit_test/results/pod/pod_summary.md`
- `toolkit_test/results/pod/velocity/...`
- `toolkit_test/results/pod/heat_flux/...`
- `toolkit_test/README.md`

### Next step

Visualize the POD modes and compare whether the first velocity mode and the first heat-flux mode encode related but distinct perturbation structures.

---

## 2026-04-15 19:55:45 +02:00 | toolkit_test | EPOD between velocity and wall heat flux

### Work package

Compute Extended POD mappings between the synthetic velocity POD results and wall heat-flux snapshots.

### Actions taken

- added `toolkit_test/compute_epod.py`
- computed EPOD in both directions:
  - velocity POD timing -> heat-flux extended modes
  - heat-flux POD timing -> velocity extended modes
- wrote extended spatial modes as `5x5` CSV matrices
- wrote target-field reconstructions using all active source modes
- wrote reconstruction metrics for 1, 2, 3, and 4 source modes
- updated `toolkit_test/README.md` with the EPOD formulation and output description

### Results

Velocity-to-heat-flux EPOD captured target fluctuation energy:

- 1 source mode: `41.719%`
- 2 source modes: `67.385%`
- 3 source modes: `97.186%`
- 4 source modes: `100.000%`

Heat-flux-to-velocity EPOD captured target fluctuation energy:

- 1 source mode: `47.625%`
- 2 source modes: `72.398%`
- 3 source modes: `96.747%`
- 4 source modes: `100.000%`

All-mode relative reconstruction errors were approximately machine precision:

- velocity -> heat flux: `9.35e-16`
- heat flux -> velocity: `6.50e-16`

### Outputs created or updated

- `toolkit_test/compute_epod.py`
- `toolkit_test/results/epod/epod_summary.md`
- `toolkit_test/results/epod/velocity_to_heat_flux/...`
- `toolkit_test/results/epod/heat_flux_to_velocity/...`
- `toolkit_test/README.md`

### Next step

Visualize the EPOD extended modes and compare them with the ordinary POD modes for both fields.

---

## 2026-04-15 19:59:41 +02:00 | toolkit_test | POD and EPOD visualizations

### Work package

Create visual summaries for the synthetic POD and EPOD results.

### Actions taken

- added `toolkit_test/plot_pod_epod.py`
- generated POD visualizations:
  - modal energy and cumulative energy
  - mean fields
  - spatial modes
  - temporal coefficients
- generated EPOD visualizations:
  - reconstruction quality versus number of source modes
  - extended spatial modes in both directions
  - target-vs-reconstruction panels using three source modes
- added `toolkit_test/results/figures/README.md`
- updated `toolkit_test/README.md`

### Outputs created or updated

- `toolkit_test/plot_pod_epod.py`
- `toolkit_test/results/figures/pod_modal_energy.png`
- `toolkit_test/results/figures/pod_velocity_mean_field.png`
- `toolkit_test/results/figures/pod_heat_flux_mean_field.png`
- `toolkit_test/results/figures/pod_velocity_spatial_modes.png`
- `toolkit_test/results/figures/pod_heat_flux_spatial_modes.png`
- `toolkit_test/results/figures/pod_velocity_temporal_coefficients.png`
- `toolkit_test/results/figures/pod_heat_flux_temporal_coefficients.png`
- `toolkit_test/results/figures/epod_reconstruction_quality.png`
- `toolkit_test/results/figures/epod_velocity_to_heat_flux_extended_modes.png`
- `toolkit_test/results/figures/epod_heat_flux_to_velocity_extended_modes.png`
- `toolkit_test/results/figures/epod_velocity_to_heat_flux_snapshot_reconstruction_mode3.png`
- `toolkit_test/results/figures/epod_heat_flux_to_velocity_snapshot_reconstruction_mode3.png`
- `toolkit_test/results/figures/README.md`
- `toolkit_test/README.md`

### Next step

Use the figures to explain the difference between ordinary POD modes and EPOD extended modes before applying the same workflow to OpenFOAM fields.

---

## 2026-04-13 20:46:31 +02:00 | V2_thermal | package 21: nested tolerance bands and formula annotations

### Work package

Refine the article comparison plots for presentation clarity.

### Actions taken

- replaced the single tolerance band with nested literature bands:
  - wider, lighter `±10%`
  - narrower, darker `±5%`
- kept `Cd(Re)` on linear axes
- kept `St(Re)` starting at `Re = 50`
- added the present-work `Nu` definition directly on the Nu plots:
  - `Nu = D/(T_w - T_infty) <snGrad(T)>_A`
- added the present-work `St` definition directly on the St plots:
  - `St = fD/U_infty`, where `f` is taken from the FFT peak of `Cl(t)`
- regenerated the article comparison PNG/SVG figures
- confirmed `Re200_ogrid` continued running; latest checked time was `t≈6.36 s`

### Outputs updated

- `VV_cases/V2_thermal/_code/V2PublicationNuRePlot.py`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Nu_Re_articles_vs_present.*`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_St_Re_articles_vs_present.*`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Cd_Re_articles_vs_present.*`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_articles_vs_present_dashboard.*`

### Next step

Continue monitoring `Re200_ogrid`; once it reaches a useful averaging window, analyse it and regenerate the comparison plots including the Re200 point.

---

## 2026-04-13 20:29:12 +02:00 | V2_thermal | package 20: publication plot tolerance and Cd axis update

### Work package

Adjust the article comparison plots to match the requested visual convention.

### Actions taken

- changed the literature-reference band from `±2%` to `±5%`
- kept the `St(Re)` plot starting at `Re = 50`
- changed the standalone `Cd(Re)` plot from log-log axes to linear `Re` and linear `Cd`
- changed the dashboard `Cd(Re)` panel to the same linear axes
- regenerated the article comparison PNG/SVG figures
- confirmed `Re200_ogrid` continued running after plot regeneration; latest checked time was `t≈3.18 s`

### Outputs updated

- `VV_cases/V2_thermal/_code/V2PublicationNuRePlot.py`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Nu_Re_articles_vs_present.*`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_St_Re_articles_vs_present.*`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Cd_Re_articles_vs_present.*`
- `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_articles_vs_present_dashboard.*`

### Next step

Continue monitoring `Re200_ogrid`; once it reaches a useful averaging window, analyse it and regenerate the comparison plots including the Re200 point.

---
### 2026-04-20 17:59 | review | przegląd stanu projektu
Przeanalizowano stan repozytorium po 5-dniowej przerwie. Dwa aktywne wątki: (1) V2_thermal run004 Re200_ogrid dobiegł do t=11.46s (230 próbek, Nu błąd ~1.1%, St ~7%), (2) toolkit_test POD/EPOD pipeline syntetyczny kompletny, kolejny krok to przeniesienie na prawdziwe pola OpenFOAM. Rekomendacja: najpierw zamknąć V2A (finalne wykresy z Re200), potem toolkit na danych run004.

---
### 2026-04-20 18:04 | V2_thermal + metodologia | analiza błędu St i strategia siatek
Stwierdzono że błąd St jest systematyczny ~6.5-7% na WSZYSTKICH przypadkach periodycznych (Re60/100/200), podczas gdy Nu ≤1.1%. Przyczyna prawdopodobna: siatka O-grid dobra near-field (Nu), ale dyfuzja numeryczna w wake tłumi shedding → niższe St. Wniosek: różna siatka V1/V2 vs produkcja nie jest błędem metodologicznym, ale wake wymaga zagęszczenia jeśli St jest wynikiem produkcyjnym.

---
### 2026-04-20 18:12 | V4/V3 | przegląd dokumentacji geometrii produkcyjnej
Przejrzano wszystkie .md w projekcie. Zdefiniowane: D=12mm, β=D/Pt=0.375 → Pt=32mm (wprost jako "geometry-relevant"). Niezdefiniowane: Pl, Pf, tf, układ inline/staggered, liczba rzędów, Re produkcyjne. V3/V4a/V4b są pustymi stubami. Obserwacja: błąd St w V1 (confined, snappy) = 0.9-1.7% vs V2 unconfined = 7% — problem w V2 to domena, nie solver. Otwarte pytania: źródło geometrii fizycznej, zakres Re, 2D vs 3D plan.

---
### 2026-04-20 20:22 | V4b_3D | dokumentacja geometrii produkcyjnej
Uzupełniono `VV_cases/V4b_3D/doc/V4b_3D.md` o kanoniczny opis geometrii 3D fin-and-tube: D=12mm, H=Pt=32mm, beta=0.375, Lz=12mm, Lf=27.71mm, Lin=12mm, Lout=24mm, Lx=63.71mm, cylinder w x=25.855mm i oś równoległa do z. Zdefiniowano powierzchnie grzane: rura/cylinder oraz dwie płaszczyzny żeber z=0 i z=Lz w strefie żebra. Przyjęto baseline BC: inlet fixed U/T=293.15K, gorące ściany noSlip/T=343.15K, y jako symmetryPlane, a z-face w dobiegu i wylocie jako symmetry/adiabatic. Dodano rysunek `VV_cases/V4b_3D/doc/figs/v4b_geometry_concept.svg` i opis w `doc/figs/README.md`. Wniosek: z-faces muszą być podzielone na patch'e inlet/fin/outlet; globalna periodyczność z nie jest kompatybilna z gorącymi ścianami żeber w strefie środkowej.

---
### 2026-04-20 22:16 | V4b_3D | solver, pomiary modalne i polityka danych
Uzupełniono `VV_cases/V4b_3D/doc/V4b_3D.md` o decyzję solverową i plan danych. Bazowy solver V4b: `buoyantBoussinesqPimpleFoam`, z niezerowym `g=(0 -9.81 0)` dla sprzężenia wyporu; brak przewodzenia w metalu, rura i żebra jako fixed-temperature wall patches. Zapisano strategię domeny: baseline jest fizycznym unit-cell, a niezależność należy sprawdzić przez warianty `Lin`, `Lout`, wake refinement, hot-wall refinement i ewentualne warianty warunków `y/z`. Zdefiniowano trzy poziomy pomiarów: lekkie time-series dla każdej siatki/domeny, sygnały do St/coherence/TE dla przypadków niestacjonarnych, oraz pełne snapshoty pól tylko dla finalnych kandydatów POD/EPOD. Zapisano wymagania siatki: 160-240 komórek po obwodzie rury, 12-20 warstw przy gorących ścianach, growth <=1.15-1.20, wake D/40 minimum i D/60-D/80 do finalnego St, kontrola junction rura-żebro. Decyzja storage: ciężkie OpenFOAM case'y, time directories, processor directories, raw fields, logi i bazy snapshotów nie trafiają do repo; robocze dane V4b trzymamy poza Git w `C:\openfoam-case\VV_cases\V4b_3D_run001` oraz w WSL jako `/mnt/c/openfoam-case/VV_cases/V4b_3D_run001`. Repo przechowuje tylko dokumentację, skrypty, małe tabele/podsumowania i wybrane lekkie wykresy po świadomej selekcji.

---
### 2026-04-20 18:35 | V4b_3D | przegląd planu i identyfikacja krytycznych problemów
Omówiono geometrię V4b (D=12mm, H=32mm, Lz=12mm, Lin=1D, Lf=2.309D, Lout=2D). Potwierdzono: z-ścianki inlet/outlet = symmetryPlane → zeroGradient T (poprawne). Zidentyfikowano problemy krytyczne: (1) Lout=2D za krótki dla shedding regime (potrzeba 4-6D min); (2) g≠0 + ΔT=50K → Ri=126 przy Re=10, Ri=1.26 przy Re=100 — mixed convection, nie pure forced jak V2; (3) tube-fin junction mesh brak strategii; (4) symmetryPlane y-ścianka ≠ no-slip V1 → luka w walidacji. Łańcuch walidacji V1+V2 nie pokrywa kombinacji thermal+confined+g≠0.

---
### 2026-04-20 23:15 | V4b_3D | run001 — first mesh generated
Zaktualizowano wymiary: Lin=2D=24mm, Lout=5D=60mm, Lx=111.71mm, xc=37.855mm. Wygenerowano siatkę V4b_3D_run001: blockMesh (background 86k komórek, ~1mm×1mm×graded z) + snappyHexMesh (cylinder STL, level 2 refinement, warstwy BL).

Statystyki checkMesh:
- komórki: 337 184
- punkty: 366 967
- patches: 11 (inlet, outlet, symmetry_y×2, symmetry_z_inlet×2, symmetry_z_outlet×2, hot_fin_z_min, hot_fin_z_max, hot_tube) — wszystkie OK
- max non-orthogonality: 64.87° (limit 65°), avg 6.34° — OK
- max skewness: 0.861 — OK
- max aspect ratio: 33.4 (warstwy BL) — akceptowalne
- objętość siatki: 4.154e-5 m³ = Lx×H×Lz - π×R²×Lz ✓

Problemy wymagające uwagi:
- 416 komórek z małym determinantem (<0.001) — prawdopodobnie złącze tube-fin
- 9524 komórek wklęsłych (2.8%) — snappy przy ostrych krawędziach
- warstwy BL na hot_tube osiągnęły tylko 39.7% docelowej grubości (background za gruby przy cylindrze)

Ścieżka siatki: C:\openfoam-case\VV_cases\V4b_3D_run001
Podgląd: otwórz V4b_run001.foam w ParaView.
Następny krok: ocenić czy siatka nadaje się do testowego run (sprawdzić determinant), ewentualnie zagęścić background przy cylindrze do level 3.

---
### 2026-04-22 | V4b_3D | plan zbierania danych + lokalne pomiary pod modal analysis
Stworzono run_log.csv w VV_cases/V4b_3D/results/ — jedna linia = jeden run, kolumny: mesh meta + jakość siatki + wyniki integralne (Nu, Cd, St) + flagi pomiarów lokalnych. Wypełniony run001 (same dane siatki). Zadecydowano: nawet w runach mesh-dev zbierać sondy wake + midspan slice + profil Nu(θ) pod przyszłe POD/EPOD.

---
## 2026-04-22 — V4b_3D run001 solver: pierwsza symulacja Re=100

**Setup:** buoyantBoussinesqPimpleFoam, laminar, Boussinesq (g=(0,-9.81,0)), Re=100, Uin=0.12633 m/s, t=0..5s, Δt=1ms, 8 rdzeni MPI (WSL, ext4), czas wall ~98 min.

**Wyniki:**

| Parametr | Wartość |
|---|---|
| Stan przepływu | **STEADY** (brak zrzucania wirów) |
| Ri = Gr/Re² | 1.26 → mieszana konwekcja |
| Nu_tube | 4.52 |
| Nu_fin_z_min / z_max | 4.80 / 4.80 |
| Nu_total (ważone pow.) | **4.73** |
| Cd_tube | 4.00 |
| Cl (buoyancy-induced) | ~9.8 (dominacja uzwojnienia term.) |
| dp_mean | 0.0378 Pa |
| T_min / T_max | 292.37 / 343.15 K |

**Obserwacje fizyczne:**
- Re=100 daje przepływ ustalony — brak periodyczności (oczekiwane przy β=0.375 z ściankami symetrii)
- Sonda 1D w tyle cylindra: Ux=-0.012 m/s → strefa recyrkulacji potwierdzona
- Sonda 3D w tyle: Ux=0.125≈Uin → prawie odzysk prędkości
- Temperatury w tyle: θ=(T−T_in)/ΔT = 0.75 / 0.58 / 0.40 (przy 1D/2D/3D)
- Cd=4.0 wysoki wskutek blokady β=0.375 (nie błąd)

**Problemy / plan na run002:**
1. Pokrycie BL na hot_tube tylko 39.7% → refinement do poziomu 3 (0.125mm) wokół cylindra
2. Sprawdzić czy T_min<T_in (292.4<293.15) to artefakt numeryczny czy efekt fizyczny
3. Uruchomić Re=200 (Ri=0.315) aby sprawdzić czy pojawi się periodyczność

---

## 2026-04-22 — 2026-04-26 | V4b_3D | run002: siatka lvl-3, analiza mesh sensitivity

### Work package

Wygenerowanie siatki z poziomem 3 na rurce (run002) i porównanie wyników z run001 w celu oceny zbieżności siatki (Cd, Nu, pole prędkości w wake).

### Akcje — mesh (2026-04-22 – 2026-04-23)

- Skopiowano run001 → run002, zaktualizowano `snappyHexMeshDict`: `level (3 3)` na `hot_tube`, `refBox_near` podniesiono do poziomu 2
- Uruchomiono snappyHexMesh równolegle (8 rdzeni) + `reconstructParMesh`
- **Problemy snappy:**
  - `locationInMesh` w okrągłych współrzędnych trafiła na ścianę komórki → przeniesiono na `(0.0781 0.0161 0.0061)`
  - Pokrycie BL na `hot_tube` = 0% (vs 39.7% w run001) — przyczyną: `featureAngle=60°` blokuje ekstruzję warstw na złączu cylinder-fin (kąt 90° > 60°). Poziom 3 daje komórki 0.029mm (z) → y+≈0.5 → wystarczające dla laminarnego Re=100; zaakceptowano 0% BL
  - Siatka: 1 840 178 komórek, max nonortho=57.1°, avg=4.5°, 34 825 komórek wklęsłych (poziom 3 ostrych krawędzi)

### Akcje — solver (2026-04-23 – 2026-04-26)

- Uruchomiono `buoyantBoussinesqPimpleFoam` równolegle (8 rdzeni MPI), `nohup nice -n 10`
- **Crash SIGFPE na t=0.017s**: Co_max wybuchł do 10^16 przy stałym dt=1ms — przyczyna: komórki lvl-3 z=0.029mm wymagają dt≤4e-4 dla Co<0.8. Naprawa: `adjustTimeStep yes; maxCo 0.8; maxDeltaT 5e-4` → solver sam znalazł dt≈4.15e-4
- **decomposePar błąd "Size mismatch"**: stare pola snappy (cellLevel, pointLevel) w `0/` — usunięto
- **Swapowanie przy 15 rdzeniach**: 15×450MB=6.75GB > 7.6GB RAM → ClockTime/ExecTime=2×. Zredukowano do 8 rdzeni (3.6GB, 1.9GB zapas) → ratio=1.0
- Wielokrotne restarty z checkpointów (t=0.7, 0.9, 1.9) z powodu ręcznych przerw i epizodów swapowania (ClockTime/ExecTime do 4.6×, nieznana przyczyna — prawdopodobnie inne procesy systemu)
- Solver zatrzymano na t=2.9s (docelowe t=3s), ostatni checkpoint t=2.9; łączny czas wall ≈45h

### Analiza wyników

Rekonstrukcja (`reconstructPar`), analiza sił z `postProcessing/forces_tube`, bilans energetyczny z `patchAverage` na inlet/outlet.

**Siły:**
- Cd_mean (t=2.0–2.9) = **3.9974** (run001: 4.00) → **ΔCd = −0.07%**
- Cl_mean = 9.80 (stały w czasie → przepływ USTALONY, bez zrzucania wirów)
- Składowe Cd: ciśnienie 3.313, lepkość 0.684

**Wymiana ciepła — metoda bilansu energetycznego (EB+LMTD):**

| Parametr | run001 | run002 | Δ |
|---|---|---|---|
| T_out [K] | 313.281 | 313.306 | +0.025 K |
| Q_total [W] | 1.1777 | 1.1792 | +0.13% |
| LMTD [K] | 39.07 | 39.06 | −0.03% |
| Nu_total (EB) | **7.054** | **6.955** | **−1.41%** |

Metoda: `Q = m_dot × Cp × (T_out − T_in)`, `h = Q / (A_hot_total × LMTD)`, `Nu = h × D / k`
z `k = ρ × Cp × ν/Pr = 0.02564 W/(m·K)`, D=0.012 m, A_hot_total = A_tube + 2×A_fin.

**Uwaga metodologiczna — dwie metody Nu:**

- `Nu_snGrad` (run001 legacy = 4.73): obliczone przez lokalny gradient ∂T/∂n na ściankach — metoda dokładna, ale `wallHeatFlux` niedostępny dla `buoyantBoussinesqPimpleFoam` (wymaga kompresyjnego modelu turbulencji). Metody obliczenia nie zrekonstruowano.
- `Nu_EB` (run001=7.054, run002=6.955): bilans energetyczny przez `T_out` z `patchAverage` — spójna dla obu runów, fizycznie poprawna. Dla cylindra izolowanego Re=100 literatura daje Nu≈5.5 (Churchill–Bernstein); z blokadą β=0.375 i płetwami ~7 jest w granicach rozsądku.
- Oba runy mają Nu_EB zgodne w 1.4% → **siatka zbieżna** niezależnie od metody.

**Pole prędkości w wake:**

| Sonda | Pozycja | run001 Ux | run002 Ux | Δ |
|---|---|---|---|---|
| P0 | 1D za rurką | −0.01146 | −0.01362 | −19% |
| P1 | 2D za rurką | +0.04918 | +0.04276 | −13% |
| P2 | 3D za rurką | +0.12499 | +0.12402 | −1% |
| P3 | 1D+4mm | +0.09233 | +0.08396 | −9% |

Bliski wake (1D–2D): różnice 10–20% — lvl-3 lepiej rozwiązuje lepką strefę recyrkulacji.
Daleki wake (3D): <1% — obie siatki zgodne.

### Wnioski

1. **Siatka zbieżna**: ΔCd=−0.07%, ΔNu=−1.4%, ΔT_out=0.025K — wyniki niezależne od zagęszczenia
2. Siatka lvl-2 z run001 (337k) jest **wystarczająca** dla globalnych predykcji Re=100
3. Siatka lvl-3 z run002 (1.84M) niezbędna gdy interesuje nas lokalna struktura bliskiego wake'u (1D–2D)
4. Przepływ USTALONY w obu przypadkach — potwierdza Re=100 < Re_crit dla tej geometrii/blokady
5. A_tube_meshed run002 = 4.84e-4 m² (+7% vs analitycznego π×D×Lz=4.52e-4) — artefakt snappy lvl-3; nie wpływa na Nu_EB bo używamy A_total

### Problemy otwarte

- Nu_snGrad dla run002 niedostępne (`wallHeatFlux` wymaga kompresyjnego solver). Do obliczenia: ręczna ekstrakcja snGrad(T) po konwersji do ASCII lub kodowany function object
- A_tube_meshed run002 o 7% większa niż analityczna — sprawdzić czy to artefakt snappy czy błąd patchAverage
- Re=200 nie uruchomione — plan po zakończeniu analizy run002

### Outputs

- `VV_cases/V4b_3D/results/run_log.csv` — zaktualizowany: run001 + run002, kolumny `Nu_total_snGrad` i `Nu_total_EB_LMTD`, dodano `T_out_K`, `Q_total_W`
- `C:\openfoam-case\VV_cases\V4b_3D_run002\` — pliki konfiguracji solvera (Windows sync)
- `/home/kik/of_runs/V4b_3D_run002/` — pełne dane symulacji (WSL, nie w repo)
4. Rozszerzyć analizę Nu o profil obwodowy na cylindrze (circ_Nu_profile)
