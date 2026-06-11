# V4b run011 GCI analysis

Date: 2026-06-05

## Mesh levels

| Level | Cells | Role |
|---|---:|---|
| coarse | 196938 | forceCoeffs comparison, common 2-3 s window |
| medium_run008 | 407440 | forceCoeffs comparison, common 2-3 s window |
| fine | 829761 | forceCoeffs comparison, common 2-3 s window |

## Force coefficient summary

| Case | Cells | Cd(t=3) | Cl(t=3) | Cm(t=3) | Cd mean 2-3s | Cl mean 2-3s | Cl RMS 2-3s |
|---|---:|---:|---:|---:|---:|---:|---:|
| coarse | 196938 | 3.325969 | 2.3201294 | 0.010300663 | 3.337671 | 2.5319474 | 2.5411913 |
| medium_run008 | 407440 | 3.3521755 | 2.3223018 | 0.010444626 | 3.3644667 | 2.5390775 | 2.5484787 |
| fine | 829761 | 3.3656233 | 2.3327514 | 0.010458878 | 3.3779463 | 2.5399038 | 2.549094 |

## GCI results

| Metric | Source | p | GCI fine/medium [%] | GCI medium/coarse [%] | Status |
|---|---|---:|---:|---:|---|
| Cd | t3 | 2.6888 | 0.56014 | 1.0638 | monotonic |
| Cl | t3 | 6.8128 | 0.13898 | 0.027762 | monotonic |
| Cm | t3 | 9.5199 | 0.019912 | 0.1905 | monotonic |
| Cd | mean_2_3 | 2.7715 | 0.53685 | 1.0398 | monotonic |
| Cl | mean_2_3 | 8.8673 | 0.0056599 | 0.046339 | monotonic |
| Cm | mean_2_3 | n/a | n/a | n/a | non-monotonic |

## Interpretation

- `Cd` shows monotonic convergence for both the instantaneous `t=3 s` value and the common `2-3 s` average.
- `Cl` is very close across the three grids; GCI is small for the `2-3 s` mean, but the apparent order is high because the medium-fine difference is much smaller than the coarse-medium difference.
- `Cm` should be treated as a secondary, small-amplitude diagnostic. The `2-3 s` mean is non-monotonic, so a formal GCI is not reported for that averaged quantity.
- This is a production-geometry grid sensitivity/GCI check for force coefficients, not an external experimental validation.

## Generated figures

- `run011_gci_Cd_timeseries_2_3s.png`
- `run011_gci_Cl_timeseries_2_3s.png`
- `run011_gci_Cm_timeseries_2_3s.png`
- `run011_gci_grid_trend_t3.png`
- `run011_gci_grid_trend_mean_2_3.png`
