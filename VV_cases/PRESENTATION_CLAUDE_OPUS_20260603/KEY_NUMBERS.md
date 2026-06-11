# Key Numbers

## V1 - hydrodynamic solver verification

Rola w prezentacji: sprawdzenie dynamiki przeplywu na znanym problemie.

Zrodla:

- `source_refs/V1_run002_summary.md`
- `source_refs/V1_comparison_vs_sahin_owens.csv`
- figury w `assets/V1_solver_verification/`

Pokazac:

- prog Hopfa / onset niestacjonarnosci;
- trend `St(Re)`;
- parity plot wzgledem literatury.

Nie mowic:

- ze V1 jest geometria produkcyjna;
- ze V1 ma dawac te same wartosci co V4b.

## V2 - thermal validation

Rola w prezentacji: walidacja liczby Nusselta dla ogrzewanego cylindra w kontrolowanej geometrii O-grid.

Zrodlo:

- `source_refs/V2_run004_summary.md`

Tabela V2:

| Re | Nu present | Nu ref | err % | Cd | St |
|---:|---:|---:|---:|---:|---:|
| 10 | 1.88065 | 1.86230 | 0.985 | 2.92589 | - |
| 20 | 2.48293 | 2.46530 | 0.715 | 2.10311 | - |
| 40 | 3.30454 | 3.28250 | 0.671 | 1.57125 | - |
| 45 | 3.47356 | 3.46566 | 0.228 | 1.50067 | - |
| 60 | 3.97777 | 3.97516 | 0.066 | 1.40861 | 0.12686 |
| 100 | 5.17196 | 5.12778 | 0.862 | 1.33290 | 0.15392 |
| 200 | 7.50399 | 7.42021 | 1.129 | 1.32336 | 0.18312 |

Kluczowy przekaz:

Wszystkie przypadki V2 maja blad `Nu` okolo `0.07-1.13%` wzgledem referencji, wiec warstwa cieplna jest mocno walidowana dla kanonicznego problemu.

## V4b - production application

Rola w prezentacji: glowny wynik inzynierski dla realniejszej geometrii elementu wymiennika.

Zrodla:

- `source_refs/V4b_run008_summary.md`
- `source_refs/V4b_final_figure_captions.md`
- figury w `assets/V4b_production_case/`

Run:

- `t_end = 10 s`;
- useful window `t = 2..10 s`;
- `20` MPI ranks;
- `Mesh OK`;
- effective record length `25.98` shedding cycles.

Aerodynamika:

- `Cd_mean = 3.361014 +/- 0.000772`;
- `Cl_rms = 0.176441 +/- 0.011097`;
- `St = 0.154261 +/- 0.009574`;
- every-second `Cl` peak: `f_shed = 3.2787 Hz`, `St = 0.15572`;
- PSD dominated by `2*f_shed`;
- pressure dominates mean/fluctuating forces.

Cieplo:

- `Nu_EB = 7.770004 +/- 0.091573`;
- `Nu_wall = 7.816521 +/- 0.012286`;
- wall-air closure `+0.706 +/- 1.075%`;
- `Q_air = 1.4703 W`;
- `Q_wall = 1.4807 W`;
- `Q_tube = 0.3618 W`;
- `Q_fins = 1.1189 W`;
- heat share tube/fins `24.43% / 75.57%`;
- `Nu_tube_wall = 8.4344`;
- `Nu_fins_wall = 7.6357`;
- `Nu_total_wall = 7.8165`;
- `Nu_EB = 7.7668` w warstwie heat-balance.

Najwazniejsze zdanie obronne:

V4b nie jest walidowane przez zgodnosc z `Cd`, `St` lub `Nu` izolowanego cylindra, bo geometria produkcyjna ma inne warunki brzegowe i inne mechanizmy przeplywu. V4b jest oceniane przez domkniecie bilansu energii, stabilnosc przebiegow, spojna czestotliwosc zrzucania wirow, niepewnosc oraz sensownosc rozkladow lokalnych.
