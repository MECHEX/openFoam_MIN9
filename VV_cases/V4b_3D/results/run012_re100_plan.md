# V4b run012 Re=100 production-geometry plan

Date: 2026-06-05

## Purpose

Run `Re=100` on the accepted V4b production geometry and mesh family, with the same sampling contract as `run008 Re=200`.

Main comparison:

- `run012 Re=100`: expected pre-Hopf / steady or weakly unsteady reference.
- `run008 Re=200`: accepted post-Hopf production reference.

This supports the honest claim: `Re=100 steady context -> Re=200 periodic production result`.

## Case

WSL case:

- `/home/hexmachina/of_runs/V4b_3D_run012_re100_production`

Setup:

- source: `/home/hexmachina/of_runs/V4b_3D_run008`
- mesh: production medium mesh, 407,440 cells
- `U_inf = 0.12633 m/s`
- `magUInf = 0.12633`
- `endTime = 10 s`
- `maxCo = 0.8`
- ranks: 20
- sampling: same as `run008`

## Run Status

Smoke:

- reached `t = 0.1 s`
- `Co_max ~= 0.751`
- solver stable

Full run:

- started from clean `t = 0`
- log: `/home/hexmachina/of_runs/V4b_3D_run012_re100_production/logs/log.foamRun_parallel.20260605_211429_run012_re100_full_from_zero.full`
- PID root: `721`

## Planned Windows

Use the same windows as `run008` where possible:

| Window | Role |
|---|---|
| `0.5..2 s` | early transient / short comparison |
| `2..6 s` | first analysis window |
| `4..8 s` | shifted window sensitivity |
| `6..10 s` | late window sensitivity |
| `2..10 s` | primary production-style window |

For `Re=100`, if `Cl_rms` collapses toward zero and no stable shedding frequency exists, POD/EPOD/TE should be reported as diagnostic/not applicable rather than interpreted mechanistically.

## Metrics To Extract

Global hydrodynamics:

- `Cd_mean`
- `Cl_mean`
- `Cl_rms`
- `St`, only if a robust spectral peak exists

Global thermal:

- `Q_air`
- `Q_wall`
- `Nu_EB`
- `Nu_wall`
- wall-air closure
- `T_out`

Modal/informational diagnostics:

- POD energy spectrum and modes
- EPOD/regression maps
- coherence/cross-phase
- transfer entropy with surrogate/FDR caution

## Expected Interpretation

If Re=100 is steady:

- it becomes the clean pre-Hopf production-geometry baseline;
- `POD mode energy` may be dominated by mean/transient adjustment rather than shedding;
- `TE` and `coherence` should not be oversold;
- the main result is contrast: absence of organized unsteady aero-thermal coupling at Re=100 versus clear phase-locked coupling at Re=200.

If Re=100 is weakly periodic:

- quantify `St`, `Cl_rms`, `Nu_EB`, `Nu_wall`;
- compare frequency and heat-transfer modulation against `run008`;
- revise the onset statement from `100 steady / 200 periodic` to a softer `Re=100 weakly unsteady or near onset`.
