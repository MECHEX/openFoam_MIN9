# plane_channel_Re100_UWT

## Setup

- Re_Dh: `100`
- channel gap: `0.012000 m`
- hydraulic diameter: `0.024000 m`
- length: `1.440000 m` (`60.0 D_h`)
- mesh: `360 x 60 x 1`
- bulk inlet velocity: `0.06315753 m/s`
- inlet temperature: `293.15 K`
- wall temperature: `303.15 K`
- thermal BC: uniform wall temperature on both channel walls
- benchmark: fully developed plane-channel UWT `Nu ~= 7.541`

## Notes

- This is a diagnostic solver/scheme benchmark, not a cylinder validation case.
- The outlet-local Nu should only be compared to the fully developed value after the thermal profile has settled.
- Analysis after the interrupted run used the latest written time, `t = 40.001357 s`.
- The temperature field remained bounded: `293.1744 K <= T <= 303.1500 K`.
- The local downstream comparison at `x/D_h = 12.083` gave `Nu = 7.5643`, only `+0.31%` above the analytic plane-channel UWT target `Nu = 7.5410`.
- The outlet plane was thermally saturated, so the accepted diagnostic comparison uses a downstream but still well-conditioned local station rather than the outlet denominator.
