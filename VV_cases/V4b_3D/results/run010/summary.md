# V4b_3D run010

Cp-consistent variable-property rerun replacing removed `run009`.

Current status:

- case path: `/home/hexmachina/of_runs/V4b_3D_run010_varprops_cp`
- parent setup: `run008`
- purpose: variable air properties with Cp-like energy capacity and dense
  movie-ready field output
- model:
  `incompressiblePerfectGas + Sutherland + eConst + sensibleInternalEnergy`
- heat capacity in `physicalProperties`: `Cv = 1005 J/(kg K)`
- naming: called `cp` because the internal-energy capacity is set to the Cp
  value used in the accepted run008 thermal scaling
- target: `t_end = 10 s`
- MPI ranks: `20`
- full-field output: every `0.02 s`
- midspan VTK: every `0.01 s`
- force/probe/wall/surface outputs: every `0.005 s`

Preparation scripts:

- `VV_cases/V4b_3D/_code/prepare_run010_varprops_cp.sh`
- `VV_cases/V4b_3D/_code/start_run010_varprops_cp_bg.sh`
- `VV_cases/V4b_3D/_code/run010_varprops_cp_foreground.sh`

Post-processing helper:

- `VV_cases/V4b_3D/results/run010/run010_q_lambda2_movie_wsl.sh`

Next steps:

1. Prepare the WSL case from run008.
2. Run `checkMesh`.
3. Run `decomposePar`.
4. Launch the solver.
5. After completion, repeat the run008/run010 global comparison and then select
   48 phase snapshots for `Q/Lambda2/vorticity`.

Partial 48-phase diagnostic:

- after a clean `stopAt writeNow`, a partial phase selection was prepared
  from the available `t = 2..5.935 s` window
- force samples in that partial window: `788`
- full `U`-field snapshots in that partial window: `198`
- selected unique phase snapshots: `48`
- 48 phase-bin coverage: no empty bins
- mean/max phase error: `0.773 deg` / `2.171 deg`
- estimated physical cycles in the partial force window: about `12.5`
- files:
  - `data/001/run010_001_partial_48_phase_snapshot_selection.csv`
  - `data/001/run010_001_partial_48_phase_times.txt`
  - `data/001/run010_001_partial_48_phase_snapshot_selection.md`

This is only a partial diagnostic. The production 48-phase selection should be
recomputed after the solver reaches `t = 10 s`.

Continuation status:

- after the partial layer-015 analysis, the solver was resumed from
  `latestTime` in tmux session `run010_varprops_cp_resume`
- resume log:
  `/home/hexmachina/of_runs/V4b_3D_run010_varprops_cp/logs/log.foamRun_parallel.20260514_resume_np20_varprops_cp`
- verified live again at `t = 5.9376 s` with 20 `foamRun` ranks running

Partial layer 015 structure/heat analysis:

- the solver was stopped cleanly at `t = 5.935 s` using `stopAt writeNow`
- `controlDict` was reset afterward to `startFrom latestTime` and
  `stopAt endTime` for later continuation
- `Q`, `Lambda2`, and `vorticity` were computed for the 48 selected partial
  phase snapshots
- VTK export outside Git:
  `/home/hexmachina/of_runs/V4b_3D_run010_varprops_cp_q_lambda2_partial48/vtk_processors`
- analysis script:
  `scripts/analyse_run010_partial_region_structure_heat_015.py`
- output directory:
  `data/015_partial`
- figure:
  `figures/015_partial/run010_015_partial_region_structure_heat_phase.png`

Selected-phase heat balance:

- `Q_wall_mean = 1.77061 W`
- `Q_air_mean = 1.77256 W`
- mean instantaneous closure over selected phases: `+0.2605%`
- `Nu_wall_mean = 9.66997`
- `Nu_EB_mean = 9.68796`

Correlation screen, 48 partial phases:

| region | corr(I_Lambda2*, paired Nu) | corr(I_Q*, paired Nu) |
|---|---:|---:|
| `R_global_control` | -0.664 | -0.732 |
| `R_sep` | -0.512 | +0.270 |
| `R_fin_junction` | -0.397 | -0.773 |
| `R_near_wake` | -0.309 | -0.461 |
| `R_far_wake` | -0.190 | -0.316 |
| `R_fin_sweep` | -0.019 | -0.413 |

Interpretation:

- Region-limited `Lambda2` remains strongest in `R_fin_junction` and `R_sep`,
  similar to run008.
- The partial heat-transfer response is much clearer than the phase variation
  of bulk `Lambda2` intensity.
- This suggests that final mechanistic interpretation should include
  structure location/convection and local wall interaction, not only integrated
  `Q/Lambda2` intensity.

Partial layer 016 lag/surrogate diagnostic:

- script:
  `scripts/analyse_run010_partial_lag_surrogates_016.py`
- outputs:
  `data/016_partial_lag_surrogates`
- figure:
  `figures/016_partial_lag_surrogates/run010_016_partial_lag_surrogate_lambda2_nu.png`
- method:
  sparse lag scan on the 48 phase-selected layer-015 snapshots, interpolated to
  `dt = 0.02 s`, with `1000` cyclic-shift surrogates
- important limitation:
  this is not a complete uniformly sampled `I_R(t)` series, so surrogate
  p-values are diagnostic only
- main result:
  the strongest apparent associations are mostly zero-lag or wrong-direction
  rather than clean positive structure-leading-heat lags
