# Re10_long100s

## Setup

- study: V2a unconfined heated cylinder
- architecture: `buoyantBoussinesqPimpleFoam` with `g = 0`
- Reynolds number: `10`
- inlet velocity: `0.012632 m/s`
- inlet temperature: `293.15 K`
- wall temperature: `303.15 K`
- diameter: `0.012000 m`
- upstream length: `15.0D`
- downstream length: `30.0D`
- domain height: `20.0D`

## Intended outputs

- mean Nusselt number `Nu`
- mean drag coefficient `Cd`
- shedding metric `St` for unsteady cases

## Results (run002, t=30s, addLayers=false)

- Nu = 5.9962  ← **WRONG**, expected ~1.86
- Nu_last_written_time = 5.9888
- Nu_samples = 30
- Cd_mean = 2.0724  ← low, expected ~2.8–3.0 for Re=10
- St = None
- Nu_Lange = 1.8101
- Nu_Bharti = 1.8623

## Diagnostics (2026-04-11)

Post-processing diagnostic on t=30s result revealed:

### T field is non-physical
- Global T range: **197.4 K – 337.4 K** (should be 293.15–303.15 K)
- Near-wall cells (owner of cylinder patch faces): 320 of 448 have T_P > T_W=303.15 K (max 305.5 K)
- 12 near-wall cells have T_P < T_IN=293.15 K (min 292.4 K)
- This causes inflated snGrad and thus inflated Nu

### snGrad statistics for cylinder patch at t=30s
- delta_perp: mean=2.4e-4 m (first cell ~0.24 mm from wall) — reasonable
- T_P mean = 301.95 K, expected ~302.8 K for Nu=1.86
- snGrad mean = 4986 K/m, expected 1550 K/m for Nu=1.86
- snGrad range: -9574 to +38787 K/m — huge scatter, confirms non-physical T

### Root cause hypotheses
1. **`limitedLinear01 1` not preventing overshoot** — global T goes to 197 K and 337 K, far outside [T_IN, T_W]. Scheme may not be bounding T in practice (only limits the limiter in [0,1], does not hard-clip).
2. **Startup transient not decayed** — t=30s may be too short; T field still carries artifacts from initial condition (U IC = (U_inf,0,0), T IC = T_IN everywhere). The thermal convection time scale L_out/U_inf ≈ 0.36/0.013 ≈ 28s.
3. **snappyHexMesh z-refinement** — even with `addLayers false`, snappy creates 8 z-layers near cylinder due to level-3 surface refinement. With `empty` patches this should be OK, but may be causing marginal non-2D effects.
4. **Nu method validation** — snGrad approach assumes T_P < T_W always; if T_P > T_W for some cells it gives negative contribution that distorts the area-weighted mean.

### Suggested fixes / next steps
- [ ] Switch div(phi,T) scheme to `Gauss vanLeer01` or `Gauss MUSCL01` which are truly bounded (TVD) for scalar transport; alternatively try `Gauss upwind` as a first diagnostic
- [ ] Run longer (100s) to fully develop the thermal field
- [ ] Print Nu(t) series to check if it is converging toward 1.86 or stabilizing near 6
- [ ] Check if Cd is also converging (expected ~2.8–3.0)
- [ ] Consider filtering out faces with negative (T_W - T_P) from Nu average
