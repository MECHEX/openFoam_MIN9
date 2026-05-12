# run007b vs run007c same-window Nu status

## Requested Check

Compare `Nu` between:

- `run007b`: attempted `hConst + sensibleEnthalpy + Boussinesq`, `Cp=1005`
- `run007c`: fallback stable `eConst + sensibleInternalEnergy + Boussinesq`,
  capacity coefficient changed to `1005`

using the same early window as the `run004b` vs `run007c` quick-look.

## Data Availability

The same `t=0.2 s` thermal comparison cannot be made:

| Run | status | available reconstructed thermal time | force samples |
|---|---|---:|---:|
| `run007b` | failed during startup | only `0` | 1 sample at `t=0` |
| `run007c` | running normally | `0.2` available | many samples |

`run007b` failed before writing any meaningful post-startup checkpoint, so it
has no valid `t=0.2` field for outlet temperature, wall heat flux, or Nu.

## Only Common Instant: t=0

`wallHeatFlux` can technically be evaluated at `t=0`, but this is an initial
condition artifact, not a physically useful Nu comparison.

| Run | Q_wall hot total at t=0 | Nu_wall using k=mu*1005/Pr |
|---|---:|---:|
| `run007b` | 138.372 W | 634.63 |
| `run007c` | 138.372 W | 634.63 |

This equality only says that both cases share the same initial mesh and
temperature boundary fields. The value is enormous because it is the artificial
initial wall gradient before the thermal field evolves. It should not be used
as a heat-transfer result.

## Conclusion

There is no valid same-window Nu comparison between `run007b` and `run007c` for
`t=0.2 s` or `0.1..0.2 s`. `run007b` is a failed thermophysical setup, not a
usable case. The correct comparison path is:

- use `run007c` for the constant-property `1005` diagnostic,
- compare `run007c` against `run004b` at `t=0.2`, then later at `0.5 s` and
  `2.0 s`,
- do not use `run007b` Nu except as evidence that `hConst+Boussinesq` is not
  viable in this setup.