- examples for `I_Lambda2* -> Nu`:
  - `R_sep -> Nu_tube_wall`: `rho* = -0.465`, `tau* = 0.000 s`
  - `R_near_wake -> Nu_tube_wall`: `rho* = -0.480`, `tau* = 0.000 s`
  - `R_fin_junction -> Nu_wall`: `rho* = -0.376`, not significant in this
    sparse diagnostic
  - `R_far_wake -> Nu_fins_wall`: `rho* = -0.398`, `tau* = +0.280 s`, but this
    is longer than `T_shed/2` and should be treated as likely alias/phase-wrap
- interpretation:
  the partial data do not yet support a causal statement that regional
  `Q/Lambda2` activity precedes local heat-transfer response. The final test
  should use a uniformly sampled vortex-intensity series after the full
  `t = 10 s` run is available.

Available-time layer 017 uniform lag/surrogate diagnostic:

- the solver was stopped cleanly again at about `t = 7.526 s`
- `Q` and `Lambda2` were computed with `foamPostProcess` for the currently
  available decomposed time directories in `t = 2..7.526 s`
- script:
  `scripts/analyse_run010_available_uniform_lag_surrogates_017.py`
- outputs:
  `data/017_available_uniform_lag_surrogates`
- figure:
  `figures/017_available_uniform_lag_surrogates/run010_017_available_uniform_lag_surrogate_lambda2_nu.png`
- method:
  region-limited `I_Q^R(t)` and `I_Lambda2^R(t)` were computed directly from
  decomposed OpenFOAM fields on a uniform `dt = 0.02 s` grid
- analysis window:
  `t = 2.000..7.520 s`, `277` samples
- cyclic-shift surrogates:
  `1000`
- heat balance on the layer-017 grid:
  - `Q_wall_mean = 1.76956 W`
  - `Q_air_mean = 1.76760 W`
  - `closure_mean = +0.4789%`
  - `Nu_wall_mean = 9.65838`
  - `Nu_EB_mean = 9.65495`
- selected `I_Lambda2* -> Nu` results:
  - `R_near_wake -> Nu_tube_wall`: `rho* = +0.839`, `tau* = -0.080 s`
    (strong but wrong direction for structure-leading-heat)
  - `R_sep -> Nu_tube_wall`: `rho* = -0.514`, `tau* = +0.160 s`
    (significant, but lag is slightly above `T_shed/2` and the sign is
    anticorrelated)
  - `R_fin_sweep -> Nu_fins_wall`: `rho* = +0.745`, `tau* = +0.220 s`
    (significant, but lag is above `T_shed/2`)
  - `R_far_wake -> Nu_fins_wall`: `rho* = +0.297`, `tau* = +0.160 s`
    (weak and beyond the accepted lag window)
- strongest screen across all tested structure/response signals:
  `R_fin_sweep -> Nu_fins_wall` using `I_Q* -> Nu`, with
  `rho* = -0.785`, `tau* = +0.020 s`; this is a statistically strong
  positive-lag anticorrelation, not a "more vortex gives more Nu" result
- interpretation:
  layer 017 is much stronger than layer 016 because it uses a uniformly sampled
  time series. It still does not yet provide a clean positive causal statement
  that increased regional vortex intensity precedes increased local `Nu`.
  The main message is phase-locked coupling with sign/lag complexity. Repeat
  after `t = 10 s` for the final paper-grade version.
- continuation:
  after layer 017, `controlDict` was reset to `startFrom latestTime` and
  `stopAt endTime`, and the solver was resumed in tmux from about `t = 7.53 s`
  with log
  `/home/hexmachina/of_runs/V4b_3D_run010_varprops_cp/logs/log.foamRun_parallel.20260514_resume2_np20_varprops_cp`

Available-time layer 018 decycling/envelope/phase-consistency diagnostic:

- script:
  `scripts/analyse_run010_available_signal_decycling_018.py`
- outputs:
  `data/018_available_signal_decycling`
- figure:
  `figures/018_available_signal_decycling/run010_018_decycled_envelope_lambda2_nu.png`
- inputs:
  layer-017 uniform `I_Q^R(t)`, `I_Lambda2^R(t)`, and heat-transfer time
  series
- methods:
  1. least-squares removal of `f_shed` and `2*f_shed` from both signals,
  2. Hilbert/analytic-signal envelope cross-correlation,
  3. phase consistency check between `f_shed` and `2*f_shed`
- main interpretation:
  decycled residual correlations often remain, but they generally do not
  become a clean positive-lag positive-correlation mechanism. The coupling is
  therefore not just numerical noise, but much of it is still phase-locked and
  sign/lag dependent.
- selected results for `I_Lambda2* -> Nu`:
  - `R_sep -> Nu_tube_wall`: after decycling, strongest signed relation
    `rho = -0.554` at `tau = +0.160 s`; envelope test is not significant
  - `R_near_wake -> Nu_tube_wall`: after decycling, `rho = +0.731` at
    `tau = -0.080 s`; strong, but wrong direction for structure-leading heat
  - `R_fin_junction -> Nu_wall`: envelope gives `rho = +0.653` at
    `tau = +0.300 s`; too long for a clean convection-delay claim
  - `R_fin_sweep -> Nu_fins_wall`: after decycling, `rho = +0.701` at
    `tau = -0.240 s`; envelope gives `rho = +0.680` at `tau = -0.080 s`,
    both wrong direction
  - `R_far_wake -> Nu_fins_wall`: envelope is not significant
- harmonic phase test:
  most pairs show nonzero `phase(2f)-2 phase(f)` mismatch, so a single true
  time-delay interpretation is weak. The result looks more like
  mode-specific phase locking than one convective delay.
- practical conclusion:
  layer 018 strengthens the interpretation that the structure/heat relation is
  real but not monotonic. It does not support the simple claim
  "more regional vortex activity precedes higher local Nu." It supports a more
  careful claim about phase-locked, region-dependent wall-interaction dynamics.
