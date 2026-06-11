# V4b run011 thermal GCI analysis

Date: 2026-06-05

Window: `2.0..3.0 s` for all three grids. Outlet `T/phi` was reconstructed for the new coarse and fine cases.

## Thermal Summary

| Case | Cells | Nu_EB mean | Nu_wall mean | closure ratio [%] | Q_air mean [W] | Q_wall mean [W] | T_out mean [K] |
|---|---:|---:|---:|---:|---:|---:|---:|
| coarse | 196938 | 7.7197558 | 7.9906023 | 3.57988 | 1.4628097 | 1.5151766 | 305.58369 |
| medium_run008 | 407440 | 7.4888198 | 7.795708 | 4.19941 | 1.4244866 | 1.4843067 | 305.25592 |
| fine | 829761 | 7.4172415 | 7.7402564 | 4.49908 | 1.4120948 | 1.4756261 | 305.15074 |

## Thermal GCI

| Metric | Source | p | GCI fine/medium [%] | GCI medium/coarse [%] | Status |
|---|---|---:|---:|---:|---|
| Nu_EB | mean | 4.7853 | 0.57179 | 1.7611 | monotonic |
| Nu_wall | mean | 5.1409 | 0.37576 | 1.2622 | monotonic |
| Q_wall | mean | 5.1897 | 0.30354 | 1.0328 | monotonic |
| T_out | mean | 4.6413 | 0.021485 | 0.064547 | monotonic |
| closure_ratio_of_means_pct | mean | 2.9347 | 8.2825 | 17.793 | monotonic |
| Nu_EB | t3 | 3.4944 | 1.2755 | 2.8827 | monotonic |
| Nu_wall | t3 | 4.8438 | 0.44881 | 1.4043 | monotonic |
| Q_wall | t3 | 5.1738 | 0.30501 | 1.0339 | monotonic |
| T_out | t3 | 3.4215 | 0.047293 | 0.10638 | monotonic |
| closure_ratio_of_means_pct | t3 | 2.9347 | 8.2825 | 17.793 | monotonic |

## Interpretation

- `Nu_EB` and `Nu_wall` both show monotonic grid trends in the common `2-3 s` window.
- Medium-grid thermal values are within about 1% of the fine grid for both independent heat-transfer definitions.
- `closure_ratio_of_means_pct` is monotonic in this short common window, but its absolute value is larger than the full production-window closure because `2-3 s` still contains outlet transport lag. Treat it as an internal consistency diagnostic, not as the primary grid-convergence observable.
- The common `2-3 s` window is shorter than the full production `run008` window (`2-10 s`), but it is the valid overlap for the new coarse/fine GCI runs. The full `run008` production window remains the reference for final closure reporting.

