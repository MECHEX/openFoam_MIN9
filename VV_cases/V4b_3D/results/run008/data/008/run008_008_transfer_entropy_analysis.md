# V4b_3D run008 transfer entropy / directionality

This is an exploratory nonlinear directionality layer. TE uses discretized signals with quantile bins and a circular-shift surrogate test. Results should be treated as support for hypotheses, not as standalone proof of causality.

## Method

- Window: `2.0..10.0 s`.
- Sampling for global/fin TE: `200.0 Hz`, `1601` samples.
- Discretization: `4` quantile bins.
- Global lags tested: `0.005, 0.010, 0.020, 0.040, 0.060, 0.080, 0.120, 0.160, 0.240, 0.320, 0.480 s`.
- Surrogates: circular source shifts, `250` for global/modal and `160` for fin x-bins.

## Global directional TE

| Source -> target | lag [s] | TE [bits] | surrogate95 | surrogate99 | p_emp | significant95 |
|---|---:|---:|---:|---:|---:|---:|
| Cl -> Q_wall | 0.240 | 0.2368 | 0.1345 | 0.1448 | 0.004 | True |
| Q_wall -> Cl | 0.080 | 0.0487 | 0.0352 | 0.0417 | 0.008 | True |
| Cl -> Q_tube | 0.080 | 0.3769 | 0.1922 | 0.2234 | 0.004 | True |
| Q_tube -> Cl | 0.080 | 0.0521 | 0.0304 | 0.0402 | 0.004 | True |
| Cl -> Q_fins | 0.240 | 0.4519 | 0.1810 | 0.2014 | 0.004 | True |
| Q_fins -> Cl | 0.080 | 0.0448 | 0.0536 | 0.0642 | 0.179 | False |
| Cl -> Nu_tube | 0.240 | 0.1413 | 0.0671 | 0.0711 | 0.004 | True |
| Nu_tube -> Cl | 0.320 | 0.0547 | 0.0251 | 0.0275 | 0.004 | True |
| Cl -> Nu_fins | 0.240 | 0.1739 | 0.0639 | 0.0710 | 0.004 | True |
| Nu_fins -> Cl | 0.320 | 0.0651 | 0.0426 | 0.0463 | 0.004 | True |
| Cl -> Nu_EB | 0.060 | 0.2602 | 0.1484 | 0.1751 | 0.004 | True |
| Nu_EB -> Cl | 0.320 | 0.0719 | 0.0269 | 0.0300 | 0.004 | True |

Significant global directions above surrogate 95%:

- `Cl -> Q_wall`: TE `0.2368` bits, lag `0.240 s`, surrogate95 `0.1345`, p_emp `0.004`
- `Q_wall -> Cl`: TE `0.0487` bits, lag `0.080 s`, surrogate95 `0.0352`, p_emp `0.008`
- `Cl -> Q_tube`: TE `0.3769` bits, lag `0.080 s`, surrogate95 `0.1922`, p_emp `0.004`
- `Q_tube -> Cl`: TE `0.0521` bits, lag `0.080 s`, surrogate95 `0.0304`, p_emp `0.004`
- `Cl -> Q_fins`: TE `0.4519` bits, lag `0.240 s`, surrogate95 `0.1810`, p_emp `0.004`
- `Cl -> Nu_tube`: TE `0.1413` bits, lag `0.240 s`, surrogate95 `0.0671`, p_emp `0.004`
- `Nu_tube -> Cl`: TE `0.0547` bits, lag `0.320 s`, surrogate95 `0.0251`, p_emp `0.004`
- `Cl -> Nu_fins`: TE `0.1739` bits, lag `0.240 s`, surrogate95 `0.0639`, p_emp `0.004`
- `Nu_fins -> Cl`: TE `0.0651` bits, lag `0.320 s`, surrogate95 `0.0426`, p_emp `0.004`
- `Cl -> Nu_EB`: TE `0.2602` bits, lag `0.060 s`, surrogate95 `0.1484`, p_emp `0.004`
- `Nu_EB -> Cl`: TE `0.0719` bits, lag `0.320 s`, surrogate95 `0.0269`, p_emp `0.004`

## Reduced fin-bin TE

- z_min significant x-bins: `16/16`.
- z_max significant x-bins: `16/16`.

Strongest fin-bin directions:

