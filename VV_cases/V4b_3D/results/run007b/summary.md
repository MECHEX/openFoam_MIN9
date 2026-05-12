# V4b_3D run007b - constant-property Cp smoke test

## Purpose

`run007b` is a short constant-property thermal-model smoke test prepared after
the heat-balance check showed that the old constant-property baseline closes
with `Cv=718`, not with the open-flow `Cp=1005` energy balance.

The case keeps the accepted production geometry and mesh from `run004b`:

- `Lin = 2D`
- `Lout = 8D`
- corrected BL mesh
- `maxCo = 0.8`
- target `endTime = 2 s`

## Model Change

Only the thermal model is changed relative to `run004b`:

| Item | run004b | run007b |
|---|---|---|
| thermo | `eConst` | `hConst` |
| energy | `sensibleInternalEnergy` | `sensibleEnthalpy` |
| heat capacity | `Cv = 718` | `Cp = 1005` |
| equation of state | `Boussinesq` | `Boussinesq` |
| transport | constant `mu`, `Pr` | constant `mu`, `Pr` |

This should keep the same aerodynamic model while making the heat equation and
the outlet energy-balance post-processing consistent with `m_dot*Cp*dT`.

## Launch

Prepare:

```bash
bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/prepare_run007b_constCp_short.sh
```

Run after `run007a` is no longer using the 20 MPI ranks:

```bash
NPROCS=20 TAG=20260508_np20_constCp_short bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/_code/start_run007b_bg.sh
```

## Planned Comparison

Compare `run007b` against:

- `run004b`: old constant-property `Cv` baseline
- `run007a`: variable-property `rho(T), mu(T)` case

Primary checks:

- `Cd_mean`, `Cl_rms`, `St`
- outlet `m_dot*Cp*(T_out - T_in)`
- `wallHeatFlux` integrated over `hot_tube`, `hot_fin_z_min`, `hot_fin_z_max`
- agreement between wall heat input and air-side heat pickup
- `Nu_EB` with consistent `Cp` and `k = mu*Cp/Pr`
