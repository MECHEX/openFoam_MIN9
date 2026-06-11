# Asset Manifest

## V1 - solver verification

| File | Suggested slide | Purpose |
|---|---:|---|
| `assets/V1_solver_verification/V1_fig1_hopf_onset.png` | 3 | Pokazuje prog niestacjonarnosci / Hopf onset. |
| `assets/V1_solver_verification/V1_fig2_St_vs_Re.png` | 3-4 | Pokazuje trend Strouhala wzgledem Re. |
| `assets/V1_solver_verification/V1_fig3_St_parity.png` | 4 | Parity plot wzgledem benchmarku/literatury. |

## V2 - thermal validation

| File | Suggested slide | Purpose |
|---|---:|---|
| `assets/V2_thermal_validation/V2_fig1_ogrid_mesh_schematic.png` | 5 | Pokazuje kontrolowana siatke O-grid dla walidacji cieplnej. |
| `assets/V2_thermal_validation/V2_fig2_Nu_vs_reference.png` | 5 | Glowne porownanie Nu z referencja. |
| `assets/V2_thermal_validation/V2_fig3_Nu_articles_vs_present.png` | 5 | Porownanie Nu z artykulami. |
| `assets/V2_thermal_validation/V2_fig4_articles_dashboard.png` | 6 | Dashboard V2: Nu/Cd/St i zakres walidacji. |

## V4b - production case

| File | Suggested slide | Purpose |
|---|---:|---|
| `assets/V4b_production_case/V4b_fig01_geometry_domain_sampling.png` | 7-8 | Geometria produkcyjna, domena i sampling. |
| `assets/V4b_production_case/V4b_fig02_forces_cl_psd.png` | 9 | Sily, Cl i PSD, czyli odpowiedz aerodynamiczna. |
| `assets/V4b_production_case/V4b_fig03_heat_balance_nu_closure.png` | 10 | Bilans ciepla i zgodnosc `Nu_EB` z `Nu_wall`. |
| `assets/V4b_production_case/V4b_fig04_tube_nu_mean_rms.png` | 11 | Lokalny rozklad Nu na rurze. |
| `assets/V4b_production_case/V4b_fig05_phase_averaged_tube_nu_theta.png` | 11 | Fazowanie odpowiedzi cieplnej na rurze. |
| `assets/V4b_production_case/V4b_fig06_fin_nu_mean_rms_coherence.png` | 11 | Rozklad na finach i koherencja. |
| `assets/V4b_production_case/V4b_fig07_pod_energy_modes.png` | 12 | Energia modow POD. |
| `assets/V4b_production_case/V4b_fig08_epod_cl_thermal_structure.png` | 12 | Sprzezenie struktur aerodynamicznych z termika. |
| `assets/V4b_production_case/V4b_fig09_cl_nu_coherence_maps.png` | 12 | Mapy koherencji `Cl-Nu`. |
| `assets/V4b_production_case/V4b_fig10_mechanism_schematic.png` | 12-13 | Schemat mechanizmu fizycznego. |

## Source references

| File | Use |
|---|---|
| `source_refs/BENCHMARK_TO_PRODUCTION_DEFENSE_20260603.md` | Metodologiczna obrona przejscia benchmark -> produkcja. |
| `source_refs/V1_run002_summary.md` | Szczegoly V1. |
| `source_refs/V1_comparison_vs_sahin_owens.csv` | Dane porownawcze V1. |
| `source_refs/V2_run004_summary.md` | Tabela walidacyjna V2. |
| `source_refs/V4b_production_run_spec.md` | Spec domeny produkcyjnej, samplingu i kontraktu runu. |
| `source_refs/V4b_audit_uncertainty.md` | Rzeczywiste `dt`, kompletność samplingu i okna niepewnosci. |
| `source_refs/V4b_campaign_comparison.md` | Kontekst wyboru zaakceptowanego setupu produkcyjnego. |
| `source_refs/V4b_run008_summary.md` | Glowne wyniki V4b run008. |
| `source_refs/V4b_final_figure_captions.md` | Podpisy i opisy finalnych figur V4b. |
