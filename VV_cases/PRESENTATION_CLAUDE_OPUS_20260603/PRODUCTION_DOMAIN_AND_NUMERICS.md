# Production Domain And Numerics

Cel tego pliku: szybka sciaga do slajdu metodologicznego o `V4b` oraz do odpowiedzi na pytania profesora o wlot, wylot, siatke, `dt` i wiarygodnosc przebiegu.

## 1. Rola `V4b`

`V4b` nie jest benchmarkiem cylindra. To przypadek produkcyjny elementu wymiennika, uruchomiony po przejsciu przez:

- `V1` - verification warstwy hydrodynamicznej,
- `V2` - validation warstwy cieplnej,
- kampanie diagnostyczne `V4b`, ktore ustalily akceptowany setup domeny i numeriki.

## 2. Akceptowana domena produkcyjna

Zrodlo: `source_refs/V4b_production_run_spec.md`

Akceptowany setup `run008`:

- `Re = 200`
- `Lin = 2D`
- `Lout = 8D`
- geometria: ogrzewana rura z finami w kanale produkcyjnym
- interpretacja fizyczna: domena jest celowo ograniczona, bo ma odtwarzac rzeczywisty przeplyw w elemencie wymiennika, a nie izolowany cylinder w szerokim polu

Znaczenie do prezentacji:

- dlugosc wlotu i wylotu nie jest przypadkowa;
- domena zostala dobrana jako kompromis miedzy realizmem geometrii, stabilnoscia obliczen i mozliwoscia wykonania bogatego samplingu;
- rozbieznosci wobec benchmarku cylindra sa oczekiwane, bo `confinement` i finy zmieniaja fizyke.

## 3. Siatka i model fizyczny

Zrodlo: `source_refs/V4b_production_run_spec.md`

Najwazniejsze ustawienia:

- corrected BL mesh
- `407,440` cells
- solver: OpenFOAM `foamRun -solver fluid`
- model: constant-property `eConst + Boussinesq + sensibleInternalEnergy`
- capacity coefficient `1005`
- `mu = 1.827e-05`
- `Pr = 0.713`

Co mowic:

- do produkcyjnego runu przyjeto setup po kampanii porownawczej, a nie pierwszy lepszy przypadek;
- wybrano konfiguracje, dla ktorej heat-balance closure jest wiarygodne.

## 4. Stabilnosc czasowa i kontrola `dt`

Zrodla:

- `source_refs/V4b_production_run_spec.md`
- `source_refs/V4b_audit_uncertainty.md`
- `source_refs/V4b_run008_summary.md`

Warunki uruchomienia i stabilnosci:

- `maxCo = 0.8`
- w `run008` poczatkowe `Co_max` pozostalo ponizej `0.8`
- `t_end = 10 s`
- odrzucany transient: `t < 2 s`
- glowne okno analizy: `t = 2..10 s`
- efektywna dlugosc rekordu: `25.98` cykli shedding, czyli powyzej planowanego minimum `20` cykli

To jest najwazniejsze zdanie:

Nie bronimy `V4b` jednym nominalnym `deltaT`, tylko stabilnoscia numeryczna, kontrola Couranta i kompletna, regularna siatka czasowa sygnalow wyjsciowych.

## 5. Rzeczywiste cadence samplingu

Zrodlo: `source_refs/V4b_audit_uncertainty.md`

Audit potwierdza kompletne i regularne probkowanie:

| Signal | expected dt [s] | samples | missing | regular |
|---|---:|---:|---:|---|
| `forceCoeffs` | `0.005` | `2001` | `0` | `True` |
| `forces_raw` | `0.005` | `2001` | `0` | `True` |
| `wallHeatFlux` | `0.005` | `2001` | `0` | `True` |
| `hot_tube_surface` | `0.005` | `2001` | `0` | `True` |
| `hot_fin_surface` | `0.005` | `2001` | `0` | `True` |
| `midspan_z0` | `0.020` | `501` | `0` | `True` |
| `outlet_T_phi` | `0.080` | `101` | `0` | `True` |

Wniosek:

- sily i sygnaly cieplne maja wysoka czestosc probkowania `200 Hz`;
- przekroj midspan i zapis outlet sa rzadsze, ale zgodne z kontraktem produkcyjnym;
- w danych nie ma brakow, ktore podwazalyby analize spektralna, coherence albo bilans energii.

## 6. Wlot, wylot i co one znacza metodologicznie

To, co warto powiedziec na spotkaniu:

- `Lin = 2D` oznacza rozwoj przeplywu przed elementem, ale nie jest to dlugi laboratoryjny kanal benchmarkowy;
- `Lout = 8D` daje miejsce na rozwiniecie wake i analize shedding/PSD/coherence za elementem;
- outlet jest dodatkowo wykorzystywany do rekonstrukcji `T/phi` potrzebnych do `Nu_EB` i bilansu ciepla;
- ten setup jest podporzadkowany pytaniu inzynierskiemu dla wymiennika, a nie literaturowemu benchmarkowi izolowanego cylindra.

## 7. Co pokazac na slajdzie

Rekomendowany zestaw:

- figura `assets/V4b_production_case/V4b_fig01_geometry_domain_sampling.png`
- 5-7 punktow z sekcji 2-5 tego pliku
- jedno zdanie obronne:

`Domena produkcyjna zostala zaakceptowana po kampanii porownawczej, a jej wiarygodnosc opiera sie na stabilnosci Couranta, kompletnej siatce czasowej probkowania, domknieciu bilansu energii i analizie obejmujacej ponad 25 cykli shedding.`

## 8. Czego nie mowic

- nie mowic, ze `Lin=2D` i `Lout=8D` sa "zwalidowane literatura cylindra";
- nie mowic, ze `V4b` ma odtwarzac wartosci benchmarkowe `Cd`, `St`, `Nu`;
- nie mowic o samej liczbie komorek jako jedynym dowodzie jakosci.

Lepsza wersja:

`Geometria i numerika produkcyjna zostaly wybrane po testach stabilnosci i porownaniach kampanii, a nastepnie ocenione przez sampling completeness, window sensitivity i heat-balance closure.`
