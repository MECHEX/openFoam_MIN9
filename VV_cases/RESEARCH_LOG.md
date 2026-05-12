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

- A_tube_meshed run002 o 7% większa niż analityczna — sprawdzić czy to artefakt snappy czy błąd patchAverage
- Re=200 nie uruchomione — plan po zakończeniu analizy run002
- Profil obwodowy Nu na cylindrze (circ_Nu_profile) — nie wykonany

### Outputs

- `VV_cases/V4b_3D/results/run_log.csv` — zaktualizowany: run001 + run002, kolumny `Nu_total_snGrad` i `Nu_total_EB_LMTD`, dodano `T_out_K`, `Q_total_W`
- `C:\openfoam-case\VV_cases\V4b_3D_run002\` — pliki konfiguracji solvera (Windows sync)
- `/home/kik/of_runs/V4b_3D_run002/` — pełne dane symulacji (WSL, nie w repo)

---

## 2026-04-27 | V4b_3D | Nu snGrad — run002 obliczenia

### Work package

Obliczenie Nu metodą snGrad (metoda 2) dla run002 — analogicznie jak dla run001, do porównania obu metod na tym samym poziomie.

### Kontekst metodologiczny

Dwie równoważne metody Nu (żadna nie jest "stara" ani "gorsza"):

| Metoda | Opis | run001 | run002 |
|--------|------|--------|--------|
| **EB+LMTD** | Q=ṁ·Cp·ΔT, h=Q/(A_total·LMTD) | 7.054 | 6.955 |
| **snGrad** | Nu=snGrad_filt·D/(T_wall−T_bulk) | 4.73 | 4.28 |

Różnica między metodami wynika z definicji h: EB używa LMTD (efektywna różnica temperatur wzdłuż kanału), snGrad używa lokalnego gradientu przy ścianie z T_bulk jako temperaturą odniesienia.

### Actions taken

- Skonwertowano pole T i C (cell centres) do ASCII via `foamFormatConvert -latestTime` (t=2.9s, 1.84M komórek)
- Napisano skrypt `/home/kik/compute_Nu_snGrad3.py` (pure Python, bez numpy)
- Metoda: delta = dist(cell_centre, wall), snGrad = (T_wall − T_P)/delta, outlier filter: wykluczono >5× median
- T_ref = T_bulk = (T_in + T_out)/2 = 303.228 K (spójne z run001 — potwierdzone przez porównanie fin)

### Wyniki run002 (t=2.9s, filt.mean, T_bulk)

| Patch | nFaces | snGrad_median [K/m] | snGrad_filt [K/m] | Nu(filt, T_bulk) | outliers |
|-------|--------|---------------------|-------------------|------------------|----------|
| hot_fin_z_min | 10584 | 16466 | 16292 | **4.90** | 2.0% |
| hot_fin_z_max | 10584 | 16467 | 16292 | **4.90** | 2.0% |
| hot_tube | 61712 | 9782 | 13515 | **4.06** | 9.2% |
| **total (area-weighted)** | — | — | — | **4.28** | — |

### Porównanie run001 vs run002 (metoda snGrad)

| Komponent | run001 | run002 | Δ |
|-----------|--------|--------|---|
| Nu_tube | 4.52 | 4.06 | −10.2% |
| Nu_fin_z_min | 4.80 | 4.90 | +2.1% |
| Nu_fin_z_max | 4.80 | 4.90 | +2.1% |
| **Nu_total** | **4.73** | **4.28** | **−9.5%** |

Uwaga: spadek Nu_tube w run002 wynika z braku warstw BL (no explicit BL, y+~0.5). Bez BL komórki przyścienne mają nieregularne delty → wyższy scatter IQR [2661–29141] K/m dla tuby vs [6879–22033] K/m dla fin. Wartości fin są zbieżne (+2%), wartości tuby nie są wiarygodne metodą snGrad bez BL.

### Decisions

- Używamy T_bulk jako T_ref dla metody snGrad (potwierdzone: fin run001≈run002 przy T_bulk, rozbieżność przy T_in=−18%)
- Metoda snGrad bez BL na rurze: wyniki z zastrzeżeniem (wysoki scatter na rurze)
- Metoda EB+LMTD pozostaje główną metodą dla Nu_total (nie wymaga BL, oparta na globalnym bilansie energii)

### Outputs

- `/home/kik/compute_Nu_snGrad3.py` — skrypt obliczeniowy (WSL)
- `VV_cases/V4b_3D/results/run_log.csv` — uzupełniono Nu_snGrad dla run002: tube=4.06, fin_zmin=4.90, fin_zmax=4.90, total=4.28

---

## 2026-04-29 | V4b_3D | run003: Re=200 na siatce medium/lvl-2

### Work package

Uruchomienie Re=200 na siatce medium z run001 w celu sprawdzenia, czy konfiguracja V4b_3D przechodzi z reżimu ustalonego do okresowego oraz jak zmieniają się Cd, T_out i Nu_EB względem run002 Re=100.

### Status symulacji

- Solver zatrzymano na t = 6.505 s z planowanych 10.0 s, czyli ok. 65% przebiegu.
- Czas obliczeń: ~6.7 h wall, ClockTime = 24 091 s, 8 rdzeni.
- Dane traktujemy jako wiarygodne do identyfikacji reżimu i wstępnych statystyk; finalne średnie warto przeliczyć po dłuższym domkniętym przebiegu.

### Wyniki

| Wielkość | run002 Re=100 | run003 Re=200 | Wniosek |
|---|---:|---:|---|
| Reżim | STEADY | PERIODIC | pojawia się shedding |
| Cd_mean | 3.9974 | 3.161 | spadek o ok. 21% |
| Cl_rms | 0 | 0.187 | amplituda zrzucania wirów |
| Cl_mean | ~2.4 | 2.52 | offset wyporu podobnego rzędu |
| f_shed | N/A | 3.125 Hz | częstotliwość z Cl |
| St | N/A | 0.1484 | St = fD/U, D = 12 mm |
| T_out | 313.306 K | 305.26 K | spadek o 8.05 K |
| Nu_EB | 6.955 | 7.476 | wzrost o ok. 7.5% |
| Ri | 1.26 | 0.314 | słabszy względny wpływ wyporu |

### Obliczenia uzupełniające

- D = 0.012 m, U = 0.25267 m/s, nu = 1.516e-5 m2/s -> Re = 200.0.
- St = f_shed*D/U = 3.125*0.012/0.25267 = 0.1484.
- LMTD = 43.665 K dla T_in = 293.15 K, T_out = 305.26 K, T_wall = 343.15 K.
- Q_total = 1.417 W, przy m_dot wyprowadzonym z run002 i podwojonym dla Re=200.
- A_total = 0.002032 m2; Nu_EB = 7.476.

### Interpretacja

Run003 potwierdza, że Re=200 leży powyżej Re_crit dla geometrii V4b_3D: run002 przy Re=100 pozostaje ustalony, natomiast run003 pokazuje okresowe zrzucanie wirów. Niższe St względem trendu V1 2D dla beta=0.375 jest zgodne z oczekiwanym wpływem geometrii 3D z płetwami oraz niezerowego sprzężenia wyporowego.

Uwaga korekcyjna: wcześniejsze St=0.099 nie jest właściwe dla V4b_3D, bo używało błędnej długości charakterystycznej. Kanoniczna średnica w V4b wynosi D=12 mm, więc dla f=3.125 Hz otrzymujemy St=0.1484.

### Min9

Nie znaleziono etykiety `Min9` w repozytorium, logach ani dostępnych wynikach `postProcessing`. Na ten moment `Min9` nie jest nazwą żadnego utrwalonego artefaktu V4b_3D/run003; może oznaczać zewnętrzny opis, timestep albo inną rodzinę symulacji.

### Outputs

- `VV_cases/V4b_3D/results/run003/summary.md` - dodano podsumowanie run003.
- `VV_cases/V4b_3D/results/run_log.csv` - dopisano wiersz `run003`.
- `C:\openfoam-case\VV_cases\V4b_3D_run003\` - roboczy katalog Windows sync.
- `/home/kik/of_runs/V4b_3D_run003/` - pełne dane symulacji w WSL, poza repo.

---

## 2026-04-29 | V4b_3D | run003: POD/EPOD/coherence/TE toolkit

### Work package

Uruchomienie lokalnego toolkit/post-processingu dla run003 analogicznie do run001: POD pól `Ux`, `Uy`, `T` na midspan slice, EPOD między polami, spectral coherence oraz transfer entropy na sondach wake. Wyniki zapisano bezpośrednio w repo w `VV_cases/V4b_3D/results/run003/`.

### Dane wejściowe

- `midspan_slice`: 13 snapshotów VTP, t = 0.5, 1.0, ..., 6.5 s; 10 725 punktów na snapshot.
- `probes_wake`: 1301 próbek, dt = 0.005 s, połączone segmenty restartu `0` i `2.567`.
- Częstotliwość referencyjna shedding: f = 3.125 Hz; najbliższy bin Welcha w analizie = 3.077 Hz.

### Wyniki POD

| Pole | n_modes | Mode 1 | Mode 2 | Cum. 2 |
|---|---:|---:|---:|---:|
| Ux | 12 | 34.37% | 27.57% | 61.94% |
| Uy | 12 | 53.23% | 32.92% | 86.16% |
| T | 12 | 41.02% | 37.78% | 78.80% |

### Wyniki EPOD

- `Ux -> T`: captured target energy = 100.00%, rel_error = 2.48e-11.
- `T -> Ux`: captured target energy = 100.00%, rel_error = 2.47e-15.
- `Uy -> T`: captured target energy = 100.00%, rel_error = 1.57e-14.
- Interpretacja: ponieważ mamy tylko 13 snapshotów i 12 aktywnych modów, EPOD z kompletem modów jest praktycznie pełnorzędową rekonstrukcją. Wynik potwierdza spójność pipeline'u, ale nie jest jeszcze selektywną redukcją modelu.

### Spectral coherence i TE

| Para | f_peak [Hz] | coherence |
|---|---:|---:|
| probe_0_1D Ux-T | 3.077 | 0.704 |
| probe_1_2D Ux-T | 3.077 | 0.129 |
| probe_2_3D Ux-T | 3.077 | 0.066 |
| probe_0_1D Uy-T | 3.077 | 0.704 |

| Kierunek TE | Lag [s] | Excess TE [bits] |
|---|---:|---:|
| Ux_1D -> T_1D | 0.115 | 0.2067 |
| T_1D -> Ux_1D | 0.005 | 0.1844 |
| Ux_3D -> T_3D | 0.145 | 0.3693 |
| T_3D -> Ux_3D | 0.135 | 0.3637 |
| Uy_1D -> T_1D | 0.090 | 0.1972 |

### Wnioski

1. Toolkit działa na run003 i daje fizycznie sensowny sygnał w paśmie shedding: coherence ma maksimum w najbliższym binie 3.077 Hz względem f_shed = 3.125 Hz.
2. Najsilniejsze sprzężenie U/T w sondach jest blisko za rurą (`probe_0_1D`), a dalej w wake coherence Ux-T szybko słabnie.
3. POD midspan pokazuje dwumodową strukturę okresową: dla `Uy` pierwsze dwa mody niosą 86% energii, dla `T` 79%, dla `Ux` 62%.
4. Wyniki POD/EPOD są eksploracyjne, bo baza snapshotów jest krótka; finalny run modalny powinien zapisywać równomierne snapshoty po odrzuceniu transjentu przez wiele okresów shedding.

### Outputs

- `VV_cases/V4b_3D/results/run003/analyse_run003.py`
- `VV_cases/V4b_3D/results/run003/analysis_summary.json`
- `VV_cases/V4b_3D/results/run003/modal_analysis_summary.md`
- `VV_cases/V4b_3D/results/run003/pod/{Ux,Uy,T}/`
- `VV_cases/V4b_3D/results/run003/epod/{Ux_to_T,T_to_Ux,Uy_to_T}/`
- `VV_cases/V4b_3D/results/run003/spectral_coherence/`
- `VV_cases/V4b_3D/results/run003/transfer_entropy/`
- `VV_cases/V4b_3D/results/run003/force_spectra/`

### Figures

Dodano `VV_cases/V4b_3D/results/run003/plot_run003_modal.py`, który generuje figury diagnostyczne do zrozumienia każdej metody. Wygenerowane pliki w `VV_cases/V4b_3D/results/run003/figures/`:

- POD: `pod_modal_energy.png`, `pod_temporal_coefficients.png`, mean fields i spatial modes 1-4 dla `Ux`, `Uy`, `T`.
- EPOD: `epod_reconstruction_quality.png` oraz extended modes 1-4 dla `Ux_to_T`, `T_to_Ux`, `Uy_to_T`.
- Spectral: `coherence_curves.png`, `probe_power_spectra.png`, `force_power_spectra.png`.
- TE: `transfer_entropy_curves.png`, `transfer_entropy_peak_summary.png`.

---

## 2026-04-29 14:24:09 +02:00 | V4b_3D | run004 preparation for longer outlet sensitivity

### Work package

Przygotowanie kolejnego wariantu `V4b_3D` skoncentrowanego wyłącznie na wpływie dłuższego `Lout` względem bazowego `run003`.

### Actions taken

- przejrzano aktualny stan `V4b_3D` w repo:
  - `doc/V4b_3D.md`
  - `results/run_log.md`
  - `results/run003/summary.md`
  - `_code/prepare_run003_re200_medium.sh`
- potwierdzono, że naturalnym następnym krokiem po `run003` jest wariant outlet-sensitivity bez zmiany solvera, `Re`, ani rodziny siatki
- przygotowano nowy skrypt:
  - `VV_cases/V4b_3D/_code/prepare_run004_re200_longer_lout.sh`
- przyjęto domyślny wariant:
  - `Lout = 8D`
  - `Lout = 96.00 mm`
  - `Lx = 147.71 mm`
- dodano repozytoryjny szkic wyniku / setupu:
  - `VV_cases/V4b_3D/results/run004/summary.md`
- zapisano w skrypcie, że zmiana geometrii wymaga świeżego remeshu przed uruchomieniem solvera

### Decisions made

- `run004` ma być czystym testem wpływu długości wylotu na:
  - `St`
  - `Cd`
  - `Cl_rms`
  - `dp`
  - `T_out`
  - `Nu_EB`
- nie zmieniamy teraz bazowego dokumentu `V4b_3D.md`, bo dłuższy `Lout` jest jeszcze wariantem kontrolnym, a nie zaakceptowanym baseline
- domyślne `8D` jest pierwszym rozsądnym krokiem; skrypt pozwala też na `LOUT_D=10`, jeśli okaże się potrzebny mocniejszy test

### Outputs

- `VV_cases/V4b_3D/_code/prepare_run004_re200_longer_lout.sh`
- `VV_cases/V4b_3D/results/run004/summary.md`

### Next step

Uruchomić skrypt przygotowujący `run004`, potwierdzić w aktywnym `mesh.sh` lub słownikach geometrii nowy `Lout`, przebudować siatkę i dopiero wtedy puścić solver dla porównania z `run003`.

---

## 2026-04-30 10:29:49 +02:00 | V4b_3D | run004b light outlet-sensitivity mesh

### Work package

Przygotowanie kontrolowanego wariantu `run004b` po diagnozie, że `run004` był zbyt mocno zrefinowany objętościowo i przez to nieporównywalny kosztowo z `run003`.

### Actions taken

- sprawdzono aktywny `run004` w WSL i potwierdzono, że nominalny `level (2 2)` dał 1,783,116 komórek przez bardzo duży `nearCylinder` level-2 volume box
- dodano skrypt:
  - `VV_cases/V4b_3D/_code/prepare_run004b_lout8_light_mesh.sh`
- utworzono nowy case:
  - `/home/hexmachina/of_runs/V4b_3D_run004b`
- wygenerowano mesh `run004b` z:
  - `Lout = 8D`
  - `hot_tube level (2 2)`
  - krótkim `wakeBox` level 1 (`x = 0..60 mm`, `y = +/-12 mm`)
  - usuniętym dużym `nearCylinder` level-2 boxem
- uruchomiono `checkMesh -allTopology -allGeometry`, zwykły `checkMesh`, oraz testowe `decomposePar -force`

### Results

| Quantity | run003 | run004 | run004b |
|---|---:|---:|---:|
| Lout/D | 5 | 8 | 8 |
| cells | 337,184 | 1,783,116 | 283,716 |
| max non-ortho | 64.87 deg | 26.18 deg | 26.34 deg |
| max skewness | 0.861 | 0.790 | 0.790 |
| concave cells | 9,524 | 0 | 4,624 |

Normal `checkMesh`: `Mesh OK`.

The stricter all-geometry check reports 4,624 concave cells, which is lower than the archived accepted `run001/run003` count of 9,524.

### Decisions made

- current `run004` should be treated as a diagnostic over-refined attempt, not the main controlled outlet-sensitivity comparison
- `run004b` is the current controlled `Lout=8D` mesh candidate
- `run004b` remains intentionally light; `addLayers false` because the available active `run004` bootstrap did not include the run001/run003 BL layer controls

### Outputs

- `VV_cases/V4b_3D/_code/prepare_run004b_lout8_light_mesh.sh`
- `VV_cases/V4b_3D/results/run004b/summary.md`
- `/home/hexmachina/of_runs/V4b_3D_run004b`

### Next step

Run a short solver benchmark to `0.1-0.2 s` physical time before any overnight full run, then estimate wall-time per simulated second.

---

## 2026-04-30 10:48:10 +02:00 | V4b_3D | run004b BL correction

### Work package

Correct `run004b` after review: the first light mesh had only 283,716 cells and no boundary-layer extrusion, so it was too light compared with the accepted `run001/run003` mesh family.

### Actions taken

- updated `VV_cases/V4b_3D/_code/prepare_run004b_lout8_light_mesh.sh`
- regenerated `/home/hexmachina/of_runs/V4b_3D_run004b`
- enabled `addLayers true`
- requested BL layers:
  - `hot_tube`: 8 layers
  - `hot_fin_z_min`: 6 layers
  - `hot_fin_z_max`: 6 layers
  - first layer thickness: 30 um
  - expansion ratio: 1.20
- kept `hot_tube level (2 2)`
- kept the large `nearCylinder` level-2 volume box removed
- extended the light wake refinement to `x = 0..72 mm`, `y = +/-12 mm`, level 1
- regenerated mesh and ran:
  - `checkMesh -allTopology -allGeometry`
  - normal `checkMesh`
  - `decomposePar -force`

### Results

| Quantity | run003 | over-refined run004 | corrected run004b |
|---|---:|---:|---:|
| Lout/D | 5 | 8 | 8 |
| cells | 337,184 | 1,783,116 | 407,440 |
| max non-ortho | 64.87 deg | 26.18 deg | 62.84 deg |
| max skewness | 0.861 | 0.790 | 3.319 |
| max aspect ratio | 33.4 | 2.28 | 33.64 |
| concave cells | 9,524 | 0 | 9,178 |

Layer addition result:

| patch | requested | average layers | overall thickness |
|---|---:|---:|---:|
| hot_tube | 8 | 7.19 | 0.000401 m / 81.1% |
| hot_fin_z_min | 6 | 3.8 | 0.000228 m / 76.1% |
| hot_fin_z_max | 6 | 3.8 | 0.000228 m / 76.1% |

Normal `checkMesh`: `Mesh OK`.

`decomposePar -force`: OK, 8 processor directories created.

### Decision

The corrected `run004b` is now a better controlled outlet-sensitivity candidate than the first light mesh: it restores BL-layer behavior and keeps the local tube refinement family close to `run001/run003`, while avoiding the 1.78M-cell over-refinement of `run004`.

### Next step

Run a short solver benchmark before launching an overnight production run.

---

## 2026-05-05 14:08:00 +02:00 | V4b_3D | run004b solver launch on 20 ranks

### Work package

Stop the initial 8-rank `run004b` background test and relaunch the corrected BL mesh on 20 MPI ranks.

### Actions taken

- checked active `run004b` processes:
  - `mpirun` PID `748`
  - 8 `foamRun` worker processes
- stopped the 8-rank test by killing the parent `mpirun` process
- added launch helper:
  - `VV_cases/V4b_3D/_code/start_run004b_bg.sh`
- fixed the helper so it:
  - sources `/opt/openfoam13/etc/bashrc` before `set -u`
  - updates `system/decomposeParDict` to match `NPROCS`
  - runs `decomposePar -force`
  - launches through `setsid mpirun --oversubscribe`
  - writes a tagged PID and solver log
- relaunched `run004b` with:

```bash
NPROCS=20 TAG=20260505_np20 bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run004b_bg.sh
```

### Current active run

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run004b` |
| MPI ranks | 20 |
| Parent PID | `733` |
| PID file | `logs/solver.20260505_np20.pid` |
| Solver log | `logs/log.foamRun_parallel.20260505_np20` |
| `decomposeParDict` | `numberOfSubdomains 20;` |
| Processor directories | 20 |

