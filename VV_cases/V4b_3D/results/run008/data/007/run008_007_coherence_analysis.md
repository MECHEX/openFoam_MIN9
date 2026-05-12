# V4b_3D run008 coherence and cross-spectral analysis

Primary window: `2.0..10.0 s`.

## Global signals

| Signal | band | f [Hz] | coherence | cross phase | phase lag [s] | xcorr lag [s] | xcorr corr |
|---|---|---:|---:|---:|---:|---:|---:|
| Q_wall | f_shed | 3.1250 | 0.5713 | -55.66 deg | -0.0472 | +0.0100 | +0.3471 |
| Q_wall | 2f_shed | 6.6406 | 0.9058 | -24.44 deg | -0.0104 | +0.0100 | +0.3471 |
| Q_tube | f_shed | 3.1250 | 0.7358 | -55.92 deg | -0.0474 | +0.0850 | +0.3421 |
| Q_tube | 2f_shed | 6.6406 | 0.9445 | +165.35 deg | +0.0700 | +0.0850 | +0.3421 |
| Q_fins | f_shed | 3.1250 | 0.3761 | -55.45 deg | -0.0470 | +0.0100 | +0.5751 |
| Q_fins | 2f_shed | 6.6406 | 0.9216 | -21.90 deg | -0.0093 | +0.0100 | +0.5751 |
| Nu_tube | f_shed | 3.1250 | 0.5608 | -100.52 deg | -0.0852 | -0.0050 | +0.3303 |
| Nu_tube | 2f_shed | 6.6406 | 0.9495 | +15.19 deg | +0.0064 | -0.0050 | +0.3303 |
| Nu_fins | f_shed | 3.1250 | 0.4361 | -109.51 deg | -0.0928 | +0.0000 | +0.5062 |
| Nu_fins | 2f_shed | 6.6406 | 0.9906 | +0.43 deg | +0.0002 | +0.0000 | +0.5062 |

## Spatial summaries

- Tube mean coherence: f_shed `0.454`, 2f_shed `0.977`.
- Tube active fraction with coherence > 0.5 at f_shed: `23.2%`.
- Tube median cross-phase lag at f_shed: `-0.0996 s`; median cross-correlation lag: `+0.0000 s`.
- Fin z_min mean coherence: f_shed `0.393`, 2f_shed `0.967`.
- Fin z_max mean coherence: f_shed `0.430`, 2f_shed `0.980`.

## Figures

- `../../figures/007/run008_007_global_coherence_crossphase.png`
- `../../figures/007/run008_007_tube_coherence_lag_maps.png`
- `../../figures/007/run008_007_fin_coherence_lag_profiles.png`
