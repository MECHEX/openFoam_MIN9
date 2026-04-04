# baseline_fine_Re120 input

## Purpose

- mesh-study

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

- mesh level = fine
- base dx = 0.002000 m
- base mesh = 168 x 12 x 1
- surface / near / wake levels = 4 / 3 / 2
- cylinder layers = 8
- wall layers = 4

## Notes

- For V1, channel height is physics because it sets beta = 0.5.
- Domain sensitivity therefore means streamwise padding, not height variation.
- Primary benchmark family: Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285
- Supporting setup note: Lu, W., Chan, L. and Ooi, A. (2025), Fluids 10(4), 84, doi:10.3390/fluids10040084
