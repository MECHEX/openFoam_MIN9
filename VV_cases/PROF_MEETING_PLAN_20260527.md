# Plan spotkania z profesorem - stan projektu na 2026-05-27

## Cel spotkania

Pokazać spójny łańcuch rozwoju projektu:

1. założenia fizyczne i pytanie badawcze,
2. weryfikację solvera i hydrodynamiki,
3. walidację ścieżki cieplnej,
4. przejście do przypadku produkcyjnego 3D,
5. jakość obecnych wyników i uczciwe ograniczenia,
6. gotowość do przygotowania materiałów do prezentacji i dalszej publikacji.

## Krótkie podsumowanie wykonanej pracy

### 1. Uporządkowanie repozytorium i metodologii

- Mamy wspólny standard archiwizacji i dokumentacji:
  - `VV_cases/README.md`
  - `VV_cases/STORAGE_STANDARD.md`
  - `VV_cases/WORKING_CHECKLIST.md`
  - `VV_cases/RESEARCH_LOG.md`
- Każde badanie ma dokument kanoniczny i historię decyzji.
- To jest mocny punkt na spotkanie, bo pokazuje kontrolę nad procesem badawczym, a nie tylko nad pojedynczym wynikiem.

### 2. V1 - weryfikacja hydrodynamiczna

- Cel V1: sprawdzić, czy setup OpenFOAM poprawnie odtwarza onset shedding i `St` dla przepływu wokół cylindra w kanale.
- Zrobiono:
  - test siatki i długości domeny dla `beta = 0.50`,
  - sweep przejścia steady -> periodic,
  - porównanie z literaturą Sahin & Owens dla `beta = 0.30`, `0.50`,
  - punkty interpolacyjne dla `beta = 0.375`,
  - dodatkowy check dla `beta = 0.60`.
- Główny wynik:
  - zgodność `St` po wejściu w reżim okresowy jest bardzo dobra, zwykle rzędu `0.1-0.7%`, a dla `beta = 0.375` około `0.9-1.7%`.
- Materiały już gotowe:
  - `VV_cases/V1_solver/doc/figs/fig1_hopf_onset.png`
  - `VV_cases/V1_solver/doc/figs/fig2_St_vs_Re.png`
  - `VV_cases/V1_solver/doc/figs/fig3_St_parity.png`

### 3. V2 - walidacja cieplna

- Cel V2a: odtworzyć referencyjne `Nu` dla ogrzewanego cylindra w przepływie wymuszonym.
- Ważny element metodologiczny:
  - pierwsza ścieżka `snappy` została odrzucona,
  - poprawna ścieżka walidacyjna to structured O-grid.
- To jest bardzo dobry element do pokazania profesorowi, bo demonstruje krytyczną selekcję metod, a nie "dopasowywanie" wyniku.
- Aktualnie zaakceptowana walidacja:
  - `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation`
- Główny wynik:
  - `Nu` zgodne z referencją w zakresie około `0.07-1.13%`,
  - temperatury bounded,
  - `0%` komórek przyściennych powyżej `T_wall`,
  - poprawna definicja `Nu` oparta o `snGrad(T)`.
- Najmocniejszy podzbiór:
  - `Re = 10..60` jako czysta walidacja,
  - `Re100` i `Re200` jako rozszerzenie unsteady/article-range, z ostrożniejszą interpretacją dla `Re200`.
- Materiały już gotowe:
  - `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2_run004_ogrid_mesh_schematic.png`
  - `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2_run004_Nu_vs_reference.png`
  - `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_Nu_Re_articles_vs_present.png`
  - `VV_cases/V2_thermal/results/study_v2a/runs/004_data_v2a_ogrid_cylinder_validation/plots/V2A_articles_vs_present_dashboard.png`

### 4. V4b - przypadek produkcyjny 3D

- Cel V4b: przejść od benchmarków do geometrii elementarnej komórki wymiennika fin-and-tube.
- Mamy zdefiniowaną geometrię i model:
  - `D = 12 mm`
  - `beta = 0.375`
  - `Lz/D = 1`
  - ogrzewana rurka i ogrzewane płetwy,
  - model Boussinesq, właściwości stałe, konfiguracja Cp-consistent.
