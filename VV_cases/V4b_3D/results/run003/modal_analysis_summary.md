# V4b_3D run003 Modal Analysis

Analyses executed on the available run003 postProcessing data in the same repo layout as run001.

## Input Data

- Midspan snapshots: 13 at t=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5]
- Probe samples: 1301, dt=0.005 s
- Target shedding frequency: 3.125 Hz

## POD Energy

| Field | modes | mode 1 | mode 2 | cumulative 2 |
|---|---:|---:|---:|---:|
| Ux | 12 | 34.37% | 27.57% | 61.94% |
| Uy | 12 | 53.23% | 32.92% | 86.16% |
| T | 12 | 41.02% | 37.78% | 78.80% |

## EPOD

| Source -> target | captured target energy | rel. error |
|---|---:|---:|
| Ux -> T | 100.00% | 2.478e-11 |
| T -> Ux | 100.00% | 2.475e-15 |
| Uy -> T | 100.00% | 1.569e-14 |

## Spectral Coherence Near Shedding

| Pair | peak f [Hz] | coherence |
|---|---:|---:|
| probe_0_1D | 3.077 | 0.704 |
| probe_1_2D | 3.077 | 0.129 |
| probe_2_3D | 3.077 | 0.066 |
| Uy_probe_0 | 3.077 | 0.704 |

## Transfer Entropy Peaks

| Pair | lag [s] | excess TE [bits] |
|---|---:|---:|
| Ux_1D_to_T_1D | 0.1150 | 0.20669 |
| T_1D_to_Ux_1D | 0.0050 | 0.18444 |
| Ux_3D_to_T_3D | 0.1450 | 0.36933 |
| T_3D_to_Ux_3D | 0.1350 | 0.36367 |
| Uy_1D_to_T_1D | 0.0900 | 0.19721 |

## Notes

- POD/EPOD use 13 midspan snapshots, so they are useful exploratory results, not final publication-grade modal statistics.
- Probe coherence and TE use the denser wake-probe time series and are better suited to identifying the shedding band.
- Full final POD/EPOD should use a longer post-transient snapshot database with uniform sampling over many shedding cycles.

## Figures

Figures are stored in `figures/`.

| Method | Figure |
|---|---|
| POD energy | `figures/pod_modal_energy.png` |
| POD temporal coefficients | `figures/pod_temporal_coefficients.png` |
| POD spatial maps | `figures/pod_Ux_spatial_modes_1_4.png`, `figures/pod_Uy_spatial_modes_1_4.png`, `figures/pod_T_spatial_modes_1_4.png` |
| EPOD reconstruction quality | `figures/epod_reconstruction_quality.png` |
| EPOD extended modes | `figures/epod_Ux_to_T_extended_modes_1_4.png`, `figures/epod_T_to_Ux_extended_modes_1_4.png`, `figures/epod_Uy_to_T_extended_modes_1_4.png` |
| Spectral coherence | `figures/coherence_curves.png` |
| Probe spectra | `figures/probe_power_spectra.png` |
| Transfer entropy | `figures/transfer_entropy_curves.png`, `figures/transfer_entropy_peak_summary.png` |
| Force spectra | `figures/force_power_spectra.png` |
