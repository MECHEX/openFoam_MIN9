# V4b_3D run004b - BL Lout=8D outlet-sensitivity mesh

## Status

Mesh generated, decomposed, and solver completed on 20 MPI ranks to `t = 6 s`.

Active WSL case:

```text
/home/hexmachina/of_runs/V4b_3D_run004b
```

Active solver log:

```text
/home/hexmachina/of_runs/V4b_3D_run004b/logs/log.foamRun_parallel.20260505_np20
```

Final solver status:

- clean termination at `Time = 6s`
- log ends with `End` and `Finalising parallel run`
- final checkpoint written under `processor*/6`
- final `ClockTime = 30720 s` on 20 MPI ranks

## Purpose

`run004b` is the controlled replacement for the over-refined `run004` attempt.
The goal is to test the longer outlet (`Lout=8D`) against `run003` with a mesh
that keeps the same basic refinement family and boundary-layer intent instead
of changing to a much heavier volume-refined mesh.

## Mesh Setup

| Parameter | Value |
|---|---:|
| Parent diagnostic case | `/home/hexmachina/of_runs/V4b_3D_run004` |
| Working case | `/home/hexmachina/of_runs/V4b_3D_run004b` |
| Re | 200 |
| Lin/D | 2.0 |
| Lout/D | 8.0 |
| Lx | 147.71 mm |
| Base mesh | 85,248 cells |
| Final mesh | 407,440 cells |
| Tube surface refinement | level `(2 2)` |
| Boundary layers | `hot_tube`: 8 requested, `hot_fin_z_min/z_max`: 6 requested |
| Layer result | tube avg 7.19 layers, fins avg 3.8 layers |
| Wake refinement | level 1, `x=0..72 mm`, `y=+/-12 mm` |
| Removed vs run004 | large `nearCylinder` level-2 volume box |
| addLayers | true |

## Mesh Quality

Normal `checkMesh` result: `Mesh OK`.

Key values:

| Metric | Value |
|---|---:|
| points | 437,881 |
| faces | 1,252,412 |
| cells | 407,440 |
| max non-orthogonality | 62.84 deg |
| average non-orthogonality | 5.93 deg |
| max skewness | 3.319 |
| max aspect ratio | 33.64 |
| min cell determinant | 0.00120 |

Layer addition from `snappyHexMesh`:

| Patch | Requested layers | Average layers | Overall thickness |
|---|---:|---:|---:|
| hot_tube | 8 | 7.19 | 0.000401 m / 81.1% |
| hot_fin_z_min | 6 | 3.8 | 0.000228 m / 76.1% |
| hot_fin_z_max | 6 | 3.8 | 0.000228 m / 76.1% |

The stricter `checkMesh -allTopology -allGeometry` reports 9,178 concave cells,
which is comparable to the archived accepted `run001/run003` count of 9,524.

## Comparison

| Run | Lout/D | Mesh intent | Cells | Notes |
|---|---:|---|---:|---|
| run001 | 5 | medium/lvl-2 | 337,184 | accepted Re=100 baseline |
| run003 | 5 | inherited run001 medium/lvl-2 | 337,184 | accepted Re=200 reference |
| run004 | 8 | accidentally broad level-2 volume refinement | 1,783,116 | too expensive for controlled outlet test |
| run004b | 8 | level-2 surface + BL + short level-1 wake | 407,440 | current controlled outlet-sensitivity mesh |

## Next Step

Analyze the completed `Lout=8D` result against `run003` (`Lout=5D`) before
deciding whether a longer `Lout=16D` case is necessary.

## Preliminary Force Results

Final `forceCoeffs` quick-look statistics:

| Window | Cd_mean | Cl_mean | Cl_std/rms |
|---|---:|---:|---:|
| `t >= 2 s` | 3.362 | 2.519 | 0.194 |
| `t >= 3 s` | 3.361 | 2.514 | 0.184 |
| `t >= 4 s` | 3.360 | 2.514 | 0.168 |

Peak picking on `Cl` shows a strong adjacent-peak component near `6.5 Hz`.
Interpreting every second peak as the fundamental shedding cycle gives:

| Window | f_shed | St |
|---|---:|---:|
| `t >= 1 s` | 3.252 Hz | 0.1544 |
| `t >= 2 s` | 3.258 Hz | 0.1547 |
| `t >= 3 s` | 3.267 Hz | 0.1552 |

Compared with `run003` (`Cd_mean = 3.161`, `Cl_mean = 2.52`,
`Cl_rms = 0.187`, `St = 0.1484`), `run004b` is qualitatively similar:
same periodic regime, nearly unchanged lift offset, comparable lift oscillation,
and slightly higher shedding frequency. The main remaining quantitative
difference is the approximately 6% higher drag coefficient.

## Analysis Plan: run003 vs run004b

Goal: determine whether extending the outlet from `Lout=5D` to `Lout=8D`
changes the scientific conclusions for the Re=200 V4b_3D case.

Primary comparison:

| Quantity | Why it matters | Planned window |
|---|---|---|
| `Cd_mean` | Checks outlet/back-pressure sensitivity in force balance | `t = 2..6 s`, plus `3..6 s` |
| `Cl_mean` | Checks buoyancy lift offset and mean asymmetry | `t = 2..6 s`, plus `3..6 s` |
| `Cl_rms` | Checks shedding amplitude | `t = 2..6 s`, plus `3..6 s` |
| `f_shed`, `St` | Checks vortex-shedding frequency | after transient rejection |
| `Cd/Cl` time traces | Confirms periodic stationarity and transient length | full `0..6 s` with highlighted windows |

Secondary comparison if available from fields/post-processing:

