# toolkit_test

Minimal synthetic velocity-field dataset for testing POD workflows.

## Contents

- `data/velocity_snapshots_5x5.json` - structured snapshot data with metadata.
- `data/velocity_snapshots_5x5_wide.csv` - the same snapshots flattened row-major for quick POD input.
- `data/heat_flux_wall_snapshots_5x5.json` - structured wall heat-flux snapshots on the same `5 x 5` grid.
- `data/heat_flux_wall_snapshots_5x5_wide.csv` - flattened heat-flux snapshots paired with the velocity snapshots.
- `figures/*.png` - color heatmaps of each snapshot.
- `plot_velocity_snapshots.py` - regenerates the velocity and heat-flux heatmaps from the JSON files.
- `compute_pod.py` - computes independent POD decompositions for velocity and wall heat flux.
- `results/pod/` - POD output data: mean fields, singular values, spatial modes, and temporal coefficients.
- `compute_epod.py` - computes EPOD mappings between velocity POD coefficients and heat-flux fields, and vice versa.
- `results/epod/` - EPOD output data: extended modes and target-field reconstruction metrics.
- `plot_pod_epod.py` - visualizes POD and EPOD results.
- `results/figures/` - POD and EPOD visual summaries.
- `compute_spectral_coherence.py` - creates a longer synthetic time series and computes spectral coherence.
- `results/coherence/` - spectral coherence data tables and figures.
- `compute_transfer_entropy.py` - computes two transfer-entropy examples: current common-driver data and a delayed causal response.
- `results/transfer_entropy/` - transfer-entropy data tables and figures.
- `compute_resolvent_analysis.py` - computes a small educational resolvent-analysis example.
- `results/resolvent/` - resolvent gains, optimal forcing modes, response modes, and figures.

## Data idea

The field is a scalar velocity magnitude on a `5 x 5` cross-section grid.

- Snapshot `s01_symmetric_core` is exactly symmetric.
- Its center value is `10`.
- All wall/boundary cells are `0`.
- Snapshots `s02` to `s05` keep the wall values at `0`, but introduce controlled skewness and shape changes.

This gives a tiny dataset suitable for checking:

- mean-field subtraction,
- snapshot matrix assembly,
- singular value decomposition,
- first spatial POD modes.

The second dataset, `wall_heat_flux`, is deliberately defined only on the boundary ring. Interior values are zero. Its perturbations are paired with the velocity snapshots but are not identical, so separate POD analyses should produce related but visibly different modes.

## POD assembly convention

Use row-major flattening:

```text
u = [u00, u01, u02, u03, u04, u10, ..., u44]^T
```

Then build a snapshot matrix:

```text
X = [u_1, u_2, u_3, u_4, u_5]
```

For the heat-flux field, use the same convention:

```text
Q = [q_1, q_2, q_3, q_4, q_5]
```

where each `q_i` has nonzero entries only on the wall/boundary ring.

For standard POD, subtract the temporal mean first:

```text
X' = X - mean(X, axis=time)
```

and then run SVD:

```text
X' = U Sigma V^T
```

## Regenerate Figures

```powershell
python .\toolkit_test\plot_velocity_snapshots.py
```

## Compute POD

```powershell
python .\toolkit_test\compute_pod.py
```

POD outputs are written to:

- `toolkit_test/results/pod/velocity/`
- `toolkit_test/results/pod/heat_flux/`

Each output folder contains:

- `snapshot_matrix.csv` - raw flattened snapshots as columns.
- `centered_snapshot_matrix.csv` - mean-subtracted snapshot matrix.
- `mean_field.csv` - temporal mean reshaped to `5 x 5`.
- `singular_values.csv` - singular values and modal energy fractions.
- `spatial_mode_XX.csv` - normalized spatial POD modes reshaped to `5 x 5`.
- `temporal_coefficients.csv` - modal amplitudes over snapshots.
- `pod_result.json` - all key POD results in one structured file.

## Compute EPOD

```powershell
python .\toolkit_test\compute_epod.py
```

EPOD outputs are written to:

- `toolkit_test/results/epod/velocity_to_heat_flux/`
- `toolkit_test/results/epod/heat_flux_to_velocity/`

For a source field `X` and target field `Y`, the script computes:

```text
X' = U Sigma V^T
A = Sigma V^T
Psi = Y' A^T (A A^T)^(-1)
Y'_hat = Psi A
```

where:

- `A` contains source-field temporal POD coefficients.
- `Psi` contains extended spatial modes of the target field.
- `Y'_hat` is the target-field fluctuation reconstructed from source-field POD timing.

Each EPOD output folder contains:

- `extended_mode_XX.csv` - target-field pattern associated with source POD mode `XX`.
- `reconstruction_metrics.csv` - target-field reconstruction quality using 1, 2, ..., active source modes.
- `target_centered_reconstruction_all_modes.csv` - reconstructed target fluctuations.
- `target_reconstruction_all_modes.csv` - reconstructed full target field after adding the target mean.
- `epod_result.json` - all key EPOD results in one structured file.

## Visualize POD and EPOD Results

```powershell
python .\toolkit_test\plot_pod_epod.py
```

The figures are written to:

- `toolkit_test/results/figures/`

## Spectral Coherence Demonstration

```powershell
python .\toolkit_test\compute_spectral_coherence.py
```

This creates a separate long time-series example with `1024` paired velocity and heat-flux snapshots. The imposed base frequency is `f0 = 1.25`, and the imposed second harmonic is `2f0 = 2.50`.

The coherence calculation uses:

```text
C_xy(f) = |S_xy(f)|^2 / (S_xx(f) S_yy(f))
```

Outputs are written to:

- `toolkit_test/data/coherence/`
- `toolkit_test/results/coherence/`
- `toolkit_test/results/coherence/figures/`

Key outputs:

- `signals.csv` - representative time signals extracted from the fields.
- `frequency_response.csv` - coherence, phase, and spectra versus frequency.
- `coherence_peak_summary.csv` - dominant coherence peaks near the imposed frequencies.
- `pod_pair_coherence.csv` - coherence matrix between the first POD temporal coefficients.
- `coherence_summary.md` - compact explanation of the generated result.

## Transfer Entropy Demonstration

```powershell
python .\toolkit_test\compute_transfer_entropy.py
```

This computes two examples:

- Example 1 uses the current long coherence signals. These signals share a synthetic oscillator, so transfer entropy may appear in both directions.
- Example 2 creates a cleaner delayed-causal signal where `q_response(t)` depends on `u_driver(t - tau)`.

Transfer entropy is estimated as:

```text
TE_{X->Y}(lag) = I(Y_t ; X_{t-lag} | Y_{t-1})
```

Outputs are written to:

- `toolkit_test/results/transfer_entropy/`
- `toolkit_test/results/transfer_entropy/figures/`

Key outputs:

- `example1_current_common_driver_te.csv` - TE curves for the current synthetic coherence data.
- `example2_delayed_causal_te.csv` - TE curves for the delayed causal example.
- `transfer_entropy_peak_summary.csv` - peak TE by direction.
- `transfer_entropy_summary.md` - compact interpretation.

## Resolvent Analysis Demonstration

```powershell
python .\toolkit_test\compute_resolvent_analysis.py
```

This is an educational reduced-order example, not a full linearized OpenFOAM/Navier-Stokes resolvent. The model is:

```text
da/dt = A a + B f
y     = C a
H(w)  = C(i w I - A)^(-1) B
```

For each frequency, the script computes:

```text
H(w) = U Sigma V*
```

where:

- `V` gives optimal forcing directions,
- `U` gives optimal response directions,
- `Sigma` gives resolvent gains.

Outputs are written to:

- `toolkit_test/results/resolvent/`
- `toolkit_test/results/resolvent/figures/`

Key outputs:

- `resolvent_gain.csv` - singular values versus frequency.
- `resolvent_peak_summary.csv` - gain peaks near `f0` and `2f0`.
- `resolvent_summary.md` - compact interpretation.
- `*_forcing_*` and `*_response_*` CSV files - real, magnitude, and phase maps for selected modes.
