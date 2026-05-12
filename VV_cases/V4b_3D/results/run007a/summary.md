# V4b_3D run007a - variable-property air smoke test

## Purpose

`run007a` checks how much the accepted production geometry changes when the air
model is upgraded from Boussinesq with constant transport properties to a
temperature-dependent `incompressiblePerfectGas`/Sutherland model.

This is intentionally a short smoke test first (`t = 2 s`). If startup,
Courant behavior, force coefficients, and thermal metrics look sane, the same
case can be extended to the production comparison window (`t = 6 s`).

## Setup Intent

| Parameter | Value |
|---|---:|
| Parent case | `/home/hexmachina/of_runs/V4b_3D_run004b` |
| Working case | `/home/hexmachina/of_runs/V4b_3D_run007a` |
| Geometry | accepted `Lin=2D`, `Lout=8D` |
| Mesh | copied from `run004b`, 407,440 cells expected |
| Baseline model | Boussinesq + constant `mu`, `Pr` |
| New model | `incompressiblePerfectGas` + `sutherland` transport |
| Pressure initialisation | gauge-style `p = 0 Pa`, `p_rgh = 0 Pa`; density uses `pRef = 101325 Pa` |
| Sutherland constants | `As = 1.458e-06`, `Ts = 110.4 K` |
| Cv | 718 J/(kg K) |
| maxCo | 0.8 |
| endTime | 2 s |
| planned MPI ranks | 20 |

## Interpretation Guardrail

This run is a physics sensitivity check, not a new geometry or mesh check. A
small difference versus `run004b` would support using the cheaper Boussinesq
constant-property model for screening studies. A larger difference, especially
in `Nu`, `T_out`, or `Cd`, would mean the final production comparison should be
done with variable properties.

Because this uses `incompressiblePerfectGas`, density is linked to temperature
through `rho = pRef/(R*T)`, while dynamic pressure does not drive compressible
density waves. That is a better low-Mach physics check for this case than full
`perfectGas`.

## Status

Plan and helper scripts prepared in the repository. The WSL case has been
generated, checked, and launched on 20 MPI ranks.

Active WSL case:

```text
/home/hexmachina/of_runs/V4b_3D_run007a
```

## Mesh Check

Normal `checkMesh`: `Mesh OK`.

| Quantity | Value |
|---|---:|
| cells | 407,440 |
| max non-orthogonality | 62.84 deg |
| average non-orthogonality | 5.93 deg |
| max skewness | 3.319 |
| max aspect ratio | 33.64 |

## Solver Launch

Active launch:

```bash
NPROCS=20 TAG=20260508_np20_varProps_incompPG_r4 bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run007a_bg.sh
```

| Item | Value |
|---|---|
| Parent MPI PID | 754 |
| MPI ranks | 20 |
| Solver log | `logs/log.foamRun_parallel.20260508_np20_varProps_incompPG_r4` |
| Target endTime | 2 s |
| Initial status | running; entered time loop |
| Initial Co max | adjusted to about 0.8 |
| Early progress check | `t = 0.01148 s` at `ClockTime = 90 s` |

## Short-Run Result

`run007a` completed cleanly to `t = 2 s`.

| Item | Value |
|---|---|
| Final status | `End` / `Finalising parallel run` |
| Final checkpoint | `processor*/2` |
| Final ClockTime | 9,932 s |
| Final Co max | about 0.784 |

Preliminary force comparison against matched early windows from `run004b`:

| Window | Run | Cd_mean | Cl_mean | Cl_rms | f_shed | St |
|---|---|---:|---:|---:|---:|---:|
| 0.5..2.0 s | run004b | 3.361209 | 2.510763 | 0.176698 | 3.2538 | 0.15453 |
| 0.5..2.0 s | run007a | 3.473619 | 2.522958 | 0.178979 | 3.2441 | 0.15407 |
| 1.0..2.0 s | run004b | 3.362182 | 2.507610 | 0.202467 | 3.2299 | 0.15340 |
| 1.0..2.0 s | run007a | 3.474742 | 2.518752 | 0.202020 | 3.2317 | 0.15348 |
| 1.5..2.0 s | run004b | 3.364359 | 2.527390 | 0.219670 | 3.2345 | 0.15361 |
| 1.5..2.0 s | run007a | 3.475999 | 2.531925 | 0.211541 | 3.2190 | 0.15288 |