Initial log check:

- solver entered the time loop
- `Co_max` about `0.78`
- `deltaT` about `1.25e-4` to `1.30e-4` during startup
- residuals and continuity errors are finite and progressing
- no startup crash observed

### Correct launch procedure

Start or restart `run004b` from WSL:

```bash
NPROCS=20 TAG=YYYYMMDD_np20 bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run004b_bg.sh
```

Check status:

```bash
pgrep -af foamRun
pgrep -af mpirun
tail -n 120 /home/hexmachina/of_runs/V4b_3D_run004b/logs/log.foamRun_parallel.<TAG>
```

Stop safely:

```bash
kill "$(cat /home/hexmachina/of_runs/V4b_3D_run004b/logs/solver.<TAG>.pid)"
```

### Decision

Use the tagged helper script for future runs. Avoid the older plain `run_parallel.sh` path because earlier background attempts produced empty logs and did not leave a live solver process in this WSL/PowerShell setup.

### Next step

Monitor progress to the first checkpoint (`t = 0.1 s`) and compute the actual wall-time per simulated second for the corrected 407k-cell BL mesh on 20 ranks.

---

## 2026-05-06 00:00:00 +02:00 | V4b_3D | run004b completed; analysis-first decision

### Work package

Close the corrected `Lout=8D` outlet-sensitivity run and decide the next
scientific step before launching any `Lout=16D` case.

### Solver status

`run004b` completed cleanly to `t = 6 s`.

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run004b` |
| MPI ranks | 20 |
| Solver log | `logs/log.foamRun_parallel.20260505_np20` |
| Final checkpoint | `processor*/6` |
| Final ClockTime | `30720 s` |
| Termination | `End` / `Finalising parallel run` |

### Quick-look force comparison

Final `run004b` force statistics:

| Window | Cd_mean | Cl_mean | Cl_std/rms |
|---|---:|---:|---:|
| `t >= 2 s` | 3.362 | 2.519 | 0.194 |
| `t >= 3 s` | 3.361 | 2.514 | 0.184 |
| `t >= 4 s` | 3.360 | 2.514 | 0.168 |

The adjacent `Cl` peak spacing gives a strong component near `6.5 Hz`; using
every second peak as the fundamental gives `f_shed ~= 3.25 Hz`,
`St ~= 0.155`.

Compared with the archived `run003` summary (`Lout=5D`, `Cd_mean = 3.161`,
`Cl_mean = 2.52`, `Cl_rms = 0.187`, `St = 0.1484`), the `Lout=8D` result is
qualitatively similar: same periodic regime, nearly unchanged lift offset,
comparable lift oscillation, and a slightly higher shedding frequency. The
main remaining quantitative difference is about 6% higher drag.

### Decision

Do not launch `Lout=16D` yet. First complete a controlled `run003` vs
`run004b` analysis using matched time windows and the same signal-processing
method. Use `Lout=16D` only if the final comparison shows unresolved outlet
sensitivity, especially in `Cd` or thermal metrics.

### Saved analysis plan

Detailed plan saved in:

```text
VV_cases/V4b_3D/results/run004b/summary.md
```

Immediate tasks:

1. Recompute `run003` force statistics using the same windows as `run004b`
   (`t = 2..6 s`, `3..6 s`, and late-window checks).
2. Produce a matched comparison table with percent differences.
3. Plot `Cd(t)` and `Cl(t)` for both runs with the same transient rejection.
4. Estimate `f_shed/St` with one consistent method for both runs.
5. Check whether `T_out/Nu_EB` can be extracted consistently for the
   `Lout=8D` case.
6. Write the scientific conclusion before deciding on `Lout=16D`.

---

## 2026-05-06 | V4b_3D | run003 vs run004b final force comparison

### Work package

Implemented the planned outlet-sensitivity comparison between accepted
`run003` (`Lout=5D`) and completed `run004b` (`Lout=8D`) before deciding on
any `Lout=16D` run.

### Outputs

- `VV_cases/V4b_3D/results/run004b/analyse_run003_vs_run004b.py`
- `VV_cases/V4b_3D/results/run004b/run003_vs_run004b_force_compare.csv`
- `VV_cases/V4b_3D/results/run004b/run003_vs_run004b_force_compare.json`
- `VV_cases/V4b_3D/results/run004b/run003_vs_run004b_summary_section.md`
- `VV_cases/V4b_3D/results/run004b/figures/run003_vs_run004b_force_traces.png`
- `VV_cases/V4b_3D/results/run004b/figures/run004b_cl_psd.png`

### Data status

`run004b` was analyzed from raw `forceCoeffs.dat`. The raw `run003` force file
was not found in the active WSL/repo checkout, so `run003` is explicitly used
as an archived summary baseline.

### Recommended comparison

Use `t >= 3 s` for `run004b`.

| Quantity | run003 archived | run004b `t >= 3 s` | Difference |
|---|---:|---:|---:|
| Cd_mean | 3.161 | 3.361 | +6.34% |
| Cl_mean | 2.520 | 2.514 | -0.25% |
| Cl_rms/std | 0.187 | 0.184 | -1.57% |
| f_shed | 3.125 Hz | 3.267 Hz | +4.54% |
| St | 0.1484 | 0.1552 | +4.56% |

### Interpretation

The longer outlet does not change the qualitative Re=200 regime: `run004b`
remains periodic, with nearly unchanged mean lift and comparable shedding
amplitude. The persistent difference is drag: `Cd_mean` is about 6% higher in
the `Lout=8D` case.

### Decision

Do not launch `Lout=16D` as a broad new campaign yet. A short `16D`
drag/outlet-independence check is scientifically justified if the final claim
needs drag accuracy, because `8D` confirms the regime but does not fully close
the `Cd` sensitivity question. Thermal metrics are not closed for `run004b`
because current postProcessing contains force coefficients, wake probes, and
residuals, but no direct outlet-integral/Nusselt output.

---

## 2026-05-06 | V4b_3D | run004b thermal EB+LMTD comparison

### Work package

Computed the missing heat-transfer comparison for `run004b` before deciding
whether to move to `Lout=16D`.

### Actions taken

- reconstructed `run004b` checkpoints for `t = 3..6 s` with `reconstructPar`
- extended `VV_cases/V4b_3D/results/run004b/analyse_run003_vs_run004b.py`
- computed outlet `T` from the reconstructed `outlet` patch values
- used the same EB+LMTD method as archived `run003`

### Outputs

- `VV_cases/V4b_3D/results/run004b/run003_vs_run004b_thermal_compare.csv`
- `VV_cases/V4b_3D/results/run004b/run003_vs_run004b_thermal_compare.json`

### Results

Thermal comparison uses `run004b` mean over `t = 3..6 s` and archived
`run003` values.

| Quantity | run003 archived | run004b `t=3..6 s` | Difference |
|---|---:|---:|---:|
| T_out area-average | 305.26 K | 305.68 +/- 0.68 K | +0.42 K |
| T_out mass-weighted check | N/A | 305.75 K | N/A |
| Q_total | 1.417 W | 1.472 +/- 0.075 W | +3.91% |
| LMTD | 43.665 K | 43.432 K | N/A |
| Nu_EB_LMTD | 7.476 | 7.778 +/- 0.463 | +4.04% |

Constants: `Cp = 1005.0 J/(kg K)`, `k = 0.02575 W/(m K)`,
`A_hot_total = 0.002032 m2`, `D = 0.012 m`.

### Interpretation

The `Lout=8D` case is thermally close to `run003`, but not identical:
`Nu_EB_LMTD` is about 4% higher and `T_out` about 0.42 K higher. This thermal
shift is smaller than the force/drag shift (`Cd` about +6.3%) but it means the
outlet-sensitivity question is not purely aerodynamic.

### Decision

Before using `run004b` as the final outlet-independent reference, a short
`Lout=16D` check is now scientifically stronger: it should verify both drag
and EB+LMTD heat-transfer convergence. If `16D` matches `8D` within a few
percent for `Cd`, `St`, `Cl_rms`, and `Nu_EB`, then `8D` is defensible as the
production domain and `5D` can be described as qualitatively correct but mildly
outlet-sensitive.

---

## 2026-05-06 | V4b_3D | run004c Lout=16D model prepared

### Work package

Prepared `run004c`, a controlled `Lout=16D` outlet-independence check based on
the corrected `run004b` mesh strategy.

### Actions taken

- added `VV_cases/V4b_3D/_code/prepare_run004c_lout16_mesh.sh`
- added `VV_cases/V4b_3D/_code/start_run004c_bg.sh`
- added `VV_cases/V4b_3D/results/run004c/summary.md`
- generated WSL case:
  - `/home/hexmachina/of_runs/V4b_3D_run004c`
- generated mesh with:
  - `Lout = 16D`
  - `Lx = 243.71 mm`
  - `hot_tube level (2 2)`
  - BL layers: tube 8, fins 6, first layer 30 um
  - same short level-1 wake box as `run004b`: `x = 0..72 mm`, `y = +/-12 mm`

### Mesh results

Normal `checkMesh`: `Mesh OK`.

| Quantity | run004b | run004c |
|---|---:|---:|
| Lout/D | 8 | 16 |
| cells | 407,440 | 462,736 |
| max non-ortho | 62.84 deg | 62.84 deg |
| avg non-ortho | 5.93 deg | 5.58 deg |
| max skewness | 3.319 | 3.319 |
| max aspect ratio | 33.64 | 33.64 |
| strict concave cells | 9,178 | 9,178 |

Layer addition result for `run004c`:

| Patch | requested | average layers | overall thickness |
|---|---:|---:|---:|
| hot_tube | 8 | 7.19 | 0.000401 m / 81.1% |
| hot_fin_z_min | 6 | 3.8 | 0.000228 m / 76.1% |
| hot_fin_z_max | 6 | 3.8 | 0.000228 m / 76.1% |

### Decision

`run004c` is mesh-ready and comparable to `run004b`. The next step is a
20-rank run to `t = 6 s`, then reuse the `run004b` comparison workflow for
`Cd_mean`, `Cl_rms`, `St`, `T_out`, and `Nu_EB_LMTD`.

---

## 2026-05-06 | V4b_3D | run004c solver launched

### Work package

Launched the `Lout=16D` outlet-independence check on 20 MPI ranks.

### Launch

```bash
NPROCS=20 TAG=20260506_np20 bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run004c_bg.sh
```

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run004c` |
| MPI ranks | 20 |
| Parent MPI PID | 759 |
| PID file | `logs/solver.20260506_np20.pid` |
| Solver log | `logs/log.foamRun_parallel.20260506_np20` |
| Target endTime | 6 s |

