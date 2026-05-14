# V4b_3D run009

Status: removed from WSL working storage.

Run009 was a variable-property diagnostic/movie rerun of run008, but it used:

```text
eConst + sensibleInternalEnergy
Cv = 718 J/(kg K)
incompressiblePerfectGas + Sutherland
```

This was the wrong heat-capacity choice for the intended Cp-consistent
comparison with run008. The heavy WSL case directory was deleted to free space:

```text
/home/hexmachina/of_runs/V4b_3D_run009_varprops_movie
```

Deletion reason:

- `run009` was dynamically useful, but not the intended Cp-capacity
  variable-property production candidate.
- The apparent wall-air heat-balance mismatch came from comparing a Cv-based
  internal-energy solve against a Cp-based outlet diagnostic.
- The replacement run is `run010_varprops_cp`, with `Cv = 1005` in the same
  stable `eConst/sensibleInternalEnergy` formulation used for the run008
  Cp-capacity logic.

Retained files under `results/run009` are historical notes/scripts/tables only;
the solver case itself is intentionally gone.
