# run004b vs run007a vs run007c partial comparison

This is a partial early/transient comparison, not the final `t=0.5..2.0 s` result.

- force window: `0.5..1.3 s`
- thermal checkpoints: `0.5, 1, 1.3 s`
- reference conductivity for `Nu_wall_ref_k`: `k_ref = 0.02575224 W/(m K)`

| Run | model | Cd | Cl_rms | Q_wall W | Q_air case W | Nu_wall case-k | Nu_wall ref-k | wall-air case diff |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| run004b | baseline eConst/Boussinesq Cv=718 | 3.3594 | 0.1297 | 1.0581 | 0.9700 | 7.7243 | 5.5185 | 9.1% |
| run007a | variable props: incompressiblePerfectGas + Sutherland | 3.4722 | 0.1436 | 1.3389 | 1.7396 | 7.2813 | 7.2813 | -23.0% |
| run007c | constant props: eConst/Boussinesq capacity=1005 | 3.3594 | 0.1297 | 1.4810 | 1.3577 | 7.7243 | 7.7243 | 9.1% |

## Key Comparisons

- `run007a` vs `run004b`: Q_wall +26.54%, Nu_wall_ref_k +31.94%, Cd +3.36%.
- `run007c` vs `run004b`: Q_wall +39.97%, Nu_wall_ref_k +39.97%, Nu_wall_case_k +0.00%.
- `run007c` vs `run007a`: Q_wall +10.61%, Nu_wall_ref_k +6.08%.

## Interpretation

Using the common reference conductivity, both `run007a` and `run007c` show higher wall heat flux/Nu than the old `run004b` baseline.
However, `run007c` is higher than `run007a` in this partial window, so the increase is not primarily caused by variable properties.
When `run007c` is normalized with its matching case conductivity (`k = mu*1005/Pr`), its wall-side Nu is almost the same as the old baseline normalized with `k = mu*718/Pr`.
The air-side balance is still early-transient and lags the wall input, so final judgment should wait for the completed `t=0.5..2.0 s` window.
