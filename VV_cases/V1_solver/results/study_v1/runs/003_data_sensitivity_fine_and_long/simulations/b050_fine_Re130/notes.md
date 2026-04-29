# b050_fine_Re130

## Input

- purpose: fine-mesh onset lower bound, β=0.50
- beta: 0.50
- Re: 130
- U_max: 0.164233 m/s
- U_bulk: 0.109489 m/s
- mesh: fine
- downstream_D: 20D
- cells: 123,502
- so_Re_crit: 124.09, so_St_crit: 0.3393

## Mesh quality

- cells: 123,502
- max non-orthogonality: 61.5°
- max skewness: 0.36 (OK)

## Run status

- t_reached: 5.1s (endTime=15s, stopped early)
- averaging window: t=3–5.1s
- regime: **STEADY**

## Force metrics

- Cd_mean: 2.833
- Cl_rms: 0.0013 (noise-level; no physical shedding)
- St: N/A

## Notes

Flow is steady at Re=130 with fine mesh. Cl oscillates at numerical-noise amplitude (~1.3e-3) alternating every timestep — this is not physical shedding (expected St≈0.34 → f≈3 Hz → T≈0.32s; noise period ≈ 2×Δt ≈ 7e-4s). Simulation incomplete (34% of endTime), but 16 expected shedding periods have passed without onset.

Contrasts with run002 bracket study (medium mesh) where Re=130 was found to be in the periodic bracket. Suggests fine mesh raises onset Re or the case needs perturbation to trigger shedding.