- Najważniejszy zaakceptowany przypadek produkcyjny:
  - `VV_cases/V4b_3D/results/run008/summary.md`
- Co zostało wcześniej zamknięte zanim uznaliśmy `run008` za bazę:
  - sensitivity outletu: `run004b` vs `run004c`,
  - sensitivity inletu: `run005`,
  - timestep / `maxCo`: `run006a/b`,
  - diagnostyka variable properties: `run007a`,
  - smoke-test stabilnej architektury: `run007c`.
- To znaczy, że `run008` nie jest pojedynczym "ładnym przypadkiem", tylko końcem kontrolowanej kampanii selekcyjnej.

### 5. Najmocniejsze wyniki z run008

- Rekord obejmuje około `25.98` cykli shedding w oknie `t = 2..10 s`.
- Integralne metryki:
  - `Cd_mean = 3.361 +/- 0.001`
  - `Cl_rms = 0.176 +/- 0.011`
  - `St = 0.154 +/- 0.010`
  - `Nu_EB = 7.770 +/- 0.092`
  - `Nu_wall = 7.817 +/- 0.012`
  - closure wall-air około `+0.706%`
- Fizyczna interpretacja:
  - około `75.6%` ciepła przenoszą płetwy, około `24.4%` rurka,
  - lokalne `Nu` na rurce silnie koreluje z `Cl`,
  - pierwsze dwa mody POD dominują energetycznie i reprezentują parę sheddingową,
  - koherencja `Cl <-> Nu_local` jest bardzo silna, szczególnie przy `2*f_shed`,
  - fazowe uśrednianie daje spójną historię mechanizmu aero-termicznego.
- Bardzo ważne:
  - mamy gotowe figury jakości "paper-grade" w:
    - `VV_cases/V4b_3D/results/run008/figures/012`

## Co mamy na pewno: weryfikacja, walidacja, produkcja

### Weryfikacja - TAK

- V1 daje wiarygodną weryfikację części hydrodynamicznej.
- Mamy test siatki, domeny, onset shedding i porównanie `St` do literatury.

### Walidacja termiczna - TAK, ale w zakresie benchmarku V2

- V2 daje dobrą walidację solvera termicznego i metody ekstrakcji `Nu`.
- To jest walidacja dla unconfined heated cylinder, a nie bezpośrednio dla geometrii V4b.

### Walidacja bezpośrednia V4b - NIE

- Dla geometrii V4b nie ma bezpośredniego benchmarku literaturowego 1:1.
- Dla V4b mamy:
  - wsparcie z V1 i V2,
  - sensitivity checks,
  - zamknięcie bilansu ciepła,
  - spójność sygnałów i analiz modalnych.
- To jest silna wiarygodność wewnętrzna, ale nie klasyczna walidacja zewnętrzna.

## Uczciwe ograniczenia, które warto powiedzieć wprost

1. `run008` to obecnie jeden główny punkt produkcyjny przy `Re = 200`.
2. V4b nie ma jeszcze pełnej macierzy `Re` wokół progu shedding dla tej geometrii.
3. V4b opiera się na argumentacji:
   - solver verified,
   - thermal path validated,
   - production case sensitivity-checked,
   - internal heat balance closed,
   ale nie na bezpośredniej walidacji literaturowej tej konkretnej geometrii.
4. `run010` jest ciekawą diagnostyką variable-properties, ale nie powinien jeszcze zastępować `run008` jako bazy prezentacji jakości wyników.
5. Transfer entropy należy pokazywać ostrożnie jako warstwę exploratory, nie jako centralny dowód.

## Czy możemy już zacząć generować dane do PowerPointa?

Tak.

Ale najlepiej rozdzielić to na dwa poziomy:

### Poziom A - można generować od razu

- slajdy o celu projektu i geometrii,
- slajdy o workflow metodologicznym,
- V1: onset + `St` parity,
- V2: O-grid walidacja `Nu`,
- V4b: geometria, sensitivity campaign, audit, heat balance, modal/coherence story,
- slajd z ograniczeniami i kolejnymi krokami.

### Poziom B - warto jeszcze dopracować przed finalną prezentacją publikacyjną

- krótkie, jednoznaczne rozróżnienie:
  - verification,
  - validation,
  - production evidence,
