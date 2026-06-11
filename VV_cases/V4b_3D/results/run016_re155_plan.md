# Run016 Re=155 Production Bracket

Purpose: narrow the Hopf/vortex-shedding onset bracket after Re=150 was steady and Re=160 showed growing/persistent oscillations.

Setup:

- Case: `/home/hexmachina/of_runs/V4b_3D_run016_re155_production`
- Parent: `/home/hexmachina/of_runs/V4b_3D_run008`
- Geometry: production V4b domain, Lin=2D, Lout=8D, Lz=1D
- Mesh: production medium, 407,440 cells
- Solver: `foamRun -solver fluid`
- MPI: 20 ranks
- `U_inf = 0.1958115 m/s`
- `Re = 155`
- `endTime = 10 s`
- `maxCo = 0.8`
- Sampling: same contract as run008/run012-run015

Decision rule:

- `Cl_std` decays to near-zero in late windows: Re=155 is pre-Hopf.
- Persistent or growing late-window oscillation plus spectral peak: Re=155 is post-Hopf.
- Ambiguous weak signal: continue bracketing with Re=152.5 or Re=157.5.
