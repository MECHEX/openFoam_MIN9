# V4b_3D run005 - Lin=4D inlet-sensitivity check

## Purpose

`run005` is a controlled inlet-sensitivity check after the outlet-length study
closed at `Lout=8D`. The goal is to test whether moving the inlet farther
upstream changes the Re=200 shedding, drag/lift, or heat-transfer metrics.

## Setup Intent

| Parameter | Value |
|---|---:|
| Parent case | `/home/hexmachina/of_runs/V4b_3D_run004b` |
| Working case | `/home/hexmachina/of_runs/V4b_3D_run005` |
| Re | 200 |
| Lin/D | 4.0 |
| Lout/D | 8.0 |
| Lx | 171.71 mm |
| Tube surface refinement | level `(2 2)` |
| Boundary layers | `hot_tube`: 8 requested, `hot_fin_z_min/z_max`: 6 requested |
| First layer | 30 um |
| Wake refinement | level 1, `x=0..72 mm`, `y=+/-12 mm` |
| Isolated change vs `run004b` | inlet buffer from `2D` to `4D` |

The near-wake refinement, hot-wall boundary-layer request, outlet length, and
solver controls are intentionally kept matched to `run004b`. The extra length
is upstream only, so the comparison isolates inlet-boundary influence.

## Decision Criteria

Use `run004b` as the accepted `Lin=2D`, `Lout=8D` reference:

| Quantity | run004b reference |
|---|---:|
| Cd_mean | 3.361 |
| Cl_mean | 2.514 |
| Cl_rms | 0.184 |
| St | 0.1552 |
| T_out | 305.68 K |
| Nu_EB | 7.778 |

Recommended acceptance bands for the short check:

| Quantity | Acceptable change vs run004b | Meaning |
|---|---:|---|
| Cd_mean | <= 2-3% | inlet is not materially affecting drag |
| Cl_mean | <= 2-3% | buoyancy/lift offset not inlet-sensitive |
| Cl_rms | <= 5% | shedding amplitude remains comparable |
| St | <= 1-2% | shedding frequency is inlet-independent |
| Nu_EB | <= 2-3% | heat-transfer metric is not inlet-sensitive |

If `run005` stays inside these bands, keep `Lin=2D`, `Lout=8D` for production
and proceed to timestep sensitivity or the longer measurement-rich production
run. If `Nu`, `Cd`, or `St` shifts outside the bands, promote `Lin=4D` to the
candidate production domain or run one additional confirmation at longer time.

## Generation

Repository helper:

```bash
bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/prepare_run005_lin4_lout8_mesh.sh
```

Mesh:

```bash
cd /home/hexmachina/of_runs/V4b_3D_run005
./mesh.sh
```

Run later on 20 MPI ranks:

```bash
NPROCS=20 TAG=20260506_np20 bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run005_bg.sh
```

## Analysis Plan

Analyze the same late window as the outlet study, preferably `t = 3..6 s`.

Primary outputs:

- `Cd_mean`, `Cl_mean`, `Cl_rms`
- `f_shed`, `St`
- `T_out`, `Q_total`, `Nu_EB_LMTD`
- min/max ranges for `Cd`, `Cl`, and outlet temperature

Primary comparison:

- `run004b`: `Lin=2D`, `Lout=8D`
- `run005`: `Lin=4D`, `Lout=8D`

## Status

Plan and case-generation helpers prepared in the repository. The WSL case has
been generated:

```text
/home/hexmachina/of_runs/V4b_3D_run005
```

The mesh has been generated and the solver has been launched on 20 MPI ranks.

## Mesh Result

Normal `checkMesh`: `Mesh OK`.

| Quantity | Value |
|---|---:|
| points | 452,929 |
| faces | 1,295,084 |
| cells | 421,264 |
| max non-orthogonality | 62.84 deg |
| average non-orthogonality | 5.84 deg |
| max skewness | 3.319 |
| max aspect ratio | 33.64 |
| min volume | 3.39e-13 m3 |
| strict concave cells | 9,178 |

The strict `checkMesh -allTopology -allGeometry` reports the same concave-cell
count as `run004b/run004c` (`9,178`), so the mesh remains comparable to the
accepted outlet-sensitivity mesh family.

## Solver Result

Launched on 20 MPI ranks and completed cleanly to `t = 6 s`:

```bash
NPROCS=20 TAG=20260506_np20 bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run005_bg.sh
```

Active solver:

| Item | Value |
|---|---|
| Parent MPI PID | 738 |
| MPI ranks | 20 |
| PID file | `logs/solver.20260506_np20.pid` |
| Solver log | `logs/log.foamRun_parallel.20260506_np20` |
| Target endTime | 6 s |
| Final status | `End` / `Finalising parallel run` |
| Final checkpoint | `processor*/6` |
| Final ClockTime | 33,469 s |
| Final Co max | 0.788 |

Monitor:

```bash
pgrep -af foamRun
tail -n 120 /home/hexmachina/of_runs/V4b_3D_run005/logs/log.foamRun_parallel.20260506_np20
```

Stop safely:

```bash
kill "$(cat /home/hexmachina/of_runs/V4b_3D_run005/logs/solver.20260506_np20.pid)"
```

## Preliminary Force Results

Quick-look statistics from raw `forceCoeffs.dat`:

| Window | Cd_mean | Cl_mean | Cl_std/rms |
|---|---:|---:|---:|
| `t >= 2 s` | 3.360 | 2.523 | 0.195 |
| `t >= 3 s` | 3.359 | 2.518 | 0.185 |
| `t >= 4 s` | 3.358 | 2.518 | 0.168 |

Against the `run004b` `Lin=2D`, `Lout=8D` reference over `t >= 3 s`
(`Cd_mean = 3.361`, `Cl_mean = 2.514`, `Cl_rms = 0.184`), the `Lin=4D`
force response is essentially unchanged:

- `Cd_mean`: about `-0.07%`
- `Cl_mean`: about `+0.16%`
- `Cl_rms`: about `+0.3%`

This is a preliminary force-only result. The final inlet-sensitivity decision
still needs matched shedding-frequency extraction and EB+LMTD `Nu` from the
reconstructed outlet fields.

## Final Inlet-Sensitivity Result

Full comparison generated by:

```bash
python3 VV_cases/V4b_3D/results/run005/analyse_inlet_sensitivity_run004b_vs_run005.py
```

Outputs:

- `run004b_vs_run005_inlet_compare.csv`
- `run004b_vs_run005_inlet_compare.json`
- `run004b_vs_run005_inlet_compare.md`
- `figures/run004b_vs_run005_inlet_sensitivity.png`

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

Conclusion: extending the inlet from `2D` to `4D` does not materially change
the Re=200 force, shedding, or EB+LMTD heat-transfer metrics. The inlet
sensitivity question is closed for the current medium BL mesh family:
`Lin=2D`, `Lout=8D` remains defensible for the next production or
timestep-sensitivity run.
