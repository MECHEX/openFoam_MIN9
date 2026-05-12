# V4b_3D run008 campaign comparison and production decision

This layer places the production record in the full V4b_3D campaign context.

## Global regime table

| Run | Role | Window | Cd_mean | Cl_rms | St | Nu | Nu definition | Closure | Status |
|---|---|---:|---:|---:|---:|---:|---|---:|---|
| run004b | accepted domain baseline | 3..6 s | 3.361490 | 0.184056 | 0.15517 | 7.777953 | Nu_EB_LMTD |  | domain baseline, pre-Cp cleanup |
| run005 | inlet sensitivity | 3..6 s | 3.359275 | 0.184616 | 0.15519 | 7.775975 | Nu_EB_LMTD |  | inlet sensitivity closed |
| run007c | Cp-capacity smoke | 0.5..2 s | 3.361209 | 0.176698 |  | 7.821736 | Nu_wall_case_k | +1.39% | short smoke, same model family as run008 |
| run008 | production reference | 2..10 s | 3.361014 | 0.176441 | 0.15426 | 7.770004 | Nu_EB | +0.71% | accepted production reference |

## Differences relative to run008

| Run | Cd diff | Cl_rms diff | Nu diff |
|---|---:|---:|---:|
| run004b | +0.014% | +4.315% | +0.102% |
| run005 | -0.052% | +4.633% | +0.077% |
| run007c smoke | +0.006% | +0.145% | +0.666% |

Note: `run007c` is a short smoke test, so its St is intentionally not used as a regime metric; the short FFT is dominated by transient/window limits.

## Short-window context

| Run | Model | Cd | Cl_rms | Q_wall [W] | Q_air case [W] | Nu_wall case-k | wall-air diff |
|---|---|---:|---:|---:|---:|---:|---:|
| run004b | baseline eConst/Boussinesq Cv=718 | 3.361209 | 0.176698 | 1.0591 | 1.0445 | 7.8217 | +1.4% |
| run007a | variable props: incompressiblePerfectGas + Sutherland | 3.473619 | 0.178979 | 1.3396 | 1.8450 | 7.3786 | -27.4% |
| run007c | constant props: eConst/Boussinesq capacity=1005 | 3.361209 | 0.176698 | 1.4824 | 1.4621 | 7.8217 | +1.4% |

## run007a status

`run007a` remains a useful variable-property diagnostic, but not a production reference. In the matched `0.5..2 s` window it has wall-air closure `-27.4%`, while `run007c` closes at `+1.4%`.

The variable-property case also shifts drag (`Cd = 3.4736`) relative to the accepted constant-property regime (`Cd ~= 3.361`). Until its energy balance is made internally consistent, it should not define the production model.

## Decision

`run008` is the production reference for this campaign.

Rationale:

- matches established aerodynamic regime from run004b/run005
- inherits run007c Cp-consistent constant-property setup
- uses 2..10 s production record with 25.98 shedding cycles
- has closed heat balance: Q_wall-Q_air about +0.706%
- contains measurement-rich sampling needed for POD/EPOD/coherence/local Nu story

## Figures

- `../../figures/011/run008_011_campaign_global_regime.png`
- `../../figures/011/run008_011_differences_vs_production.png`
- `../../figures/011/run008_011_short_vs_production.png`
- `../../figures/011/run008_011_run007a_diagnostic_status.png`
