# Plan prezentacji

## Slajd 1 - Tytul i pytanie badawcze

Tytul: Walidacja numeryczna i analiza przeplywu/ciepla w geometrii wymiennika.

Teza: Projekt przechodzi od benchmarkow V&V do zastosowania produkcyjnego.

Pokazac:

- schemat drogi `V1 -> V2 -> V4b`;
- krotko: solver, OpenFOAM, cylinder, transfer ciepla, produkcyjny element wymiennika.

## Slajd 2 - Dlaczego potrzebujemy V&V

Teza: Najpierw sprawdzamy narzedzie na problemach, dla ktorych znamy odpowiedz, dopiero potem ufamy wynikom geometrii produkcyjnej.

Pokazac:

- 3 bloki: `V1 hydrodynamics`, `V2 heat transfer`, `V4b production geometry`;
- definicje: verification = czy solver odtwarza znane zachowanie; validation = czy model cieplny daje zgodne wielkosci; application = analiza realnej geometrii.

## Slajd 3 - V1: weryfikacja hydrodynamiczna solvera

Teza: Solver poprawnie odtwarza przejscie do niestacjonarnosci i liczbe Strouhala w benchmarku.

Figury:

- `assets/V1_solver_verification/V1_fig1_hopf_onset.png`
- `assets/V1_solver_verification/V1_fig2_St_vs_Re.png`
- opcjonalnie `assets/V1_solver_verification/V1_fig3_St_parity.png`

Notatka:

V1 nie jest geometria produkcyjna. To kontrolowany test aerodynamiczny.

## Slajd 4 - V1: co zostalo potwierdzone

Teza: V1 daje zaufanie do dynamiki wirnikowej, sily nosnej/oporowej i czestotliwosci zrzucania wirow.

Pokazac:

- zgodnosc trendu `St(Re)`;
- zgodnosc progu niestacjonarnosci;
- informacje z `source_refs/V1_run002_summary.md` i `source_refs/V1_comparison_vs_sahin_owens.csv`.

## Slajd 5 - V2: walidacja cieplna

Teza: Model wymiany ciepla odtwarza literaturowe wartosci liczby Nusselta dla cylindra w kontrolowanej siatce O-grid.

Figury:

- `assets/V2_thermal_validation/V2_fig1_ogrid_mesh_schematic.png`
- `assets/V2_thermal_validation/V2_fig2_Nu_vs_reference.png`
- `assets/V2_thermal_validation/V2_fig3_Nu_articles_vs_present.png`

Kluczowy przekaz:

W tabeli V2 bledy `Nu` dla macierzy Re sa okolo `0.07-1.13%`, co daje mocna walidacje warstwy cieplnej.

## Slajd 6 - V2: zakres walidacji i ograniczenia

Teza: V2 waliduje fizyke cieplna, ale nie udaje geometrii wymiennika.

Pokazac:

- `assets/V2_thermal_validation/V2_fig4_articles_dashboard.png`;
- zakres `Re = 10..200`;
- kontrolowana geometria cylindra, a nie zwezony kanal z finami.

Zdanie obronne:

Walidacja V2 odpowiada na pytanie "czy model cieplny liczy poprawnie w znanym przypadku?", a nie "czy produkcyjna geometria ma identyczne Nu jak izolowany cylinder?".

## Slajd 7 - Most metodologiczny: benchmark vs produkcja

Teza: Zmiana geometrii zmienia odpowiedz fizyczna, wiec rozbieznosc V4b wzgledem benchmarku nie jest bledem sama w sobie.

Pokazac:

- porownanie koncepcyjne: cylinder benchmarkowy vs kanal/element wymiennika;
- hasla: confinement, inlet/outlet development, fins, local acceleration, 3D effects, heat split.

Figury:

- `assets/V4b_production_case/V4b_fig01_geometry_domain_sampling.png`

## Slajd 8 - V4b: konfiguracja produkcyjna i jakosc obliczen

Teza: V4b to pelny run produkcyjny ze stabilna siatka, kompletnym zapisem i oknem analizy obejmujacym okolo 26 cykli zrzucania wirow.

Figury:

- `assets/V4b_production_case/V4b_fig01_geometry_domain_sampling.png`

Liczby:

