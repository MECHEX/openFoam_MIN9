# V4b_3D outlet sensitivity: 5D vs 8D vs 16D

`run004b` and `run004c` use the matched window `t = 3..6 s`; `run003` uses archived summary values.

| Run | Lout/D | Cd_mean | Cl_mean | Cl_rms | f_shed | St | T_out | Nu_EB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| run003 | 5 | 3.161 | 2.520 | 0.187 | 3.125 | 0.1484 | 305.26 | 7.476 |
| run004b | 8 | 3.361 | 2.514 | 0.184 | 3.267 | 0.1552 | 305.68 +/- 0.68 | 7.778 +/- 0.463 |
| run004c | 16 | 3.361 | 2.511 | 0.182 | 3.254 | 0.1546 | 305.72 +/- 0.13 | 7.803 +/- 0.089 |

## Key Differences

| Comparison | Cd | St | Nu_EB |
|---|---:|---:|---:|
| 8D vs 5D | +6.34% | +4.56% | +4.04% |
| 16D vs 5D | +6.33% | +4.15% | +4.37% |
| 16D vs 8D | -0.01% | -0.40% | +0.32% |

## Conclusion

The `16D` result is essentially identical to `8D` for the force metrics and very close for EB+LMTD heat transfer. This closes the main outlet-independence question: `8D` is sufficient for production use, while `5D` is qualitatively correct but mildly outlet-sensitive in drag and heat transfer.