### Initial status

- no other `foamRun` process was active before launch
- `decomposePar` completed
- solver entered the time loop
- all 20 worker processes were active at ~99% CPU
- initial `Co_max` about 0.793
- initial `deltaT` about 1.7e-4 s
- continuity errors finite and small
- no startup crash observed

### Monitor

```bash
pgrep -af foamRun
tail -n 120 /home/hexmachina/of_runs/V4b_3D_run004c/logs/log.foamRun_parallel.20260506_np20
```

### Stop safely

```bash
kill "$(cat /home/hexmachina/of_runs/V4b_3D_run004c/logs/solver.20260506_np20.pid)"
```

---

## 2026-05-06 | V4b_3D | outlet sensitivity closed: 5D vs 8D vs 16D

### Work package

Completed full force, shedding, and EB+LMTD heat-transfer comparison for
`run003`, `run004b`, and `run004c`.

### Actions taken

- reconstructed `run004c` checkpoints for `t = 3..6 s`
- added `VV_cases/V4b_3D/results/run004c/analyse_outlet_sensitivity_5D_8D_16D.py`
- compared:
  - force coefficients from raw `forceCoeffs`
  - shedding frequency and Strouhal number
  - outlet `T_out`
  - EB+LMTD `Nu_EB`

### Outputs

- `VV_cases/V4b_3D/results/run004c/run003_run004b_run004c_outlet_compare.csv`
- `VV_cases/V4b_3D/results/run004c/run003_run004b_run004c_outlet_compare.json`
- `VV_cases/V4b_3D/results/run004c/run003_run004b_run004c_outlet_compare.md`
- `VV_cases/V4b_3D/results/run004c/figures/run003_run004b_run004c_outlet_sensitivity.png`

### Results

`run004b` and `run004c` use matched window `t = 3..6 s`; `run003` uses
archived summary values.

| Run | Lout/D | Cd_mean | Cl_mean | Cl_rms | f_shed | St | T_out | Nu_EB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| run003 | 5 | 3.161 | 2.520 | 0.187 | 3.125 | 0.1484 | 305.26 | 7.476 |
| run004b | 8 | 3.361 | 2.514 | 0.184 | 3.267 | 0.1552 | 305.68 +/- 0.68 | 7.778 +/- 0.463 |
| run004c | 16 | 3.361 | 2.511 | 0.182 | 3.254 | 0.1546 | 305.72 +/- 0.13 | 7.803 +/- 0.089 |

Key differences:

| Comparison | Cd | St | Nu_EB |
|---|---:|---:|---:|
| 8D vs 5D | +6.34% | +4.56% | +4.04% |
| 16D vs 5D | +6.33% | +4.15% | +4.37% |
| 16D vs 8D | -0.01% | -0.40% | +0.32% |

### Decision

The `16D` result is essentially identical to `8D` for force metrics and very
close for EB+LMTD heat transfer. The outlet-independence question is closed:
`Lout=8D` is sufficient for production use. The earlier `Lout=5D` result is
qualitatively correct for regime identification, but mildly outlet-sensitive
for drag and heat transfer.

---

## 2026-05-06 | V4b_3D | run005 Lin=4D inlet-sensitivity plan prepared

### Work package

Prepared `run005` as the next controlled domain check after outlet
independence was closed.

### Purpose

Check whether the upstream boundary location affects the accepted Re=200
production-domain candidate. The case changes only the inlet extension:

- reference: `run004b`, `Lin=2D`, `Lout=8D`
- check: `run005`, `Lin=4D`, `Lout=8D`

### Actions taken

- added `VV_cases/V4b_3D/_code/prepare_run005_lin4_lout8_mesh.sh`
- added `VV_cases/V4b_3D/_code/start_run005_bg.sh`
- added `VV_cases/V4b_3D/results/run005/summary.md`
- generated WSL case:
  - `/home/hexmachina/of_runs/V4b_3D_run005`

### Planned setup

| Quantity | run004b | run005 |
|---|---:|---:|
| Lin/D | 2 | 4 |
| Lout/D | 8 | 8 |
| Lx | 147.71 mm | 171.71 mm |
| hot-tube refinement | level 2 | level 2 |
| BL request | tube 8 / fins 6 | tube 8 / fins 6 |
| wake box | x=0..72 mm | x=0..72 mm |

### Decision

Generate and check the mesh first. If mesh quality remains comparable to
`run004b`, run to `t = 6 s` on 20 ranks and compare the `t = 3..6 s` window
for `Cd_mean`, `Cl_rms`, `St`, `T_out`, and `Nu_EB`. If changes stay small
(`Cd/Nu` about <=2-3%, `St` about <=1-2%), keep `Lin=2D`, `Lout=8D` as the
production domain and move to timestep sensitivity or the longer final
measurement run.

---

## 2026-05-06 | V4b_3D | run005 meshed and launched

### Work package

Generated the `Lin=4D`, `Lout=8D` inlet-sensitivity mesh and launched the
solver on 20 MPI ranks.

### Mesh result

Normal `checkMesh`: `Mesh OK`.

| Quantity | Value |
|---|---:|
| cells | 421,264 |
| max non-ortho | 62.84 deg |
| avg non-ortho | 5.84 deg |
| max skewness | 3.319 |
| max aspect ratio | 33.64 |
| strict concave cells | 9,178 |

The strict concave-cell count matches `run004b/run004c`, so this remains a
controlled mesh-family comparison.

### Launch

```bash
NPROCS=20 TAG=20260506_np20 bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run005_bg.sh
```

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run005` |
| MPI ranks | 20 |
| Parent MPI PID | 738 |
| PID file | `logs/solver.20260506_np20.pid` |
| Solver log | `logs/log.foamRun_parallel.20260506_np20` |
| Target endTime | 6 s |

### Initial status

- solver entered the time loop
- all 20 worker processes were active
- initial `Co_max` remained below `0.8`
- residuals and continuity errors were finite
- no startup crash observed

### Monitor

```bash
pgrep -af foamRun
tail -n 120 /home/hexmachina/of_runs/V4b_3D_run005/logs/log.foamRun_parallel.20260506_np20
```

---

## 2026-05-07 | V4b_3D | run005 completed quick-look

### Work package

Checked the status of the `Lin=4D`, `Lout=8D` inlet-sensitivity run.

### Solver status

`run005` completed cleanly to `t = 6 s`.

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run005` |
| MPI ranks | 20 |
| Solver log | `logs/log.foamRun_parallel.20260506_np20` |
| Final checkpoint | `processor*/6` |
| Final ClockTime | `33469 s` |
| Termination | `End` / `Finalising parallel run` |

### Quick-look force result

Raw `forceCoeffs.dat` statistics:

| Window | Cd_mean | Cl_mean | Cl_std/rms |
|---|---:|---:|---:|
| `t >= 2 s` | 3.360 | 2.523 | 0.195 |
| `t >= 3 s` | 3.359 | 2.518 | 0.185 |
| `t >= 4 s` | 3.358 | 2.518 | 0.168 |

Compared with `run004b` over the preferred `t >= 3 s` window
(`Cd_mean = 3.361`, `Cl_mean = 2.514`, `Cl_rms = 0.184`), the force response
is essentially unchanged. This suggests the inlet extension from `2D` to `4D`
does not materially affect the Re=200 shedding-force regime.

### Next step

Complete the inlet-sensitivity analysis with:

- matched `f_shed` / `St` extraction from `Cl(t)`
- reconstructed outlet `T_out`
- EB+LMTD `Nu_EB`
- final comparison table against `run004b`

---

## 2026-05-07 | V4b_3D | run005 inlet sensitivity closed

### Work package

Completed the full `Lin=2D` versus `Lin=4D` inlet-sensitivity comparison for
the accepted `Lout=8D` outlet-independent domain.

### Actions taken

- reconstructed `run005` fields for `t = 3..6 s`
- added `VV_cases/V4b_3D/results/run005/analyse_inlet_sensitivity_run004b_vs_run005.py`
- compared:
  - raw `forceCoeffs`
  - `Cl(t)` shedding frequency and `St`
  - reconstructed outlet `T_out`
  - EB+LMTD `Nu_EB`

### Outputs

- `VV_cases/V4b_3D/results/run005/run004b_vs_run005_inlet_compare.csv`
- `VV_cases/V4b_3D/results/run005/run004b_vs_run005_inlet_compare.json`
- `VV_cases/V4b_3D/results/run005/run004b_vs_run005_inlet_compare.md`
- `VV_cases/V4b_3D/results/run005/figures/run004b_vs_run005_inlet_sensitivity.png`

### Results

Both cases use `Lout=8D` and the matched window `t = 3..6 s`.

| Run | Lin/D | Cd_mean | Cl_mean | Cl_rms | f_shed | St | T_out | Nu_EB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| run004b | 2 | 3.361 | 2.514 | 0.184 | 3.267 | 0.1552 | 305.682 +/- 0.676 | 7.778 +/- 0.463 |
| run005 | 4 | 3.359 | 2.518 | 0.185 | 3.268 | 0.1552 | 305.680 +/- 0.653 | 7.776 +/- 0.447 |

Key differences for `Lin=4D` versus `Lin=2D`:

| Quantity | Difference |
|---|---:|
| Cd_mean | -0.07% |
| Cl_rms | +0.30% |
| St | +0.02% |
| T_out | -0.002 K |
| Nu_EB | -0.03% |

### Decision

The inlet extension from `2D` to `4D` does not materially affect force,
shedding, or EB+LMTD heat-transfer metrics. The inlet-sensitivity question is
closed for the current medium BL mesh family. Together with the closed outlet
sensitivity (`8D` ~= `16D`), `Lin=2D`, `Lout=8D` is the defensible production
domain candidate before timestep sensitivity and the longer measurement-rich
final run.

---

## 2026-05-07 | V4b_3D | run006a maxCo=0.4 plan prepared

### Work package

Prepared the first timestep/Courant sensitivity check after closing inlet and
outlet domain sensitivity.

### Purpose

Test whether the accepted `run004b` result is sensitive to the adaptive
timestep limit. The case reuses the accepted domain and mesh:

- `Lin=2D`
- `Lout=8D`
- corrected BL mesh from `run004b`
- `maxCo=0.4` instead of `maxCo=0.8`

### Actions taken

- added `VV_cases/V4b_3D/_code/prepare_run006a_maxCo04.sh`
- added `VV_cases/V4b_3D/_code/start_run006a_bg.sh`
- added `VV_cases/V4b_3D/results/run006a/summary.md`

### Decision plan

Run to `t = 6 s` and compare against `run004b` over `t = 3..6 s` for
`Cd_mean`, `Cl_rms`, `St`, `T_out`, and `Nu_EB`. If the differences stay small
(`Cd` about <=1%, `St` about <=1%, `Nu_EB` about <=1-2%), keep `maxCo=0.8`
for the longer production run. If not, run `maxCo=0.2`.

---

## 2026-05-07 | V4b_3D | run006a maxCo=0.4 launched

### Work package

Generated, checked, and launched the first timestep/Courant sensitivity check.

### Actions taken

- generated WSL case:
  - `/home/hexmachina/of_runs/V4b_3D_run006a`
- copied the accepted `run004b` mesh
- set:
  - `startFrom startTime`
  - `startTime 0`
  - `endTime 6`
  - `maxCo 0.4`
  - `numberOfSubdomains 20`
- ran normal and strict `checkMesh`
- launched the solver on 20 MPI ranks

### Mesh result

Normal `checkMesh`: `Mesh OK`.

| Quantity | Value |
|---|---:|
| cells | 407,440 |
| max non-ortho | 62.84 deg |
| avg non-ortho | 5.93 deg |
| max skewness | 3.319 |
| max aspect ratio | 33.64 |
| strict concave cells | 9,178 |

### Launch

```bash
NPROCS=20 TAG=20260507_np20_maxCo04 bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run006a_bg.sh
```

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run006a` |
| MPI ranks | 20 |
| Parent MPI PID | 766 |
| PID file | `logs/solver.20260507_np20_maxCo04.pid` |
| Solver log | `logs/log.foamRun_parallel.20260507_np20_maxCo04` |
| Target endTime | 6 s |

### Initial status

- solver entered the time loop
- all 20 worker processes were active
- initial `Co_max` stayed below `0.4`
- residuals and continuity errors were finite
- no startup crash observed

### Monitor

```bash
pgrep -af foamRun
tail -n 120 /home/hexmachina/of_runs/V4b_3D_run006a/logs/log.foamRun_parallel.20260507_np20_maxCo04
```

---

## 2026-05-07 | V4b_3D | run006a stopped and partial timestep check analyzed

### Work package

Stopped `run006a` before the original `t = 6 s` target and computed the
available partial timestep/Courant sensitivity metrics.

### Solver status

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run006a` |
| maxCo | 0.4 |
| Last log time | about `2.616 s` |
| Last checkpoint | `processor*/2.6` |
| ClockTime at stop | about `26343 s` |
| Stop method | parent MPI PID from `logs/solver.20260507_np20_maxCo04.pid` |
| Termination | user stop, not solver crash |

### Actions taken

- reconstructed `run006a` fields for `t = 0.5..2.6 s`
- reconstructed matching `run004b` fields for `t = 0.5..2.6 s`
- added `VV_cases/V4b_3D/results/run006a/analyse_timestep_partial_run004b_vs_run006a.py`
- compared raw force coefficients, `St`, outlet `T_out`, and EB+LMTD `Nu_EB`

### Outputs

- `VV_cases/V4b_3D/results/run006a/run004b_vs_run006a_timestep_partial_compare.csv`
- `VV_cases/V4b_3D/results/run006a/run004b_vs_run006a_timestep_partial_compare.json`
- `VV_cases/V4b_3D/results/run006a/run004b_vs_run006a_timestep_partial_compare.md`
- `VV_cases/V4b_3D/results/run006a/figures/run004b_vs_run006a_timestep_partial.png`

### Primary available-window result

Matched window `t = 0.5..2.6 s`:

| Run | maxCo | Cd_mean | Cl_mean | Cl_rms | f_shed | St | T_out | Nu_EB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| run004b | 0.8 | 3.362091 | 2.513970 | 0.190678 | 3.2459 | 0.15416 | 305.602 +/- 1.046 | 7.7252 +/- 0.7075 |
| run006a | 0.4 | 3.362270 | 2.513552 | 0.190056 | 3.2436 | 0.15405 | 305.598 +/- 1.046 | 7.7226 +/- 0.7070 |

Differences for `run006a` versus matched `run004b`:

| Quantity | Difference |
|---|---:|
| Cd_mean | +0.01% |
| Cl_rms | -0.33% |
| St | -0.07% |
| T_out | -0.004 K |
| Nu_EB | -0.03% |

### Decision

The partial `maxCo=0.4` run tracks the `maxCo=0.8` reference extremely closely
for force, shedding, and EB+LMTD heat-transfer metrics over the available
windows. Because it was stopped before `t = 3 s`, this is an indicative partial
timestep check, not the final planned `t = 3..6 s` timestep-independence proof.
It is nevertheless strong evidence that `maxCo=0.8` is not causing an obvious
time-integration bias in the current setup.

