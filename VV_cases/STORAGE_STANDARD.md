# VV Cases Storage Standard

## Purpose

This document defines the simplified repository layout for `VV_cases`.

The repository is intended to remain readable and article-oriented.
It is not meant to mirror every OpenFOAM working directory in full.

## Core rule

There are only two documentation layers:

- `VV_cases/RESEARCH_LOG.md`
  chronological log of work, debugging, decisions, and packages
- `VV_cases/<study>/doc/<study>.md`
  clean canonical technical description of the accepted setup and results

`RESEARCH_LOG.md` is appended.
`doc/<study>.md` is rewritten and improved over time.

## Study-level layout

Each study should be kept as simple as possible:

```text
VV_cases/
  Vx_name/
    _code/
    doc/
      Vx_name.md
      figs/
    results/
      study_vx/
        runs/
          001_data_<slug>/
          002_data_<slug>/
```

No additional study-level `publication/`, `study_summary/`, or cache folders should be
kept in the active structure unless there is a strong technical reason.

## Study-level code

Python helper scripts for a study should be stored in:

- `VV_cases/<study>/_code/`

This keeps the study root cleaner and separates code from documentation and archived results.

## What belongs in `doc/`

`doc/<study>.md` should contain the current accepted:

- objective
- literature reference
- geometry
- boundary conditions
- numerical setup
- mesh description or mesh-independence notes
- residual/convergence description
- accepted result tables
- accepted comparison with literature

`doc/figs/` should contain only figures explicitly cited by `doc/<study>.md`.

## Runs

A run is one attempt or one computational campaign.

Examples:

- `001_data_beta05_initial_verification`
- `002_data_sahin_owens_poiseuille_verification`

Different Reynolds numbers or mesh variants can belong to the same run.
A new run number is used only after a major correction, restart, or methodological change.

## Simplified run layout

Each run should be flattened to:

```text
001_data_<slug>/
  run.md
  summary.csv
  summary.md
  plots/          # optional, only for run-specific comparison plots
  simulations/
```

### `run.md`

This is the human-readable description of the run as a whole.
It replaces the earlier split across `00_notes`, `01_run_setup`, and similar folders.

### `summary.csv` and `summary.md`

These store the aggregated results of the run.
They replace the earlier `03_run_summary/` folder.

### `plots/`

Optional.
Use only if a run genuinely needs run-level comparison plots.
Study-level final figures still belong only in `doc/figs/`.

## Simplified simulation layout

Each simulation inside a run should be flattened to:

```text
simulations/
  <simulation_slug>/
    notes.md
```

### `notes.md`

This single file should describe the case in plain technical language and may include:

- case name
- geometry
- Reynolds number
- mesh identifier
- accepted cell count
- important setup details
- outcome
- key metrics
- interpretation

The repository should not keep mirrored `0/`, `constant/`, `system/`, raw time directories,
or per-simulation plot folders in the active V&V structure unless explicitly needed later.

## Practical implication

The repo is for:

- clean study documentation
- compact run summaries
- article-oriented material

The repo is not the primary storage location for every raw OpenFOAM artifact.

## Naming

Use short stable slugs:

- run: `001_data_beta05_initial_verification`
- simulation: `baseline_medium_Re160`

Avoid spaces and long prose in names.

## Workflow

1. Create the next numbered run.
2. Add or update `run.md`.
3. Add simulation folders with `notes.md`.
4. Update `summary.csv` and `summary.md`.
5. Update `doc/<study>.md` if the accepted setup or accepted results changed.
6. Copy only cited figures to `doc/figs/`.
7. Append the package to `VV_cases/RESEARCH_LOG.md`.

## Migration policy

When old studies are simplified:

- keep the current accepted meaning
- remove redundant layers
- prefer one clear location over several overlapping ones

The active repository should favor clarity over archival completeness.
