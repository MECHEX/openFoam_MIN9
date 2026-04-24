# V2A article comparison and next simulations

## Reference ranges

| source | usable quantities here | Re range | max Re | notes |
|---|---|---:|---:|---|
| Bharti et al. (2007) | Nu for CWT/UHF steady cross-flow | 10-45 | 45 | no useful Cd, Cl, or St curve for our comparison |
| Lange et al. (1998) | Nu, St, onset, digitized Cd trend | 1e-4-200 | 200 | Cl is not given as a usable Cl(Re) curve |
| Present work, run 004 | Nu, Cd, Cl tail diagnostics; St only once shedding exists | 10-200 so far | 200 | includes cases above Lange Re_c = 45.9 |

## Nu correlation sign check

The Lange Nu fit used here is the PDF-checked version already implemented in `V2AStudy.py`:

`Nu = 0.082 Re^0.5 + 0.734 Re^x`, with `x = 0.05 + 0.226 Re^0.085`.

The alternative `x = -0.05 + ...` would give the lower values listed in the scratch notes, but it does not match the local Lange PDF extraction.

## Recommended next simulations

| priority | case | role | suggested endTime | suggested writeInterval | main metrics |
|---:|---|---|---:|---:|---|
| 1 | Re45_ogrid | closes Bharti max-Re point and sits just below Lange onset | 120 s | 0.5 s | Nu, Cd, bounded T, no St expected |
| 2 | Re60_ogrid | first clean shedding case above Re_c | 80 s | 0.1 s | time-mean Nu, Cd, St from Cl FFT |
| 3 | Re100_ogrid | mid-range Lange unsteady validation | 60 s | 0.05 s | time-mean Nu, Cd, St |
| 4 | Re200_ogrid | maximum Lange-range check | 40 s | 0.025 s | time-mean Nu, Cd, St; mesh sensitivity likely needed |

If Re200 differs by more than about 5% in Nu or St, repeat Re100/Re200 on a refined O-grid before using the high-Re points in the article.
