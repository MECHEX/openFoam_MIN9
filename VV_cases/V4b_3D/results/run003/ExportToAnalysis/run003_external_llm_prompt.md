# External LLM Prompt For Deep Analysis Of run003

Use the following prompt as-is or with only minor edits.

---

You are acting as a senior CFD researcher and scientific analyst. Your task is to deeply analyze the exported results of a 3D mixed-convection fin-and-tube CFD case and produce physically rigorous conclusions, not just surface-level summaries.

I will provide you with a compact analysis pack and a set of supporting result files from a run called `V4b_3D run003`.

## Your Role

Please behave like a careful expert reviewer who:
- distinguishes robust conclusions from exploratory ones,
- checks whether the claimed physical interpretation is actually supported by the data,
- identifies possible numerical or sampling artefacts,
- proposes the most scientifically valuable next steps,
- and explains the physics in a way that is useful for publication planning and future simulation design.

Do not just restate the tables. I want interpretation, synthesis, critique, and prioritized recommendations.

## Context

This is a 3D fin-and-tube mixed-convection case:
- periodic vortex shedding appears at `Re = 200`,
- the corresponding `Re = 100` case (`run002`) was steady,
- the current run was stopped early at `t = 6.505 s` out of a `10.0 s` target,
- nevertheless the signals already show a periodic regime,
- lightweight modal/spectral post-processing was run in the repo:
  - POD on midspan slice snapshots,
  - EPOD between `Ux`, `Uy`, and `T`,
  - spectral coherence on wake probes,
  - transfer entropy on wake probes,
  - force spectra cross-checks.

Important methodological constraint:
- POD/EPOD were computed from only `13` snapshots, sampled every `0.5 s`,
- the shedding frequency is `f_shed = 3.125 Hz`, so the shedding period is about `0.32 s`,
- therefore POD/EPOD are exploratory and spatially informative, but frequency/phase conclusions from those snapshots are limited,
- the probe time series are much denser: `1301` samples with `dt = 0.005 s`, and are more trustworthy for spectral and lag analysis.

## Main File To Read First

Start from this file:

`run003_analysis_pack.md`

This file already consolidates:
- case metadata,
- integral CFD results,
- comparison versus the steady run002 case,
- POD summary,
- reduced EPOD payload,
- coherence near `f_shed` and `2*f_shed`,
- transfer entropy payload,
- figure reading order,
- and a shortlist of analysis questions.

## Additional Files You Should Use

Please also use the following files as supporting evidence where relevant:

- `summary.md`
- `modal_analysis_summary.md`
- `analysis_summary.json`
- `pod/Ux/singular_values.csv`
- `pod/Uy/singular_values.csv`
- `pod/T/singular_values.csv`
- `epod/Ux_to_T/reconstruction_metrics.csv`
- `epod/T_to_Ux/reconstruction_metrics.csv`
- `epod/Uy_to_T/reconstruction_metrics.csv`
- `spectral_coherence/coherence_curves.csv`
- `spectral_coherence/power_spectra.csv`
- `transfer_entropy/te_peak_summary.csv`

If you can reason over figures, also use these:
- `figures/pod_modal_energy.png`
- `figures/pod_temporal_coefficients.png`
- `figures/pod_Uy_spatial_modes_1_4.png`
- `figures/pod_T_spatial_modes_1_4.png`
- `figures/epod_reconstruction_quality.png`
- `figures/coherence_curves.png`
- `figures/probe_power_spectra.png`
- `figures/transfer_entropy_peak_summary.png`
- `figures/transfer_entropy_curves.png`

## What I Want You To Analyze

Please answer the following in depth.

### 1. Physical Regime Interpretation

Explain what kind of unsteady regime this run most likely represents.

Specifically assess:
- whether the evidence supports a coherent shedding regime rather than generic unsteadiness,
- how strong the transition from steady `run002` to periodic `run003` appears,
- whether the observed Strouhal number and force behavior look physically plausible for this geometry and mixed-convection setting,
- how the 3D fin-and-tube geometry and buoyancy may alter the classical 2D cylinder interpretation.

### 2. POD Interpretation

Analyze what the POD results really tell us.

Please discuss:
- why `Uy` appears more low-dimensional than `Ux`,
- what it means that `T` is also relatively compact in the first few modes,
- whether the first two POD modes likely represent a meaningful oscillatory pair,
- what conclusions are valid despite the coarse snapshot spacing,
- what conclusions should **not** be drawn because of undersampling.

