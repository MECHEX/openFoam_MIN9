# Working Checklist

Read this file before starting a new block of work in `VV_cases`.

## Before starting

1. Identify the target study.
2. Read `VV_cases/STORAGE_STANDARD.md`.
3. Check the canonical study document:
   - `VV_cases/<study>/doc/<study>.md`
4. Decide whether the task is:
   - new run
   - update inside an existing run
   - post-processing
   - documentation-only
   - plotting-only
5. Reserve the next run number only if the whole campaign is genuinely new.

## Active repository model

The active repo is intentionally simplified.

Use:

- `VV_cases/<study>/_code/` for study-specific Python scripts
- `VV_cases/RESEARCH_LOG.md` for chronology
- `VV_cases/<study>/doc/<study>.md` for clean technical description
- `results/.../runs/<run>/run.md` for run-level notes
- `results/.../runs/<run>/summary.csv` and `summary.md` for run summaries
- `results/.../runs/<run>/simulations/<case>/notes.md` for compact per-case records

Do not rebuild complicated folder hierarchies unless we explicitly decide to restore them.

## During the work

1. Keep the working OpenFOAM case outside the simplified archived structure when possible.
2. Do not overwrite old numbered runs.
3. If only a few simulations change within the same campaign, keep them under the same run.
4. Keep final study-level figures only in `doc/figs/`.

## After the work package

1. Update the relevant run folder.
2. Update `summary.csv` and `summary.md` if results changed.
3. Update `doc/<study>.md` if the accepted setup or accepted results changed.
4. Copy only cited figures into `doc/figs/`.
5. Append a timestamped entry to `VV_cases/RESEARCH_LOG.md`.

## Minimum questions before leaving

- What was changed?
- Which run was touched?
- Which simulations changed?
- Was `doc/<study>.md` updated?
- Was `RESEARCH_LOG.md` updated?
- What should happen next?

## Non-negotiable rule

No substantial task is complete until:

- `VV_cases/RESEARCH_LOG.md` is updated
- the relevant canonical study document is consistent with the accepted current state
