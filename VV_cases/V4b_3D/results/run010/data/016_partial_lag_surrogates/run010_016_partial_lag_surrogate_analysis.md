# V4b_3D run010 partial layer 016

Sparse lag scan with cyclic-shift surrogates for the incomplete run010.

## Important limitation

This analysis uses the 48 phase-selected layer-015 snapshots, not a
complete uniformly sampled vortex-intensity time series. The selected
samples were interpolated to `dt = 0.02 s` before lag scanning. Treat
this as a diagnostic/prototype result only; recompute after run010
reaches `t = 10 s` using a uniformly sampled `I_R(t)` series.

## Inputs

- input table: `data\015_partial\run010_015_partial_region_structure_heat_merged.csv`
- selected snapshots per region: `48`
- interpolated grid: `188` samples, `dt = 0.020 s`
- lag range: `+-T_shed = +-0.3080 s`
- cyclic-shift surrogates: `1000`

## Best diagnostic associations

| pair | structure_signal | response_signal | rho_star | tau_star_s | tau_over_T_shed | surrogate_p95_absrho | surrogate_p99_absrho | empirical_p | tau_conv_s_assumed | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R_fin_junction -> Nu_wall | I_Q* | Nu | -0.8273 | 0 | 0 | 0.4228 | 0.4512 | 0.000999 | 0.02372 | significant but wrong-direction/zero-lag |
| R_near_wake -> Nu_tube_wall | I_Q* | Nu | -0.6018 | 0 | 0 | 0.323 | 0.3296 | 0.000999 | 0.07115 | significant but wrong-direction/zero-lag |
| R_fin_sweep -> Nu_fins_wall | I_Q* | Nu | -0.601 | 0 | 0 | 0.4929 | 0.5177 | 0.000999 | 0.07905 | significant but wrong-direction/zero-lag |
| R_sep -> Nu_tube_wall | I_Q* | Q | 0.5742 | -0.12 | -0.3896 | 0.3655 | 0.4069 | 0.000999 | 0.03557 | significant but wrong-direction/zero-lag |
| R_fin_sweep -> Nu_fins_wall | I_Lambda2* | Q | -0.4808 | 0 | 0 | 0.2649 | 0.2659 | 0.000999 | 0.07905 | significant but wrong-direction/zero-lag |
| R_near_wake -> Nu_tube_wall | I_Lambda2* | Nu | -0.4804 | 0 | 0 | 0.435 | 0.4472 | 0.000999 | 0.07115 | significant but wrong-direction/zero-lag |
| R_sep -> Nu_tube_wall | I_Lambda2* | Nu | -0.4649 | 0 | 0 | 0.4198 | 0.4239 | 0.000999 | 0.03557 | significant but wrong-direction/zero-lag |
| R_far_wake -> Nu_fins_wall | I_Q* | Q | -0.454 | -0.3 | -0.974 | 0.4146 | 0.421 | 0.000999 | 0.1581 | significant but wrong-direction/zero-lag |

## Interpretation

A positive `tau_star_s` means that the structure signal leads the heat
response. A negative value means the heat response leads, or the pair is
phase-locked in a way that the present sparse diagnostic cannot resolve
directionally. Because the input is phase-selected rather than uniformly
sampled, the surrogate p-values should be read as screening metrics, not
final publication-grade significance.
