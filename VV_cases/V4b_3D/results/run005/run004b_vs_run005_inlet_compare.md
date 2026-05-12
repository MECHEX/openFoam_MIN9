# V4b_3D inlet sensitivity: Lin=2D vs Lin=4D

Both cases use `Lout=8D` and the matched window `t = 3..6 s`.

| Run | Lin/D | Cd_mean | Cl_mean | Cl_rms | f_shed | St | T_out | Nu_EB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| run004b | 2 | 3.361 | 2.514 | 0.184 | 3.267 | 0.1552 | 305.682 +/- 0.676 | 7.778 +/- 0.463 |
| run005 | 4 | 3.359 | 2.518 | 0.185 | 3.268 | 0.1552 | 305.680 +/- 0.653 | 7.776 +/- 0.447 |

## Differences

| Comparison | Cd | Cl_rms | St | T_out | Nu_EB |
|---|---:|---:|---:|---:|---:|
| Lin=4D vs Lin=2D | -0.07% | +0.30% | +0.02% | -0.002 K | -0.03% |

## Conclusion

The `Lin=4D` inlet check is essentially identical to the accepted `Lin=2D`, `Lout=8D` reference for forces, shedding frequency, and EB+LMTD heat transfer. This closes the inlet-sensitivity question for the current medium BL mesh family: `Lin=2D`, `Lout=8D` remains defensible for the next production or timestep-sensitivity run.
