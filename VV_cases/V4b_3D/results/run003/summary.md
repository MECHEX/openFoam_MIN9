# V4b_3D run003 - summary

## Setup

| Parameter | Value |
|---|---|
| Date | 2026-04-29 |
| Re | 200 |
| Ri | 0.314 (mixed convection weaker than Re=100) |
| Mesh | medium / snappyHexMesh level-2, inherited from run001 |
| Cells | 337,184 |
| Lin/D | 2.0 |
| Lout/D | 5.0 |
| bg cell xy | 1.0 mm |
| Refine tube | level-2 |
| BL layers tube | 8, first layer 30 um |
| BL layers fin | 6, first layer 30 um |
| Solver | buoyantBoussinesqPimpleFoam |
| t_end | 6.505 s / 10.0 s target |
| Wall time | ~6.7 h (ClockTime = 24,091 s, 8 cores) |

## Status

The solver was stopped at t = 6.505 s, about 65% of the 10 s target. The available signal is already periodic and is useful as an onset/regime result, but final publication-quality averages should be recomputed after a longer completed run.

## Flow Results

| Quantity | Value | Notes |
|---|---|---|
| Regime | **PERIODIC** | vortex shedding present |
| Cd_mean | 3.161 | -21% vs run002 (3.9974) |
| Cl_rms | 0.187 | shedding amplitude |
| Cl_mean | 2.52 | buoyancy lift offset |
| f_shed | 3.125 Hz | from Cl spectrum |
| St | 0.1484 | St = f D / U, with D = 0.012 m and U = 0.25267 m/s |
| T_out | 305.26 K | -8.05 K vs run002 |

## Heat Transfer Results

| Method | Nu_total |
|---|---|
| **EB+LMTD** (preferred) | **7.476** |
| snGrad | N/A |

- LMTD = 43.665 K
- Q_total = 1.417 W
- A_total = 0.002032 m2, inherited from run002 energy-balance calibration
- Nu_EB increased from 6.955 at Re=100 to 7.476 at Re=200

## Comparison Vs Run002

| Quantity | run002 (Re=100) | run003 (Re=200) | Change |
|---|---:|---:|---:|
| Regime | STEADY | PERIODIC | shedding onset crossed |
| Cd_mean | 3.9974 | 3.161 | -21% |
| Cl_rms | 0 | 0.187 | shedding appears |
| T_out | 313.306 K | 305.26 K | -8.05 K |
| Nu_EB | 6.955 | 7.476 | +7.5% |
| Ri | 1.26 | 0.314 | -75% |

## Interpretation

Re=200 is above the critical Reynolds number for this V4b_3D configuration. The Re=100 run002 case is steady, while run003 develops periodic shedding. The measured Strouhal number is lower than the V1 2D beta=0.375 reference trend, which is consistent with the 3D fin-and-tube geometry and nonzero buoyancy coupling.

The earlier St=0.099 estimate should not be used for this run: it came from using the wrong characteristic length. With the canonical V4b diameter D = 12 mm, St = 0.1484.

## Min9 Check

No `Min9` label was found in the repository, logs, or postProcessing outputs available during this update. If `Min9` refers to a timestep, external case label, or another simulation family, it is not represented in the current V4b_3D run003 result artifacts.

## Modal Toolkit Results

Full exploratory toolkit post-processing was run from this repository with outputs stored under `VV_cases/V4b_3D/results/run003/`.

| Method | Key result |
|---|---|
| POD Ux | mode 1 = 34.37%, mode 2 = 27.57%, cumulative 2 = 61.94% |
| POD Uy | mode 1 = 53.23%, mode 2 = 32.92%, cumulative 2 = 86.16% |
| POD T | mode 1 = 41.02%, mode 2 = 37.78%, cumulative 2 = 78.80% |
| EPOD | all-mode reconstructions give ~100% captured target energy because only 13 synchronized snapshots are available |
| Spectral coherence | strongest wake thermal coupling near shedding at 3.077 Hz: probe_0 Ux-T coherence = 0.704 |
| Transfer entropy | strongest exploratory TE: Ux_3D -> T_3D, lag = 0.145 s, excess TE = 0.369 bits |

Important limitation: POD/EPOD use 13 midspan snapshots from t=0.5..6.5 s, so they are exploratory and useful for checking method behavior. Probe coherence and TE use 1301 samples at dt=0.005 s and are the more reliable indicators of the shedding band in this partial run.

Figures for interpreting each method are in `VV_cases/V4b_3D/results/run003/figures/`. Start with `pod_modal_energy.png`, `pod_temporal_coefficients.png`, `coherence_curves.png`, and `transfer_entropy_peak_summary.png`.

## Modal Interpretation

### How To Read The Figures

- `pod_modal_energy.png`: bar height is fluctuation energy carried by each POD mode; the black line is cumulative energy. A steep cumulative curve means the field is low-dimensional and organized.
- `pod_temporal_coefficients.png`: modal amplitudes versus time. Oscillatory paired coefficients indicate a periodic structure, but here they should not be used to infer frequency because the snapshot interval is 0.5 s.
- `pod_*_spatial_modes_1_4.png`: red/blue lobes are positive/negative fluctuations around the mean field. The sign itself is arbitrary; the physically important part is the shape and pairing of lobes.
- `epod_reconstruction_quality.png`: captured target energy versus number of source POD modes. The early-mode slope is more informative than the final all-mode value.
- `coherence_curves.png`: frequency-domain coupling between wake velocity and temperature probes. Values near 1 mean the two signals share strong frequency content.
- `transfer_entropy_*`: lagged directional predictability. TE is not proof of causality by itself in a periodically forced system, but it helps identify delay and dominant information direction.