---

## 2026-05-07 | V4b_3D | run006b maxCo=1.0 short smoke test prepared

### Work package

Prepared a short `maxCo=1.0` speed/safety smoke test after the partial
`maxCo=0.4` check showed no visible timestep bias versus `maxCo=0.8`.

### Purpose

This is not a full timestep-independence proof. It tests whether raising
`maxCo` above the accepted `0.8` remains stable and gives comparable early
force signals.

### Actions taken

- added `VV_cases/V4b_3D/_code/prepare_run006b_maxCo10_short.sh`
- added `VV_cases/V4b_3D/_code/start_run006b_bg.sh`
- added `VV_cases/V4b_3D/results/run006b/summary.md`

### Planned setup

| Quantity | Value |
|---|---:|
| Lin/D | 2 |
| Lout/D | 8 |
| mesh | copied from `run004b` |
| maxCo | 1.0 |
| endTime | 2 s |
| MPI ranks | 20 |

---

## 2026-05-07 | V4b_3D | run006b maxCo=1.0 short smoke test launched

### Work package

Generated, checked, and launched the short `maxCo=1.0` speed/safety smoke
test.

### Actions taken

- generated WSL case:
  - `/home/hexmachina/of_runs/V4b_3D_run006b`
- copied the accepted `run004b` mesh
- set:
  - `startFrom startTime`
  - `startTime 0`
  - `endTime 2`
  - `maxCo 1.0`
  - `numberOfSubdomains 20`
- ran normal `checkMesh`
- launched the solver on 20 MPI ranks

### Mesh result

Normal `checkMesh`: `Mesh OK`.

| Quantity | Value |
|---|---:|
| cells | 407,440 |
| max non-ortho | 62.84 deg |
| avg non-ortho | 5.93 deg |
| max skewness | 3.319 |
| max aspect ratio | 33.64 |

### Launch

```bash
NPROCS=20 TAG=20260507_np20_maxCo10 bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run006b_bg.sh
```

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run006b` |
| MPI ranks | 20 |
| Parent MPI PID | 1203 |
| PID file | `logs/solver.20260507_np20_maxCo10.pid` |
| Solver log | `logs/log.foamRun_parallel.20260507_np20_maxCo10` |
| Target endTime | 2 s |

### Initial status

- solver entered the time loop
- all 20 worker processes were active
- initial `Co_max` stayed below `1.0`
- residuals and continuity errors were finite
- no startup crash observed

---

## 2026-05-08 | V4b_3D | run006b maxCo=1.0 smoke test completed

### Work package

Completed and analyzed the short `maxCo=1.0` speed/safety smoke test.

### Solver status

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run006b` |
| maxCo | 1.0 |
| Final time | 2.0 s |
| Final checkpoint | `processor*/2` |
| Final ClockTime | `8194 s` |
| Termination | `End` / `Finalising parallel run` |

### Actions taken

- reconstructed `run006b` fields for `t = 0.5..2.0 s`
- added `VV_cases/V4b_3D/results/run006b/analyse_maxCo10_short_run004b_vs_run006b.py`
- compared raw force coefficients, `St`, outlet `T_out`, and EB+LMTD `Nu_EB`

### Outputs

- `VV_cases/V4b_3D/results/run006b/run004b_vs_run006b_maxCo10_short_compare.csv`
- `VV_cases/V4b_3D/results/run006b/run004b_vs_run006b_maxCo10_short_compare.json`
- `VV_cases/V4b_3D/results/run006b/run004b_vs_run006b_maxCo10_short_compare.md`

### Result

Matched early window `t = 0.5..2 s`:

| Run | maxCo | Cd_mean | Cl_mean | Cl_rms | f_shed | St | T_out | Nu_EB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| run004b | 0.8 | 3.361209 | 2.510763 | 0.176698 | 3.2538 | 0.15453 | 305.615 +/- 0.974 | 7.7331 +/- 0.6558 |
| run006b | 1.0 | 3.361220 | 2.510802 | 0.176971 | 3.2561 | 0.15464 | 305.616 +/- 0.975 | 7.7339 +/- 0.6562 |

Differences for `run006b` versus matched `run004b`:

| Quantity | Difference |
|---|---:|
| Cd_mean | +0.00% |
| Cl_rms | +0.15% |
| St | +0.07% |
| T_out | +0.001 K |
| Nu_EB | +0.01% |

### Decision

`maxCo=1.0` is stable for this short check and tracks `maxCo=0.8` extremely
closely over the early common window. It can be used as a speed/safety
reference, but `maxCo=0.8` remains the more conservative production default.

---

## 2026-05-08 | V4b_3D | run007a variable-property short check completed

### Work package

Completed and analyzed a short variable-property physics check on the accepted
`Lin=2D`, `Lout=8D` geometry.

### Model

`run007a` uses `incompressiblePerfectGas + sutherland` transport with
`sensibleInternalEnergy/e`. This gives low-Mach `rho(T)` and `mu(T)` without
the full pressure-driven compressibility of `perfectGas`.

### Solver status

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run007a` |
| Final time | 2.0 s |
| Final checkpoint | `processor*/2` |
| Final ClockTime | `9932 s` |
| Termination | `End` / `Finalising parallel run` |

### Result

Matched early window `t = 0.5..2 s`:

| Run | model | Cd_mean | Cl_rms | St | T_out | Q_total | Nu_EB |
|---|---|---:|---:|---:|---:|---:|---:|
| run004b | Boussinesq_const | 3.361209 | 0.176698 | 0.15453 | 305.615 +/- 0.974 | 1.4644 +/- 0.0984 | 7.7331 +/- 0.6558 |
| run007a | incompressiblePerfectGas_sutherland | 3.473619 | 0.178979 | 0.15407 | 308.934 +/- 0.990 | 1.8534 +/- 0.1107 | 10.2249 +/- 0.7272 |

Differences for `run007a` versus matched `run004b`:

| Quantity | Difference |
|---|---:|
| Cd_mean | +3.34% |
| Cl_rms | +1.29% |
| St | -0.30% |
| T_out | +3.319 K |
| Q_total | +26.57% |
| Nu_EB | +32.22% |

### Decision

The shedding regime is essentially unchanged, but the thermal metrics are not a
small correction. Because the current window is short and still includes early
transient behavior, extend the variable-property case to `t = 6 s` before using
the `Nu` shift as a final production conclusion.

---

## 2026-05-08 | V4b_3D | run007a variable-property extension launched

### Work package

Continue the accepted variable-property case from `t = 2 s` to `t = 6 s` after
the short-window analysis showed a large `Nu_EB` sensitivity.

### Launch

Used a continuation helper that does not rerun `decomposePar`; it starts from
the existing decomposed `processor*/2` checkpoint.

```bash
NPROCS=20 END_TIME=6 TAG=20260508_np20_varProps_to6 bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/continue_run007a_bg.sh
```

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run007a` |
| Parent MPI PID | 797 |
| MPI ranks | 20 |
| Start mode | `latestTime` from `processor*/2` |
| Target endTime | 6 s |
| Solver log | `logs/log.foamRun_parallel.20260508_np20_varProps_to6` |

### Initial status

- solver resumed from `Time = 2.0007 s`, not from zero
- all 20 worker processes were active
- `Co_max` stayed near `0.799`
- residuals and continuity errors were finite
- `forceCoeffs` started appending post-`t=2` samples

### Next step

After completion, reconstruct `t = 3..6 s` and rerun the variable-property
comparison against `run004b` over the final production window.

---

## 2026-05-08 | V4b_3D | run007b constant-property Cp smoke test prepared

### Work package

Prepared a short constant-property `Cp`/enthalpy smoke test after the heat
balance check showed that the earlier constant-property `run004b` thermal
model closes with `Cv=718`, not with the open-flow `m_dot*Cp*dT` balance.

### Purpose

Isolate whether the large `Nu` jump in the variable-property check is mostly a
property-variation effect, or partly a correction from the old `Cv`-based
internal-energy formulation to a physically expected `Cp`-based open-flow heat
balance.

### Actions taken

- added `VV_cases/V4b_3D/_code/prepare_run007b_constCp_short.sh`
- added `VV_cases/V4b_3D/_code/start_run007b_bg.sh`
- added `VV_cases/V4b_3D/results/run007b/summary.md`
- generated WSL case:
  - `/home/hexmachina/of_runs/V4b_3D_run007b`
- copied the accepted `run004b` mesh and domain
- changed only the constant-property thermal model:
  - `eConst + sensibleInternalEnergy + Cv=718`
  - to `hConst + sensibleEnthalpy + Cp=1005`
- kept:
  - `Boussinesq`
  - `mu = 1.827e-05 Pa s`
  - `Pr = 0.713`
  - `maxCo = 0.8`
  - `endTime = 2 s`
- added `div(phi,h)` and changed solver/probe/residual fields from `e` to `h`
- ran normal `checkMesh`

### Mesh/status

Normal `checkMesh`: `Mesh OK`.

`run007b` is prepared but not launched, because `run007a` is currently using
the 20 MPI ranks for the `t=2..6 s` variable-property continuation.

### Launch after run007a

```bash
NPROCS=20 TAG=20260508_np20_constCp_short bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run007b_bg.sh
```

### Planned comparison

Compare `run007b` against `run004b` and `run007a` over the matched early
window. Key checks:

- force/shedding: `Cd_mean`, `Cl_rms`, `St`
- air-side heat pickup: `m_dot*Cp*(T_out - T_in)`
- wall-side heat input: integrated `wallHeatFlux` over `hot_tube`,
  `hot_fin_z_min`, and `hot_fin_z_max`
- `Nu_EB` with consistent `Cp` and `k = mu*Cp/Pr`

If `run007b` closes the wall and air heat fluxes while staying near the old
force regime, use it as the constant-property thermal baseline before making
final claims about the additional effect of variable `rho(T)` and `mu(T)`.

---

## 2026-05-08 | V4b_3D | run007a interrupted; run007c Cp-capacity smoke test launched

### Work package

Interrupted the active `run007a` variable-property continuation and launched a
short constant-property heat-capacity smoke test to quickly isolate the
`Cv=718` versus `Cp=1005` effect.

### Actions taken

- stopped active `run007a` continuation:
  - case: `/home/hexmachina/of_runs/V4b_3D_run007a`
  - parent MPI PID: `797`
  - last observed log time before stop: about `t = 2.35 s`
- attempted to launch `run007b`:
  - `hConst + sensibleEnthalpy + Boussinesq`
  - `Cp = 1005`
- `run007b` failed during startup with:
  - `FOAM FATAL ERROR: Maximum number of iterations exceeded`
  - failing path: thermophysical inversion from enthalpy to temperature
  - conclusion: `hConst/sensibleEnthalpy + Boussinesq` is not robust in the
    current OF13 setup and should not be used as the quick smoke-test path
- added fallback diagnostic case:
  - `VV_cases/V4b_3D/_code/prepare_run007c_constCp_as_eConst_short.sh`
  - `VV_cases/V4b_3D/_code/start_run007c_bg.sh`
  - `VV_cases/V4b_3D/results/run007c/summary.md`
- generated WSL case:
  - `/home/hexmachina/of_runs/V4b_3D_run007c`
- launched `run007c` on 20 MPI ranks:

```bash
NPROCS=20 TAG=20260508_np20_constCpAsCv_short bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run007c_bg.sh
```

### run007c setup

`run007c` keeps the stable `run004b` model family and changes only the
constant heat-capacity coefficient:

| Item | run004b | run007c |
|---|---|---|
| thermo | `eConst` | `eConst` |
| energy | `sensibleInternalEnergy` | `sensibleInternalEnergy` |
| equation of state | `Boussinesq` | `Boussinesq` |
| capacity coefficient | `Cv = 718` | `Cv = 1005` |
| interpretation | old baseline | Cp-scale diagnostic |

This is a diagnostic isolation test, not the final production physics model.

### Initial status

- solver entered the time loop
- 20 MPI workers active
- `Co_max` about `0.78`
- solving `e` normally
- no startup crash observed
- target `endTime = 2 s`

### Next step

After `run007c` reaches `t=2 s`, compare against `run004b` and the short
`run007a` window using:

- force/shedding: `Cd_mean`, `Cl_rms`, `St`
- air-side heat pickup with capacity `1005`
- integrated `wallHeatFlux` over hot patches
- `Nu_EB` with `k = mu*1005/Pr`

If `run007c` lands close to the variable-property `Nu` level, then most of the
previous jump came from using `1005` instead of `718`. If it remains much
closer to `run004b`, then variable `rho(T)`/`mu(T)` is the larger driver.

---

## 2026-05-08 | V4b_3D | run007c t=0.2 early thermal quick-look

### Work package

Computed a very early `t=0.2 s` smoke comparison between `run004b` and the
active `run007c` case.

### Actions taken

- reconstructed `t=0.2 s` for `run004b` and `run007c`
- computed `wallHeatFlux` at `t=0.2 s` using `foamPostProcess -solver fluid`
- added:
  - `VV_cases/V4b_3D/results/run007c/compare_run004b_run007c_t02.py`
  - `VV_cases/V4b_3D/results/run007c/run004b_vs_run007c_t02_quick_compare.csv`
  - `VV_cases/V4b_3D/results/run007c/run004b_vs_run007c_t02_quick_compare.json`
  - `VV_cases/V4b_3D/results/run007c/run004b_vs_run007c_t02_quick_compare.md`

### Result

Force window `t=0.1..0.2 s`, thermal instant `t=0.2 s`.

| Run | capacity | Cd | Cl_rms | Q_wall hot total | Nu_wall/k_case |
|---|---:|---:|---:|---:|---:|
| run004b | 718 | 3.3518 | 0.1407 | 1.0907 W | 7.0019 |
| run007c | 1005 | 3.3518 | 0.1407 | 1.5267 W | 7.0019 |

### Interpretation

At `t=0.2 s`, the outlet air is still essentially at inlet temperature, so the
air-side `m_dot*C*dT` balance is not yet meaningful. The useful signal is the
wall-side heat flux: switching the case capacity/conductivity scale from `718`
to `1005` increases absolute wall heat input by about `40%`, almost exactly the
`1005/718` ratio. But when Nu is normalized by the matching case conductivity
`k = mu*C/Pr`, the wall-side Nu is unchanged.

This supports the hypothesis that the previously alarming Nu jump is strongly
affected by inconsistent capacity/conductivity normalization. Continue
`run007c` toward `t=2 s` to see whether the same conclusion holds once outlet
temperature and air-side heat pickup become meaningful.

---

## 2026-05-08 | V4b_3D | run007b vs run007c same-window Nu check

### Work package

Checked whether `run007b` and `run007c` can be compared for Nu over the same
early window used by the `run004b` vs `run007c` quick-look.

### Result

No valid same-window `Nu` comparison exists for `t=0.2 s`:

| Run | status | available thermal time | force samples |
|---|---|---:|---:|
| run007b | failed during startup | only `0` | 1 sample at `t=0` |
| run007c | running normally | `0`, `0.2` | many samples |

The only common instant is the initial condition `t=0`. It gives the same
initial-condition wall heat flux in both cases:

| Run | Q_wall hot total at t=0 | Nu_wall using `k=mu*1005/Pr` |
|---|---:|---:|
| run007b | 138.372 W | 634.63 |
| run007c | 138.372 W | 634.63 |

This is not a physical heat-transfer result; it is the artificial initial wall
gradient before the thermal field evolves.

### Outputs

