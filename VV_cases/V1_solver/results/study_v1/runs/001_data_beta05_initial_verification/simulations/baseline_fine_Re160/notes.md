# baseline_fine_Re160

## Input

# baseline_fine_Re160 input

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

## Output

# baseline_fine_Re160 output

## Run status

- mesh check status = missing
- interpreted regime = not-run-or-failed

## Mesh summary

- cells = None
- points = None
- faces = None
- max non-orthogonality = None

## Force metrics

- time reached [s] = None
- Cd_mean = None
- Cd_std = None
- Cl_rms = None
- frequency [Hz] = None
- St = None

## Benchmark comment

- Comparison is against the Sahin confined-cylinder benchmark family, with emphasis on onset behaviour and force convergence.
- Relative comparison is limited because one of the cases is not periodic.
- For V1, height is not treated as a numerical-domain variable because it defines beta = 0.5.

## Sources

- Sahin, M. and Owens, R.G. (2004), Phys. Fluids 16, 1305-1320, doi:10.1063/1.1668285
- Lu, W., Chan, L. and Ooi, A. (2025), Fluids 10(4), 84, doi:10.3390/fluids10040084