- `fin_z_min_xbin_14` at x=`10.33 mm`: TE `0.3789` bits, lag `0.080 s`, surrogate95 `0.1907`
- `fin_z_min_xbin_13` at x=`8.66 mm`: TE `0.3200` bits, lag `0.080 s`, surrogate95 `0.1698`
- `fin_z_max_xbin_10` at x=`3.81 mm`: TE `0.2478` bits, lag `0.080 s`, surrogate95 `0.1111`
- `fin_z_min_xbin_15` at x=`11.83 mm`: TE `0.3641` bits, lag `0.080 s`, surrogate95 `0.2308`
- `fin_z_min_xbin_11` at x=`5.20 mm`: TE `0.2778` bits, lag `0.080 s`, surrogate95 `0.1480`
- `fin_z_min_xbin_10` at x=`3.81 mm`: TE `0.2407` bits, lag `0.080 s`, surrogate95 `0.1147`
- `fin_z_max_xbin_11` at x=`5.20 mm`: TE `0.2677` bits, lag `0.080 s`, surrogate95 `0.1471`
- `fin_z_max_xbin_15` at x=`11.83 mm`: TE `0.3769` bits, lag `0.080 s`, surrogate95 `0.2583`

## Modal TE

Significant modal directions above surrogate 95%:

- `Cl -> POD_U_1`: TE `0.5840` bits, lag `0.320 s`, surrogate95 `0.2004`, p_emp `0.004`
- `POD_U_1 -> Cl`: TE `0.6409` bits, lag `0.320 s`, surrogate95 `0.2189`, p_emp `0.004`
- `Cl -> POD_U_2`: TE `0.6713` bits, lag `0.320 s`, surrogate95 `0.2070`, p_emp `0.004`
- `POD_U_2 -> Cl`: TE `0.4503` bits, lag `0.320 s`, surrogate95 `0.2123`, p_emp `0.004`
- `Cl -> POD_U_3`: TE `0.6330` bits, lag `0.320 s`, surrogate95 `0.0901`, p_emp `0.004`
- `POD_U_3 -> Cl`: TE `0.5979` bits, lag `0.320 s`, surrogate95 `0.0580`, p_emp `0.004`
- `Cl -> POD_U_4`: TE `0.1677` bits, lag `0.320 s`, surrogate95 `0.0808`, p_emp `0.004`
- `POD_U_4 -> Cl`: TE `0.0918` bits, lag `0.320 s`, surrogate95 `0.0587`, p_emp `0.004`
- `Cl -> POD_T_2`: TE `0.6989` bits, lag `0.320 s`, surrogate95 `0.2117`, p_emp `0.004`
- `POD_T_2 -> Cl`: TE `1.2168` bits, lag `0.040 s`, surrogate95 `0.6187`, p_emp `0.004`
- `Cl -> POD_T_3`: TE `0.1604` bits, lag `0.160 s`, surrogate95 `0.0831`, p_emp `0.004`
- `POD_T_3 -> Cl`: TE `0.0945` bits, lag `0.320 s`, surrogate95 `0.0687`, p_emp `0.004`
- `Cl -> POD_T_4`: TE `0.6832` bits, lag `0.320 s`, surrogate95 `0.1031`, p_emp `0.004`
- `POD_T_4 -> Cl`: TE `0.6188` bits, lag `0.320 s`, surrogate95 `0.0750`, p_emp `0.004`
- `POD_joint_1 -> Cl`: TE `0.2641` bits, lag `0.160 s`, surrogate95 `0.1592`, p_emp `0.004`
- `Cl -> POD_joint_2`: TE `0.6629` bits, lag `0.320 s`, surrogate95 `0.2090`, p_emp `0.004`

## Interpretation

- Treat TE here as a directionality screen. Coherence/cross-phase from layer 007 remain the safer publication-grade evidence.
- A direction is highlighted only when actual TE exceeds the circular-shift surrogate 95% threshold.
- If global heat-transfer TE is weak while coherence is strong, that usually means the coupling is periodic/phase-locked but not strongly nonlinear-directional under this short-record estimator.

## Figures

- `../../figures/008/run008_008_global_transfer_entropy.png`
- `../../figures/008/run008_008_global_te_lag_sensitivity.png`
- `../../figures/008/run008_008_fin_te_x_profiles.png`
- `../../figures/008/run008_008_modal_te_heatmap.png`
