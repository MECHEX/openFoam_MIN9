# EPOD Results Summary

EPOD is computed between the synchronized synthetic velocity and wall heat-flux datasets.

Here EPOD means: take the temporal coefficients from the POD of one field and use them to reconstruct correlated modes of the other field.

For source field `X` and target field `Y`:

```text
X' = U Sigma V^T
A = Sigma V^T
Psi = Y' A^T (A A^T)^(-1)
Y'_hat = Psi A
```

`Psi` contains the extended spatial modes of the target field associated with the source-field temporal POD coefficients.

## Reconstruction Metrics

| direction | source | target | modes used | relative error | captured target energy |
|---|---|---|---:|---:|---:|
| velocity_to_heat_flux | velocity | heat_flux | 1 | 0.763419 | 41.719% |
| velocity_to_heat_flux | velocity | heat_flux | 2 | 0.571094 | 67.385% |
| velocity_to_heat_flux | velocity | heat_flux | 3 | 0.167761 | 97.186% |
| velocity_to_heat_flux | velocity | heat_flux | 4 | 9.34725e-16 | 100.000% |
| heat_flux_to_velocity | heat_flux | velocity | 1 | 0.723709 | 47.625% |
| heat_flux_to_velocity | heat_flux | velocity | 2 | 0.525377 | 72.398% |
| heat_flux_to_velocity | heat_flux | velocity | 3 | 0.180347 | 96.747% |
| heat_flux_to_velocity | heat_flux | velocity | 4 | 6.50062e-16 | 100.000% |

## Output Folders

- `results/epod/velocity_to_heat_flux/`
- `results/epod/heat_flux_to_velocity/`
