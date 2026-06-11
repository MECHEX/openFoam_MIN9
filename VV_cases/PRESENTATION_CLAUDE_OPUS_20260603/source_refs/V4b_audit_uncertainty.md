# V4b_3D run008 audit and uncertainty

This is the foundation audit before any higher-order interpretation.

## Sampling Completeness

| Signal | expected dt [s] | samples | expected 0..10 | missing | median dt [s] | dt min/max [s] | regular |
|---|---:|---:|---:|---:|---:|---:|---|
| forceCoeffs | 0.00500 | 2001 | 2001 | 0 | 0.00500 | 0.00500/0.00500 | True |
| forces_raw | 0.00500 | 2001 | 2001 | 0 | 0.00500 | 0.00500/0.00500 | True |
| wallHeatFlux | 0.00500 | 2001 | 2001 | 0 | 0.00500 | 0.00500/0.00500 | True |
| hot_tube_surface | 0.00500 | 2001 | 2001 | 0 | 0.00500 | 0.00500/0.00500 | True |
| hot_fin_surface | 0.00500 | 2001 | 2001 | 0 | 0.00500 | 0.00500/0.00500 | True |
| midspan_z0 | 0.02000 | 501 | 501 | 0 | 0.02000 | 0.02000/0.02000 | True |
| outlet_T_phi | 0.08000 | 101 | 101 | 0 | 0.08000 | 0.08000/0.08000 | True |

## Window Metrics With Cycle-Block Bootstrap 95% Half-Widths

| Window | cycles | force n | outlet n | wall n | Cd | Cl_rms | St | Nu_EB | Nu_wall | closure [%] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2..10 | 25.98 | 1601 | 101 | 1601 | 3.361014 +/- 0.000772 | 0.176441 +/- 0.011097 | 0.154261 +/- 0.009574 | 7.770004 +/- 0.091573 | 7.816521 +/- 0.012286 | +0.706 +/- 1.075 |
| 3..10 | 22.98 | 1401 | 88 | 1401 | 3.360512 +/- 0.000724 | 0.169254 +/- 0.009951 | 0.155942 +/- 0.009449 | 7.806401 +/- 0.101372 | 7.819670 +/- 0.014647 | +0.211 +/- 1.039 |
| 4..10 | 19.98 | 1201 | 76 | 1201 | 3.359978 +/- 0.000480 | 0.161001 +/- 0.007714 | 0.158184 +/- 0.012287 | 7.789356 +/- 0.080865 | 7.813261 +/- 0.011372 | +0.416 +/- 0.998 |
| 2..6 | 11.99 | 801 | 51 | 801 | 3.362291 +/- 0.001254 | 0.193722 +/- 0.016443 | 0.142306 +/- 0.020021 | 7.768459 +/- 0.163091 | 7.823033 +/- 0.020754 | +0.946 +/- 1.677 |
| 6..10 | 12.98 | 801 | 51 | 801 | 3.359746 +/- 0.000524 | 0.157070 +/- 0.005738 | 0.154165 +/- 0.014602 | 7.785278 +/- 0.114744 | 7.810126 +/- 0.016480 | +0.457 +/- 1.261 |

## Interpretation

- The main `2..10 s` record contains more than 25 shedding cycles, so it exceeds the planned 20-cycle minimum.
- Force, wall-flux, tube-surface, fin-surface, and midspan sampling are complete on their intended grids.
- Outlet `T/phi` is reconstructed on the production checkpoint cadence and is sufficient for EB/Nu uncertainty at the global level.
- Window sensitivity should be used before making claims about small differences between runs.

## Figures

- `../../figures/001/run008_audit_sampling_completeness_cadence.png`
- `../../figures/001/run008_audit_effective_record_length.png`
- `../../figures/001/run008_audit_block_bootstrap_uncertainty.png`
- `../../figures/001/run008_audit_window_sensitivity.png`
