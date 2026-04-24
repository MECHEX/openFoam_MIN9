# Resolvent Analysis Demonstration

This is a small educational resolvent-analysis example, not a full OpenFOAM linearization.

The linear model is:

```text
da/dt = A a + B f
y     = C a
H(w)  = C(i w I - A)^(-1) B
```

The state `a` contains two damped oscillators:

- base oscillator near `f0 = 1.25`
- second oscillator near `2f0 = 2.5`

For each frequency, SVD is applied to `H(w)`:

```text
H(w) = U Sigma V*
```

- columns of `V` are optimal forcing directions
- columns of `U` are optimal response directions
- singular values `Sigma` are amplification gains

## Gain Peaks

| label | target frequency | peak frequency | leading gain |
|---|---:|---:|---:|
| base_frequency_f0 | 1.250 | 1.250 | 2.1028 |
| second_harmonic_2f0 | 2.500 | 2.500 | 0.6341 |

## Stored Leading Modes

| label | frequency | sigma1 |
|---|---:|---:|
| f0 | 1.250 | 2.1028 |
| 2f0 | 2.500 | 0.6341 |

## Main Figures

- `figures/resolvent_gain_curves.png`
- `figures/resolvent_mode_shapes_f0.png`
- `figures/resolvent_mode_shapes_2f0.png`
- `figures/resolvent_response_phase_f0.png`
- `figures/resolvent_response_phase_2f0.png`
