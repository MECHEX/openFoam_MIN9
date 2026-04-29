# run003 Analysis Pack

This file is a compact export package for deep external LLM analysis of `V4b_3D run003`.

It intentionally contains:
- physical context,
- key scalar outcomes,
- reduced modal/spectral/TE payloads,
- interpretation constraints,
- concrete questions for the external model.

It intentionally does **not** inline full raw spatial mode tables, full extended-mode fields, or all full-resolution curves, because those would greatly expand context while adding limited reasoning value for a first-pass LLM analysis.

## 1. Case Metadata

| Key | Value |
|---|---|
| Study | `VV_cases/V4b_3D/results/run003` |
| Date | `2026-04-29` |
| Flow regime | `PERIODIC` |
| Re | `200` |
| Ri | `0.314` |
| Geometry family | `V4b_3D fin-and-tube` |
| Diameter D | `0.012 m` |
| Inlet velocity Uin | `0.25267 m/s` |
| Mesh | `medium / level-2, inherited from run001` |
| Cells | `337,184` |
| Lin/D | `2.0` |
| Lout/D | `5.0` |
| Solver | `buoyantBoussinesqPimpleFoam` |
| Run status | stopped at `t = 6.505 s` of `10.0 s` target |
| Wall time | `~6.7 h`, `8 cores` |

## 2. Integral Results

| Quantity | Value | Note |
|---|---:|---|
| `Cd_mean` | `3.161` | `-21%` vs run002 Re=100 |
| `Cl_rms` | `0.187` | nonzero shedding amplitude |
| `Cl_mean` | `2.52` | buoyancy offset in lift |
| `f_shed` | `3.125 Hz` | from force/lift interpretation |
| `St` | `0.1484` | computed with `D = 12 mm` |
| `T_out` | `305.26 K` | `-8.05 K` vs run002 |
| `Nu_EB` | `7.476` | preferred heat-transfer metric |
| `Q_total` | `1.417 W` | EB+LMTD workflow |
| `LMTD` | `43.665 K` | from inlet/outlet/hot-wall temperatures |

## 3. Comparison Vs Run002

| Quantity | run002 Re=100 | run003 Re=200 | Change |
|---|---:|---:|---:|
| Regime | `STEADY` | `PERIODIC` | shedding onset crossed |
| `Cd_mean` | `3.9974` | `3.161` | `-21%` |
| `Cl_rms` | `0` | `0.187` | shedding appears |
| `T_out` | `313.306 K` | `305.26 K` | `-8.05 K` |
| `Nu_EB` | `6.955` | `7.476` | `+7.5%` |
| `Ri` | `1.26` | `0.314` | `-75%` |

## 4. Data Availability And Reliability

| Data family | Availability | Reliability note |
|---|---|---|
| Midspan VTP snapshots | `13` snapshots at `t=0.5..6.5 s`, every `0.5 s` | good for spatial structure and modal energy ranking; too sparse for precise frequency/phase inference |
| Wake probes | `1301` samples, `dt = 0.005 s` | best source for spectral and delay analysis |
| Force spectra | available from `force.dat` columns | useful as frequency cross-check, but column semantics are not labeled in the export |
| Figures | available under `figures/` | useful human-readable interpretation layer |

Key limitation:
- The shedding period is about `1 / 3.125 = 0.32 s`, so POD snapshots sampled every `0.5 s` are **undersampled** relative to the oscillation. POD/EPOD are exploratory, while probe coherence and TE are more trustworthy for frequency-domain conclusions.

## 5. POD Summary

| Field | Active modes | Mode 1 energy | Mode 2 energy | Mode 1+2 cumulative | Mode 1-4 cumulative |
|---|---:|---:|---:|---:|---:|
| `Ux` | `12` | `34.37%` | `27.57%` | `61.94%` | `93.42%` |
| `Uy` | `12` | `53.23%` | `32.92%` | `86.16%` | `95.07%` |
| `T` | `12` | `41.02%` | `37.78%` | `78.80%` | `91.88%` |

Interpretive hint:
- `Uy` is the cleanest low-dimensional hydrodynamic marker.
- `T` is strongly organized by the same oscillatory structure.
- `Ux` is less compact, suggesting stronger contamination by wake-deficit breathing, recirculation deformation, and harmonics.

## 6. EPOD Reduced Payload

All-mode EPOD reaches ~100% captured energy because 13 snapshots give 12 active modes and the basis is nearly full-rank. The informative part is early-mode growth:

| Direction | 1 mode | 2 modes | 4 modes | 8 modes | All modes interpretation |
|---|---:|---:|---:|---:|---|
| `Ux -> T` | `4.94%` | `20.09%` | `29.81%` | `73.39%` | weak low-order predictor |
| `T -> Ux` | `6.95%` | `16.26%` | `32.56%` | `61.28%` | weak low-order predictor |
| `Uy -> T` | `40.41%` | `78.21%` | `90.61%` | `97.52%` | strong low-order predictor |

Interpretive hint:
- The thermal field is much more compactly linked to `Uy` than to `Ux`.
- This supports a lateral wake sweeping / vortex-shedding control picture for temperature fluctuations.

## 7. Spectral Coherence Payload

Nearest Welch bins used in local interpretation:
- near `f_shed`: `3.076923077 Hz`
- near `2*f_shed`: `6.153846154 Hz`

### Coherence near `f_shed`

