# Re20_ogrid

## Setup

- Re: `20`
- U_inf: `0.025263012 m/s`
- solver: `buoyantBoussinesqPimpleFoam` with `g = 0`
- mesh: structured O-grid from `blockMesh`, no snappyHexMesh
- thermal scheme: `div(phi,T) Gauss vanLeer`
- cylinder thermal BC: `fixedValue 303.15 K`
- far-field T: `293.15 K`
- Lange Nu: `2.4087`
- Bharti Nu: `2.4653`

## Notes

- Quality gate: temperature must remain bounded before Nu is interpreted.
- Nu is extracted from wall-normal `snGrad(T)` on the cylinder patch.

## Results

- latest time = `100.00002444666187`
- Nu_tail_mean = `2.4829304949864373`
- Nu_last = `2.4829304949864373`
- Nu_Lange = `2.4087`
- Nu_Bharti = `2.4653`
- Cd_tail_mean = `2.103105835367948`
- Cl_tail_rms = `1.141887054054262e-09`
- St_present = `None`
- St_Lange = `None`
- mesh_cells = `10240`
- T_min/T_max = `293.15` / `303.06283` K
- cylinder owner cells above T_wall = `0.0` %
