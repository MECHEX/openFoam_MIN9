# plane_channel_Re10_UWT

## Setup

- Re_Dh: `10`
- channel gap: `0.012000 m`
- hydraulic diameter: `0.024000 m`
- length: `1.440000 m` (`60.0 D_h`)
- mesh: `360 x 60 x 1`
- bulk inlet velocity: `0.006315753 m/s`
- inlet temperature: `293.15 K`
- wall temperature: `303.15 K`
- thermal BC: uniform wall temperature on both channel walls
- benchmark: fully developed plane-channel UWT `Nu ~= 7.541`

## Notes

- This is a diagnostic solver/scheme benchmark, not a cylinder validation case.
- The outlet-local Nu should only be compared to the fully developed value after the thermal profile has settled.
