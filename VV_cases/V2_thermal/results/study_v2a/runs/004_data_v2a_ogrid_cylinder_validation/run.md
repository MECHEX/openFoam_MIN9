# 004_data_v2a_ogrid_cylinder_validation

## Purpose

Structured cylinder recovery run for V2A after the snappy mesh produced a non-physical temperature field.

## Mesh

- topology: 8-block O-grid, pure `blockMesh`
- outer square domain: `30.50D x 30.50D`
- cylinder diameter: `0.012000 m`
- span: `0.010000 m`, one `empty` cell
- cells around cylinder: `128`
- radial cells: `80`
- radial expansion ratio: `40` from cylinder to far field

## Simulation matrix

| case | Re | endTime | target | status |
|---|---:|---:|---:|---|
| Re10_ogrid | 10 | 100.0 | Nu ~= 1.8623 | case generated |
| Re20_ogrid | 20 | 100.0 | Nu ~= 2.4653 | case generated |
| Re40_ogrid | 40 | 100.0 | Nu ~= 3.2825 | case generated |
| Re45_ogrid | 45 | 120.0 | Nu ~= 3.4657 | case generated |
| Re60_ogrid | 60 | 80.0 | Nu ~= 3.9752 | case generated |
| Re100_ogrid | 100 | 60.0 | Nu ~= 5.1278 | case generated |
| Re200_ogrid | 200 | 40.0 | Nu ~= 7.4202 | case generated |

## Optional extension

- low-Re Bharti matrix cases are included; optional higher-Re extension: `45, 60, 100, 200`
- publication table and plots are generated only from bounded O-grid runs