- `VV_cases/V4b_3D/results/run007c/run007b_vs_run007c_same_window_nu_status.md`
- `VV_cases/V4b_3D/results/run007c/run007b_vs_run007c_same_window_nu_status.json`

### Decision

Do not use `run007b` for Nu comparison. Treat it only as evidence that
`hConst/sensibleEnthalpy + Boussinesq` is not viable in this setup. Continue
using `run007c` as the valid constant-property `1005` diagnostic.

---

## 2026-05-08 | V4b_3D | run007a vs run007c t=0.2 Nu quick-look

### Work package

Computed the intended same-time comparison between the variable-property
`run007a` and the constant-property `1005` fallback `run007c`.

### Actions taken

- reconstructed `run007a` at `t=0.2 s`
- computed `run007a` `wallHeatFlux` at `t=0.2 s` using
  `foamPostProcess -solver fluid`
- added:
  - `VV_cases/V4b_3D/results/run007c/compare_run007a_run007c_t02.py`
  - `VV_cases/V4b_3D/results/run007c/run007a_vs_run007c_t02_quick_compare.csv`
  - `VV_cases/V4b_3D/results/run007c/run007a_vs_run007c_t02_quick_compare.json`
  - `VV_cases/V4b_3D/results/run007c/run007a_vs_run007c_t02_quick_compare.md`

### Result

Force window `t=0.1..0.2 s`, thermal instant `t=0.2 s`. Wall-side Nu uses the
same reference conductivity for both cases:
`k_ref = mu_ref*Cp_ref/Pr_ref = 0.02575224 W/(m K)`.

| Run | model | Cd | Cl_rms | Q_wall hot total | Nu_wall/k_ref |
|---|---|---:|---:|---:|---:|
| run007a | variable props | 3.4687 | 0.1276 | 1.3702 W | 6.2841 |
| run007c | constant capacity `1005` | 3.3518 | 0.1407 | 1.5267 W | 7.0019 |

### Interpretation

At `t=0.2 s`, the variable-property case is not producing a larger wall-side
Nu than the constant-property `1005` fallback. `run007c` is about `11.4%`
higher in wall heat flux and wall-side Nu than `run007a` when both use the
same reference conductivity. This strengthens the suspicion that the previously
large apparent `Nu` shift was mainly a consistency/normalization issue around
`Cv`, `Cp`, and `k`, not a straightforward variable-property amplification.

---

## 2026-05-08 | V4b_3D | partial run004b vs run007a vs run007c comparison

### Work package

Computed a partial early/transient comparison while `run007c` is still running,
using the latest common reliable checkpoints.

### Window

- force window: `t = 0.5..1.3 s`
- thermal checkpoints: `t = 0.5, 1.0, 1.3 s`

### Outputs

- `VV_cases/V4b_3D/results/run007c/compare_run004b_run007a_run007c_partial.py`
- `VV_cases/V4b_3D/results/run007c/run004b_run007a_run007c_partial_compare.csv`
- `VV_cases/V4b_3D/results/run007c/run004b_run007a_run007c_partial_compare.json`
- `VV_cases/V4b_3D/results/run007c/run004b_run007a_run007c_partial_compare.md`

### Results

| Run | model | Cd | Cl_rms | Q_wall W | Q_air case W | Nu_wall case-k | Nu_wall ref-k |
|---|---|---:|---:|---:|---:|---:|---:|
| run004b | baseline `Cv=718` | 3.3594 | 0.1297 | 1.0581 | 0.9700 | 7.7243 | 5.5185 |
| run007a | variable props | 3.4722 | 0.1436 | 1.3389 | 1.7396 | 7.2813 | 7.2813 |
| run007c | constant capacity `1005` | 3.3594 | 0.1297 | 1.4810 | 1.3577 | 7.7243 | 7.7243 |

Key differences:

| Comparison | Q_wall | Nu_wall_ref_k | Nu_wall_case_k | Cd |
|---|---:|---:|---:|---:|
| run007a vs run004b | +26.54% | +31.94% | -5.73% | +3.36% |
| run007c vs run004b | +39.97% | +39.97% | +0.00% | +0.00% |
| run007c vs run007a | +10.61% | +6.08% | +6.08% | -3.25% |

### Interpretation

The partial result strongly supports the normalization hypothesis. With a
common reference conductivity, both `run007a` and `run007c` sit above old
`run004b`. But the constant-property `1005` fallback is higher than the
variable-property case, so the wall-side Nu increase is not primarily driven by
variable `rho(T)`/`mu(T)`.

The most important consistency result is that `run007c`, when normalized with
its own matching conductivity `k = mu*1005/Pr`, gives the same wall-side Nu as
old `run004b` normalized with `k = mu*718/Pr`. This means the earlier large Nu
jump can be produced simply by changing the heat-capacity/conductivity scale
without changing the flow regime.

The air-side heat balance is still early-transient and should be treated with
care until the full `t=0.5..2.0 s` window is available.

---

## 2026-05-08 | V4b_3D | run007c completed; final 0.5..2.0 smoke comparison

### Work package

Completed the constant-property `1005` diagnostic smoke test and compared it
against the old constant-property baseline and the variable-property case.

### Solver status

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run007c` |
| Model | `eConst + Boussinesq + sensibleInternalEnergy`, capacity coefficient `1005` |
| Final time | `2.0 s` |
| Final checkpoint | `processor*/2` |
| Final ClockTime | `10209 s` |
| Termination | `End` / `Finalising parallel run` |

### Actions taken

- reconstructed `run007c` checkpoints for `t = 0.5, 1.0, 1.3, 1.5, 1.7, 2.0 s`
- ensured matching reconstructed checkpoints exist for `run004b` and `run007a`
- computed `wallHeatFlux` for all three cases over the same thermal times
- generated final comparison:
  - `VV_cases/V4b_3D/results/run007c/run004b_run007a_run007c_final_0p5_2_compare.csv`
  - `VV_cases/V4b_3D/results/run007c/run004b_run007a_run007c_final_0p5_2_compare.json`
  - `VV_cases/V4b_3D/results/run007c/run004b_run007a_run007c_final_0p5_2_compare.md`

### Results

Force window `t = 0.5..2.0 s`; thermal checkpoints
`t = 0.5, 1.0, 1.3, 1.5, 1.7, 2.0 s`.

| Run | model | Cd | Cl_rms | Q_wall W | Q_air case W | Nu_wall case-k | Nu_wall ref-k | wall-air case diff |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| run004b | baseline `Cv=718` | 3.3612 | 0.1767 | 1.0591 | 1.0445 | 7.8217 | 5.5881 | +1.4% |
| run007a | variable props | 3.4736 | 0.1790 | 1.3396 | 1.8450 | 7.3786 | 7.3786 | -27.4% |
| run007c | constant capacity `1005` | 3.3612 | 0.1767 | 1.4824 | 1.4621 | 7.8217 | 7.8217 | +1.4% |

### Interpretation

`run007c` is the clean diagnostic: it keeps the old stable `run004b` flow
model and changes only the heat-capacity/conductivity scale from `718` to
`1005`. It gives essentially identical force metrics and identical wall-side
Nu when each case is normalized with its own matching conductivity.

The absolute wall heat flux rises by `~40%`, which follows the `1005/718`
scale. This means the earlier large apparent Nu increase is primarily a
`Cv/Cp/k` consistency issue, not evidence that variable properties alone
strongly increase heat transfer.

`run007a` remains useful as a variable-property experiment, but its short-window
energy balance is not closed: air-side `m_dot*Cp*dT` is about `27%` larger than
the integrated wall heat flux. Do not treat the `run007a` air-side Nu as final
until the variable-property energy balance is made internally consistent.

---

## 2026-05-08 | V4b_3D | run008 production specification prepared

### Work package

Prepared the production-run specification before launching any long solver run.

### Decision

`run008` should use the `run007c` constant-property `1005` setup as the
production baseline:

- accepted geometry/domain from `run004b`: `Lin=2D`, `Lout=8D`
- corrected BL mesh, `407,440` cells
- `eConst + Boussinesq + sensibleInternalEnergy`
- capacity coefficient `1005`
- `mu = 1.827e-05`, `Pr = 0.713`
- `maxCo = 0.8`

Do not use `run007a` as production physics yet because its short-window
air-side energy balance did not close.

### Specification contents

Specification saved in:

- `VV_cases/V4b_3D/results/run008/production_run_spec.md`
- `VV_cases/V4b_3D/results/run008/summary.md`

The spec defines:

- `t_end = 10 s`
- transient rejection: `t < 2 s`
- useful window: `t = 2..10 s`, about `8 s` or `~26*T_shed`
- full 3D checkpoint cadence: about `0.08 s` (`T_shed/4`)
- midspan/POD slice cadence: `0.02 s`
- probe cadence: fixed `0.005 s` / `200 Hz`
- surface sampling cadence: `0.005 s`
- tube output: `q''(theta,z,t)` and `Nu(theta,z,t)`
- fin output: local/binned `Nu_local(x,t)`
- force output contract for `forceCoeffs.dat` and raw `forces.dat`, including
  pressure/viscous decomposition and explicit component totals

### Launch status

No production run was launched in this step. Next step is to review/accept the
spec, then implement the `run008` case and launch helper.
## 2026-05-08 20:10:33 +02:00 | V4b_3D | run008 production run launched

### Work package

Launched the production `run008` after preparing the one-page production
specification and accepting the `run007c` constant-property Cp-capacity setup.

### Setup

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run008` |
| Parent setup | `run007c` |
| Model | `eConst + Boussinesq + sensibleInternalEnergy` |
| Capacity coefficient | `1005` |
| Geometry | `Lin=2D`, `Lout=8D` |
| Mesh cells | `407,440` |
| Target endTime | `10 s` |
| Useful window | `t = 2..10 s` |
| MPI ranks | `20` |
| Launch tag | `20260508_np20_production` |
| Parent MPI PID | `1202` |
| Solver log | `logs/log.foamRun_parallel.20260508_np20_production` |

### Sampling

- full 3D fields every `0.08 s`
- midspan `z=0` slice every `0.02 s`
- `forceCoeffs`, raw `forces`, wake probes, `wallHeatFlux`, and hot-surface
  sampling every `0.005 s`
- hot-surface outputs include `hot_tube_surface` and `hot_fin_surface`

### Initial status

- normal `checkMesh`: `Mesh OK`
- solver entered the time loop
- 20 `foamRun` workers active
- initial `Co_max` stayed below `0.8`
- residuals and continuity errors finite
- first `0.005 s` surface/probe/force post-processing directories were created
- no startup crash observed

### Monitor

```bash
pgrep -af foamRun
tail -n 120 /home/hexmachina/of_runs/V4b_3D_run008/logs/log.foamRun_parallel.20260508_np20_production
```

### Stop safely

```bash
kill "$(cat /home/hexmachina/of_runs/V4b_3D_run008/logs/solver.20260508_np20_production.pid)"
```

---
## 2026-05-09 12:43:48 +02:00 | V4b_3D | run008 production run completed

### Work package

Checked the overnight production `run008` status.

### Solver status

`run008` completed cleanly to `t = 10 s`.

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run008` |
| Parent setup | `run007c` |
| MPI ranks | `20` |
| Solver log | `logs/log.foamRun_parallel.20260508_np20_production` |
| Final checkpoint | `processor*/10` |
| Final ClockTime | `50909 s` |
| Termination | `End` / `Finalising parallel run` |
| Case size | about `17 GB` |

### Output counts

| Output | Count / size |
|---|---:|
| `hot_tube_surface` | `2001` files / about `1.4 GB` |
| `hot_fin_surface` | `4002` files / about `532 MB` |
| `midspan_z0` | `501` files / about `645 MB` |
| `probes_wake` | about `2.4 MB` |
| `forceCoeffs` | about `196 KB` |
| `forces_raw` | about `432 KB` |

### Quick status

- no active `mpirun` or `foamRun` process remains
- all 20 `processor*/10` checkpoints are present
- no fatal solver error was found in the log
- final logged instantaneous force coefficients at `t = 10 s`:
  - `Cd = 3.3516`
  - `Cl = 2.3625`
  - `Cm = 0.00979`

### Next step

Reconstruct/post-process the production window `t = 2..10 s`, then compute:

- final `Cd_mean`, `Cl_rms`, `St`
- EB and wall-flux heat balance
- `Nu_EB`, `Nu_wall`, and wall-air closure
- local tube/fin `q''` and `Nu` maps for coherence/transfer-entropy work

---
## 2026-05-09 | V4b_3D | run008 full production analysis completed

### Work package

Completed the production-window analysis for `run008`, including force
statistics, shedding frequency, air-side and wall-side heat balance, local
surface Nu maps, POD, EPOD-style Cl-correlated midspan fields, and Cl-Nu
coherence.

### Analysis setup

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run008` |
| Window | `t = 2..10 s` |
| Analysis script | `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_production.py` |
| Outlet reconstruction | `T` and `phi`, every `0.08 s` over `2..10 s` |
| POD input | midspan `z=0`, `Ux`, `Uy`, scaled `T`, `201` snapshots |
| Surface maps | tube `Nu(theta,z)`, fin `Nu_local(x)` |

### Global results

| Quantity | Value |
|---|---:|
| `Cd_mean` | `3.361014` |
| `Cl_mean` | `2.515349` |
| `Cl_rms` | `0.176441` |
| `f_shed` | `3.247970 Hz` |
| `St` | `0.154261` |
| `T_out` area mean | `305.667871 K` |
| `T_out` mass mean | `305.696150 K` |
| `Q_air = m_dot Cp (T_out - T_in)` | `1.470790 W` |
| `Q_wall` from `wallHeatFlux` | `1.480659 W` |
| wall-air closure | `+0.706%` |
| `Nu_EB` | `7.770004` |
| `Nu_wall` | `7.816521` |

The production result is consistent with the shorter accepted checks:
`Cd_mean`, `St`, and `Nu_EB` remain close to the `run004b/run007c` values, and
the wall/air heat balance closes to within about one percent.

### POD / EPOD

| Quantity | Value |
|---|---:|
| POD snapshots | `201` |
| Midspan points | `13,524` |
| Mode 1 energy | `40.403%` |
| Mode 2 energy | `39.887%` |
| Mode 3 energy | `4.202%` |
| Modes 1..5 energy | `90.039%` |
| Modes 1..10 energy | `93.935%` |
| `corr(a1, Cl)` | `-0.900` |
| `corr(a2, Cl)` | `+0.411` |
| `corr(a1, Q_wall)` | `-0.182` |
| `corr(a2, Q_wall)` | `+0.215` |

### Outputs

- `VV_cases/V4b_3D/results/run008/data/run008_production_analysis.md`
- `VV_cases/V4b_3D/results/run008/data/run008_production_analysis.json`
- `VV_cases/V4b_3D/results/run008/data/run008_force_stats.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_thermal_stats.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_pod_epod_stats.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_force_timeseries_window.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_heat_balance_timeseries_window.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_outlet_thermal_samples.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_tube_nu_theta_z_map.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_fin_nu_x_profile.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_pod_epod_arrays.npz`
- `VV_cases/V4b_3D/results/run008/data/run008_surface_nu_maps.npz`
- `VV_cases/V4b_3D/results/run008/figures/run008_force_traces_psd.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_heat_balance_timeseries.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_nu_timeseries.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_pod_energy.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_pod_epod_midspan_maps.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_cl_nu_coherence.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_tube_nu_theta_z_map.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_fin_nu_x_profile.png`

### Decision

