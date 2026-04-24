# Re10_long100s literature comparison

## Scope

- case: `Re10_long100s` stopped run post-processing only
- literature for `Nu`: Lange (1998) and Bharti (2007)
- literature for `St`: not reported in these thermal papers; at `Re = 10` the expected regime is steady, so any spectral peak from `Cl` is treated as transient only

## Summary table

| quantity | value |
|---|---:|
| time covered by `Nu(t)` | 299.0002 s |
| Nu tail mean (second half) | 7.1756 |
| Nu mean over last 10 s | 7.0873 |
| Nu_Lange | 1.8101 |
| Nu_Bharti | 1.8623 |
| error vs Lange | +296.42% |
| error vs Bharti | +285.31% |
| Cd tail mean | 2.9501 |
| Cl_rms tail | 2.769084 |
| transient spectral peak St | 0.0497 |

## Interpretation

- `Nu` remains far above the literature target (`7.1756` vs `1.8623` from Bharti and `1.8101` from Lange), so this stopped run does not yet reproduce the expected steady thermal solution.
- `Nu(t)` therefore acts here as a diagnostic curve, not as a validated benchmark result.
- The extracted spectral `St` is reported only as a transient signal descriptor. It is not physically comparable to literature for `Re = 10`, where periodic shedding is not expected.
