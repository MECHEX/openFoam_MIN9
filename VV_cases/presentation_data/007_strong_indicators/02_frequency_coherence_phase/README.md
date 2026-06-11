# 02_frequency_coherence_phase

This stage tests whether the unsteady aerodynamic/shedding signal `Cl(t)` is phase-related to local heat-transfer response.

Inputs:

- `Nu_3D(x,t)` from `00_fullNu3D_xt`, computed from full hot-surface heat flux and full y-z-plane `T_bulk`.
- high-resolution `forceCoeffs.dat` for `Cl(t)` and `Cd(t)`.

Method:

- Dominant shedding frequency is estimated from high-resolution `Cl(t)` in the 8-10 s window.
- `Cl(t)` is interpolated to the available full-3D Nu snapshots.
- Coherence, cross spectral phase, phase-derived delay, zero-lag Pearson, and cross-correlation lag are computed for selected 1 mm strips.

Important limitation:

The full-3D Nu signal has only `26` snapshots per Re in the 8-10 s window, because this is how often full volume fields are available. Welch coherence therefore uses only about `2` segments. Treat these frequency-domain results as exploratory support, not final standalone statistical proof.

Steady/no-shedding cases are flagged with `valid_shedding_signal = false` when `std(Cl) <= 0.001`; their dominant frequency is intentionally reported as `NaN` because a PSD peak would only represent numerical noise.

Outputs:

- `stage02_timeseries_Cl_Nu_Q_selected_strips.csv`
- `stage02_coherence_phase_metrics.csv`
- `stage02_dominant_Cl_frequency_summary.csv`
- `fig01_time_traces_Cl_vs_Nu_x5p5`
- `fig02_Nu3Dxt_coherence_delay_by_x`
- `fig02_QtotalstripW_coherence_delay_by_x`
- `fig03_dominant_Cl_St_by_Re`

Recommended interpretation:

Use this stage to identify candidate strips and delays. For publication-grade spectral claims, increase full-field write frequency or compute exact `Nu_3D(x,t)` online during simulation/postProcess so that `Nu` has the same temporal resolution as `forceCoeffs`.
