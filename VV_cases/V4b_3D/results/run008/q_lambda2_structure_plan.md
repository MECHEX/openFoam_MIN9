# run008 Q/lambda2 structure-identification plan

## Purpose

Use the existing `run008` full 3D snapshots to identify vortical structures and
connect them to the local heat-transfer maps already produced for the tube and
fins.

The goal is not to replace the POD/coherence story. The goal is to name the
flow structures behind it: Karman vortices, near-junction structures, wake
recirculation, and any coherent fin-surface sweeping events that explain local
`Nu(theta,z,t)` and `Nu_local(x,t)`.

## Available inputs

- production case: `/home/hexmachina/of_runs/V4b_3D_run008`
- full 3D checkpoints every `0.08 s`
- production analysis window: `t = 2..10 s`
- high-cadence local tube Nu maps from layer `004`
- high-cadence fin Nu profiles from layer `005`
- phase reference from `Cl` Hilbert phase in layer `002`
- phase-averaged midspan fields from layer `009`

## Recommended first pass

Start with a lightweight qualitative pass before building a large new pipeline.

1. Select representative phases from layer `009`:
   - `Cl_min` / maximum `abs(Cl)`
   - `Cl` zero crossing
   - `Cl_max`
   - `Q_fins` maximum
2. For the nearest full 3D checkpoints, compute:
   - vorticity magnitude
   - `Q`-criterion
   - optionally `lambda2` if the gradient tensor output is convenient
3. Export compact VTK/VTU surfaces outside Git:
   - positive `Q` iso-surfaces
   - colored by `T`, `Ux`, or distance/phase marker
   - tube and fin walls colored by local `Nu`
4. Make a small figure set:
   - instantaneous `Q` iso-surfaces at key phases
   - near-fin/junction close-up
   - matched tube `Nu(theta,z)` or fin `Nu_local(x)` panel for the same phase

## Quantitative follow-up

If the first pass shows interpretable structures, add a compact metric layer:

- phase-bin average of positive `Q` volume in the near wake
- near-fin positive `Q` volume or circulation proxy near `z=0` and `z=Lz`
- correlation/coherence between those structure metrics and:
  - tube upper-lower Nu asymmetry
  - `Q_tube`
  - `Q_fins`
  - selected fin `Nu_local(x)` bins

This would turn the visualization into a measurable structure-to-heat-transfer
link.

## Expected interpretation

Likely structure mapping:

| structure | current evidence | Q/lambda2 role |
|---|---|---|
| Karman shedding pair | POD modes 1/2, `Cl`, `St ~= 0.154` | direct vortical identification |
| symmetric `2*f_shed` response | global local-Nu coherence at second harmonic | show repeated wall-sweeping events every half-cycle |
| tube-fin junction structures | spanwise `Nu(theta,z)` variation | verify near-fin vortical topology |
| wake recirculation | wake probes and phase-averaged midspan fields | connect recirculation position to fin/tube Nu lags |

## Decision

This is worth doing. It is the most direct next post-processing step if the
manuscript needs a stronger physical-structure figure. It should be kept
separate from the accepted `001..012` layers until the first visual pass proves
that the structures are clean enough to cite.
