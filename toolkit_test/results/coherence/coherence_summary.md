# Spectral Coherence Demonstration

This folder contains a long synthetic `5x5` velocity and wall heat-flux time series.

- snapshots: `1024`
- time step: `0.05`
- sampling frequency: `20.0`
- imposed base frequency: `1.25`
- imposed second harmonic: `2.5`

The magnitude-squared coherence is computed as:

```text
C_xy(f) = |S_xy(f)|^2 / (S_xx(f) S_yy(f))
```

where `S_xy` is the Welch cross-spectrum and `S_xx`, `S_yy` are the Welch auto-spectra.

## POD Energy of the Long Series

| dataset | mode 1 | mode 2 | mode 3 | cumulative 3 modes |
|---|---:|---:|---:|---:|
| velocity | 73.23% | 17.66% | 9.01% | 99.90% |
| heat_flux | 53.35% | 40.39% | 5.33% | 99.07% |

## Coherence Peaks

| pair | expected frequency | peak frequency | peak coherence | phase at peak |
|---|---:|---:|---:|---:|
| u_skew_vs_q_skew | 1.250 | 1.250 | 1.000 | 142.1 deg |
| u_core_mean_vs_q_wall_mean | 2.500 | 2.500 | 1.000 | -20.1 deg |
| u_pod_a1_vs_q_pod_a1 | 1.250 | 1.250 | 0.998 | 168.7 deg |
| u_pod_a2_vs_q_pod_a2 | 2.500 | 2.500 | 0.671 | 138.6 deg |

## Main Figures

- `figures/coherence_snapshot_gallery.png`
- `figures/coherence_input_signals.png`
- `figures/coherence_power_spectra.png`
- `figures/coherence_curves.png`
- `figures/coherence_pod_modal_energy.png`
- `figures/coherence_pod_mode_pair_heatmaps.png`
