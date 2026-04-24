# Re10_ogrid

## Setup

- Re: `10`
- U_inf: `0.012631506 m/s`
- solver: `buoyantBoussinesqPimpleFoam` with `g = 0`
- mesh: structured O-grid from `blockMesh`, no snappyHexMesh
- thermal scheme: `div(phi,T) Gauss vanLeer`
- cylinder thermal BC: `fixedValue 303.15 K`
- far-field T: `293.15 K`
- Lange Nu: `1.8101`
- Bharti Nu: `1.8623`

## Notes

- Quality gate: temperature must remain bounded before Nu is interpreted.
- Nu is extracted from wall-normal `snGrad(T)` on the cylinder patch.

## Results

- latest time = `99.9938040058392`
- Nu_tail_mean = `1.880652032516138`
- Nu_last = `1.8806434729364834`
- Nu_Lange = `1.8101`
- Nu_Bharti = `1.8623`
- Cd_tail_mean = `2.925892225804564`
- Cl_tail_rms = `1.8597964647841878e-10`
- St_present = `None`
- St_Lange = `None`
- mesh_cells = `10240`
- T_min/T_max = `293.15` / `303.0717` K
- cylinder owner cells above T_wall = `0.0` %
