# V4b_3D run008

Production run completed.

Current status:

- case path: `/home/hexmachina/of_runs/V4b_3D_run008`
- parent setup: `run007c`
- model: constant-property `eConst + Boussinesq + sensibleInternalEnergy`
  with capacity coefficient `1005`
- target: `t_end = 10 s`
- useful analysis window: `t = 2..10 s`
- MPI ranks: `20`
- launch tag: `20260508_np20_production`
- parent MPI PID: `1202`
- solver log:
  `/home/hexmachina/of_runs/V4b_3D_run008/logs/log.foamRun_parallel.20260508_np20_production`
- final time: `10 s`
- final checkpoint: `processor*/10`
- final ClockTime: `50909 s`
- termination: `End` / `Finalising parallel run`

Initial checks:

- normal `checkMesh`: `Mesh OK`
- solver entered the time loop
- 20 `foamRun` worker processes active
- initial `Co_max` stayed below `0.8`
- residuals and continuity errors finite
- first `0.005 s` post-processing outputs were created for:
  `forceCoeffs`, `forces_raw`, `probes_wake`, `wallHeatFlux`,
  `hot_tube_surface`, and `hot_fin_surface`
- `midspan_z0` surface output directory is present

Completion/storage check:

- no active `mpirun` / `foamRun` process remains
- `processor*/10` exists for all 20 ranks
- final case size: about `17 GB`
- surface/slice output counts:
  - `hot_tube_surface`: `2001` files
  - `hot_fin_surface`: `4002` files
  - `midspan_z0`: `501` files

Analysis reset:

- previous loose production/POD/coupling analysis artifacts were removed
- current analysis state contains only the foundation audit and uncertainty pass
- current script: `scripts/analyse_run008_audit_uncertainty.py`

Audit result for the primary window `t = 2..10 s`:

- effective record length: `25.98` shedding cycles
- `forceCoeffs`, `forces_raw`, `wallHeatFlux`, `hot_tube_surface`,
  `hot_fin_surface`, `midspan_z0`, and reconstructed outlet `T/phi` are
  complete on their intended time grids
- `Cd_mean = 3.361014 +/- 0.000772`
- `Cl_rms = 0.176441 +/- 0.011097`
- `St = 0.154261 +/- 0.009574`
- `Nu_EB = 7.770004 +/- 0.091573`
- `Nu_wall = 7.816521 +/- 0.012286`
- wall-air closure = `+0.706 +/- 1.075%`

Current audit outputs:

- `data/001/run008_audit_uncertainty.md`
- `data/001/run008_audit_uncertainty.json`
- `data/001/run008_audit_sampling_completeness.csv`
- `data/001/run008_audit_window_uncertainty.csv`
- `figures/001/run008_audit_sampling_completeness_cadence.png`
- `figures/001/run008_audit_effective_record_length.png`
- `figures/001/run008_audit_block_bootstrap_uncertainty.png`
- `figures/001/run008_audit_window_sensitivity.png`

Aerodynamic layer `002`:

- script: `scripts/analyse_run008_aerodynamics.py`
- output report: `data/002/run008_002_aerodynamics.md`
- raw-force decomposition is cylinder-only and consistent with `forceCoeffs`
  to roundoff because both function objects use `patches (hot_tube)` and
  `rhoInf = 1.205`
- every-second `Cl` peak gives `f_shed = 3.2787 Hz`, `St = 0.15572`
- adjacent `Cl` peak component is `6.5574 Hz`; PSD power is dominated by this
  `2*f_shed` component
- pressure dominates mean and fluctuating lift/drag:
  `Cd_p = 2.9036`, `Cd_v = 0.4574`, `Cl_p,rms = 0.1638`,
  `Cl_v,rms = 0.0145`
- figures:
  - `figures/002/run008_002_force_pressure_viscous_decomposition.png`
  - `figures/002/run008_002_force_psd_harmonics.png`
  - `figures/002/run008_002_phase_portraits_hilbert.png`
  - `figures/002/run008_002_phase_conditioned_cycle.png`

Heat-balance layer `003`:

