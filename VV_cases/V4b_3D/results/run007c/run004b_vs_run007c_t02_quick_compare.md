# run004b vs run007c t=0.2 quick comparison

This is a very early startup sanity check, not a production averaging window.

| Run | capacity | Cd 0.1..0.2 | Cl_rms 0.1..0.2 | T_out mass K | Q_wall W | Q_air case-cap W | Q_air Cp1005 W | Nu_wall/k_case |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| run004b | 718 | 3.3518 | 0.1407 | 293.1503 | 1.0907 | 0.0000 | 0.0000 | 7.0019 |
| run007c | 1005 | 3.3518 | 0.1407 | 293.1502 | 1.5267 | 0.0000 | 0.0000 | 7.0019 |

## Early interpretation

- `run007c` wall heat input is +39.97% vs `run004b`.
- `run007c` case-normalized wall Nu is -0.00% vs `run004b`.
- `run007c` air-side heat pickup using its case capacity is -2.02% vs `run004b`.

At this very early time, the larger heat flux mainly follows the increased thermal conductivity/capacity scale. When Nu is normalized with the matching case conductivity, it is not comparably inflated.