Early interpretation: the shedding regime is essentially unchanged, but the
variable-property model raises `Cd` by about `3.3%` in the matched short window.
Wake temperature probes are also higher in `run007a`, so the next step is a
proper reconstructed-field energy-balance/Nu comparison before deciding whether
to extend the variable-property case to `t = 6 s`.

## Short Nu / Thermal Comparison

Fields were reconstructed for `t = 0.5..2 s` and compared with the same early
window from `run004b`.

Generated outputs:

- `run004b_vs_run007a_varprops_short_compare.csv`
- `run004b_vs_run007a_varprops_short_compare.json`
- `run004b_vs_run007a_varprops_short_compare.md`

Primary matched window:

| Run | model | window | Cd_mean | Cl_rms | St | T_out | Q_total | Nu_EB |
|---|---|---|---:|---:|---:|---:|---:|---:|
| run004b | Boussinesq_const | 0.5..2.0 s | 3.361209 | 0.176698 | 0.15453 | 305.615 +/- 0.974 | 1.4644 +/- 0.0984 | 7.7331 +/- 0.6558 |
| run007a | incompressiblePerfectGas_sutherland | 0.5..2.0 s | 3.473619 | 0.178979 | 0.15407 | 308.934 +/- 0.990 | 1.8534 +/- 0.1107 | 10.2249 +/- 0.7272 |

Differences for `run007a` versus matched `run004b`:

| Quantity | Difference |
|---|---:|
| Cd_mean | +3.34% |
| Cl_rms | +1.29% |
| St | -0.30% |
| T_out | +3.319 K |
| Q_total | +26.57% |
| Nu_EB | +32.22% |

Interpretation: the short-window vortex-shedding regime remains nearly the
same, but the thermal response is not a small correction. Because the analysis
window is still early/transient, this should be treated as a strong indication
to run the variable-property model to `t = 6 s`, not as the final production
Nu delta.

## Extension To 6 s

After the short-window Nu result showed a large thermal sensitivity, `run007a`
was continued from the decomposed `t = 2 s` checkpoint toward `t = 6 s`.

Continuation helper:

```bash
NPROCS=20 END_TIME=6 TAG=20260508_np20_varProps_to6 bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/continue_run007a_bg.sh
```

| Item | Value |
|---|---|
| Parent MPI PID | 797 |
| MPI ranks | 20 |
| Start mode | `latestTime` from existing `processor*/2` |
| Target endTime | 6 s |
| Solver log | `logs/log.foamRun_parallel.20260508_np20_varProps_to6` |
| Initial continuation status | running; confirmed `Time = 2.0007 s` |
| Initial continuation Co max | about 0.799 |

Monitor:

```bash
pgrep -af foamRun
tail -n 120 /home/hexmachina/of_runs/V4b_3D_run007a/logs/log.foamRun_parallel.20260508_np20_varProps_to6
```

Stop safely:

```bash
kill "$(cat /home/hexmachina/of_runs/V4b_3D_run007a/logs/solver.20260508_np20_varProps_to6.pid)"
```

Estimated remaining wall time from the short run cost is roughly `5-6 h` for
the continuation from `t = 2 s` to `t = 6 s`.

Monitor:

```bash
pgrep -af foamRun
tail -n 120 /home/hexmachina/of_runs/V4b_3D_run007a/logs/log.foamRun_parallel.20260508_np20_varProps_incompPG_r4
```

Stop safely:

```bash
kill "$(cat /home/hexmachina/of_runs/V4b_3D_run007a/logs/solver.20260508_np20_varProps_incompPG_r4.pid)"
```

## Startup Notes

The first attempted variant used `sensibleEnthalpy/h`. OpenFOAM accepted the
thermophysical package, but the inherited numerics lacked `div(phi,h)` and an
`h` solver entry. To keep the comparison closer to `run004b`, the active setup
uses `sensibleInternalEnergy/e`.

A second attempted variant used full `perfectGas + sutherland`. It entered the
first time step, then hit a floating-point exception in the thermophysical
correction. The active low-Mach setup is therefore
`incompressiblePerfectGas + sutherland`.