- script: `scripts/analyse_run008_heat_balance.py`
- output report: `data/003/run008_003_heat_balance.md`
- ratio-of-means wall-air closure: `+0.706%`
- instantaneous closure: mean `+0.914%`, std `4.661%`
- `Q_air = 1.4703 W`, `Q_wall = 1.4807 W`
- `Q_tube = 0.3618 W`, `Q_fins = 1.1189 W`
- tube/fins heat share: `24.43%` / `75.57%`
- `Nu_tube_wall = 8.4344`, `Nu_fins_wall = 7.6357`,
  `Nu_total_wall = 7.8165`, `Nu_EB = 7.7668`
- `Nu_wall` and `Nu_EB` differ by `+0.640%`
- lag estimate gives `Q_wall -> Q_air` about `+1.66 s`, but correlation is
  weak (`~0.15`), so this is diagnostic rather than a robust convection-time
  conclusion
- figures:
  - `figures/003/run008_003_heat_balance_timeseries_closure.png`
  - `figures/003/run008_003_heat_balance_lag.png`
  - `figures/003/run008_003_heat_shares_and_nu.png`
  - `figures/003/run008_003_nu_eb_vs_wall_scatter.png`

Local tube Nu layer `004`:

- script: `scripts/analyse_run008_tube_local_nu.py`
- output report: `data/004/run008_004_tube_local_nu.md`
- local definition: `Nu(theta,z,t) = q'' D / (k LMTD(t))`
- phase reference: `Cl` analytic signal from layer `002`
- samples: `1601`, bins: `96 x 30` in `theta,z`, phase bins: `32`
- `Nu_mean_area_proxy = 8.5881`
- `Nu_rms_area_proxy = 0.0978`
- `A1_mean = 0.0253`, `A1_max = 0.0630`
- `A2_mean = 0.0215`, `A2_max = 0.0596`
- peak z-averaged mean Nu occurs near `theta = 155.6 deg`
- mean angular asymmetry magnitude: `0.2909 Nu`, max `1.3253 Nu`
- global upper-lower Nu asymmetry correlates strongly with lift:
  `corr(upper-lower Nu, Cl) = +0.900`, best short-lag corr `+0.922`
  at `-0.005 s`
- figures:
  - `figures/004/run008_004_tube_nu_maps_mean_rms_harmonics.png`
  - `figures/004/run008_004_tube_nu_phase_asymmetry_maps.png`
  - `figures/004/run008_004_tube_phase_averaged_nu_maps.png`
  - `figures/004/run008_004_tube_nu_theta_profiles_asymmetry.png`
  - `figures/004/run008_004_tube_nu_z_characteristic_angles.png`
  - `figures/004/run008_004_tube_asymmetry_vs_cl.png`

Local fin Nu layer `005`:

- script: `scripts/analyse_run008_fin_local_nu.py`
- output report: `data/005/run008_005_fin_local_nu.md`
- local definition: `Nu_local(x,t) = q''(x,t) D / (k LMTD(t))`
- samples: `1601`, x bins: `80`, valid bins per fin: `61`
- mean Nu:
  - `hot_fin_z_min = 4.5669`
  - `hot_fin_z_max = 4.5412`
- mean RMS Nu:
  - `z_min = 0.0482`
  - `z_max = 0.0498`
- harmonic amplitudes:
  - `A1_mean z_min/z_max = 0.0136 / 0.0130`
  - `A2_mean z_min/z_max = 0.0095 / 0.0111`
- fin symmetry:
  - mean absolute antisymmetric component `0.0148 Nu`
  - mean fin-pair time correlation `0.858`
  - `A1` phase difference `z_max-z_min = -3.33 deg`
  - median lag difference `z_max-z_min = +0.0000 s`
- coupling to `Cl`:
  - mean coherence near `f_shed`: `0.606` on `z_min`, `0.613` on `z_max`
  - active coupled zones: `50.8%` of valid x bins on `z_min`, `49.2%` on `z_max`
  - median lag estimates: `-0.075 s` on both fin sides
- figures:
  - `figures/005/run008_005_fin_nu_x_profiles.png`
  - `figures/005/run008_005_fin_phase_coherence_lag.png`
  - `figures/005/run008_005_fin_nu_xt_maps.png`
  - `figures/005/run008_005_fin_active_coupled_zones.png`