Do not treat POD as automatically authoritative just because mode energies are clean.

### 3. EPOD Interpretation

Analyze the EPOD results carefully.

I do **not** want a naive statement like “EPOD gives 100%, therefore the coupling is perfect.”

Instead:
- explain why all-mode EPOD reaching ~100% is expected with nearly full-rank reconstruction,
- focus on the low-mode behavior,
- compare `Ux -> T`, `T -> Ux`, and `Uy -> T`,
- assess whether the data truly support the claim that thermal fluctuations are more strongly tied to transverse wake motion than to streamwise wake deficit,
- explain the physical meaning of that claim if it is supported.

### 4. Spectral Interpretation

Analyze the probe spectra and coherence in detail.

In particular:
- assess the significance of the coherence near `f_shed`,
- explain why the coherence and PSD near `2*f_shed` may be even more important,
- discuss whether a dominant `2*f_shed` response is physically reasonable for thermal or heat-transfer-related quantities,
- explain what it would mean physically if local thermal modulation peaks twice per shedding cycle,
- assess whether the near-wake to downstream coherence decay is meaningful.

Please be explicit about whether `2*f_shed` looks like a real physical signature or a possible processing artefact.

### 5. Transfer Entropy Interpretation

Interpret the TE results conservatively and intelligently.

Please discuss:
- what TE can and cannot tell us in a periodically forced CFD system,
- how to interpret the lag times relative to the shedding period,
- whether the observed lags support a transport-delay interpretation,
- whether the bidirectional TE at the 3D probe is likely to represent true two-way coupling or shared predictability from a common oscillatory process.

### 6. Integrated Cross-Method Interpretation

This is the most important part.

Please synthesize the methods together and tell me whether they consistently support the following narrative:

> At `Re = 200`, the V4b_3D configuration enters a coherent shedding regime.  
> The transverse wake dynamics (`Uy`) are the cleanest low-dimensional hydrodynamic signal.  
> Thermal fluctuations are strongly organized by the same wake dynamics.  
> The thermal field is more tightly linked to lateral wake sweeping/vortex motion than to streamwise wake deficit alone.  
> Heat-transfer-relevant dynamics likely contain an important second harmonic near `2*f_shed`.

I want you to explicitly judge:
- which parts of that narrative are strongly supported,
- which are moderately supported,
- which are still speculative.

### 7. Scientific Quality Assessment

Assess the quality of the current evidence from the standpoint of:
- internal consistency,
- sampling adequacy,
- robustness,
- publishability.

Please separate:
- what is already strong enough for internal research conclusions,
- what is strong enough to appear in a paper draft,
- what still requires another run or improved diagnostics.

### 8. Next Best Simulations And Diagnostics

I want a prioritized next-step plan.

Please recommend:
- what next run should be executed,
- what data should be sampled more densely,
- whether the biggest value would come from:
  - longer completed runtime,
  - denser POD snapshots,
  - phase-averaged fields,
  - wall-resolved `Nu(theta,z,t)` or heat-flux proxy,
  - better force decomposition,
  - other diagnostics.

Please order the next steps by scientific value, not by convenience.

### 9. Risks, Artefacts, And Alternative Interpretations

Please challenge the current interpretation.

Identify:
- the most likely over-interpretations,
- the biggest numerical or methodological risks,
- plausible alternative explanations for the observed modal or spectral behavior,
- and what evidence would falsify the current favorite interpretation.

### 10. Final Output Structure

Please structure your answer in the following sections:

1. `Executive summary`
2. `What the data strongly support`
3. `What is plausible but not yet proven`
4. `Method-by-method interpretation`
5. `Deep physical interpretation`
6. `Main risks and caveats`
7. `Recommended next steps`
8. `Most publication-ready claims right now`

## Style Requirements

Please write like a thoughtful expert reviewer:
- precise,
- skeptical where needed,
- physically grounded,
- but still constructive.

Avoid:
- generic praise,
- vague language,
- shallow repetition of the tables,
- pretending the evidence is stronger than it is.

If you think some of the current conclusions are overstated, say so directly and explain why.

## Final Question To Answer Explicitly

At the end, answer this in a short dedicated paragraph:

> If you had to summarize the deepest scientific insight from this run in 2-3 sentences, what would it be?

---

Now read the supplied files and produce the analysis.