### POD Reading

The POD result is strongest for transverse velocity and temperature:

| Field | Mode 1+2 | Mode 1-4 | Interpretation |
|---|---:|---:|---|
| Ux | 61.94% | 93.42% | streamwise wake needs several components: mean-deficit breathing, recirculation change, and harmonic content |
| Uy | 86.16% | 95.07% | transverse wake motion is strongly organized by shedding |
| T | 78.80% | 91.88% | thermal field is also organized by the periodic wake |

This is the first strong modal indication that run003 is not merely "unsteady": it has a coherent, low-dimensional shedding structure. `Uy` is the cleanest marker of vortex shedding, while `T` follows that motion closely enough to form a compact thermal modal basis. `Ux` is less purely two-mode because streamwise velocity contains both wake deficit and periodic wake deformation.

Important sampling caveat: the midspan snapshots are separated by 0.5 s, while the shedding period is about 1/3.125 = 0.32 s. Therefore the POD maps are useful for spatial structure and energy ranking, but not for precise frequency/phase inference.

### EPOD Reading

The all-mode EPOD reconstructions report ~100% captured target energy, but that should not be over-interpreted: 13 synchronized snapshots give 12 active modes, so using all modes is nearly a full-rank reconstruction. The early-mode behavior is the meaningful part:

| EPOD direction | 1 mode | 2 modes | 4 modes | Interpretation |
|---|---:|---:|---:|---|
| Ux -> T | 4.94% | 20.09% | 29.81% | streamwise velocity alone is a weak low-order predictor of temperature |
| T -> Ux | 6.95% | 16.26% | 32.56% | temperature alone does not compactly reconstruct Ux |
| Uy -> T | 40.41% | 78.21% | 90.61% | transverse wake motion is strongly tied to thermal structure |

This is probably the most useful EPOD result: thermal fluctuations are much more compactly linked to `Uy` than to `Ux`. Physically, the heat-transfer field appears to respond to lateral vortex-shedding motion and wake sweeping rather than only to streamwise velocity deficit.

### Spectral Coherence Reading

Near the lift/shedding frequency, the closest Welch bin is 3.077 Hz, consistent with f_shed = 3.125 Hz:

| Pair | coherence at ~f_shed |
|---|---:|
| probe_0_1D Ux-T | 0.704 |
| probe_1_2D Ux-T | 0.129 |
| probe_2_3D Ux-T | 0.066 |
| probe_0_1D Uy-T | 0.704 |

The wake-temperature coupling at the fundamental shedding frequency is strongest close behind the tube and weakens downstream. That suggests the immediate near-wake is where vortex motion most directly modulates local temperature.

The probe spectra and coherence also show a stronger response around 6.154 Hz, approximately 2*f_shed. At probe 0, PSD at 6.154 Hz is much larger than at 3.077 Hz for `Ux`, `Uy`, and `T`; coherence is also near unity at 6.154 Hz. This is physically plausible: lift changes sign once per shedding half-cycle, but mixing intensity and heat-transfer-like quantities can peak twice per full shedding cycle. For heat-transfer interpretation, both f_shed and 2*f_shed should be tracked in later runs.

### Transfer Entropy Reading

The TE peaks show lagged predictive coupling on the order of 0.09-0.145 s:

| Direction | Lag | Excess TE |
|---|---:|---:|
| Ux_1D -> T_1D | 0.115 s | 0.2067 bits |
| T_1D -> Ux_1D | 0.005 s | 0.1844 bits |
| Ux_3D -> T_3D | 0.145 s | 0.3693 bits |
| T_3D -> Ux_3D | 0.135 s | 0.3637 bits |
| Uy_1D -> T_1D | 0.090 s | 0.1972 bits |

With a shedding period of ~0.32 s, these delays correspond to roughly 0.28-0.45 shedding periods. This supports a transport/delay picture: wake motion changes mixing first, and the temperature signal follows after a fraction of the cycle. The bidirectional TE at the 3D probe should be read as shared periodic predictability rather than literal two-way causation.

### Deep Run003 Takeaways

1. Re=200 produces a coherent shedding regime, not just noisy unsteadiness.
2. The transverse wake field (`Uy`) is the cleanest low-dimensional hydrodynamic marker: two POD modes carry 86% of its fluctuation energy.
3. Temperature is strongly organized by the same wake dynamics: two thermal POD modes carry 79% of thermal fluctuation energy.
4. EPOD indicates that `Uy` predicts thermal structure much better than `Ux`; the key coupling mechanism is lateral wake sweeping/vortex motion.
5. Heat-transfer-related signals likely contain an important second harmonic near 2*f_shed. This may be more relevant to local heat-transfer intensity than the fundamental lift frequency alone.
6. Current POD/EPOD results are exploratory because snapshots are sparse. Probe-based coherence/TE are more reliable for frequency-domain conclusions in this partial run.

Recommended next modal run: after rejecting the transient, save midspan and wall-thermal snapshots every 0.02-0.04 s for many shedding periods, and add surface-resolved `Nu(theta,z,t)` or wall heat-flux proxy. That would turn the current exploratory POD/EPOD into publication-grade modal evidence.

## External Data

`C:\openfoam-case\VV_cases\V4b_3D_run003\` (Windows sync target)
`/home/kik/of_runs/V4b_3D_run003/` (WSL, full field data)
