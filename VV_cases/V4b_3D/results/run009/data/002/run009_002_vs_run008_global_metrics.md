# V4b_3D run009 vs run008 global comparison

Window: `t = 2..10 s`.

Run definitions:

- `run008`: constant-property accepted production reference.
- `run009`: variable-property rerun, completed to `10 s`.

Important convention: `Cl` has a strong adjacent/second component near
`6.56 Hz`; the reported physical shedding `St` follows the same convention
as run008, using every-second `Cl` peak.

| metric | run008 | run009 | delta % |
|---|---:|---:|---:|
| `Cd_mean` | 3.36101 | 3.4739 | +3.359% |
| `Cl_mean` | 2.51417 | 2.52778 | +0.542% |
| `Cl_rms` | 0.176441 | 0.168789 | -4.337% |
| `f_shed_hz` | 3.27869 | 3.27869 | -0.000% |
| `f_cl_adjacent_hz` | 6.55738 | 6.55738 | -0.000% |
| `St` | 0.15572 | 0.15572 | -0.000% |
| `Nu_EB` | 7.77 | 10.3342 | +33.001% |
| `Nu_wall` | 7.81652 | 7.38417 | -5.531% |
| `Nu_tube_wall` | 8.43441 | 7.7347 | -8.296% |
| `Nu_fins_wall` | 7.63566 | 7.28156 | -4.637% |
| `Q_wall` | 1.48066 | 1.33701 | -9.702% |
| `Q_air` | 1.47028 | 1.86986 | +27.178% |
| `closure_pct` | 0.706213 | -28.497 | -4135.186% |

Interpretation:

- The variable-property run keeps the same shedding frequency/St within this
  metric resolution.
- Drag is higher in run009, consistent with the earlier variable-property
  smoke-run warning.
- Wall-side Nu is the cleaner heat-transfer comparison here; air-side Nu is
  reconstructed from decomposed outlet mass flux and should be treated as a
  diagnostic until a full heat-balance audit is repeated for run009.