Modal layer `006`:

- script: `scripts/analyse_run008_modal_006.py`
- output report: `data/006/run008_006_modal_analysis.md`
- source: `midspan_z0`, `t = 2..10 s`, `401` snapshots, `13524` points
- POD sets:
  - `U`
  - `T`
  - RMS-scaled joint `U+T`
- POD energy:
  - `U` modes 1/2: `40.70% / 40.52%`
  - `T` modes 1/2: `39.70% / 38.27%`
  - joint `U+T` modes 1/2: `40.22% / 39.76%`
- pair dominance:
  - `U` modes 1+2 contain `87.45%` of first-8-mode energy
  - `T` modes 1+2 contain `84.00%` of first-8-mode energy
- strongest correlations:
  - `T` POD mode 1 with `Cl`: `-0.9865`
  - joint POD mode 1 with `Cl`: `-0.9781`
  - `U` POD mode 1 with `Cd`: `-0.8503`
- DMD sanity-check frequencies:
  - near `f_shed`: `3.3577 Hz`
  - near `2*f_shed`: `6.5695 Hz`
- figures:
  - `figures/006/run008_006_pod_energy.png`
  - `figures/006/run008_006_pod_phase_portraits.png`
  - `figures/006/run008_006_pod_mode_maps.png`
  - `figures/006/run008_006_pod_signal_correlations.png`
  - `figures/006/run008_006_epod_spod_maps.png`
  - `figures/006/run008_006_dmd_sanity_modes.png`

Coherence / cross-spectral layer `007`:

- script: `scripts/analyse_run008_coherence_007.py`
- output report: `data/007/run008_007_coherence_analysis.md`
- global coherence with `Cl`:
  - `Q_wall`: `0.571` at `f_shed`, `0.906` at `2*f_shed`
  - `Q_tube`: `0.736` at `f_shed`, `0.945` at `2*f_shed`
  - `Q_fins`: `0.376` at `f_shed`, `0.922` at `2*f_shed`
  - `Nu_tube`: `0.561` at `f_shed`, `0.950` at `2*f_shed`
  - `Nu_fins`: `0.436` at `f_shed`, `0.991` at `2*f_shed`
- spatial coherence:
  - tube mean coherence: `0.454` at `f_shed`, `0.977` at `2*f_shed`
  - tube active fraction with coherence > 0.5 at `f_shed`: `23.2%`
  - fin mean coherence at `f_shed`: `0.393` (`z_min`), `0.430` (`z_max`)
  - fin mean coherence at `2*f_shed`: `0.967` (`z_min`), `0.980` (`z_max`)
- lag diagnostics:
  - tube median cross-phase lag at `f_shed`: `-0.0996 s`
  - tube median cross-correlation lag at `f_shed`: `+0.0000 s`
- figures:
  - `figures/007/run008_007_global_coherence_crossphase.png`
  - `figures/007/run008_007_tube_coherence_lag_maps.png`
  - `figures/007/run008_007_fin_coherence_lag_profiles.png`

Transfer entropy / directionality layer `008`:

- script: `scripts/analyse_run008_transfer_entropy_008.py`
- output report: `data/008/run008_008_transfer_entropy_analysis.md`
- method:
  - exploratory quantile-discretized TE
  - 4 bins
  - circular-shift surrogate test
  - 250 surrogates for global/modal signals
  - 160 surrogates for reduced fin x-bins
- strongest global directions above surrogate 95%:
  - `Cl -> Q_wall`: `0.2368 bits`, lag `0.240 s`, surrogate95 `0.1345`
  - `Cl -> Q_tube`: `0.3769 bits`, lag `0.080 s`, surrogate95 `0.1922`
  - `Cl -> Q_fins`: `0.4519 bits`, lag `0.240 s`, surrogate95 `0.1810`
  - `Cl -> Nu_tube`: `0.1413 bits`, lag `0.240 s`, surrogate95 `0.0671`
  - `Cl -> Nu_fins`: `0.1739 bits`, lag `0.240 s`, surrogate95 `0.0639`
  - `Cl -> Nu_EB`: `0.2602 bits`, lag `0.060 s`, surrogate95 `0.1484`
