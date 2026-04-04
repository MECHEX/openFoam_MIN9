# V1 Study Plan

- Goal: verify V1 on a confined no-slip cylinder benchmark before moving to V2-V4b.
- Height is not a free domain variable in V1 because it sets beta = 0.5.
- Streamwise domain sensitivity is checked with a longer 10D/30D case.
- Mesh sensitivity is checked at Re = 160 where periodic shedding should be easier to resolve.
- A medium-mesh Re sweep brackets the onset region.

- Benchmark family: Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285
- Setup support: Lu, W., Chan, L. and Ooi, A. (2025), Fluids 10(4), 84, doi:10.3390/fluids10040084

| case | purpose | Re | mesh | upstream | downstream |
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
