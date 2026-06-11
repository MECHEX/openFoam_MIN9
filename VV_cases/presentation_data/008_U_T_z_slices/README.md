# 008 U, T and vortex-criterion z-slices

Purpose: visual comparison of velocity magnitude, temperature, streamlines and vortex criteria on three streamwise planes between the heated fin walls.

Planes:

| plane | fraction from z_min | z [m] | z [mm] |
|---|---:|---:|---:|
| z20 | 0.20 | -0.003600 | -3.600 |
| z50 | 0.50 | 0.000000 | 0.000 |
| z80 | 0.80 | 0.003600 | 3.600 |

Source time: `t = 10 s` from the previously completed production runs.

Generated outputs:

- `raw_vtk/`: copied OpenFOAM VTK cut planes with `U`, `T`, `Q` and `Lambda2`.
- `csv/`: pointwise x-y-z, Ux, Uy, Uz, |U|, T, Q and Lambda2 for every Re/plane.
- `figures/*_Umag_T_*`: interpolated maps of velocity magnitude and temperature. These replace the older point-rendered version so the sampling/mesh is no longer visible.
- `figures/*_streamlines_Umag_*`: velocity magnitude background with in-plane streamlines from Ux-Uy.
- `figures/*_Q_Lambda2_*`: vortex-criterion maps. Q>0 marks vortex-dominated regions; Lambda2<0 marks vortex-core regions.
- `figures/overview_*`: compact comparison across Re and z-planes with common color scales.

Note: OpenFOAM emitted local eigenvalue warnings while writing `Lambda2`. The field was still written and sampled. Treat `Lambda2` here as a qualitative vortex-core diagnostic, best used together with Q and the velocity streamlines rather than as a standalone scalar proof.

Summary statistics:

| Re | plane | U_mean [m/s] | U_max [m/s] | T_mean [K] | Q_p95 [1/s2] | Lambda2_p05 [1/s2] |
|---:|---|---:|---:|---:|---:|---:|
| 150 | z20 | 0.17145 | 0.43631 | 315.494 | 1468.127 | -499.881 |
| 150 | z50 | 0.20470 | 0.44902 | 311.142 | 1854.134 | -148.267 |
| 150 | z80 | 0.17155 | 0.43631 | 315.485 | 1464.567 | -509.307 |
| 159 | z20 | 0.18172 | 0.45707 | 315.290 | 1617.217 | -560.475 |
| 159 | z50 | 0.21629 | 0.46986 | 310.854 | 2092.904 | -166.140 |
| 159 | z80 | 0.18183 | 0.45707 | 315.281 | 1625.296 | -546.729 |
| 160 | z20 | 0.19780 | 0.48853 | 313.899 | 2083.865 | -728.162 |
| 160 | z50 | 0.22192 | 0.49106 | 310.112 | 2129.305 | -548.168 |
| 160 | z80 | 0.19795 | 0.48855 | 313.890 | 2080.581 | -719.009 |
| 200 | z20 | 0.24162 | 0.59148 | 312.437 | 3411.554 | -1347.894 |
| 200 | z50 | 0.27915 | 0.58477 | 308.940 | 4440.756 | -763.849 |
| 200 | z80 | 0.26211 | 0.59970 | 311.888 | 3985.593 | -1113.113 |