- weaker reverse-direction TE also appears for several global pairs; interpret this as common periodic/phase-locked dynamics rather than direct thermal feedback to lift
- reduced fin-bin result:
  - significant `Cl -> Nu_local(x)` bins: `16/16` on `z_min`, `16/16` on `z_max`
  - strongest bins occur around `x ~= 3.8..11.8 mm`, with best TE about `0.38 bits`
- modal result:
  - many POD coefficients show significant TE in both directions relative to `Cl`
  - this is expected for a low-dimensional shedding oscillator and should be treated as directionality screening, not causal proof
- figures:
  - `figures/008/run008_008_global_transfer_entropy.png`
  - `figures/008/run008_008_global_te_lag_sensitivity.png`
  - `figures/008/run008_008_fin_te_x_profiles.png`
  - `figures/008/run008_008_modal_te_heatmap.png`

Phase-averaging physical-story layer `009`:

- script: `scripts/analyse_run008_phase_averaging_009.py`
- output report: `data/009/run008_009_phase_averaging_analysis.md`
- phase definition:
  - Hilbert phase of `Cl` from layer `002`
  - 16 phase bins over `t = 2..10 s`
- processed fields/signals:
  - `Cl`, `Cd`, `Cm`
  - `Q_wall`, `Q_tube`, `Q_fins`
  - `Nu_tube_wall`, `Nu_fins_wall`, `Nu_EB`
  - tube `Nu(theta,z,phi)`
  - fin `Nu_local(x,phi)`
  - midspan phase-averaged `U`, `T`
- key phase events:
  - maximum `abs(Cl)` occurs at phase `236.25 deg` and corresponds to `Cl_min`
  - `Cl_max`: `281.25 deg`, lag `+45.0 deg` / `+0.0381 s`
  - `Q_tube_max`: `236.25 deg`, lag `+0.0 deg` / `+0.0000 s`
  - `Q_fins_max`: `303.75 deg`, lag `+67.5 deg` / `+0.0572 s`
  - `Q_wall_max`: `303.75 deg`, lag `+67.5 deg` / `+0.0572 s`
  - `Nu_tube_wall_max`, `Nu_fins_wall_max`, and `Nu_EB_max`: `123.75 deg`, lag `-112.5 deg` / `-0.0953 s`
- physical interpretation:
  - tube integrated heat pickup peaks with maximum `abs(Cl)`
  - fins and total wall heat pickup peak later by about `0.057 s`
  - wall/Nu maxima are phase-locked but not identical to instantaneous integrated `Q`, because the LMTD/outlet-based normalization and local redistribution matter
- figures:
  - `figures/009/run008_009_phase_global_cycle.png`
  - `figures/009/run008_009_tube_nu_phase_grid.png`
  - `figures/009/run008_009_fin_nu_phase_map.png`
  - `figures/009/run008_009_midspan_wake_speed_phase_grid.png`
  - `figures/009/run008_009_midspan_temperature_phase_grid.png`
  - `figures/009/run008_009_phase_story_key_frames.png`

Wake-probe dynamics layer `010`:

- script: `scripts/analyse_run008_wake_probes_010.py`
- output report: `data/010/run008_010_wake_probes_analysis.md`
- source data:
  - 13 wake probes from `postProcessing/probes_wake/0/U` and `T`
  - window `t = 2..10 s`
  - `1601` samples at `200 Hz`
- probe roles:
  - strongest `Uy` RMS: probe `2` at `(x,y) = (30, 0) mm`, RMS `0.11429 m/s`
  - best `Uy-Cl` coherence near `f_shed`: probe `2`, coherence `0.883`, lag `Uy -> Cl = -0.0500 s`
  - best `Uy-Q_wall` coherence near `f_shed`: probe `6`, coherence `0.905`, lag `Uy -> Q_wall = +0.4200 s`
  - best `Uy -> local Nu` coherence at `f_shed`: probe `9`, `fin_z_max`, `x = 6.06 mm`, coherence `0.985`
  - best `Uy -> local Nu` coherence at `2f_shed`: probe `2`, `fin_z_max`, `x = 3.64 mm`, coherence `0.994`
