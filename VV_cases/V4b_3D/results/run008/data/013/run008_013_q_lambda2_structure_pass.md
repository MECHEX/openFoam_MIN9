# V4b_3D run008 Q/lambda2 structure pass

## Status

This layer selects representative full-field checkpoints and prepares the
OpenFOAM execution path for `Q`, `Lambda2`, and `vorticity` fields. Heavy
VTK exports are intentionally written outside Git.

## Selected checkpoints

| label | reason | target phase [deg] | selected t [s] | selected phase [deg] | error [deg] |
|---|---|---:|---:|---:|---:|
| `cl_zero_down` | lift zero-crossing, descending branch | 11.25 | 2.720 | 11.48 | +0.23 |
| `cl_zero_up` | lift zero-crossing, ascending branch | 78.75 | 7.440 | 78.67 | -0.08 |
| `nu_global_max` | maximum Nu_tube/Nu_fins/Nu_EB phase | 123.75 | 6.880 | 123.56 | -0.19 |
| `cl_min_qtube_max` | Cl minimum and Q_tube maximum phase | 236.25 | 3.840 | 241.08 | +4.83 |
| `cl_max` | Cl maximum phase | 281.25 | 2.160 | 281.39 | +0.14 |
| `qfins_qwall_max` | Q_fins and Q_wall maximum phase | 303.75 | 5.040 | 304.97 | +1.22 |

## OpenFOAM runner

- script: `scripts/run008_q_lambda2_013_wsl.sh`
- case: `/home/hexmachina/of_runs/V4b_3D_run008`
- heavy export directory: `/home/hexmachina/of_runs/V4b_3D_run008_q_lambda2_013`

Run from WSL or PowerShell/WSL:

```bash
bash /mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V4b_3D/results/run008/scripts/run008_q_lambda2_013_wsl.sh
```

## Export check

| label | time [s] | VTK files | VTK size [MB] |
|---|---:|---:|---:|
| `cl_zero_down` | 2.720 | 240 | 67.009 |
| `cl_zero_up` | 7.440 | 240 | 67.009 |
| `nu_global_max` | 6.880 | 240 | 67.009 |
| `cl_min_qtube_max` | 3.840 | 240 | 67.009 |
| `cl_max` | 2.160 | 240 | 67.009 |
| `qfins_qwall_max` | 5.040 | 240 | 67.009 |

## Cell-count structure metrics

These are first-pass proxies, not volume-integrated vortex measures. They
use all decomposed cells with equal weight.

| label | time [s] | Q>0 frac | Lambda2<0 frac | Q p99 | |omega| p99 |
|---|---:|---:|---:|---:|---:|
| `cl_zero_down` | 2.720 | 0.4726 | 0.4393 | 2.19e+04 | 993 |
| `cl_zero_up` | 7.440 | 0.4624 | 0.4224 | 2.2e+04 | 991 |
| `nu_global_max` | 6.880 | 0.4772 | 0.4175 | 2.22e+04 | 993 |
| `cl_min_qtube_max` | 3.840 | 0.4834 | 0.4230 | 2.22e+04 | 994 |
| `cl_max` | 2.160 | 0.4836 | 0.4359 | 2.22e+04 | 991 |
| `qfins_qwall_max` | 5.040 | 0.4748 | 0.4189 | 2.2e+04 | 992 |

## Interpretation guide

- `Q > 0` isolates rotation-dominated regions and should directly expose the
  shedding vortices behind the POD mode pair.
- `Lambda2 < 0` is the companion check for coherent vortex cores.
- The selected `qfins_qwall_max` and `nu_global_max` checkpoints are the key
  tests for whether the heat-transfer response is tied to wake sweeping or
  delayed fin-surface organization.
- The first pass should be inspected in ParaView before promoting this into a
  formal quantitative layer.