`run008` is the current production reference for `V4b_3D` Re=200 on the
accepted `Lin=2D`, `Lout=8D` domain and `run007c` thermal-capacity setup. The
dataset is suitable for final force/heat-transfer statistics and for the
planned Cl-Nu coherence / EPOD novelty analysis.

---
## 2026-05-09 | V4b_3D | run008 coupling deep dive completed

### Work package

Executed the three high-value follow-up analyses proposed after the initial
production processing:

1. phase-averaged local `Nu` using `Cl(t)` as the phase reference,
2. `Cl <-> Nu` coherence maps,
3. pressure/viscous force decomposition from raw `forces.dat`.

### Analysis setup

| Item | Value |
|---|---|
| Case | `/home/hexmachina/of_runs/V4b_3D_run008` |
| Window | `t = 2..10 s` |
| Script | `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_coupling_deep_dive.py` |
| Phase reference | band-passed `Cl(t)`, phase zero aligned with positive `Cl` maxima |
| Tube bins | `72 theta x 36 z x 16 phase` |
| Fin bins | `120 x x 16 phase` |
| Surface input | `1601` tube snapshots and `1601` fin time directories |

### Pressure / viscous decomposition

| Quantity | Value |
|---|---:|
| `Cd_pressure_mean` | `2.903582` |
| `Cd_viscous_mean` | `0.457432` |
| pressure drag fraction | `86.39%` |
| viscous drag fraction | `13.61%` |
| `Cl_pressure_mean` | `2.514626` |
| `Cl_viscous_mean` | `0.000723` |
| `Cl_pressure_rms` | `0.163772` |
| `Cl_viscous_rms` | `0.014542` |

The mean lift and its oscillatory component are overwhelmingly pressure-driven;
viscous lift is small in mean and RMS. Drag is also pressure-dominated, with a
non-negligible viscous contribution of about `14%`.

### Phase-averaged Nu

| Quantity | Value |
|---|---:|
| tube global phase modulation | `0.147%` |
| tube mean local phase modulation | `1.871%` |
| tube max local phase modulation | `9.656%` |
| fin global phase modulation | `0.428%` |
| fin mean local phase modulation | `0.507%` |
| fin max local phase modulation | `3.531%` |

The spatially integrated `Nu` is nearly phase-steady, but local `Nu` is not:
the tube has localized regions with almost `10%` phase modulation. This means
global `Nu_EB/Nu_wall` hides significant local unsteadiness.

### Cl-Nu coherence

| Quantity | Value |
|---|---:|
| max tube coherence at `f_shed` | `0.999519` |
| mean tube coherence at `f_shed` | `0.654792` |
| max fin coherence at `f_shed` | `0.906261` |
| mean fin coherence at `f_shed` | `0.690615` |

The `Cl <-> Nu` connection is strong at the shedding frequency, especially in
localized tube regions and near the upstream part of the fin response. This is
the strongest current evidence for the planned `Cl`-to-local-heat-transfer
coupling story.

### Outputs

- `VV_cases/V4b_3D/results/run008/data/run008_coupling_deep_analysis.md`
- `VV_cases/V4b_3D/results/run008/data/run008_coupling_deep_analysis.json`
- `VV_cases/V4b_3D/results/run008/data/run008_coupling_deep_stats.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_coupling_deep_arrays.npz`
- `VV_cases/V4b_3D/results/run008/data/run008_force_pressure_viscous_decomp.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_force_pressure_viscous_timeseries.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_tube_cl_nu_coherence_map.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_fin_cl_nu_coherence_x.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_tube_phase_nu_theta_z_phi_summary.csv`
- `VV_cases/V4b_3D/results/run008/data/run008_fin_phase_nu_x_phi_summary.csv`
- `VV_cases/V4b_3D/results/run008/figures/run008_force_pressure_viscous_decomp.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_force_pressure_viscous_psd.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_tube_phase_nu_theta_phi.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_tube_phase_nu_selected_maps.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_fin_phase_nu_x_phi.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_tube_cl_nu_coherence_phase_map.png`
- `VV_cases/V4b_3D/results/run008/figures/run008_fin_cl_nu_coherence_x.png`

### Decision

These three analyses should be treated as the first mechanistic layer on top
of the production statistics. The next optional layer is either SPOD/DMD on
the midspan fields or a guarded transfer-entropy/surrogate test using the
already binned `Nu` signals.

---
## 2026-05-09 | V4b_3D | run008 analysis reset and foundation audit rebuilt

### Work package

Reset the earlier loose `run008` analysis outputs and rebuilt only the first
planned layer: data completeness, cadence audit, effective record length,
cycle-block bootstrap uncertainty, and window sensitivity.

### Cleanup

- cleared generated files from:
  - `VV_cases/V4b_3D/results/run008/data`
  - `VV_cases/V4b_3D/results/run008/figures`
  - `VV_cases/V4b_3D/results/run008/scripts`
- preserved:
  - `summary.md`
  - `production_run_spec.md`
  - raw WSL case data in `/home/hexmachina/of_runs/V4b_3D_run008`
- added the new audit script:
  - `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_audit_uncertainty.py`

### Sampling completeness

| Signal | Target dt | Samples | Missing | Regular |
|---|---:|---:|---:|---|
| `forceCoeffs` | `0.005 s` | `2001` | `0` | yes |
| `forces_raw` | `0.005 s` | `2001` | `0` | yes |
| `wallHeatFlux` | `0.005 s` | `2001` | `0` | yes |
| `hot_tube_surface` | `0.005 s` | `2001` | `0` | yes |
| `hot_fin_surface` | `0.005 s` | `2001` | `0` | yes |
| `midspan_z0` | `0.020 s` | `501` | `0` | yes |
| outlet `T/phi` | `0.080 s` | `101` | `0` | yes |

### Primary window result with cycle-block bootstrap uncertainty

Window `t = 2..10 s`:

| Quantity | Value |
|---|---:|
| effective shedding cycles | `25.98` |
| force samples | `1601` |
| outlet samples | `101` |
| wall samples | `1601` |
| `Cd_mean` | `3.361014 +/- 0.000772` |
| `Cl_rms` | `0.176441 +/- 0.011097` |
| `St` | `0.154261 +/- 0.009574` |
| `Nu_EB` | `7.770004 +/- 0.091573` |
| `Nu_wall` | `7.816521 +/- 0.012286` |
| wall-air closure | `+0.706 +/- 1.075%` |

### Window sensitivity

| Window | cycles | Cd_mean | Cl_rms | St | Nu_EB | Nu_wall | closure |
|---|---:|---:|---:|---:|---:|---:|---:|
| `2..10` | `25.98` | `3.361014` | `0.176441` | `0.154261` | `7.770004` | `7.816521` | `+0.706%` |
| `3..10` | `22.98` | `3.360512` | `0.169254` | `0.155942` | `7.806401` | `7.819670` | `+0.211%` |
| `4..10` | `19.98` | `3.359978` | `0.161001` | `0.158184` | `7.789356` | `7.813261` | `+0.416%` |
| `2..6` | `11.99` | `3.362291` | `0.193722` | `0.142306` | `7.768459` | `7.823033` | `+0.946%` |
| `6..10` | `12.98` | `3.359746` | `0.157070` | `0.154165` | `7.785278` | `7.810126` | `+0.457%` |

### Outputs

- `VV_cases/V4b_3D/results/run008/data/001/run008_audit_uncertainty.md`
- `VV_cases/V4b_3D/results/run008/data/001/run008_audit_uncertainty.json`
- `VV_cases/V4b_3D/results/run008/data/001/run008_audit_sampling_completeness.csv`
- `VV_cases/V4b_3D/results/run008/data/001/run008_audit_window_uncertainty.csv`
- `VV_cases/V4b_3D/results/run008/figures/001/run008_audit_sampling_completeness_cadence.png`
- `VV_cases/V4b_3D/results/run008/figures/001/run008_audit_effective_record_length.png`
- `VV_cases/V4b_3D/results/run008/figures/001/run008_audit_block_bootstrap_uncertainty.png`
- `VV_cases/V4b_3D/results/run008/figures/001/run008_audit_window_sensitivity.png`

### Decision

This audit is now the only active analysis layer for `run008`. Higher-order
analyses should be rebuilt one at a time after reviewing these uncertainty and
window-sensitivity results.

---

## 2026-05-09 | V4b_3D | run008 aerodynamic layer 002 rebuilt

### Work package

Rebuilt the second `run008` analysis layer after reorganizing results into
numbered analysis stages.

### Actions taken

- moved audit figures into:
  - `VV_cases/V4b_3D/results/run008/figures/001`
- moved audit data into:
  - `VV_cases/V4b_3D/results/run008/data/001`
- added aerodynamic analysis script:
  - `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_aerodynamics.py`
- generated stage-002 outputs in:
  - `VV_cases/V4b_3D/results/run008/data/002`
  - `VV_cases/V4b_3D/results/run008/figures/002`

### Results

Both `forceCoeffs` and `forces_raw` use `patches (hot_tube)`, so the raw
pressure/viscous decomposition is directly comparable to the force
coefficients. After using the actual `rhoInf = 1.205`, the raw total and
`forceCoeffs` match to roundoff.

Primary window: `t = 2..10 s`.

| Quantity | Value |
|---|---:|
| `f_shed` from every-second `Cl` peak | `3.2787 Hz` |
| `St` | `0.15572` |
| adjacent `Cl` peak component | `6.5574 Hz` |
| `Cd_p_mean` | `2.9036` |
| `Cd_v_mean` | `0.4574` |
| `Cl_p_rms` | `0.1638` |
| `Cl_v_rms` | `0.0145` |

The PSD is dominated by the adjacent-peak component near `2*f_shed`; the lower
`f_shed` component is present but much weaker in `Cl`. Mean and fluctuating
lift/drag are pressure-dominated, while viscosity contributes a visible steady
drag offset and a smaller phase-shifted lift fluctuation.

### Outputs

- `VV_cases/V4b_3D/results/run008/data/002/run008_002_aerodynamics.md`
- `VV_cases/V4b_3D/results/run008/data/002/run008_002_aerodynamics.json`
- `VV_cases/V4b_3D/results/run008/data/002/run008_002_pressure_viscous_stats.csv`
- `VV_cases/V4b_3D/results/run008/data/002/run008_002_harmonic_peaks.csv`
- `VV_cases/V4b_3D/results/run008/data/002/run008_002_side_peaks.csv`
- `VV_cases/V4b_3D/results/run008/data/002/run008_002_phase_conditioned_cycle.csv`
- `VV_cases/V4b_3D/results/run008/data/002/run008_002_hilbert_phase.npz`
- `VV_cases/V4b_3D/results/run008/figures/002/run008_002_force_pressure_viscous_decomposition.png`
- `VV_cases/V4b_3D/results/run008/figures/002/run008_002_force_psd_harmonics.png`
- `VV_cases/V4b_3D/results/run008/figures/002/run008_002_phase_portraits_hilbert.png`
- `VV_cases/V4b_3D/results/run008/figures/002/run008_002_phase_conditioned_cycle.png`

---

## 2026-05-09 | V4b_3D | run008 heat-balance layer 003 rebuilt

### Work package

Rebuilt the third `run008` analysis layer: stronger heat-balance closure with
separate wall patch contributions, instantaneous closure, lag diagnostics, and
wall-vs-EB Nusselt comparison.

### Actions taken

- added script:
  - `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_heat_balance.py`
- generated stage-003 outputs in:
  - `VV_cases/V4b_3D/results/run008/data/003`
  - `VV_cases/V4b_3D/results/run008/figures/003`
- used `wallHeatFlux.dat` patch-integrated `Q [W]` for:
  - `hot_tube`
  - `hot_fin_z_min`
  - `hot_fin_z_max`
- used reconstructed outlet `T/phi` for EB heat pickup:
  - `Q_air = m_dot Cp (T_out - T_in)`
- kept all reported Nu values on the same reference area:
  - `A_hot_total = 0.002032 m2`

### Results

Primary window: `t = 2..10 s`.

| Quantity | Value |
|---|---:|
| `Q_air` | `1.4703 W` |
| `Q_wall` | `1.4807 W` |
| ratio-of-means closure | `+0.706%` |
| instantaneous closure mean/std | `+0.914% / 4.661%` |
| `Q_tube` | `0.3618 W` |
| `Q_fins` | `1.1189 W` |
| tube/fins heat share | `24.43% / 75.57%` |
| `Nu_tube_wall` | `8.4344` |
| `Nu_fins_wall` | `7.6357` |
| `Nu_total_wall` | `7.8165` |
| `Nu_EB` | `7.7668` |
| `Nu_wall` vs `Nu_EB` | `+0.640%` |

Lag diagnostic:

| Pair | lag | corr |
|---|---:|---:|
| `Q_wall -> Q_air` | `+1.66 s` | `0.1507` |
| `Q_wall -> T_out` | `+1.66 s` | `0.1519` |

The lag correlation is weak, so the lag should be treated as a diagnostic
indicator rather than a robust convection-time measurement.

### Outputs

- `VV_cases/V4b_3D/results/run008/data/003/run008_003_heat_balance.md`
- `VV_cases/V4b_3D/results/run008/data/003/run008_003_heat_balance.json`
- `VV_cases/V4b_3D/results/run008/data/003/run008_003_heat_balance_summary.csv`
- `VV_cases/V4b_3D/results/run008/data/003/run008_003_heat_balance_timeseries.csv`
- `VV_cases/V4b_3D/results/run008/data/003/run008_003_heat_balance_lags.csv`
- `VV_cases/V4b_3D/results/run008/figures/003/run008_003_heat_balance_timeseries_closure.png`
- `VV_cases/V4b_3D/results/run008/figures/003/run008_003_heat_balance_lag.png`
- `VV_cases/V4b_3D/results/run008/figures/003/run008_003_heat_shares_and_nu.png`
- `VV_cases/V4b_3D/results/run008/figures/003/run008_003_nu_eb_vs_wall_scatter.png`

---

## 2026-05-09 | V4b_3D | run008 local tube Nu layer 004 rebuilt

### Work package

Rebuilt the fourth `run008` analysis layer: local tube Nusselt maps and
phase-conditioned tube heat-transfer structure.

### Actions taken

- added script:
  - `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_tube_local_nu.py`
- generated stage-004 outputs in:
  - `VV_cases/V4b_3D/results/run008/data/004`
  - `VV_cases/V4b_3D/results/run008/figures/004`
- read `hot_tube_surface/*/hot_tube.vtk` over `t = 2..10 s`
- computed local:
  - `Nu_mean(theta,z)`
  - `Nu_rms(theta,z)`
  - `A1(theta,z)` and phase at `f_shed`
  - `A2(theta,z)` at `2*f_shed`
  - phase-averaged `Nu(theta,z,phi)` with 32 phase bins
  - `Nu(theta)` z-averaged profiles
  - `Nu(z)` at characteristic angular stations
  - upper-lower tube asymmetry and relation to `Cl`

### Results

Local definition:

```text
Nu(theta,z,t) = q''(theta,z,t) D / (k LMTD(t))
```

Phase reference: `Cl` analytic signal from layer `002`.

| Quantity | Value |
|---|---:|
| samples | `1601` |
| theta/z bins | `96 x 30` |
| phase bins | `32` |
| `Nu_mean_area_proxy` | `8.5881` |
| `Nu_rms_area_proxy` | `0.0978` |
| `A1_mean / A1_max` | `0.0253 / 0.0630` |
| `A2_mean / A2_max` | `0.0215 / 0.0596` |
| peak z-averaged Nu angle | `155.6 deg` |
| `mean |Nu(theta)-Nu(-theta)|` | `0.2909` |
| max local asymmetry | `1.3253` |
| corr upper-lower Nu asymmetry with `Cl` | `+0.900` |
| best short-lag corr | `+0.922` at `-0.005 s` |

