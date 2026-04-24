# Re45_ogrid

## Setup

- Re: `45`
- U_inf: `0.056841777 m/s`
- solver: `buoyantBoussinesqPimpleFoam` with `g = 0`
- mesh: structured O-grid from `blockMesh`, no snappyHexMesh
- thermal scheme: `div(phi,T) Gauss vanLeer`
- cylinder thermal BC: `fixedValue 303.15 K`
- far-field T: `293.15 K`
- Lange Nu: `3.4657`
- Bharti Nu: `n/a`

## Notes

- Quality gate: temperature must remain bounded before Nu is interpreted.
- Nu is extracted from wall-normal `snGrad(T)` on the cylinder patch.

## Results

- latest time = `6.499870988752811`
- Nu_tail_mean = `3.473561140160554`
- Nu_last = `3.473561140160554`
- Nu_Lange = `3.4657`
- Nu_Bharti = `None`
- Cd_tail_mean = `1.5006671000000003`
- Cl_tail_rms = `6.043150087394951e-07`
- St_present = `None`
- St_Lange = `None`
- mesh_cells = `10240`
- T_min/T_max = `293.15` / `303.03729` K
- cylinder owner cells above T_wall = `0.0` %
