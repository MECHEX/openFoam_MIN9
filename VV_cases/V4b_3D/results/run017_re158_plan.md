# run017_re158 plan

Purpose: midpoint production-geometry run between Re=155 steady and Re=160 shedding.

Setup:

- Case: `/home/hexmachina/of_runs/V4b_3D_run017_re158_production`
- Parent: `/home/hexmachina/of_runs/V4b_3D_run008`
- U_inf: `0.1996014 m/s`
- Re: `158`
- Mesh/domain/solver/postProcessing: same contract as run016 Re155
- Target: `10 s`
- Main diagnostic window: `8-10 s`

Decision rule:

- If late-window `Cl_rms` remains numerical-noise level, Re158 is pre-Hopf/steady and next useful point is Re159.
- If late-window `Cl_rms` grows or keeps a spectral peak, Re158 is post-Hopf/shedding and next useful point is Re157.
