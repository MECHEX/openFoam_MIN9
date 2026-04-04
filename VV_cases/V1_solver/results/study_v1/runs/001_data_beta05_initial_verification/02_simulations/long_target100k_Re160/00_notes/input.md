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
