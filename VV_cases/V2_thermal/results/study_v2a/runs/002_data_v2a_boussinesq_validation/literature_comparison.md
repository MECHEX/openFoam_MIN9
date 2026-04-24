# V2a literature comparison

## Current reference

- active comparison case: `Re10_long100s`
- source file with case-specific details:
  - `literature_comparison_Re10_long100s.md`
- note:
  - the earlier short `Re10` smoke-test is superseded for comparison purposes

## Summary table

| quantity | value |
|---|---:|
| time covered by `Nu(t)` | 47.0012 s |
| Nu tail mean (second half) | 6.8857 |
| Nu mean over last 10 s | 6.0189 |
| Nu_Lange | 1.8101 |
| Nu_Bharti | 1.8623 |
| error vs Lange | +280.41% |
| error vs Bharti | +269.74% |
| Cd tail mean | 2.5775 |
| Cl_rms tail | 2.616600 |
| transient spectral peak St | 0.0659 |

## Reading

- `Nu(t)` is now extracted with the accepted definition from Bharti and Lange:
  - area-averaged wall-normal temperature gradient on the cylinder patch
- the stopped run still remains far above the literature target
- this means the current `Re10_long100s` result is useful diagnostically, but is not yet a validated literature match
- `St` is reported only as a transient spectral descriptor
- `St` is not literature-comparable here because the reference thermal papers do not report shedding Strouhal and `Re = 10` should remain steady
