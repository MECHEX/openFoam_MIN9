# VV Cases Workspace

This directory groups verification and validation studies for the confined-cylinder project.

## Core files

- `STORAGE_STANDARD.md`
  Defines how every study (`V1`, `V2`, `V3`, ...) should store runs, simulations, raw data, plots, and notes.
- `WORKING_CHECKLIST.md`
  The short operational checklist to read before starting a new batch of work.
- `RESEARCH_LOG.md`
  Chronological research notebook. Every completed work package should be logged there with a timestamp.

## Rule of use

Before starting a new block of work:

1. Read `WORKING_CHECKLIST.md`.
2. Confirm the target study and run naming.
3. After the work package is finished, append an entry to `RESEARCH_LOG.md`.

## Current convention

- one `run` means one campaign / one attempt
- one run can contain many simulations
- different `Re`, meshes, or domain variants usually sit inside the same run
- a new run number is created only when the whole campaign is repeated after failure or a major correction

## Current transition state

`V1_solver/results/study_v1` has already been migrated to the campaign-style layout.
Other studies should follow the same convention as they are cleaned up or extended.
