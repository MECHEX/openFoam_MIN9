# 004_data_v2a_ogrid_cylinder_validation summary

| case | Re | cells | latest t | Nu | ref | err % | Cd | St | T range | cylinder > Tw | status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| Re10_ogrid | 10 | 10240 | 99.9938040058392 | 1.880652032516138 | 1.8623 | 0.9854498478299912 | 2.925892225804564 | None | 293.15 - 303.0717 | 0.0 | bounded; candidate |
| Re20_ogrid | 20 | 10240 | 100.00002444666187 | 2.4829304949864373 | 2.4653 | 0.7151460263025678 | 2.103105835367948 | None | 293.15 - 303.06283 | 0.0 | bounded; candidate |
| Re40_ogrid | 40 | 10240 | 100.00009658477386 | 3.3045409684503424 | 3.2825 | 0.6714689550751622 | 1.5712531 | None | 293.15 - 303.0436 | 0.0 | bounded; candidate |
| Re45_ogrid | 45 | 10240 | 119.99882505070333 | 3.473561140160554 | 3.465657777620164 | 0.22804797956182193 | 1.5006671000000003 | None | 293.15 - 303.03729 | 0.0 | bounded; candidate |
| Re60_ogrid | 60 | 10240 | 79.80032909099046 | 3.9777695233677153 | 3.9751563171796196 | 0.06573845100888408 | 1.4086128487933636 | 0.1268603141132264 | 293.15 - 303.0173 | 0.0 | bounded; candidate |
| Re100_ogrid | 100 | 10240 | 24.51296228 | 5.171960704715537 | 5.127775395230791 | 0.8616857424340693 | 1.3329013896417783 | 0.153915299907654 | 293.15 - 302.96858 | 0.0 | bounded; candidate |
| Re200_ogrid | 200 | 10240 | 11.46423001 | 7.503991370178309 | 7.420205234233615 | 1.1291619746330137 | 1.3233592708982693 | 0.1831173921008645 | 293.14999 - 302.90929 | 0.0 | diagnostic |

## Figures

- `plots/V2_run004_ogrid_mesh_schematic.png`
- `plots/V2_run004_Nu_vs_reference.png`
- `plots/V2A_Nu_Re_articles_vs_present.png`
- `plots/V2A_St_Re_articles_vs_present.png`
- `plots/V2A_Cd_Re_articles_vs_present.png`
- `plots/V2A_articles_vs_present_dashboard.png`
- `publication_Nu_Re_data.csv`
- `publication_articles_vs_present_data.csv`
- `plots/Re10_ogrid_Nu_vs_time.png`
- `plots/Re20_ogrid_Nu_vs_time.png`
- `plots/Re40_ogrid_Nu_vs_time.png`
- `plots/Re45_ogrid_Nu_vs_time.png`
- `plots/Re60_ogrid_Nu_vs_time.png`
- `plots/Re100_ogrid_Nu_vs_time.png`
- `plots/Re200_ogrid_Nu_vs_time.png`

## Reading

- This run is the structured-cylinder replacement for the rejected snappy run 002.
- The low-Re O-grid matrix currently passes the boundedness and Nu checks for all completed cases.
