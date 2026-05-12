# V4b_3D run008 wake probes and wake dynamics

Wake-probe analysis links local wake velocity/temperature signals with lift, wall heat transfer, outlet temperature, and local fin Nu.

## Probe setup

- probes: `13`
- window: `2.0..10.0 s`
- samples: `1601`
- sampling: `200.0 Hz`

## Best wake probes

- strongest `Uy` RMS: probe `2` at `(x,y)=(30.0, 0.0) mm`, RMS `0.11429 m/s`.
- highest coherence `Uy-Cl` near `f_shed`: probe `2`, coherence `0.883`, lag `Uy -> Cl` `-0.0500 s`.
- highest coherence `Uy-Q_wall` near `f_shed`: probe `6`, coherence `0.905`, lag `Uy -> Q_wall` `+0.4200 s`.
- best `Uy -> local Nu` at `f_shed`: probe `9`, `fin_z_max`, x=`6.06 mm`, coherence `0.985`.
- best `Uy -> local Nu` at `2f_shed`: probe `2`, `fin_z_max`, x=`3.64 mm`, coherence `0.994`.

## Top probes by coherence(Uy, Cl)

| probe | x [mm] | y [mm] | Uy RMS | PSD peak [Hz] | coh Uy-Cl | lag Uy->Cl [s] | coh Uy-Qwall | lag Uy->Qwall [s] |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 30.0 | 0.0 | 0.11429 | 6.641 | 0.883 | -0.0500 | 0.631 | +0.0400 |
| 8 | 40.0 | 6.0 | 0.11297 | 6.641 | 0.766 | -0.0200 | 0.592 | -0.1600 |
| 9 | 60.0 | 6.0 | 0.08198 | 6.641 | 0.568 | -0.0300 | 0.661 | -0.8600 |
| 6 | 100.0 | 0.0 | 0.05347 | 6.641 | 0.462 | -0.0600 | 0.905 | +0.4200 |
| 0 | 10.0 | 0.0 | 0.02663 | 6.641 | 0.371 | +0.0350 | 0.658 | -0.1050 |
| 10 | 20.0 | -6.0 | 0.05442 | 6.641 | 0.316 | -0.0050 | 0.223 | -0.0750 |

## Top probe/local-Nu coherence pairs

| probe | probe x [mm] | probe y [mm] | side | Nu x [mm] | coh f_shed | coh 2f_shed |
|---:|---:|---:|---|---:|---:|---:|
| 9 | 60.0 | 6.0 | fin_z_max | 6.06 | 0.985 | 0.984 |
| 9 | 60.0 | 6.0 | fin_z_max | 5.37 | 0.966 | 0.987 |
| 9 | 60.0 | 6.0 | fin_z_max | 6.76 | 0.963 | 0.984 |
| 9 | 60.0 | 6.0 | fin_z_min | 6.06 | 0.954 | 0.988 |
| 9 | 60.0 | 6.0 | fin_z_min | 3.64 | 0.951 | 0.971 |
| 9 | 60.0 | 6.0 | fin_z_max | 2.26 | 0.948 | 0.986 |
| 9 | 60.0 | 6.0 | fin_z_max | 6.41 | 0.947 | 0.982 |
| 9 | 60.0 | 6.0 | fin_z_min | 5.37 | 0.945 | 0.985 |

## Interpretation

- `Uy` probes closest to the near wake carry the strongest lift-related signal; downstream/centerline probes are useful for PSD but can lose phase specificity.
- Positive lag means the target signal lags the probe signal in the cross-correlation convention.
- Local fin Nu coherence identifies which wake probe is the best reduced sensor for heat-transfer coupling.

## Figures

- `../../figures/010/run008_010_probe_layout_coherence.png`
- `../../figures/010/run008_010_probe_uy_psd.png`
- `../../figures/010/run008_010_probe_cross_correlation_lags.png`
- `../../figures/010/run008_010_probe_to_local_nu_coherence_rank.png`
