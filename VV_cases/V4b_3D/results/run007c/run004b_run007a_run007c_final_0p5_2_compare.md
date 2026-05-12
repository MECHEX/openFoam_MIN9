# run004b vs run007a vs run007c final 0.5..2.0 smoke comparison

This is the completed short `run007c` smoke-test comparison, not a long production average.

- force window: `0.5..2.0 s`
- thermal checkpoints: `0.5, 1, 1.3, 1.5, 1.7, 2 s`
- reference conductivity for `Nu_wall_ref_k`: `k_ref = 0.02575224 W/(m K)`

| Run | model | Cd | Cl_rms | Q_wall W | Q_air case W | Nu_wall case-k | Nu_wall ref-k | wall-air case diff |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| run004b | baseline eConst/Boussinesq Cv=718 | 3.3612 | 0.1767 | 1.0591 | 1.0445 | 7.8217 | 5.5881 | 1.4% |
| run007a | variable props: incompressiblePerfectGas + Sutherland | 3.4736 | 0.1790 | 1.3396 | 1.8450 | 7.3786 | 7.3786 | -27.4% |
| run007c | constant props: eConst/Boussinesq capacity=1005 | 3.3612 | 0.1767 | 1.4824 | 1.4621 | 7.8217 | 7.8217 | 1.4% |

## Key Comparisons

- `run007a` vs `run004b`: Q_wall +26.49%, Nu_wall_ref_k +32.04%, Cd +3.34%.
- `run007c` vs `run004b`: Q_wall +39.97%, Nu_wall_ref_k +39.97%, Nu_wall_case_k +0.00%.
- `run007c` vs `run007a`: Q_wall +10.66%, Nu_wall_ref_k +6.01%.

## Interpretation

Using the common reference conductivity, both `run007a` and `run007c` show higher wall heat flux/Nu than the old `run004b` baseline.
However, `run007c` is higher than `run007a` in this completed smoke-test window, so the increase is not primarily caused by variable properties.
When `run007c` is normalized with its matching case conductivity (`k = mu*1005/Pr`), its wall-side Nu is almost the same as the old baseline normalized with `k = mu*718/Pr`.
For `run004b` and `run007c`, the wall-side and air-side heat rates close to about 1.4%, while `run007a` remains energetically inconsistent over this short window.
