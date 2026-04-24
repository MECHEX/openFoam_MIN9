# long_medium_Re200

## Input

# long_medium_Re200 input

## Purpose

- benchmark-vs-sahin

## Geometry

- D = 0.012000 m
- beta = 0.500
- upstream = 10.0D
- downstream = 30.0D
- H = 0.024000 m

## Flow setup

- Re = 200.0
- Uc = 0.252666667 m/s
- Ub = 0.168444444 m/s
- inlet profile = parabolic
- top/bottom/cylinder = no-slip
- front/back = empty

## Mesh setup

- mesh level = medium
- base dx = 0.002500 m
- base mesh = 192 x 12 x 1
- surface / near / wake levels = 3 / 2 / 1
- cylinder layers = 6
- wall layers = 2

## Notes

- For V1, channel height is physics because it sets beta = 0.5.
- Domain sensitivity therefore means streamwise padding, not height variation.
- Primary benchmark family: Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285
- Supporting setup note: Lu, W., Chan, L. and Ooi, A. (2025), Fluids 10(4), 84, doi:10.3390/fluids10040084

## Output

# long_medium_Re200 output

## Run status

- mesh check status = warn
- interpreted regime = periodic

## Mesh summary

- cells = 46040
- points = 61265
- faces = 152862
- max non-orthogonality = 62.2589883

## Force metrics

- time reached [s] = 3.859379711760226
- Cd_mean = 2.4004203135554567
- Cd_std = 0.001946962118732633
- Cl_rms = 0.04252463204533066
- frequency [Hz] = 7.3918061204144365
- St = 0.35106203210411574

## Benchmark comment

- Comparison is against the Sahin confined-cylinder benchmark family, with emphasis on onset behaviour and force convergence.
- Delta Cd_mean vs baseline_medium_Re160 = -6.75%. Delta St vs baseline_medium_Re160 = +2.61%.
- For V1, height is not treated as a numerical-domain variable because it defines beta = 0.5.

## Sources

- Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285
- Lu, W., Chan, L. and Ooi, A. (2025), Fluids 10(4), 84, doi:10.3390/fluids10040084
