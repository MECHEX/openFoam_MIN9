# Re60_ogrid

## Setup

- Re: `60`
- U_inf: `0.075789037 m/s`
- solver: `buoyantBoussinesqPimpleFoam` with `g = 0`
- mesh: structured O-grid from `blockMesh`, no snappyHexMesh
- thermal scheme: `div(phi,T) Gauss vanLeer`
- cylinder thermal BC: `fixedValue 303.15 K`
- far-field T: `293.15 K`
- Lange Nu: `3.9752`
- Bharti Nu: `n/a`

## Notes

- Quality gate: temperature must remain bounded before Nu is interpreted.
- Nu is extracted from wall-normal `snGrad(T)` on the cylinder patch.

## Results

- latest time = `None`
- Nu_tail_mean = `3.9777695233677153`
- Nu_last = `3.978055362404896`
- Nu_Lange = `3.9752`
- Nu_Bharti = `None`
- Cd_tail_mean = `1.4086128487933636`
- Cl_tail_rms = `0.07323216701543298`
- St_present = `0.1268603141132264`
- St_Lange = `0.13575833333333334`
- mesh_cells = `10240`
- T_min/T_max = `293.15` / `303.0173` K
- cylinder owner cells above T_wall = `0.0` %