- `Lin = 2D`, `Lout = 8D`;
- `407,440` cells;
- `maxCo = 0.8`, a w `run008` poczatkowe `Co_max < 0.8`;
- `t_end = 10 s`;
- okno analizy `t = 2..10 s`;
- efektywna dlugosc rekordu `25.98` cykli;
- `Mesh OK`;
- `20` MPI ranks.

Zrodlo pomocnicze:

- `PRODUCTION_DOMAIN_AND_NUMERICS.md`

## Slajd 9 - V4b: aerodynamika

Teza: Produkcyjna geometria daje spojna, periodyczna odpowiedz aerodynamiczna, ale z wartosciami wynikajacymi z ograniczonej domeny i geometrii wymiennika.

Figury:

- `assets/V4b_production_case/V4b_fig02_forces_cl_psd.png`

Liczby:

- `Cd_mean = 3.361014 +/- 0.000772`;
- `Cl_rms = 0.176441 +/- 0.011097`;
- `St = 0.154261 +/- 0.009574`;
- co drugi pik `Cl`: `f_shed = 3.2787 Hz`, `St = 0.15572`.

## Slajd 10 - V4b: bilans ciepla i Nu

Teza: Wynik cieplny V4b jest wiarygodny, bo bilans energia-sciana zamyka sie w granicach niepewnosci.

Figury:

- `assets/V4b_production_case/V4b_fig03_heat_balance_nu_closure.png`

Liczby:

- `Nu_EB = 7.770004 +/- 0.091573`;
- `Nu_wall = 7.816521 +/- 0.012286`;
- wall-air closure `+0.706 +/- 1.075%`;
- `Q_air = 1.4703 W`, `Q_wall = 1.4807 W`.

## Slajd 11 - V4b: lokalna fizyka wymiennika

Teza: V4b pokazuje nie tylko sredni wynik, ale rozklad lokalny i mechanizm wymiany ciepla na rurze oraz finach.

Figury:

- `assets/V4b_production_case/V4b_fig04_tube_nu_mean_rms.png`
- `assets/V4b_production_case/V4b_fig05_phase_averaged_tube_nu_theta.png`
- `assets/V4b_production_case/V4b_fig06_fin_nu_mean_rms_coherence.png`

Liczby:

- `Q_tube = 0.3618 W`, `Q_fins = 1.1189 W`;
- udzial ciepla: tube/fins `24.43% / 75.57%`;
- `Nu_tube_wall = 8.4344`;
- `Nu_fins_wall = 7.6357`.

## Slajd 12 - Tryby, sprzezenie i mechanizm

Teza: Analiza modalna i koherencja wskazuja, ze struktury aerodynamiczne sa powiazane z lokalnym transferem ciepla.

Figury:

- `assets/V4b_production_case/V4b_fig07_pod_energy_modes.png`
- `assets/V4b_production_case/V4b_fig08_epod_cl_thermal_structure.png`
- `assets/V4b_production_case/V4b_fig09_cl_nu_coherence_maps.png`
- `assets/V4b_production_case/V4b_fig10_mechanism_schematic.png`

## Slajd 13 - Wniosek glowny

Teza: Mamy obronna sciezke od benchmarku do produkcji: V1 sprawdza dynamike przeplywu, V2 sprawdza cieplo, V4b wykorzystuje te narzedzia w realniejszej geometrii.

Powiedziec:

- V1/V2 sa dowodem poprawnosci narzedzia w warunkach referencyjnych;
- V4b jest wynikiem inzynierskim dla geometrii produkcyjnej;
- roznice V4b wzgledem benchmarku sa oczekiwane, bo fizyka zostala zmieniona przez geometrie.

## Slajd 14 - Ryzyka, uczciwosc i dalsze kroki

Teza: Wyniki sa gotowe do pokazania, ale nalezy jasno nazwac ograniczenia.

Wymienic:

- V4b nie powinno byc oceniane jako blad wzgledem izolowanego cylindra;
- warto pokazac niezaleznosc od siatki/czasu tylko na tyle, ile mamy;
- jesli profesor zapyta o dodatkowa walidacje produkcyjna, mozna zaproponowac porownanie z eksperymentem lub korelacjami dla kanalow/finow jako kolejny etap.
