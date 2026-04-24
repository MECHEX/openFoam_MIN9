# Re200_ogrid

## Setup

- Re: `200`
- U_inf: `0.25263012 m/s`
- solver: `buoyantBoussinesqPimpleFoam` with `g = 0`
- mesh: structured O-grid from `blockMesh`, no snappyHexMesh
- thermal scheme: `div(phi,T) Gauss vanLeer`
- cylinder thermal BC: `fixedValue 303.15 K`
- far-field T: `293.15 K`
- Lange Nu: `7.4202`
- Bharti Nu: `n/a`

## Notes

- Quality gate: temperature must remain bounded before Nu is interpreted.
- Nu is extracted from wall-normal `snGrad(T)` on the cylinder patch.

## Results

- latest time = `None`
- Nu_tail_mean = `7.503991370178309`
- Nu_last = `7.4817558797476424`
- Nu_Lange = `7.4202`
- Nu_Bharti = `None`
- Cd_tail_mean = `1.3233592708982693`
- Cl_tail_rms = `0.444334815094187`
- St_present = `0.1831173921008645`
- St_Lange = `0.19696750000000002`
- mesh_cells = `10240`
- T_min/T_max = `293.14999` / `302.90929` K
- cylinder owner cells above T_wall = `0.0` %
