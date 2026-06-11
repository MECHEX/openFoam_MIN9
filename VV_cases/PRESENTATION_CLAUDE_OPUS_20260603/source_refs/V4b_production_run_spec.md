# V4b_3D run008 - production run specification

## Purpose and Accepted Setup

`run008` is the proposed production run after the domain, timestep, and
`Cv/Cp/k` checks. It should use the accepted `run004b/run007c` geometry and
mesh:

- `Re = 200`
- `Lin = 2D`, `Lout = 8D`
- corrected BL mesh, `407,440` cells
- `maxCo = 0.8`
- OpenFOAM `foamRun -solver fluid`
- thermophysics from `run007c`: `eConst + Boussinesq + sensibleInternalEnergy`
  with capacity coefficient `1005`, `mu = 1.827e-05`, `Pr = 0.713`

Do **not** use `run007a` as production physics yet. It is useful as a
variable-property experiment, but its short-window air-side heat balance did
not close.

## Record Length

The measured shedding frequency is about `3.25 Hz`, so
`T_shed ~= 0.31 s`. The useful averaging window must cover at least
`20*T_shed ~= 6.2-6.4 s` after startup transient.

Production target:

- `t_end = 10 s`
- discard transient: `t < 2 s`
- useful window: `t = 2..10 s`, about `8 s` or `~26*T_shed`

This is the minimum credible production record for spectra, coherence,
transfer entropy, and mean/rms force/thermal statistics.

## Sampling and Storage

Use two output layers:

- full 3D checkpoint fields every `T_shed/4 ~= 0.08 s`
- reduced post-processing data at higher cadence

Recommended full-field write:

- `writeControl adjustableRunTime`
- `writeInterval 0.08`
- fields: `U`, `p`, `p_rgh`, `T`, `rho` if available
- expected count to `10 s`: about `125` full 3D frames

Midspan/POD snapshots:

- midspan `z=0` slice every `0.02 s`
- this is `<= T_shed/15`
- useful-window count `2..10 s`: about `400` slices
- fields: `U`, `T`, `p_rgh`, optional vorticity in post

Probes:

- keep 200 Hz explicitly, not by timestep-count
- `writeControl adjustableRunTime`
- `writeInterval 0.005`
- fields: `U`, `p`, `p_rgh`, `T`, and `rho` if present
- locations: keep the current wake probe line unless a separate probe-layout
  change is documented

## Surface Sampling for Heat-Transfer Coherence

Add surface sampling at `0.005 s` for local heat-transfer signals. This is
required for `Cl <-> Nu` coherence and transfer entropy.

Hot tube:

- sample `q''(theta,z,t)` on `hot_tube`
- compute `theta = atan2(y, x)` around the tube centre
- retain `z` coordinate
- compute `Nu(theta,z,t) = q'' D / [k (T_hot - T_in)]`
- store both raw face data and binned `(theta,z)` maps

Hot fins:

- sample `q''(x,y,t)` on `hot_fin_z_min` and `hot_fin_z_max`
- compute local/binned `Nu_local(x,t)`, with y-averaging documented
- retain raw face data so the binning can be changed later

Implementation note:

- use `wallHeatFlux` in solver context to generate local wall heat flux
- use sampled patch/surface output for `wallHeatFlux` and `T`
- use a post-processing script to convert face coordinates to
  `theta,z` or `x` bins and to write compact CSV/Parquet/HDF5 summaries

## Force Output Contract

Write both `forceCoeffs` and raw `forces`.

`forceCoeffs.dat` columns are:

- `Time`
- `Cm`
- `Cd`
- `Cl`
- `Cl(f)`
- `Cl(r)`

Add a `forces` function object for `hot_tube` with output every `0.005 s`.
OpenFOAM 13 `forces.dat` writes:

- `Time`
- `CofR = (x y z)`
- `forces(pressure viscous)`:
  `(Fx_p Fy_p Fz_p) (Fx_v Fy_v Fz_v)`
- `moments(pressure viscous)`:
  `(Mx_p My_p Mz_p) (Mx_v My_v Mz_v)`

Derived totals must be computed explicitly:

- `Fx = Fx_p + Fx_v`
- `Fy = Fy_p + Fy_v`
- `Fz = Fz_p + Fz_v`
- `Mx = Mx_p + Mx_v`
- `My = My_p + My_v`
- `Mz = Mz_p + Mz_v`

This avoids repeating the `run003` ambiguity about force columns.

## Launch Decision

Do not launch `run008` until:

- this specification is accepted,
- `controlDict` changes are reviewed,
- storage estimate is accepted,
- a start script and stop/restart procedure are written,
- a post-run analysis script path is reserved.