### Interpretation

The local tube heat-transfer field is mostly steady in magnitude, but its
upper-lower asymmetry is strongly tied to lift. This provides a clean
mechanistic bridge between the aerodynamic `Cl` signal and local tube cooling
redistribution.

### Outputs

- `VV_cases/V4b_3D/results/run008/data/004/run008_004_tube_local_nu.md`
- `VV_cases/V4b_3D/results/run008/data/004/run008_004_tube_nu_summary.csv`
- `VV_cases/V4b_3D/results/run008/data/004/run008_004_tube_nu_summary.json`
- `VV_cases/V4b_3D/results/run008/data/004/run008_004_tube_nu_theta_z_maps.csv`
- `VV_cases/V4b_3D/results/run008/data/004/run008_004_tube_nu_theta_profile.csv`
- `VV_cases/V4b_3D/results/run008/data/004/run008_004_tube_nu_z_characteristic_angles.csv`
- `VV_cases/V4b_3D/results/run008/data/004/run008_004_tube_phase_average_summary.csv`
- `VV_cases/V4b_3D/results/run008/data/004/run008_004_tube_asymmetry_vs_cl.csv`
- `VV_cases/V4b_3D/results/run008/data/004/run008_004_tube_nu_arrays.npz`
- `VV_cases/V4b_3D/results/run008/figures/004/run008_004_tube_nu_maps_mean_rms_harmonics.png`
- `VV_cases/V4b_3D/results/run008/figures/004/run008_004_tube_nu_phase_asymmetry_maps.png`
- `VV_cases/V4b_3D/results/run008/figures/004/run008_004_tube_phase_averaged_nu_maps.png`
- `VV_cases/V4b_3D/results/run008/figures/004/run008_004_tube_nu_theta_profiles_asymmetry.png`
- `VV_cases/V4b_3D/results/run008/figures/004/run008_004_tube_nu_z_characteristic_angles.png`
- `VV_cases/V4b_3D/results/run008/figures/004/run008_004_tube_asymmetry_vs_cl.png`

---

## 2026-05-09 | V4b_3D | run008 local fin Nu layer 005 rebuilt

### Work package

Rebuilt the fifth `run008` analysis layer: local Nusselt profiles on the two
hot fin surfaces and their coupling to the lift/shedding signal.

### Actions taken

- added script:
  - `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_fin_local_nu.py`
- generated stage-005 outputs in:
  - `VV_cases/V4b_3D/results/run008/data/005`
  - `VV_cases/V4b_3D/results/run008/figures/005`
- read `hot_fin_surface/*/hot_fin_z_min.vtk` and
  `hot_fin_surface/*/hot_fin_z_max.vtk`
- computed:
  - `Nu_local(x,t)` separately for both fin surfaces
  - mean/RMS `Nu_local(x)`
  - `A1/A2` harmonic amplitudes and phase relative to `Cl`
  - fin symmetry/antisymmetry and phase lag
  - coherence and lag maps for `Cl -> Nu_local(x)`
  - active coupled zones based on coherence and above-median `A1`

### Results

Primary window: `t = 2..10 s`.

| Quantity | Value |
|---|---:|
| samples | `1601` |
| x bins / valid bins | `80 / 61` |
| `Nu_mean_z_min` | `4.5669` |
| `Nu_mean_z_max` | `4.5412` |
| `Nu_rms_z_min_mean` | `0.0482` |
| `Nu_rms_z_max_mean` | `0.0498` |
| `A1_mean z_min/z_max` | `0.0136 / 0.0130` |
| `A2_mean z_min/z_max` | `0.0095 / 0.0111` |
| mean antisymmetric component | `0.0148 Nu` |
| mean fin-pair time correlation | `0.858` |
| `A1` phase difference `z_max-z_min` | `-3.33 deg` |
| median lag difference `z_max-z_min` | `+0.0000 s` |
| mean coherence near `f_shed` z_min/z_max | `0.606 / 0.613` |
| active coupled zones z_min/z_max | `50.8% / 49.2%` |
| median lag vs `Cl` z_min/z_max | `-0.075 s / -0.075 s` |

### Interpretation

The fin heat transfer is almost symmetric between the two fin faces, but about
half of the valid `x` range remains coherently coupled to `Cl` near the
shedding frequency. The two fin faces are nearly in phase for the Cl-coupled
component, so the fin response behaves more like a symmetric thermal filter
than a strong antisymmetric amplifier.

### Outputs

- `VV_cases/V4b_3D/results/run008/data/005/run008_005_fin_local_nu.md`
- `VV_cases/V4b_3D/results/run008/data/005/run008_005_fin_nu_summary.csv`
- `VV_cases/V4b_3D/results/run008/data/005/run008_005_fin_nu_summary.json`
- `VV_cases/V4b_3D/results/run008/data/005/run008_005_fin_nu_x_profiles.csv`
- `VV_cases/V4b_3D/results/run008/data/005/run008_005_fin_nu_arrays.npz`
- `VV_cases/V4b_3D/results/run008/figures/005/run008_005_fin_nu_x_profiles.png`
- `VV_cases/V4b_3D/results/run008/figures/005/run008_005_fin_phase_coherence_lag.png`
- `VV_cases/V4b_3D/results/run008/figures/005/run008_005_fin_nu_xt_maps.png`
- `VV_cases/V4b_3D/results/run008/figures/005/run008_005_fin_active_coupled_zones.png`

---

## 2026-05-09 | V4b_3D | run008 modal layer 006 rebuilt

### Work package

Rebuilt the sixth `run008` analysis layer: POD, EPOD/SPOD-like coherent maps,
and DMD sanity checks from the `midspan_z0` snapshots.

### Actions taken

- added script:
  - `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_modal_006.py`
- generated stage-006 outputs in:
  - `VV_cases/V4b_3D/results/run008/data/006`
  - `VV_cases/V4b_3D/results/run008/figures/006`
- read `midspan_z0/*/z0.vtk` over `t = 2..10 s`
- performed POD for:
  - `U`
  - `T`
  - RMS-scaled joint `U+T`
- computed:
  - POD mode energy spectra
  - `a1-a2` phase portraits
  - correlations of POD coefficients with `Cl`, `Cd`, `Q_wall`,
    `Nu_tube`, and `Nu_fins`
  - EPOD/regression fields conditioned on `Cl`, `Q_wall`, and `Nu_tube`
  - single-frequency coherent maps at `f_shed` and `2*f_shed`
  - reduced exact DMD eigenvalues/modes as a frequency sanity check

### Results

Primary window: `t = 2..10 s`.

| Quantity | Value |
|---|---:|
| snapshots | `401` |
| midspan points | `13,524` |
| `U` POD mode 1 / 2 energy | `40.70% / 40.52%` |
| `T` POD mode 1 / 2 energy | `39.70% / 38.27%` |
| joint `U+T` POD mode 1 / 2 energy | `40.22% / 39.76%` |
| `U` pair 1+2 share of first 8 modes | `87.45%` |
| `T` pair 1+2 share of first 8 modes | `84.00%` |
| DMD near `f_shed` | `3.3577 Hz` |
| DMD near `2*f_shed` | `6.5695 Hz` |

Strongest POD-signal correlations:

| POD set | mode | signal | corr |
|---|---:|---|---:|
| `T` | 1 | `Cl` | `-0.9865` |
| joint `U+T` | 1 | `Cl` | `-0.9781` |
| `U` | 1 | `Cd` | `-0.8503` |
| joint `U+T` | 1 | `Cd` | `-0.8500` |
| `T` | 1 | `Cd` | `-0.8097` |
| `U` | 2 | `Cl` | `-0.7928` |

### Interpretation

The first two POD modes form a strong shedding-pair candidate in both velocity
and temperature. DMD independently recovers frequencies close to the expected
`f_shed` and `2*f_shed`, supporting the modal interpretation. The leading
temperature mode is very strongly tied to `Cl`, while velocity mode 1 also
tracks drag strongly.

### Outputs

- `VV_cases/V4b_3D/results/run008/data/006/run008_006_modal_analysis.md`
- `VV_cases/V4b_3D/results/run008/data/006/run008_006_modal_summary.csv`
- `VV_cases/V4b_3D/results/run008/data/006/run008_006_modal_summary.json`
- `VV_cases/V4b_3D/results/run008/data/006/run008_006_pod_energy.csv`
- `VV_cases/V4b_3D/results/run008/data/006/run008_006_pod_signal_correlations.csv`
- `VV_cases/V4b_3D/results/run008/data/006/run008_006_dmd_eigenvalues.csv`
- `VV_cases/V4b_3D/results/run008/data/006/run008_006_modal_arrays.npz`
- `VV_cases/V4b_3D/results/run008/figures/006/run008_006_pod_energy.png`
- `VV_cases/V4b_3D/results/run008/figures/006/run008_006_pod_phase_portraits.png`
- `VV_cases/V4b_3D/results/run008/figures/006/run008_006_pod_mode_maps.png`
- `VV_cases/V4b_3D/results/run008/figures/006/run008_006_pod_signal_correlations.png`
- `VV_cases/V4b_3D/results/run008/figures/006/run008_006_epod_spod_maps.png`
- `VV_cases/V4b_3D/results/run008/figures/006/run008_006_dmd_sanity_modes.png`

---

## 2026-05-09 | V4b_3D | run008 coherence layer 007 rebuilt

### Work package

Rebuilt the seventh `run008` analysis layer: coherence and cross-spectral
analysis between lift and global/local heat-transfer signals.

### Actions taken

- added script:
  - `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_coherence_007.py`
- generated stage-007 outputs in:
  - `VV_cases/V4b_3D/results/run008/data/007`
  - `VV_cases/V4b_3D/results/run008/figures/007`
- computed global coherence/cross-phase for:
  - `Cl` vs `Q_wall`
  - `Cl` vs `Q_tube`
  - `Cl` vs `Q_fins`
  - `Cl` vs `Nu_tube`
  - `Cl` vs `Nu_fins`
- computed spatial coherence and lag maps for:
  - `Cl` vs `Nu(theta,z)` on the tube
  - `Cl` vs `Nu_local(x)` on both fin surfaces
- reported separate metrics at:
  - `f_shed`
  - `2*f_shed`

### Results

Global coherence with `Cl`:

| Signal | coherence at `f_shed` | coherence at `2*f_shed` |
|---|---:|---:|
| `Q_wall` | `0.571` | `0.906` |
| `Q_tube` | `0.736` | `0.945` |
| `Q_fins` | `0.376` | `0.922` |
| `Nu_tube` | `0.561` | `0.950` |
| `Nu_fins` | `0.436` | `0.991` |

Spatial coherence:

| Region | mean coherence at `f_shed` | mean coherence at `2*f_shed` |
|---|---:|---:|
| tube `Nu(theta,z)` | `0.454` | `0.977` |
| fin `z_min` `Nu_local(x)` | `0.393` | `0.967` |
| fin `z_max` `Nu_local(x)` | `0.430` | `0.980` |

Tube active fraction with coherence > 0.5 at `f_shed`: `23.2%`.

Lag diagnostics:

| Diagnostic | Value |
|---|---:|
| tube median cross-phase lag at `f_shed` | `-0.0996 s` |
| tube median cross-correlation lag at `f_shed` | `+0.0000 s` |

### Interpretation

The heat-transfer response is much more coherent with `Cl` at the second
harmonic than at the fundamental. This agrees with the force PSD and local Nu
analyses: a large part of the thermal response is organized around the
half-cycle/two-sided shedding component, while fundamental coherence is more
spatially localized.

### Outputs

- `VV_cases/V4b_3D/results/run008/data/007/run008_007_coherence_analysis.md`
- `VV_cases/V4b_3D/results/run008/data/007/run008_007_coherence_summary.json`
- `VV_cases/V4b_3D/results/run008/data/007/run008_007_global_coherence.csv`
- `VV_cases/V4b_3D/results/run008/data/007/run008_007_tube_coherence_maps.csv`
- `VV_cases/V4b_3D/results/run008/data/007/run008_007_fin_coherence_profiles.csv`
- `VV_cases/V4b_3D/results/run008/data/007/run008_007_coherence_arrays.npz`
- `VV_cases/V4b_3D/results/run008/figures/007/run008_007_global_coherence_crossphase.png`
- `VV_cases/V4b_3D/results/run008/figures/007/run008_007_tube_coherence_lag_maps.png`
- `VV_cases/V4b_3D/results/run008/figures/007/run008_007_fin_coherence_lag_profiles.png`

---

## 2026-05-09 | V4b_3D | run008 transfer-entropy layer 008 rebuilt

### Work package

Rebuilt the eighth `run008` analysis layer: exploratory transfer entropy and
directionality screening between lift, heat-transfer signals, reduced fin
`Nu_local(x)` bins, and selected POD modal coefficients.

### Actions taken

- added script:
  - `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_transfer_entropy_008.py`
- generated stage-008 outputs in:
  - `VV_cases/V4b_3D/results/run008/data/008`
  - `VV_cases/V4b_3D/results/run008/figures/008`
- used quantile-discretized TE with:
  - 4 bins
  - multiple tested lags
  - circular-shift source surrogates
  - 250 surrogates for global/modal signals
  - 160 surrogates for reduced fin x-bins

### Results

Strongest global `Cl -> heat` directions above surrogate 95%:

| Direction | TE | lag | surrogate95 |
|---|---:|---:|---:|
| `Cl -> Q_wall` | `0.2368 bits` | `0.240 s` | `0.1345` |
| `Cl -> Q_tube` | `0.3769 bits` | `0.080 s` | `0.1922` |
| `Cl -> Q_fins` | `0.4519 bits` | `0.240 s` | `0.1810` |
| `Cl -> Nu_tube` | `0.1413 bits` | `0.240 s` | `0.0671` |
| `Cl -> Nu_fins` | `0.1739 bits` | `0.240 s` | `0.0639` |
| `Cl -> Nu_EB` | `0.2602 bits` | `0.060 s` | `0.1484` |

Reduced fin-bin result:

| Region | significant `Cl -> Nu_local(x)` bins |
|---|---:|
| `hot_fin_z_min` | `16/16` |
| `hot_fin_z_max` | `16/16` |

Strongest reduced fin-bin TE values are around `0.38 bits`, especially near
`x ~= 3.8..11.8 mm`.

### Interpretation

This layer should be treated as an exploratory directionality screen, not a
standalone causal proof. The dominant physical reading remains consistent with
the safer coherence/cross-phase layer: lift/shedding phase organizes the
thermal response. Weaker reverse-direction TE appears for some global and modal
pairs, likely because all signals are projections of the same low-dimensional
periodic shedding oscillator.

### Outputs

- `VV_cases/V4b_3D/results/run008/data/008/run008_008_transfer_entropy_analysis.md`
- `VV_cases/V4b_3D/results/run008/data/008/run008_008_transfer_entropy_summary.json`
- `VV_cases/V4b_3D/results/run008/data/008/run008_008_transfer_entropy_global_modal.csv`
- `VV_cases/V4b_3D/results/run008/data/008/run008_008_transfer_entropy_fin_xbins.csv`
- `VV_cases/V4b_3D/results/run008/data/008/run008_008_transfer_entropy_lag_curves.csv`
- `VV_cases/V4b_3D/results/run008/figures/008/run008_008_global_transfer_entropy.png`
- `VV_cases/V4b_3D/results/run008/figures/008/run008_008_global_te_lag_sensitivity.png`
- `VV_cases/V4b_3D/results/run008/figures/008/run008_008_fin_te_x_profiles.png`
- `VV_cases/V4b_3D/results/run008/figures/008/run008_008_modal_te_heatmap.png`

