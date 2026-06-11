# 006_data_v2_production_like_short

Production-like V2 rerun on the compact V4b-style domain and mesh family.

- runtime root: `/home/hexmachina/of_runs/V2_production_like_short`
- solver chain: `foamRun -solver fluid`
- geometry family: compact V4b-like domain, heated cylinder only

| case | old key | Re | endTime [s] | writeInterval [s] |
|---|---|---:|---:|---:|
| Re10_prodLike | Re10_ogrid | 10 | 18.0 | 0.5 |
| Re20_prodLike | Re20_ogrid | 20 | 18.0 | 0.5 |
| Re40_prodLike | Re40_ogrid | 40 | 18.0 | 0.5 |
| Re60_prodLike | Re60_ogrid | 60 | 12.0 | 0.2 |
| Re100_prodLike | Re100_ogrid | 100 | 10.0 | 0.1 |