| Quantity | Purpose |
|---|---|
| wake probes `U/T/p` | Compare near-wake signal phase and dominant frequencies |
| outlet temperature `T_out` | Check heat-transfer sensitivity to outlet length |
| energy-balance `Nu_EB` | Check whether thermal conclusion changes |
| final pressure/velocity fields | Inspect whether outlet still affects recirculation/wake |

Decision criteria:

- If `Cl_mean`, `Cl_rms`, and `St` remain close and only `Cd` shifts mildly,
  report `Lout=8D` as confirming the same flow regime, with drag retaining
  measurable outlet sensitivity.
- If `Cd` remains about 5-7% higher but `St/Cl_rms` are stable, recommend one
  short `Lout=16D` confirmation case only for drag/outlet independence.
- If heat-transfer metrics differ materially after recomputation, treat outlet
  length as a thermal-domain sensitivity and postpone 16D until the energy
  balance extraction is checked.

Immediate tasks:

1. Recompute `run003` force statistics using the same windows used for
   `run004b`, not only the archived summary values.
2. Produce a small comparison table for `run003` vs `run004b` with percent
   differences.
3. Plot `Cd(t)` and `Cl(t)` for both runs with matched time windows.
4. Estimate `f_shed/St` with the same method for both runs.
5. Check whether `T_out/Nu_EB` can be extracted consistently from available
   fields or whether reconstruction/post-processing is needed first.
6. Write a short conclusion: "outlet extension changes X, does not change Y".

## Final run003 vs run004b comparison

This section is generated by `analyse_run003_vs_run004b.py`.

Data status:

- `run004b`: raw `forceCoeffs.dat`, completed to `t = 6 s`.
- `run003`: archived summary baseline; raw force file not found in the active WSL/repo checkout.

| Run/window | Cd_mean | Cl_mean | Cl_rms/std | f_shed | St | Cd diff vs run003 | St diff vs run003 |
|---|---:|---:|---:|---:|---:|---:|---:|
| run003 archived reported window | 3.161 | 2.520 | 0.187 | 3.125 | 0.1484 | N/A | N/A |
| run004b t >= 2 s | 3.362 | 2.519 | 0.194 | 3.258 | 0.1547 | +6.37% | +4.27% |
| run004b t >= 3 s | 3.361 | 2.514 | 0.184 | 3.267 | 0.1552 | +6.34% | +4.56% |
| run004b t >= 4 s | 3.360 | 2.514 | 0.168 | 3.283 | 0.1559 | +6.31% | +5.07% |

Recommended comparison window: `t >= 3 s`.

Interpretation:

- The flow regime remains periodic; `run004b` gives `St = 0.1552` versus `run003` `St = 0.1484`.
- The mean lift offset is essentially unchanged: `Cl_mean = 2.514` versus `run003` `2.520`.
- The shedding amplitude is comparable: `Cl_rms/std = 0.184` versus `run003` `0.187`.
- Drag remains measurably higher in the `Lout=8D` case: `Cd_mean = 3.361`, `+6.34%` versus `run003`.

Decision:

Do not start `Lout=16D` as a broad new campaign yet. The `8D` outlet confirms the same qualitative shedding regime, but the persistent drag offset is large enough that a short `16D` drag/outlet-independence check is scientifically justified if drag accuracy is important for the final claim. The thermal comparison below shows heat transfer also has a smaller but nonzero outlet-length sensitivity.

Generated outputs:

- `run003_vs_run004b_force_compare.csv`
- `run003_vs_run004b_force_compare.json`
- `run003_vs_run004b_thermal_compare.csv`
- `run003_vs_run004b_thermal_compare.json`
- `figures/run003_vs_run004b_force_traces.png`
- `figures/run004b_cl_psd.png`

## Thermal EB+LMTD comparison

Thermal metrics are computed from reconstructed `run004b` outlet patch values and averaged over the same recommended late window.

| Quantity | run003 archived | run004b t = 3..6 s | Difference |
|---|---:|---:|---:|
| T_out area-average | 305.26 K | 305.68 +/- 0.68 K | +0.42 K |
| T_out mass-weighted check | N/A | 305.75 K | N/A |
| Q_total | 1.417 W | 1.472 +/- 0.075 W | +3.91% |
| LMTD | 43.665 K | 43.432 K | N/A |
| Nu_EB_LMTD | 7.476 | 7.778 +/- 0.463 | +4.04% |

Constants used for `run004b`: `Cp = 1005.0 J/(kg K)`, `k = 0.02575 W/(m K)`, `A_hot_total = 0.002032 m2`, `D = 0.012 m`.

Thermal interpretation: the `Lout=8D` case gives a slightly higher outlet temperature and EB+LMTD Nusselt number than the archived `run003` value. The change is smaller than the drag shift but not zero, so heat-transfer metrics should be included in the `8D` vs possible `16D` decision.

## Launch Procedure

Use the repo helper script from WSL:

```bash
NPROCS=20 TAG=20260505_np20 bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run004b_bg.sh
```

What the script does:

- sources OpenFOAM 13 before enabling strict shell mode
- updates `system/decomposeParDict` to match `NPROCS`
- runs `decomposePar -force`
- starts `foamRun -solver fluid -parallel` with `setsid mpirun --oversubscribe`
- writes PID to `logs/solver.<TAG>.pid`
- writes solver log to `logs/log.foamRun_parallel.<TAG>`

Check whether it is running:

```bash
pgrep -af foamRun
pgrep -af mpirun
tail -n 120 /home/hexmachina/of_runs/V4b_3D_run004b/logs/log.foamRun_parallel.20260505_np20
```

Stop safely through the parent MPI process:

```bash
kill "$(cat /home/hexmachina/of_runs/V4b_3D_run004b/logs/solver.20260505_np20.pid)"
```