| Pair | Coherence at `~3.077 Hz` |
|---|---:|
| `probe_0_1D` (`Ux-T`) | `0.7040` |
| `probe_1_2D` (`Ux-T`) | `0.1286` |
| `probe_2_3D` (`Ux-T`) | `0.0659` |
| `Uy_probe_0` (`Uy-T`) | `0.7040` |

### Coherence near `2*f_shed`

| Pair | Coherence at `~6.154 Hz` |
|---|---:|
| `probe_0_1D` (`Ux-T`) | `0.9974` |
| `probe_1_2D` (`Ux-T`) | `0.9754` |
| `probe_2_3D` (`Ux-T`) | `0.9635` |
| `Uy_probe_0` (`Uy-T`) | `0.9966` |

### PSD values at `f_shed` and `2*f_shed`

| Signal | PSD at `~3.077 Hz` | PSD at `~6.154 Hz` |
|---|---:|---:|
| `Ux_p0` | `4.419e-06` | `3.921e-04` |
| `Uy_p0` | `3.522e-07` | `1.643e-03` |
| `T_p0` | `2.149e-02` | `1.756` |

Interpretive hint:
- The fundamental shedding band is visible, but the response near `2*f_shed` is much stronger in the local probe spectra and coherence.
- This may indicate that heat-transfer-relevant modulation is more naturally tied to a second harmonic than to the signed lift oscillation alone.

## 8. Transfer Entropy Payload

| Pair | Peak lag samples | Peak lag s | TE bits | Excess TE bits | Surrogate p95 bits |
|---|---:|---:|---:|---:|---:|
| `Ux_1D_to_T_1D` | `23` | `0.115` | `0.2259` | `0.2067` | `0.0274` |
| `T_1D_to_Ux_1D` | `1` | `0.005` | `0.2058` | `0.1844` | `0.0273` |
| `Ux_3D_to_T_3D` | `29` | `0.145` | `0.3987` | `0.3693` | `0.0385` |
| `T_3D_to_Ux_3D` | `27` | `0.135` | `0.3872` | `0.3637` | `0.0321` |
| `Uy_1D_to_T_1D` | `18` | `0.090` | `0.2161` | `0.1972` | `0.0278` |

Interpretive hint:
- With shedding period `~0.32 s`, most TE lags fall in the `0.28-0.45` cycle range.
- This supports a delayed thermal response to wake motion.
- Bidirectional TE at the 3D probe should not be treated as literal two-way causation without stronger controls; it likely reflects shared periodic predictability.

## 9. Force-Spectrum Cross-Check

Unlabeled `force.dat` numeric columns all show their selected local peak near `3.076923077 Hz`.

This is a useful cross-check that the forcing/shedding band is consistently present across multiple dynamic outputs, even if the exported columns are not semantically labeled here.

## 10. Suggested Human Figure Reading Order

Best figures for a human reviewer or a multimodal model:

1. `figures/pod_modal_energy.png`
2. `figures/pod_temporal_coefficients.png`
3. `figures/pod_Uy_spatial_modes_1_4.png`
4. `figures/pod_T_spatial_modes_1_4.png`
5. `figures/epod_reconstruction_quality.png`
6. `figures/coherence_curves.png`
7. `figures/probe_power_spectra.png`
8. `figures/transfer_entropy_peak_summary.png`
9. `figures/transfer_entropy_curves.png`

## 11. Source Files In This Repo

Primary source files behind this pack:

- `summary.md`
- `modal_analysis_summary.md`
- `analysis_summary.json`
- `pod/Ux/singular_values.csv`
- `pod/Uy/singular_values.csv`
- `pod/T/singular_values.csv`
- `epod/Ux_to_T/reconstruction_metrics.csv`
- `epod/T_to_Ux/reconstruction_metrics.csv`
- `epod/Uy_to_T/reconstruction_metrics.csv`
- `spectral_coherence/coherence_curves.csv`
- `spectral_coherence/power_spectra.csv`
- `transfer_entropy/te_peak_summary.csv`
- `figures/*.png`

## 12. Questions For External LLM Analysis

Use the following tasks/questions when prompting the external model:

1. Does the combined POD + EPOD + coherence + TE evidence support the hypothesis that temperature dynamics in run003 are controlled more strongly by transverse wake motion (`Uy`) than by streamwise wake deficit (`Ux`)?
2. How strong is the evidence that `2*f_shed` is a physically important thermal or heat-transfer harmonic rather than a numerical artifact?
3. Given the sparse POD snapshot cadence (`0.5 s`) versus shedding period (`~0.32 s`), which conclusions remain robust and which should be treated only as exploratory?
4. What reduced-order physical narrative best explains the full set of observations:
   `Uy` low-dimensionality,
   strong `Uy -> T` EPOD,
   high near-wake coherence at `f_shed`,
   and even stronger spectral signature near `2*f_shed`?
5. What additional data would most improve confidence:
   denser midspan snapshots,
   surface `Nu(theta,z,t)`,
   phase-averaged wake fields,
   longer probe records,
   or something else?
6. Which results appear most publication-ready already, and which require another completed run or improved sampling?

## 13. Recommended Prompt Preamble

Suggested opening text for an external LLM:

> Below is a compact export package for a 3D fin-and-tube mixed-convection CFD run (`Re=200`) that shows periodic vortex shedding. Please analyze the physics of the results, assess the strength of the evidence behind each claim, identify the most defensible conclusions, and separate robust findings from artifacts or sampling limitations.

