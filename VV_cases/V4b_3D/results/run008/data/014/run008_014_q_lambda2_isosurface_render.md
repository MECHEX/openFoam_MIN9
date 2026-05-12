# V4b_3D run008 Q/Lambda2 iso-surface render pass

## Method

- input VTK root: `/home/hexmachina/of_runs/V4b_3D_run008_q_lambda2_013/vtk_processors`
- Q iso-surface: `Q = 3000`
- Lambda2 iso-surface: `Lambda2 = -1000`
- Q surfaces are rendered in orange.
- Lambda2 surfaces are overlaid in blue as a companion vortex-core check.
- hot tube and fin patches are shown as translucent context geometry.

## Screenshots

| label | time [s] | phase [deg] | screenshot |
|---|---:|---:|---|
| `cl_zero_down` | 2.720 | 11.48 | `figures/014/run008_014_iso_Q_Lambda2_cl_zero_down.png` |
| `cl_zero_up` | 7.440 | 78.67 | `figures/014/run008_014_iso_Q_Lambda2_cl_zero_up.png` |
| `nu_global_max` | 6.880 | 123.56 | `figures/014/run008_014_iso_Q_Lambda2_nu_global_max.png` |
| `cl_min_qtube_max` | 3.840 | 241.08 | `figures/014/run008_014_iso_Q_Lambda2_cl_min_qtube_max.png` |
| `cl_max` | 2.160 | 281.39 | `figures/014/run008_014_iso_Q_Lambda2_cl_max.png` |
| `qfins_qwall_max` | 5.040 | 304.97 | `figures/014/run008_014_iso_Q_Lambda2_qfins_qwall_max.png` |

## Reading

This is a visual structure-identification layer.  It should be read together
with layer `013`, which records the selected phases and first-pass global
cell-count metrics. The next useful quantitative step is to restrict the
Q/Lambda2 measures to near-wake and tube-fin-junction regions.

The current thresholds are deliberately visual rather than universal:
`Q = 3000` and `Lambda2 = -1000` expose coherent near-tube and wake structures
without flooding the whole domain. The blue `Lambda2` cores and orange `Q`
surfaces are not identical, which is expected; agreement between them is the
useful evidence for compact vortex cores, while the broader `Q` patches show
rotation-dominated regions around those cores.

The strongest use of this pass is phase comparison. The selected snapshots show
that the identifiable structures move and reorganize between the `Cl` extrema,
zero crossings, and the heat-transfer extrema. This supports a structure-to-heat
transfer follow-up, but it should not yet be treated as a quantitative proof of
local `Nu` control until the surfaces are measured in restricted regions near
the wake, tube-fin junctions, and fin-surface sweeping zones.
