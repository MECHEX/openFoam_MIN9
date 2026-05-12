# run007a vs run007c t=0.2 quick comparison

This is a very early startup sanity check, not a production averaging window.
Nu is normalized with the same reference conductivity `k_ref = mu_ref*Cp_ref/Pr_ref = 0.02575224 W/(m K)` for both cases.

| Run | model | Cd 0.1..0.2 | Cl_rms 0.1..0.2 | T_out mass K | Q_wall W | Q_air Cp1005 W | Nu_wall/k_ref |
|---|---|---:|---:|---:|---:|---:|---:|
| run007a | variable props: incompressiblePerfectGas + Sutherland | 3.4687 | 0.1276 | 293.1505 | 1.3702 | 0.00006074 | 6.2841 |
| run007c | constant props: eConst/Boussinesq capacity=1005 | 3.3518 | 0.1407 | 293.1502 | 1.5267 | 0.00002584 | 7.0019 |

## Early interpretation

- `run007c` wall heat input is +11.42% versus `run007a` at `t=0.2 s`.
- `run007c` wall-side Nu using common `k_ref` is +11.42% versus `run007a`.
- Force coefficients are almost unchanged at this early time: Cd difference -3.37%.

At this very early checkpoint, the variable-property case is not producing a larger wall-side Nu than the Cp-scale constant-property fallback. The constant `1005` fallback is actually about 11% higher in wall heat flux/Nu than `run007a` when both are normalized with the same reference k.
