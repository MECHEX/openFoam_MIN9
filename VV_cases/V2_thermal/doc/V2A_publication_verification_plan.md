# V2A Publication Verification Recovery Plan

## Current conclusion

The current snappy-cylinder `Re10_long100s` result from run 002 is diagnostic only.
It must not be used as the article validation result because the temperature field is
not bounded by the imposed physical limits.

| item | expected | observed | decision |
|---|---:|---:|---|
| cylinder T range | 293.15-303.15 K | 197.40-337.41 K | reject run 002 Nu |
| cylinder owner cells above `T_wall` | 0% | 71.43% | reject run 002 Nu |
| channel solver check, T range | 293.15-303.15 K | 293.174-303.150 K | solver path OK |
| channel solver check, Nu | 7.541 | 7.564 | +0.31%, pass |

## What the article should show

Use the cylinder validation only after run 004 or later produces a bounded
temperature field on a structured cylinder mesh.

| artifact | content | source |
|---|---|---|
| verification table | Re, mesh, domain, Nu present, Nu Lange, Nu Bharti, error %, boundedness status | structured cylinder/O-grid run |
| Nu vs Re figure | present results against Lange correlation and Bharti tabulated points | structured cylinder/O-grid run |
| convergence figure | Nu(t) for at least the Re10 pilot and one higher-Re case | structured cylinder/O-grid run |
| mesh figure | O-grid/blockMesh near-cylinder view with first-cell resolution | structured cylinder/O-grid run |
| diagnostic appendix figure | channel local Nu profile vs analytic 7.541 | run 003 only, optional |

## Quality gates before publication

- `T_min >= T_in` and `T_max <= T_wall` within numerical tolerance.
- `0%` cylinder near-wall owner cells hotter than `T_wall`.
- Nu is computed from wall-normal `snGrad(T)` on the cylinder surface, not from
  `postProcess -func grad(T)`.
- The wall-normal gradient and reference temperature difference are taken from the
  same physical definition used by Bharti/Lange.
- The mesh has structured wall-normal spacing around the cylinder; snappy without
  wall layers is not accepted for the publication Nu table.
- Re10 should be steady and long enough for thermal convergence; higher Re should
  use tail averages after discarding transient time.

## Execution status

1. Run 003 was kept as a solver/scheme sanity check: it proves that
   `buoyantBoussinesqPimpleFoam`, `g = 0`, and `Gauss vanLeer` reproduce a known
   thermal benchmark on an orthogonal mesh.
2. Run 004 replaced the rejected snappy-cylinder branch with a structured O-grid
   cylinder mesh.
3. The low-Re Bharti matrix is now complete for `Re = 10, 20, 40`.
4. The current article comparison assets now cover `Nu(Re)`, `St(Re)`, `Cd(Re)`,
   and `Cl(Re)` in the sense allowed by the two references:
   Bharti contributes only `Nu`, Lange contributes `Nu`, `St`, onset, and digitized
   `Cd`, while neither paper gives a usable `Cl(Re)` curve.
5. Add higher-Re cases only as a separate Lange-range extension beyond the Bharti
   low-Re table; these should be treated as unsteady/time-averaged cases.

## Reference range and next case plan

| source | usable quantities here | Re range | max Re | notes |
|---|---|---:|---:|---|
| Bharti et al. (2007) | `Nu` for steady CWT/UHF cross-flow | 10-45 | 45 | no useful `Cd`, `Cl`, or `St` curve for this comparison |
| Lange et al. (1998) | `Nu`, `St`, onset, digitized `Cd` trend | 1e-4-200 | 200 | `Cl` appears only as an auxiliary quantity, not a reusable `Cl(Re)` curve |
| present run 004 | `Nu`, `Cd`, `Cl` tail diagnostic | 10-40 so far | 40 | all current cases are below `Re_c = 45.9` |

Recommended next simulations:

| priority | case | role | suggested endTime | suggested writeInterval | main metrics |
|---:|---|---|---:|---:|---|
| 1 | `Re45_ogrid` | closes Bharti max-Re point and sits just below Lange onset | 120 s | 0.5 s | `Nu`, `Cd`, bounded `T`, no `St` expected |
| 2 | `Re60_ogrid` | first clean shedding case above `Re_c` | 80 s | 0.1 s | time-mean `Nu`, `Cd`, `St` from `Cl` FFT |
| 3 | `Re100_ogrid` | mid-range Lange unsteady validation | 60 s | 0.05 s | time-mean `Nu`, `Cd`, `St` |
| 4 | `Re200_ogrid` | maximum Lange-range check | 40 s | 0.025 s | time-mean `Nu`, `Cd`, `St`; mesh sensitivity likely needed |

If `Re200` differs by more than about 5% in `Nu` or `St`, repeat `Re100/Re200`
on a refined O-grid before using the high-Re points in the article.

## Run 004 low-Re result

The structured-cylinder replacement cases now pass the main quality gate.

| case | Re | Nu present | Nu Lange | Nu Bharti | error vs Bharti | T bounded | status |
|---|---:|---:|---:|---:|---:|---|---|
| Re10_ogrid | 10 | 1.8807 | 1.8101 | 1.8623 | +0.99% | yes | publication candidate |
| Re20_ogrid | 20 | 2.4829 | 2.4087 | 2.4653 | +0.72% | yes | publication candidate |
| Re40_ogrid | 40 | 3.3045 | 3.2805 | 3.2825 | +0.67% | yes | publication candidate |

This result supports moving from the rejected snappy-cylinder branch to the structured
O-grid branch for the article verification table. The low-Re matrix is sufficient for
the Bharti tabulated comparison currently implemented in the study script.

## Non-publication material

The invalid run 002 cylinder plots can remain in the repository as debugging evidence,
but they should not appear as validation figures except perhaps in an internal methods
note explaining why the mesh/extraction path was changed.