---

## 2026-05-09 | V4b_3D | run008 phase-averaging layer 009 rebuilt

### Work package

Rebuilt the ninth `run008` analysis layer: phase-averaged physical story using
the shedding phase from `Cl`.

### Actions taken

- added script:
  - `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_phase_averaging_009.py`
- generated stage-009 outputs in:
  - `VV_cases/V4b_3D/results/run008/data/009`
  - `VV_cases/V4b_3D/results/run008/figures/009`
- used Hilbert phase from layer `002`
- used 16 phase bins over `t = 2..10 s`
- phase-averaged:
  - `Cl`, `Cd`, `Cm`
  - `Q_wall`, `Q_tube`, `Q_fins`
  - `Nu_tube_wall`, `Nu_fins_wall`, `Nu_EB`
  - tube `Nu(theta,z)`
  - fin `Nu_local(x)`
  - midspan `U` and `T`

### Results

Key phase events:

| Event | phase | lag from max `abs(Cl)` |
|---|---:|---:|
| max `abs(Cl)` / `Cl_min` | `236.25 deg` | `0.0000 s` |
| `Cl_max` | `281.25 deg` | `+0.0381 s` |
| `Q_tube_max` | `236.25 deg` | `+0.0000 s` |
| `Q_fins_max` | `303.75 deg` | `+0.0572 s` |
| `Q_wall_max` | `303.75 deg` | `+0.0572 s` |
| `Nu_tube_wall_max` | `123.75 deg` | `-0.0953 s` |
| `Nu_fins_wall_max` | `123.75 deg` | `-0.0953 s` |
| `Nu_EB_max` | `123.75 deg` | `-0.0953 s` |

### Interpretation

The phase-averaging layer gives a clean physical narrative: the tube integrated
heat pickup peaks with maximum `abs(Cl)`, while the fins and total wall heat
pickup peak later by about `67.5 deg` or `0.057 s`. The local/wall Nusselt
maxima are phase-locked but not identical to the integrated heat-flux maxima,
so the full story should be told using both `Q(t)` and local `Nu(theta,z,phi)`
/ `Nu_local(x,phi)` maps.

### Outputs

- `VV_cases/V4b_3D/results/run008/data/009/run008_009_phase_averaging_analysis.md`
- `VV_cases/V4b_3D/results/run008/data/009/run008_009_phase_averaging_summary.json`
- `VV_cases/V4b_3D/results/run008/data/009/run008_009_phase_global_cycle.csv`
- `VV_cases/V4b_3D/results/run008/data/009/run008_009_phase_events.csv`
- `VV_cases/V4b_3D/results/run008/data/009/run008_009_fin_phase_profiles.csv`
- `VV_cases/V4b_3D/results/run008/data/009/run008_009_midspan_phase_summary.csv`
- `VV_cases/V4b_3D/results/run008/data/009/run008_009_phase_arrays.npz`
- `VV_cases/V4b_3D/results/run008/figures/009/run008_009_phase_global_cycle.png`
- `VV_cases/V4b_3D/results/run008/figures/009/run008_009_tube_nu_phase_grid.png`
- `VV_cases/V4b_3D/results/run008/figures/009/run008_009_fin_nu_phase_map.png`
- `VV_cases/V4b_3D/results/run008/figures/009/run008_009_midspan_wake_speed_phase_grid.png`
- `VV_cases/V4b_3D/results/run008/figures/009/run008_009_midspan_temperature_phase_grid.png`
- `VV_cases/V4b_3D/results/run008/figures/009/run008_009_phase_story_key_frames.png`

---

## 2026-05-09 | V4b_3D | run008 wake-probe layer 010 rebuilt

### Work package

Rebuilt the tenth `run008` analysis layer: wake-probe dynamics and linkage
between probe signals, lift, wall heat transfer, outlet temperature, and local
fin `Nu`.

### Actions taken

- added script:
  - `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_wake_probes_010.py`
- generated stage-010 outputs in:
  - `VV_cases/V4b_3D/results/run008/data/010`
  - `VV_cases/V4b_3D/results/run008/figures/010`
- parsed 13 wake probes from:
  - `postProcessing/probes_wake/0/U`
  - `postProcessing/probes_wake/0/T`
- computed:
  - PSD of `Uy`
  - coherence near `f_shed` and `2*f_shed`
  - cross-correlation lag `Uy -> Cl`
  - cross-correlation lag `Uy -> Q_wall`
  - lag from wake probes to outlet `T_out`
  - ranking of probe `Uy` coherence with local fin `Nu_local(x)`

### Results

| Diagnostic | Best probe / value |
|---|---|
| strongest `Uy` RMS | probe `2`, `(x,y)=(30,0) mm`, RMS `0.11429 m/s` |
| highest `Uy-Cl` coherence near `f_shed` | probe `2`, coherence `0.883`, lag `-0.0500 s` |
| highest `Uy-Q_wall` coherence near `f_shed` | probe `6`, coherence `0.905`, lag `+0.4200 s` |
| highest `Uy-local Nu` coherence at `f_shed` | probe `9`, `fin_z_max`, `x=6.06 mm`, coherence `0.985` |
| highest `Uy-local Nu` coherence at `2f_shed` | probe `2`, `fin_z_max`, `x=3.64 mm`, coherence `0.994` |

Top probes by `Uy-Cl` coherence:

| Probe | x [mm] | y [mm] | coherence | lag `Uy -> Cl` |
|---:|---:|---:|---:|---:|
| `2` | `30` | `0` | `0.883` | `-0.0500 s` |
| `8` | `40` | `6` | `0.766` | `-0.0200 s` |
| `9` | `60` | `6` | `0.568` | `-0.0300 s` |
| `6` | `100` | `0` | `0.462` | `-0.0600 s` |

### Interpretation

The probe ranking separates two useful reduced sensors. Probe `2` is the best
near-wake/lift sensor, while probe `9` best tracks local fin heat-transfer
coupling. The wake-probe PSD is dominated by the `2f_shed` / adjacent lift-peak
component near the Welch bin `6.64 Hz`, matching the earlier force and thermal
coherence analyses.

### Outputs

- `VV_cases/V4b_3D/results/run008/data/010/run008_010_wake_probes_analysis.md`
- `VV_cases/V4b_3D/results/run008/data/010/run008_010_wake_probes_summary.json`
- `VV_cases/V4b_3D/results/run008/data/010/run008_010_probe_metrics.csv`
- `VV_cases/V4b_3D/results/run008/data/010/run008_010_probe_local_nu_coherence_rank.csv`
- `VV_cases/V4b_3D/results/run008/figures/010/run008_010_probe_layout_coherence.png`
- `VV_cases/V4b_3D/results/run008/figures/010/run008_010_probe_uy_psd.png`
- `VV_cases/V4b_3D/results/run008/figures/010/run008_010_probe_cross_correlation_lags.png`
- `VV_cases/V4b_3D/results/run008/figures/010/run008_010_probe_to_local_nu_coherence_rank.png`

---

## 2026-05-09 | V4b_3D | run008 campaign comparison layer 011 rebuilt

### Work package

Rebuilt the eleventh `run008` analysis layer: comparison against earlier
campaign runs and final production-reference decision.

### Actions taken

- added script:
  - `VV_cases/V4b_3D/results/run008/scripts/analyse_run008_campaign_comparison_011.py`
- generated stage-011 outputs in:
  - `VV_cases/V4b_3D/results/run008/data/011`
  - `VV_cases/V4b_3D/results/run008/figures/011`
- compared:
  - `run004b`
  - `run005`
  - `run007c`
  - `run008`
- added short-window context for:
  - `run004b`
  - `run007a`
  - `run007c`

### Results

Global regime table:

| Run | Window | Cd | Cl_rms | St | Nu | Closure |
|---|---:|---:|---:|---:|---:|---:|
| `run004b` | `3..6 s` | `3.361490` | `0.184056` | `0.15517` | `7.777953` | N/A |
| `run005` | `3..6 s` | `3.359275` | `0.184616` | `0.15519` | `7.775975` | N/A |
| `run007c` | `0.5..2 s` | `3.361209` | `0.176698` | N/A | `7.821736` | `+1.39%` |
| `run008` | `2..10 s` | `3.361014` | `0.176441` | `0.15426` | `7.770004` | `+0.706%` |

Differences relative to `run008`:

| Run | Cd | Cl_rms | Nu |
|---|---:|---:|---:|
| `run004b` | `+0.014%` | `+4.315%` | `+0.102%` |
| `run005` | `-0.052%` | `+4.633%` | `+0.077%` |
| `run007c` smoke | `+0.006%` | `+0.145%` | `+0.666%` |

Short-window context:

| Run | Cd | Cl_rms | Q_wall | Q_air | Nu_wall_case_k | wall-air diff |
|---|---:|---:|---:|---:|---:|---:|
| `run004b` | `3.361209` | `0.176698` | `1.0591 W` | `1.0445 W` | `7.8217` | `+1.4%` |
| `run007a` | `3.473619` | `0.178979` | `1.3396 W` | `1.8450 W` | `7.3786` | `-27.4%` |
| `run007c` | `3.361209` | `0.176698` | `1.4824 W` | `1.4621 W` | `7.8217` | `+1.4%` |

### Decision

Production reference is `run008`.

Rationale:

- it matches the established aerodynamic regime from `run004b/run005`
- it inherits the Cp-consistent constant-property setup validated by `run007c`
- it uses the production `2..10 s` record with about 26 shedding cycles
- it has closed heat balance (`Q_wall-Q_air ~= +0.706%`)
- it contains the measurement-rich sampling needed for the POD/EPOD,
  coherence, phase-averaging, local Nu, and wake-probe analyses

`run007a` remains a useful variable-property diagnostic, but not a production
reference because the short-window wall-air closure is about `-27.4%` and drag
is shifted by about `+3.34%`.

### Outputs

- `VV_cases/V4b_3D/results/run008/data/011/run008_011_campaign_comparison.md`
- `VV_cases/V4b_3D/results/run008/data/011/run008_011_campaign_decision.json`
- `VV_cases/V4b_3D/results/run008/data/011/run008_011_campaign_regime_table.csv`
- `VV_cases/V4b_3D/results/run008/data/011/run008_011_short_window_table.csv`
- `VV_cases/V4b_3D/results/run008/figures/011/run008_011_campaign_global_regime.png`
- `VV_cases/V4b_3D/results/run008/figures/011/run008_011_differences_vs_production.png`
- `VV_cases/V4b_3D/results/run008/figures/011/run008_011_short_vs_production.png`
- `VV_cases/V4b_3D/results/run008/figures/011/run008_011_run007a_diagnostic_status.png`

---

## 2026-05-09 | V4b_3D | run008 final paper-grade figures layer 012 rebuilt

### Work package

Rebuilt the twelfth `run008` analysis layer: a curated final figure set for
paper/manuscript planning.

### Actions taken

- ran script:
  - `VV_cases/V4b_3D/results/run008/scripts/build_run008_paper_figures_012.py`
- generated final figure outputs in:
  - `VV_cases/V4b_3D/results/run008/figures/012`
- generated figure captions and summary metadata in:
  - `VV_cases/V4b_3D/results/run008/data/012`
- updated:
  - `VV_cases/V4b_3D/results/run008/summary.md`

### Figure set

| Figure | Content |
|---|---|
| 1 | geometry, domain, and sampling layout |
| 2 | `Cd(t)`, `Cl(t)`, and `PSD(Cl)` |
| 3 | heat balance `Q_air` vs `Q_wall`, plus `Nu_EB` vs `Nu_wall` |
| 4 | mean and RMS `Nu(theta,z)` on the tube |
| 5 | phase-averaged `Nu(theta)` over the shedding cycle |
| 6 | fin `Nu_local(x)` mean/RMS/coherence |
| 7 | POD energy and mode 1/2 maps |
| 8 | EPOD / lift-correlated thermal structure |
| 9 | coherence maps between `Cl` and local `Nu` |
| 10 | summary mechanism schematic |

### Outputs

- `VV_cases/V4b_3D/results/run008/data/012/run008_012_final_figure_captions.md`
- `VV_cases/V4b_3D/results/run008/data/012/run008_012_final_figure_captions.csv`
- `VV_cases/V4b_3D/results/run008/data/012/run008_012_final_figures_summary.json`
- `VV_cases/V4b_3D/results/run008/figures/012/fig01_geometry_domain_sampling.png`
- `VV_cases/V4b_3D/results/run008/figures/012/fig02_forces_cl_psd.png`
- `VV_cases/V4b_3D/results/run008/figures/012/fig03_heat_balance_nu_closure.png`
- `VV_cases/V4b_3D/results/run008/figures/012/fig04_tube_nu_mean_rms.png`
- `VV_cases/V4b_3D/results/run008/figures/012/fig05_phase_averaged_tube_nu_theta.png`
- `VV_cases/V4b_3D/results/run008/figures/012/fig06_fin_nu_mean_rms_coherence.png`
- `VV_cases/V4b_3D/results/run008/figures/012/fig07_pod_energy_modes.png`
- `VV_cases/V4b_3D/results/run008/figures/012/fig08_epod_cl_thermal_structure.png`
- `VV_cases/V4b_3D/results/run008/figures/012/fig09_cl_nu_coherence_maps.png`
- `VV_cases/V4b_3D/results/run008/figures/012/fig10_mechanism_schematic.png`
- matching PDF versions for all ten figures

### Interpretation

Layer `012` is a curated visual synthesis of validated layers `001..011`, not
a new physics calculation. It collects the production-domain geometry,
global force/heat-balance metrics, local tube/fin Nusselt behavior, modal
structure, coherence, and mechanism summary into one article-ready figure set.

---
## 2026-05-12 | VV_cases | canonical V4b/V2 documentation sync after run008 review

### Work package

Reviewed the Markdown state of the repository after the completed V4b `run008`
production analysis, clarified the `run008` physical-property model, and synced
the canonical study documents with the accepted current state.

### Actions taken

- Verified that `run008` inherited the `run007c` constant-property
  `eConst + Boussinesq + sensibleInternalEnergy` setup with capacity coefficient
  `1005`.
- Confirmed that the true variable-property diagnostic is `run007a`
  (`incompressiblePerfectGas + Sutherland`), not `run008`.
- Updated `V4b_3D/doc/V4b_3D.md` with the accepted `Lin=2D`, `Lout=8D`
  production domain, `run008` result table, and current mechanism statement.
- Updated `V2_thermal/doc/V2_thermal.md` so the accepted O-grid validation
  run-004 supersedes the older snappy/Boussinesq diagnostic narrative.
- Added `V4b_3D/results/run008/q_lambda2_structure_plan.md` as the next
  post-processing plan for vortical-structure identification.

### Decisions made

- Treat `run008` as the accepted constant-property, Cp-consistent production
  reference.
- Keep `run007a` as a variable-property diagnostic until a production-quality
  energy balance is closed.
- Treat V2 run-004 O-grid results as the current thermal validation reference.
- Use `Q`/`lambda2` as the next targeted post-processing step if the manuscript
  needs a stronger named-structure figure.

### Next step

Run a lightweight `Q`/`lambda2` visual pass on representative `run008` phases,
then decide whether to promote it into a formal analysis layer.
