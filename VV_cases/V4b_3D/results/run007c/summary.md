# V4b_3D run007c - constant Cp-as-eConst smoke test

## Purpose

`run007c` is a short fallback smoke test after `run007b`
(`hConst/sensibleEnthalpy + Boussinesq`) failed during startup. It keeps the
stable `run004b` energy formulation and changes only the heat-capacity
coefficient from `718` to `1005`.

This is not a new production model. It is a diagnostic test to isolate whether
the large thermal shift seen in `run007a` is already explained by using a
`Cp`-scale heat capacity instead of the old `Cv=718` coefficient.

## Setup

| Item | Value |
|---|---|
| parent | `run004b` |
| geometry | `Lin=2D`, `Lout=8D` |
| mesh | copied corrected BL mesh |
| thermo | `eConst` |
| energy | `sensibleInternalEnergy` |
| equation of state | `Boussinesq` |
| changed coefficient | `Cv=1005` instead of `718` |
| endTime | `2 s` |
| maxCo | `0.8` |

## Planned Checks

- solver stability to `t=2 s`
- `Cd_mean`, `Cl_rms`, `St` against `run004b`
- air-side heat pickup using `1005*(T_out-T_in)`
- integrated `wallHeatFlux` over the hot patches
- whether `Nu_EB` lands near the earlier variable-property result or closer
  to the old constant-property baseline

## Early t=0.2 Quick-Look

Outputs:

- `run004b_vs_run007c_t02_quick_compare.csv`
- `run004b_vs_run007c_t02_quick_compare.json`
- `run004b_vs_run007c_t02_quick_compare.md`

This is a startup sanity check only. The outlet air has not warmed up yet, so
air-side `m_dot*C*dT` is not meaningful at `t=0.2 s`. The useful diagnostic is
the wall-side heat flux and its Nu normalization.

| Run | capacity | Cd 0.1..0.2 | Cl_rms 0.1..0.2 | Q_wall hot total | Nu_wall/k_case |
|---|---:|---:|---:|---:|---:|
| run004b | 718 | 3.3518 | 0.1407 | 1.0907 W | 7.0019 |
| run007c | 1005 | 3.3518 | 0.1407 | 1.5267 W | 7.0019 |

Interpretation: increasing the case heat-capacity scale from `718` to `1005`
increases the absolute wall heat flux by about `40%`, as expected from
`1005/718`. However, when Nu is normalized with the matching case conductivity
`k=mu*C/Pr`, the early wall-side Nu is essentially unchanged. This suggests the
previous apparent Nu jump can be strongly affected by inconsistent heat-flux
and conductivity/heat-capacity normalization, not necessarily by a changed flow
regime.

## run007b vs run007c Nu Status

Output:

- `run007b_vs_run007c_same_window_nu_status.md`
- `run007b_vs_run007c_same_window_nu_status.json`

There is no valid same-window `Nu` comparison between `run007b` and `run007c`
for the `t=0.2 s` quick-look. `run007b` failed during startup and has only the
initial `t=0` state plus one force sample. The only common thermal instant is
`t=0`, where both cases give the same artificial initial-condition wall heat
flux:

| Run | Q_wall hot total at t=0 | Nu_wall using k=mu*1005/Pr |
|---|---:|---:|
| run007b | 138.372 W | 634.63 |
| run007c | 138.372 W | 634.63 |

This value is not physically meaningful; it is the initial wall-gradient
artifact before the thermal field evolves. `run007b` should therefore be kept
only as a failed-setup diagnostic, while `run007c` remains the usable
constant-property `1005` smoke test.

## run007a vs run007c t=0.2 Quick-Look

Outputs:

- `run007a_vs_run007c_t02_quick_compare.csv`
- `run007a_vs_run007c_t02_quick_compare.json`
- `run007a_vs_run007c_t02_quick_compare.md`

This compares the variable-property `run007a` against the constant-property
`1005` fallback `run007c` at the same `t=0.2 s` checkpoint. Wall-side Nu is
normalized with the same reference conductivity
`k_ref = mu_ref*Cp_ref/Pr_ref = 0.02575224 W/(m K)`.

| Run | model | Cd 0.1..0.2 | Cl_rms 0.1..0.2 | Q_wall hot total | Nu_wall/k_ref |
|---|---|---:|---:|---:|---:|
| run007a | variable props | 3.4687 | 0.1276 | 1.3702 W | 6.2841 |
| run007c | constant capacity `1005` | 3.3518 | 0.1407 | 1.5267 W | 7.0019 |

