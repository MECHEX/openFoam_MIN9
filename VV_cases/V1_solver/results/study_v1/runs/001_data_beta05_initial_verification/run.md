# 001_data_beta05_initial_verification

## run scope

# 001_data_beta05_initial_verification

## Meaning of this run

- In V1, one run is one verification campaign / attempt.
- Multiple simulations with different Reynolds numbers, meshes, or domain lengths belong to the same run.
- A new run number is used only when the whole attempt is repeated after a failed or superseded campaign.

## Simulations included in this run

| simulation | purpose | Re | mesh | upstream | downstream |
|---|---|---:|---|---:|---:|
| baseline_coarse_Re160 | mesh-study | 160 | coarse | 8D | 20D |
| baseline_medium_Re100 | transition-sweep | 100 | medium | 8D | 20D |
| baseline_medium_Re120 | transition-sweep | 120 | medium | 8D | 20D |
| baseline_medium_Re140 | transition-sweep | 140 | medium | 8D | 20D |
| baseline_medium_Re160 | mesh-study+transition-sweep | 160 | medium | 8D | 20D |
| long_medium_Re200 | benchmark-vs-sahin | 200 | medium | 10D | 30D |
| baseline_fine_Re160 | mesh-study | 160 | fine | 8D | 20D |
| long_medium_Re160 | streamwise-domain-check | 160 | medium | 10D | 30D |
| long_target100k_Re160 | mesh-study replacement around 100k cells | 160 | target100k | 10D | 30D |
