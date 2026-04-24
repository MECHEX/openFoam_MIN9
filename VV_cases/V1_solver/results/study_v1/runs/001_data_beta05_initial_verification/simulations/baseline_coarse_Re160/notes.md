# baseline_coarse_Re160

## Input

# baseline_coarse_Re160 input

## Purpose

- mesh-study

## Geometry

- D = 0.012000 m
- beta = 0.500
- upstream = 8.0D
- downstream = 20.0D
- H = 0.024000 m

## Flow setup

- Re = 160.0
- Uc = 0.202133333 m/s
- Ub = 0.134755556 m/s
- inlet profile = parabolic
- top/bottom/cylinder = no-slip
- front/back = empty

## Mesh setup

- mesh level = coarse
- base dx = 0.003000 m
- base mesh = 120 x 12 x 1
- surface / near / wake levels = 2 / 1 / 1
- cylinder layers = 4
- wall layers = 1

## Notes

- For V1, channel height is physics because it sets beta = 0.5.
- Domain sensitivity therefore means streamwise padding, not height variation.
- Primary benchmark family: Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285
- Supporting setup note: Lu, W., Chan, L. and Ooi, A. (2025), Fluids 10(4), 84, doi:10.3390/fluids10040084

## Output

# baseline_coarse_Re160 output

## Run status

- mesh check status = warn
- interpreted regime = periodic

## Mesh summary

- cells = 8598
- points = 13748
- faces = 30692
- max non-orthogonality = 64.6620201

## Force metrics

- time reached [s] = 3.000387037157397
- Cd_mean = 2.539713778731536
- Cd_std = 0.0007158412967756127
- Cl_rms = 0.03519574745916982
- frequency [Hz] = 5.589045598739485
- St = 0.3318034986059061

## Benchmark comment

- Comparison is against the Sahin confined-cylinder benchmark family, with emphasis on onset behaviour and force convergence.
- Delta Cd_mean vs baseline_medium_Re160 = -1.34%. Delta St vs baseline_medium_Re160 = -3.02%.
- For V1, height is not treated as a numerical-domain variable because it defines beta = 0.5.

## Sources

- Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285
- Lu, W., Chan, L. and Ooi, A. (2025), Fluids 10(4), 84, doi:10.3390/fluids10040084
