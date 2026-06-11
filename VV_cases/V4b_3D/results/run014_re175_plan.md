# Run014 Re=175 Production Bracket

Purpose: test whether the V4b production geometry has crossed the Hopf/vortex-shedding onset between the already steady Re=150 case and the expected periodic Re=200 case.

Setup:

- Case: `/home/hexmachina/of_runs/V4b_3D_run014_re175_production`
- Parent: `/home/hexmachina/of_runs/V4b_3D_run008`
- Geometry: production V4b domain, Lin=2D, Lout=8D, Lz=1D
- Mesh: production medium, 407,440 cells
- Solver: `foamRun -solver fluid`
- MPI: 20 ranks
- `U_inf = 0.2210775 m/s`
- `Re = 175`
- `endTime = 10 s`
- `maxCo = 0.8`
- Sampling: same contract as run008/run012/run013

Decision rule:

- `Cl_std` decays to near-zero in late windows: Re=175 is pre-Hopf.
- Persistent late-window oscillation plus spectral peak: Re=175 is post-Hopf.
- Ambiguous weak signal: continue bracketing with Re=185 or Re=165.
