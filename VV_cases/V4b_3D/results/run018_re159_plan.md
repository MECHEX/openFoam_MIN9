# run018_re159 plan

Purpose: final midpoint production-geometry run between Re=158 steady and Re=160 shedding.

Setup:

- Case: `/home/hexmachina/of_runs/V4b_3D_run018_re159_production`
- Parent: `/home/hexmachina/of_runs/V4b_3D_run008`
- U_inf: `0.2008647 m/s`
- Re: `159`
- Mesh/domain/solver/postProcessing: same contract as run016/Re155 and run017/Re158
- Target: `10 s`
- Main diagnostic window: `8-10 s`

Decision rule:

- If late-window `Cl_rms` remains numerical-noise level, Re159 is pre-Hopf/steady and current onset bracket becomes Re159-Re160.
- If late-window `Cl_rms` grows or keeps a spectral peak, Re159 is post-Hopf/shedding and current onset bracket becomes Re158-Re159.
