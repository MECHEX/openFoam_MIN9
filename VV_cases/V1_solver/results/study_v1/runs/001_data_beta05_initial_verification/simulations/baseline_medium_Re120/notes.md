# baseline_medium_Re120

## Input

# baseline_medium_Re120 input

## Purpose

- transition-sweep

## Geometry

- D = 0.012000 m
- beta = 0.500
- upstream = 8.0D
- downstream = 20.0D
- H = 0.024000 m

## Flow setup

- Re = 120.0
- Uc = 0.151600000 m/s
- Ub = 0.101066667 m/s
- inlet profile = parabolic
- top/bottom/cylinder = no-slip
- front/back = empty

## Mesh setup

- mesh level = medium
- base dx = 0.002500 m
- base mesh = 134 x 12 x 1
- surface / near / wake levels = 3 / 2 / 1
- cylinder layers = 6
- wall layers = 2

## Notes

- For V1, channel height is physics because it sets beta = 0.5.
- Domain sensitivity therefore means streamwise padding, not height variation.
- Primary benchmark family: Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285
- Supporting setup note: Lu, W., Chan, L. and Ooi, A. (2025), Fluids 10(4), 84, doi:10.3390/fluids10040084

## Output

# baseline_medium_Re120 output

## Run status

- mesh check status = warn
- interpreted regime = steady-or-weakly-unsteady

## Mesh summary

- cells = 44492
- points = 58516
- faces = 147078
- max non-orthogonality = 62.71802589

## Force metrics

- time reached [s] = 2.000284575266415
- Cd_mean = 2.8684561890625946
- Cd_std = 0.0006082884890142685
- Cl_rms = 0.00037482373668180105
- frequency [Hz] = None
- St = None

## Benchmark comment

- Comparison is against the Sahin confined-cylinder benchmark family, with emphasis on onset behaviour and force convergence.
- Delta Cd_mean vs baseline_medium_Re160 = +11.43%.
- For V1, height is not treated as a numerical-domain variable because it defines beta = 0.5.

## Sources

- Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285
- Lu, W., Chan, L. and Ooi, A. (2025), Fluids 10(4), 84, doi:10.3390/fluids10040084