- selekcję 6-10 najmocniejszych figur z run008,
- jedną tabelę "quality gates" dla całego projektu,
- jedną figurę spinającą V1 -> V2 -> V4b.

## Proponowany układ prezentacji dla profesora

1. Problem i motywacja
   - dlaczego cylinder confined / fin-and-tube
   - jakie pytanie fizyczne chcemy rozwiązać

2. Architektura projektu
   - `V1 = hydro verification`
   - `V2 = thermal validation`
   - `V4b = production 3D case`

3. V1 - weryfikacja hydrodynamiki
   - literatura odniesienia
   - test siatki i domeny
   - onset i `St`
   - wniosek: hydrodynamic chain is trusted

4. V2 - walidacja cieplna
   - odrzucona ścieżka `snappy`
   - przejście na O-grid
   - zgodność `Nu`
   - boundedness temperatury
   - wniosek: thermal chain is trusted

5. V4b - konfiguracja przypadku produkcyjnego
   - geometria
   - model fizyczny
   - measurement plan
   - kampania sensitivity

6. V4b - jakość danych
   - długość rekordu
   - audit completeness
   - closure heat balance
   - stabilność integralnych metryk

7. V4b - główne wyniki fizyczne
   - siły i `St`
   - udział rurki i płetw w wymianie ciepła
   - lokalne mapy `Nu`
   - POD / coherence / phase-averaging

8. Co jest naprawdę nowe
   - ilościowe sprzężenie `Cl <-> Nu_local`
   - rozdzielenie roli `f_shed` i `2*f_shed`
   - mechanistyczna historia fazowa

9. Ograniczenia i ryzyka
   - brak pełnej zewnętrznej walidacji V4b
   - jeden główny punkt `Re`
   - variable properties nadal diagnostyczne

10. Następny krok
   - albo materiał konferencyjno-raportowy,
   - albo rozszerzenie macierzy `Re` dla V4b,
   - albo dopięcie finalnego pakietu publikacyjnego.

## Minimalny zestaw slajdów, który już dziś da się złożyć

1. Cel projektu + luka badawcza.
2. Mapa projektu `V1 -> V2 -> V4b`.
3. Geometria V4b.
4. V1: `fig1_hopf_onset.png`.
5. V1: `fig3_St_parity.png`.
6. V2: `V2_run004_ogrid_mesh_schematic.png`.
7. V2: `V2_run004_Nu_vs_reference.png`.
8. V2: `V2A_articles_vs_present_dashboard.png`.
9. V4b: `fig01_geometry_domain_sampling.png`.
10. V4b: `fig03_heat_balance_nu_closure.png`.
11. V4b: `fig04_tube_nu_mean_rms.png`.
12. V4b: `fig07_pod_energy_modes.png`.
13. V4b: `fig09_cl_nu_coherence_maps.png`.
14. V4b: `fig10_mechanism_schematic.png`.
15. Wnioski + ograniczenia + plan dalszy.

## Rekomendacja przed spotkaniem

Nie zaczynałbym od najbardziej złożonych analiz modalnych.

Najlepsza narracja jest taka:

1. najpierw pokażemy, że umiemy ufać solverowi,
2. potem pokażemy, że umiemy ufać ścieżce cieplnej,
3. dopiero potem pokażemy bogaty wynik V4b.

Wtedy profesor ocenia jakość wyników na bazie pełnego łańcucha wiarygodności, a nie tylko na podstawie jednej efektownej figurki.

## Ocena gotowości

- `V1`: gotowe do pokazania.
- `V2`: gotowe do pokazania.
- `V4b run008`: gotowe do pokazania jako wynik produkcyjny i mechanistyczny.
- `V4b run010`: jeszcze nie jako podstawa głównej narracji.
- PowerPoint: można zaczynać już teraz.

## Co warto zrobić jako następny praktyczny krok

1. Wybrać finalne 10-15 figur do prezentacji.
2. Dopisać jedną zbiorczą tabelę:
   - study,
   - cel,
   - status,
   - typ dowodu,
   - główny wynik,
   - ograniczenie.
3. Przygotować 1-slajdowe rozróżnienie:
   - verification,
   - validation,
   - production evidence.
4. Dopiero potem robić wersję "ładną" do PowerPointa.
