# Transfer Entropy Demonstration

This folder contains two transfer-entropy examples.

Transfer entropy is estimated as a lagged conditional mutual information:

```text
TE_{X->Y}(lag) = I(Y_t ; X_{t-lag} | Y_{t-1})
```

The continuous signals are discretized into `5` quantile bins.
A shuffled-source baseline with `60` surrogates is subtracted to reduce finite-sample bias.

## Peak Summary

| example | pair | peak lag samples | peak lag time | TE | surrogate mean | excess TE |
|---|---|---:|---:|---:|---:|---:|
| current_common_driver | u_skew_to_q_skew | 38 | 1.900 | 0.8051 | 0.0231 | 0.7820 |
| current_common_driver | q_skew_to_u_skew | 26 | 1.300 | 0.7694 | 0.0238 | 0.7456 |
| current_common_driver | u_pod_a1_to_q_pod_a1 | 24 | 1.200 | 0.9940 | 0.0313 | 0.9627 |
| current_common_driver | q_pod_a1_to_u_pod_a1 | 19 | 0.950 | 0.9681 | 0.0235 | 0.9445 |
| delayed_causal | u_driver_to_q_response | 7 | 0.350 | 1.2092 | 0.0585 | 1.1507 |
| delayed_causal | q_response_to_u_driver | 4 | 0.200 | 0.0831 | 0.0600 | 0.0231 |
| delayed_causal | independent_to_q_response | 2 | 0.100 | 0.0741 | 0.0591 | 0.0150 |

## Interpretation

- Example 1 uses the existing coherence dataset. Since velocity and heat flux are driven by a shared synthetic oscillator, TE may appear in both directions and should be interpreted as directional predictability, not proof of physical causality.
- Example 2 uses a delayed causal construction, where `q_response(t)` depends on `u_driver(t - tau)` plus its own memory and noise. The expected dominant direction is therefore `u_driver -> q_response` near the imposed delay.

## Main Figures

- `figures/te_input_signals.png`
- `figures/te_example1_current_common_driver.png`
- `figures/te_example2_delayed_causal.png`
- `figures/te_peak_summary.png`
