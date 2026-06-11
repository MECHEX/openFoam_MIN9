# 005_data_of13_fluid_consistency_short

Short solver-consistency rerun of V2 O-grid validation cases on the OF13 `foamRun -solver fluid` chain used by V4b.

- runtime root: `/home/hexmachina/of_runs/V2_run_of13_fluid_short`
- source setups: `/mnt/c/Users/wisie_101/Documents/GitHub/openFoam_MIN9/VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/simulations`
- solver chain: `foamRun -solver fluid`
- thermophysical model: `heRhoThermo + eConst + Boussinesq + sensibleInternalEnergy`

## Case matrix

| case | Re | endTime [s] | role |
|---|---:|---:|---|
| Re10_ogrid | 10 | 60.0 | OF13 fluid consistency check |
| Re20_ogrid | 20 | 60.0 | OF13 fluid consistency check |
| Re40_ogrid | 40 | 60.0 | OF13 fluid consistency check |
| Re60_ogrid | 60 | 40.0 | OF13 fluid consistency check |
| Re100_ogrid | 100 | 20.0 | OF13 fluid consistency check |
