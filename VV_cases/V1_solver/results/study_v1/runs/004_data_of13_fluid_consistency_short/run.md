# 004_data_of13_fluid_consistency_short

Short solver-consistency rerun of V1 on the OF13 `foamRun -solver fluid` chain used by V4b.

- runtime root: `/home/hexmachina/of_runs/V1_run_of13_fluid_short`
- solver chain: `foamRun -solver fluid`
- thermophysical model: `heRhoThermo + eConst + Boussinesq + sensibleInternalEnergy`
- thermal mode for V1: effectively isothermal (`g=0`, uniform `T`) so the run remains hydrodynamic in practice

## Case matrix

| case | beta | Re | endTime [s] | role |
|---|---:|---:|---:|---|
| b030_medium_Re090 | 0.300 | 90 | 6.0 | direct literature point, periodic |
| b030_medium_Re095 | 0.300 | 95 | 6.0 | direct literature point, periodic |
| b0375_medium_Re105 | 0.375 | 105 | 6.0 | geometry-relevant near onset |
| b0375_medium_Re120 | 0.375 | 120 | 6.0 | geometry-relevant periodic |
| b050_medium_Re125 | 0.500 | 125 | 10.0 | direct literature point, just below onset |
| b050_medium_Re135 | 0.500 | 135 | 10.0 | direct literature point, periodic |
| b060_medium_Re125 | 0.600 | 125 | 10.0 | additional confinement, just below onset |
| b060_medium_Re135 | 0.600 | 135 | 8.0 | additional confinement, periodic |
