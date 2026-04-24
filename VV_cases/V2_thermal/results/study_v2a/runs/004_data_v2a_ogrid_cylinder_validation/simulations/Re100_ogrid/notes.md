# Re100_ogrid

## Setup

- Re: `100`
- U_inf: `0.12631506 m/s`
- solver: `buoyantBoussinesqPimpleFoam` with `g = 0`
- mesh: structured O-grid from `blockMesh`, no snappyHexMesh
- thermal scheme: `div(phi,T) Gauss vanLeer`
- cylinder thermal BC: `fixedValue 303.15 K`
- far-field T: `293.15 K`
- Lange Nu: `5.1278`
- Bharti Nu: `n/a`

## Notes

- Quality gate: temperature must remain bounded before Nu is interpreted.
- Nu is extracted from wall-normal `snGrad(T)` on the cylinder patch.

## Results

- latest time = `None`
- Nu_tail_mean = `5.171960704715537`
- Nu_last = `5.173294774389111`
- Nu_Lange = `5.1278`
- Nu_Bharti = `None`
- Cd_tail_mean = `1.3329013896417783`
- Cl_tail_rms = `0.206267321552868`
- St_present = `0.153915299907654`
- St_Lange = `0.164335`
- mesh_cells = `10240`
- T_min/T_max = `293.15` / `302.96858` K
- cylinder owner cells above T_wall = `0.0` %