- interpretation:
  - probe `2` is the best reduced wake sensor for lift/shedding
  - probe `9` is the best reduced wake sensor for local fin heat-transfer coupling
  - wake-probe PSD is dominated by the `2f_shed`/adjacent-lift-peak component near the Welch bin `6.64 Hz`
- figures:
  - `figures/010/run008_010_probe_layout_coherence.png`
  - `figures/010/run008_010_probe_uy_psd.png`
  - `figures/010/run008_010_probe_cross_correlation_lags.png`
  - `figures/010/run008_010_probe_to_local_nu_coherence_rank.png`

Campaign comparison / production decision layer `011`:

- script: `scripts/analyse_run008_campaign_comparison_011.py`
- output report: `data/011/run008_011_campaign_comparison.md`
- compared:
  - `run004b`
  - `run005`
  - `run007c`
  - `run008`
- global regime table:
  - `run004b`: `Cd=3.361490`, `Cl_rms=0.184056`, `St=0.15517`, `Nu_EB=7.777953`
  - `run005`: `Cd=3.359275`, `Cl_rms=0.184616`, `St=0.15519`, `Nu_EB=7.775975`
  - `run007c` smoke: `Cd=3.361209`, `Cl_rms=0.176698`, `Nu_wall_case_k=7.821736`, closure `+1.39%`
  - `run008` production: `Cd=3.361014`, `Cl_rms=0.176441`, `St=0.15426`, `Nu_EB=7.770004`, closure `+0.706%`
- differences relative to `run008`:
  - `run004b`: `Cd +0.014%`, `Cl_rms +4.315%`, `Nu +0.102%`
  - `run005`: `Cd -0.052%`, `Cl_rms +4.633%`, `Nu +0.077%`
  - `run007c` smoke: `Cd +0.006%`, `Cl_rms +0.145%`, `Nu +0.666%`
- `run007a` status:
  - variable-property diagnostic only
  - short-window wall-air closure `-27.4%`
  - `Cd=3.4736`, shifted by about `+3.34%` versus constant-property baseline
  - not a production reference until its energy balance is internally consistent
- decision:
  - production reference = `run008`
  - rationale: stable established regime, Cp-consistent constant-property setup, `2..10 s` production window, heat-balance closure, and measurement-rich sampling
- figures:
  - `figures/011/run008_011_campaign_global_regime.png`
  - `figures/011/run008_011_differences_vs_production.png`
  - `figures/011/run008_011_short_vs_production.png`
  - `figures/011/run008_011_run007a_diagnostic_status.png`

Sampling setup:

- full 3D fields every `0.08 s`
- force coefficients, raw forces, wake probes, wall heat flux, and hot
  surface sampling every `0.005 s`
- midspan `z=0` slice every `0.02 s`

Final paper-grade figure layer `012`:

- script: `scripts/build_run008_paper_figures_012.py`
- captions/report:
  - `data/012/run008_012_final_figure_captions.md`
  - `data/012/run008_012_final_figure_captions.csv`
  - `data/012/run008_012_final_figures_summary.json`
- figures are saved as both PNG and PDF in `figures/012`
- figure set:
  - Figure 1: geometry, domain, and sampling layout
  - Figure 2: `Cd(t)`, `Cl(t)`, and `PSD(Cl)`
  - Figure 3: heat balance `Q_air` vs `Q_wall` and `Nu_EB` vs `Nu_wall`
  - Figure 4: mean and RMS `Nu(theta,z)` on the tube
  - Figure 5: phase-averaged `Nu(theta)` over the shedding cycle
  - Figure 6: fin `Nu_local(x)` mean/RMS/coherence
  - Figure 7: POD energy and mode 1/2 maps
  - Figure 8: EPOD / lift-correlated thermal structure
  - Figure 9: coherence maps between `Cl` and local `Nu`
  - Figure 10: summary mechanism schematic
- interpretation:
  - `012` is a curated article-ready overview, not a new physical analysis
  - it distills the validated layers `001..011` into a compact visual set for manuscript planning and discussion
