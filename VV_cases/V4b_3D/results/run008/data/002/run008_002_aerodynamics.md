# V4b_3D run008 aerodynamic analysis

Scope: `forceCoeffs` and `forces_raw` both use patch `hot_tube`; pressure/viscous decomposition is therefore cylinder-only and directly comparable to Cd/Cl/Cm.

Primary window: `2.0..10.0 s`.
Shedding frequency from every-second Cl peak: `3.2787 Hz`, `St = 0.15572`.
Adjacent Cl-peak component: `6.5574 Hz` from `53` detected peaks.
The PSD is dominated by the adjacent-peak component near `2*f_shed`; the lower `f_shed` component is present but much weaker in Cl.

## Consistency check

| Quantity | raw total - forceCoeffs mean |
|---|---:|
| Cd | 1.483129e-11 |
| Cl | -6.712903e-11 |
| Cm | -1.513703e-13 |

## Pressure/viscous component statistics

| Component | mean | RMS | RMS / total RMS | phase vs total | corr vs total |
|---|---:|---:|---:|---:|---:|
| Cd_p | 2.903582 | 0.006054 | 89.74% | +2.79 deg | 0.9989 |
| Cd_v | 0.457432 | 0.000754 | 11.18% | -22.90 deg | 0.9259 |
| Cl_p | 2.514626 | 0.163823 | 92.82% | +0.89 deg | 0.9991 |
| Cl_v | 0.000723 | 0.014546 | 8.24% | -10.42 deg | 0.8812 |
| Cm_p | 0.000000 | 0.000000 | 0.00% | +50.10 deg | 0.2848 |
| Cm_v | 0.008024 | 0.001574 | 100.00% | -0.00 deg | 1.0000 |

## Harmonics

| Signal | target | target Hz | peak Hz | St | relative power |
|---|---|---:|---:|---:|---:|
| Cd | f0 | 3.2787 | 3.3203 | 0.15770 | -16.02 dB |
| Cd | 2f0 | 6.5574 | 6.6406 | 0.31539 | +0.00 dB |
| Cd | 3f0 | 9.8361 | 9.7656 | 0.46382 | -24.40 dB |
| Cl | f0 | 3.2787 | 3.3203 | 0.15770 | -39.91 dB |
| Cl | 2f0 | 6.5574 | 6.6406 | 0.31539 | +0.00 dB |
| Cl | 3f0 | 9.8361 | 9.7656 | 0.46382 | -38.23 dB |
| Cm | f0 | 3.2787 | 3.3203 | 0.15770 | -34.90 dB |
| Cm | 2f0 | 6.5574 | 6.6406 | 0.31539 | +0.00 dB |
| Cm | 3f0 | 9.8361 | 9.7656 | 0.46382 | -42.36 dB |
| Cl_pressure | f0 | 3.2787 | 3.3203 | 0.15770 | -39.99 dB |
| Cl_pressure | 2f0 | 6.5574 | 6.6406 | 0.31539 | +0.00 dB |
| Cl_pressure | 3f0 | 9.8361 | 9.7656 | 0.46382 | -38.14 dB |
| Cl_viscous | f0 | 3.2787 | 3.1250 | 0.14842 | -38.98 dB |
| Cl_viscous | 2f0 | 6.5574 | 6.6406 | 0.31539 | +0.00 dB |
| Cl_viscous | 3f0 | 9.8361 | 9.7656 | 0.46382 | -39.17 dB |
| Cm_pressure | f0 | 3.2787 | 3.3203 | 0.15770 | -37.29 dB |
| Cm_pressure | 2f0 | 6.5574 | 6.6406 | 0.31539 | +0.00 dB |
| Cm_pressure | 3f0 | 9.8361 | 9.7656 | 0.46382 | -39.96 dB |

## Dominant peaks / side peaks

| Signal | rank | peak Hz | St | relative power |
|---|---:|---:|---:|---:|
| Cd | 1 | 6.6406 | 0.31539 | +0.00 dB |
| Cd | 2 | 3.3203 | 0.15770 | -16.02 dB |
| Cd | 3 | 13.0859 | 0.62151 | -22.62 dB |
| Cd | 4 | 9.7656 | 0.46382 | -24.40 dB |
| Cd | 5 | 2.7344 | 0.12987 | -24.52 dB |
| Cl | 1 | 6.6406 | 0.31539 | +0.00 dB |
| Cl | 2 | 5.4688 | 0.25974 | -30.15 dB |
| Cl | 3 | 7.8125 | 0.37105 | -35.73 dB |
| Cl | 4 | 1.1719 | 0.05566 | -37.64 dB |
| Cl | 5 | 9.7656 | 0.46382 | -38.23 dB |
| Cm | 1 | 6.6406 | 0.31539 | +0.00 dB |
| Cm | 2 | 5.4688 | 0.25974 | -28.79 dB |
| Cm | 3 | 3.3203 | 0.15770 | -34.90 dB |
| Cm | 4 | 7.8125 | 0.37105 | -37.88 dB |
| Cm | 5 | 2.7344 | 0.12987 | -41.93 dB |
| Cl_pressure | 1 | 6.6406 | 0.31539 | +0.00 dB |
| Cl_pressure | 2 | 5.4688 | 0.25974 | -30.18 dB |
| Cl_pressure | 3 | 7.8125 | 0.37105 | -35.70 dB |
| Cl_pressure | 4 | 1.1719 | 0.05566 | -37.81 dB |
| Cl_pressure | 5 | 9.7656 | 0.46382 | -38.14 dB |
| Cl_viscous | 1 | 6.6406 | 0.31539 | +0.00 dB |
| Cl_viscous | 2 | 5.4688 | 0.25974 | -29.75 dB |
| Cl_viscous | 3 | 7.8125 | 0.37105 | -36.15 dB |
| Cl_viscous | 4 | 1.1719 | 0.05566 | -36.87 dB |
| Cl_viscous | 5 | 3.1250 | 0.14842 | -38.98 dB |
| Cm_pressure | 1 | 6.6406 | 0.31539 | +0.00 dB |
| Cm_pressure | 2 | 5.4688 | 0.25974 | -29.16 dB |
| Cm_pressure | 3 | 13.0859 | 0.62151 | -35.48 dB |
| Cm_pressure | 4 | 7.8125 | 0.37105 | -37.06 dB |
| Cm_pressure | 5 | 3.3203 | 0.15770 | -37.29 dB |

## Figures

- `../../figures/002/run008_002_force_pressure_viscous_decomposition.png`
- `../../figures/002/run008_002_force_psd_harmonics.png`
- `../../figures/002/run008_002_phase_portraits_hilbert.png`
- `../../figures/002/run008_002_phase_conditioned_cycle.png`
