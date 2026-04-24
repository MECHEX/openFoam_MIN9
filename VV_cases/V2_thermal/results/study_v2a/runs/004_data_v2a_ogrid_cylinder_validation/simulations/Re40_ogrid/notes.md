# Re40_ogrid

## Setup

- Re: `40`
- U_inf: `0.050526024 m/s`
- solver: `buoyantBoussinesqPimpleFoam` with `g = 0`
- mesh: structured O-grid from `blockMesh`, no snappyHexMesh
- thermal scheme: `div(phi,T) Gauss vanLeer`
- cylinder thermal BC: `fixedValue 303.15 K`
- far-field T: `293.15 K`
- Lange Nu: `3.2805`
- Bharti Nu: `3.2825`

## Notes

- Quality gate: temperature must remain bounded before Nu is interpreted.
- Nu is extracted from wall-normal `snGrad(T)` on the cylinder patch.

## Results

- latest time = `100.00009658477386`
- Nu_tail_mean = `3.3045409684503424`
- Nu_last = `3.3045409684503424`
- Nu_Lange = `3.2805`
- Nu_Bharti = `3.2825`
- Cd_tail_mean = `1.5712531`
- Cl_tail_rms = `8.724623786903208e-13`
- St_present = `None`
- St_Lange = `None`
- mesh_cells = `10240`
- T_min/T_max = `293.15` / `303.0436` K
- cylinder owner cells above T_wall = `0.0` %
