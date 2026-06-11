# Run015 Re=160 Production Bracket

Purpose: narrow the Hopf/vortex-shedding onset bracket after Re=150 was steady and Re=175 was periodic.

Setup:

- Case: `/home/hexmachina/of_runs/V4b_3D_run015_re160_production`
- Parent: `/home/hexmachina/of_runs/V4b_3D_run008`
- Geometry: production V4b domain, Lin=2D, Lout=8D, Lz=1D
- Mesh: production medium, 407,440 cells
- Solver: `foamRun -solver fluid`
- MPI: 20 ranks
- `U_inf = 0.202128 m/s`
- `Re = 160`
- `endTime = 10 s`
- `maxCo = 0.8`
- Sampling: same contract as run008/run012-run014

Decision rule:

- `Cl_std` decays to near-zero in late windows: Re=160 is pre-Hopf.
- Persistent late-window oscillation plus spectral peak: Re=160 is post-Hopf.
- Ambiguous weak signal: continue bracketing with Re=155 or Re=165.
