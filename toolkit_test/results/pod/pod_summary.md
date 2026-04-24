# POD Results Summary

POD is computed independently for the synthetic velocity field and the synthetic wall heat-flux field.

For each dataset, the snapshot matrix uses row-major flattened `5x5` fields as columns:

```text
X = [x_1, x_2, x_3, x_4, x_5]
```

The temporal mean is subtracted before SVD:

```text
X' = X - mean(X)
X' = U Sigma V^T
```

Interpretation:

- `mean_field.csv` is the temporal mean field reshaped back to `5x5`.
- `spatial_mode_XX.csv` is one normalized spatial POD mode reshaped to `5x5`.
- `temporal_coefficients.csv` contains `Sigma V^T`, i.e. the amplitude of each mode in each snapshot.
- `singular_values.csv` contains modal energy fractions, computed from `sigma_i^2 / sum(sigma^2)`.

## Modal Energy

| dataset | active modes | mode | singular value | energy fraction | cumulative energy |
|---|---:|---:|---:|---:|---:|
| velocity | 4 | 1 | 2.37585 | 50.780% | 50.780% |
| velocity | 4 | 2 | 1.76435 | 28.004% | 78.784% |
| velocity | 4 | 3 | 1.47013 | 19.443% | 98.227% |
| velocity | 4 | 4 | 0.443996 | 1.773% | 100.000% |
| heat_flux | 4 | 1 | 5.39052 | 43.056% | 43.056% |
| heat_flux | 4 | 2 | 4.55741 | 30.776% | 73.832% |
| heat_flux | 4 | 3 | 4.09254 | 24.818% | 98.649% |
| heat_flux | 4 | 4 | 0.954721 | 1.351% | 100.000% |

## Output Folders

- `results/pod/velocity/`
- `results/pod/heat_flux/`