Interpretation: at this very early checkpoint, the variable-property case is
not the reason for a larger wall-side Nu. The constant-property `1005`
fallback is about `11.4%` higher in wall heat flux and wall-side Nu than
`run007a` when both are normalized with the same reference `k`.

## Partial 0.5..1.3 Comparison

Outputs:

- `compare_run004b_run007a_run007c_partial.py`
- `run004b_run007a_run007c_partial_compare.csv`
- `run004b_run007a_run007c_partial_compare.json`
- `run004b_run007a_run007c_partial_compare.md`

This is a partial early/transient comparison while `run007c` is still running.

| Run | model | Cd | Cl_rms | Q_wall W | Q_air case W | Nu_wall case-k | Nu_wall ref-k |
|---|---|---:|---:|---:|---:|---:|---:|
| run004b | baseline `Cv=718` | 3.3594 | 0.1297 | 1.0581 | 0.9700 | 7.7243 | 5.5185 |
| run007a | variable props | 3.4722 | 0.1436 | 1.3389 | 1.7396 | 7.2813 | 7.2813 |
| run007c | constant capacity `1005` | 3.3594 | 0.1297 | 1.4810 | 1.3577 | 7.7243 | 7.7243 |

Key partial-window differences:

- `run007a` vs `run004b`: `Q_wall +26.54%`, `Nu_wall_ref_k +31.94%`,
  `Cd +3.36%`
- `run007c` vs `run004b`: `Q_wall +39.97%`, `Nu_wall_ref_k +39.97%`,
  but `Nu_wall_case_k +0.00%`
- `run007c` vs `run007a`: `Q_wall +10.61%`, `Nu_wall_ref_k +6.08%`

Interpretation: with common reference conductivity, both `run007a` and
`run007c` are above the old `run004b` baseline. But `run007c` is higher than
`run007a`, so the increase is not primarily caused by variable properties.
When `run007c` is normalized with its own matching conductivity
`k = mu*1005/Pr`, its wall-side Nu is essentially identical to old `run004b`
normalized with `k = mu*718/Pr`.

## Final 0.5..2.0 Smoke Comparison

Outputs:

- `run004b_run007a_run007c_final_0p5_2_compare.csv`
- `run004b_run007a_run007c_final_0p5_2_compare.json`
- `run004b_run007a_run007c_final_0p5_2_compare.md`

Completed `run007c` to `t=2 s` and compared against `run004b` and `run007a`
over the matched short smoke-test window.

| Run | model | Cd | Cl_rms | Q_wall W | Q_air case W | Nu_wall case-k | Nu_wall ref-k | wall-air case diff |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| run004b | baseline `Cv=718` | 3.3612 | 0.1767 | 1.0591 | 1.0445 | 7.8217 | 5.5881 | +1.4% |
| run007a | variable props | 3.4736 | 0.1790 | 1.3396 | 1.8450 | 7.3786 | 7.3786 | -27.4% |
| run007c | constant capacity `1005` | 3.3612 | 0.1767 | 1.4824 | 1.4621 | 7.8217 | 7.8217 | +1.4% |

Key final smoke-test differences:

- `run007a` vs `run004b`: `Q_wall +26.49%`, `Nu_wall_ref_k +32.04%`,
  `Cd +3.34%`
- `run007c` vs `run004b`: `Q_wall +39.97%`, `Nu_wall_ref_k +39.97%`,
  but `Nu_wall_case_k +0.00%`
- `run007c` vs `run007a`: `Q_wall +10.66%`, `Nu_wall_ref_k +6.01%`

Final smoke-test interpretation: `run007c` reproduces `run004b` almost exactly
in forces and in wall-side Nu when each case is normalized with its own
matching conductivity. The absolute heat flux rises by `~40%` simply because
the thermal capacity/conductivity scale was changed from `718` to `1005`.
Therefore the large apparent Nu jump is primarily a `Cv/Cp/k` consistency
issue, not evidence that variable properties alone strongly increase heat
transfer.

`run007a` remains physically interesting, but its short-window energy balance
is not closed: air-side `m_dot*Cp*dT` is about `27%` larger than wall-side
`wallHeatFlux`. Do not use its air-side Nu as a final production conclusion
until the variable-property energy balance is made internally consistent.
