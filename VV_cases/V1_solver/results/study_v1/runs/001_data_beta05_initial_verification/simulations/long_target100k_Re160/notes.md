# long_target100k_Re160

## Input

# long_target100k_Re160 input

## Purpose

- mesh-study replacement around 100k cells

## Geometry

- D = 0.012000 m
- beta = 0.500
- upstream = 10.0D
- downstream = 30.0D
- H = 0.024000 m

## Flow setup

- Re = 160.0
- Uc = 0.202133333 m/s
- Ub = 0.134755556 m/s
- inlet profile = parabolic
- top/bottom/cylinder = no-slip
- front/back = empty

## Mesh setup

- mesh level = target100k
- base dx = 0.002200 m
- base mesh = 218 x 12 x 1
- surface / near / wake levels = 4 / 2 / 2
- cylinder layers = 6
- wall layers = 2

## Notes

- For V1, channel height is physics because it sets beta = 0.5.
- Domain sensitivity therefore means streamwise padding, not height variation.
- Primary benchmark family: Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285
- Supporting setup note: Lu, W., Chan, L. and Ooi, A. (2025), Fluids 10(4), 84, doi:10.3390/fluids10040084

## Output

# long_target100k_Re160 output

## Run status

- mesh check status = warn
- interpreted regime = periodic

## Mesh summary

- cells = 104104
- points = 131408
- faces = 338881
- max non-orthogonality = 62.31331662

## Force metrics

- time reached [s] = 6.000179931425576
- Cd_mean = 2.585379554177505
- Cd_std = 3.7643924255716915e-05
- Cl_rms = 0.005137039700922534
- frequency [Hz] = 5.82586580189343
- St = 0.3458627454949926

## Benchmark comment

- Comparison is against the Sahin confined-cylinder benchmark family, with emphasis on onset behaviour and force convergence.
- Delta Cd_mean vs baseline_medium_Re160 = +0.43%. Delta St vs baseline_medium_Re160 = +1.09%.
- For V1, height is not treated as a numerical-domain variable because it defines beta = 0.5.

## Sources

- Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285
- Lu, W., Chan, L. and Ooi, A. (2025), Fluids 10(4), 84, doi:10.3390/fluids10040084
