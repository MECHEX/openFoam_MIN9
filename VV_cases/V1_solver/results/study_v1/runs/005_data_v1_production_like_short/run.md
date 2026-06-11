# 005_data_v1_production_like_short

Production-like V1 rerun on the compact V4b-style domain and mesh family.

- runtime root: `/home/hexmachina/of_runs/V1_production_like_short`
- solver chain: `foamRun -solver fluid`
- geometry family: compact V4b-like domain, beta = 0.375

| case | old key | beta | Re | endTime [s] | role |
|---|---|---:|---:|---:|---|
| b0375_prod_Re105 | b0375_medium_Re105 | 0.375 | 105 | 4.0 | near projected onset, production-like domain |
| b0375_prod_Re120 | b0375_medium_Re120 | 0.375 | 120 | 5.0 | above onset, production-like domain |
| b0375_prod_Re135 | b0375_medium_Re120 | 0.375 | 135 | 5.0 | extra-above onset, production-like domain |
