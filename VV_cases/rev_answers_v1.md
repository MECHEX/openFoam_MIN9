# rev_answers_v1

Data: 2026-06-04

Cel dokumentu: zebrac w jednym miejscu odpowiedzi na uwagi recenzenta dotyczace prezentacji i projektu CFD/OpenFOAM. Dokument jest samodzielny: zawiera liczby, interpretacje i braki bez koniecznosci zagladania do innych plikow.

## 1. Najkrotszy werdykt

Repo zawiera mocne odpowiedzi na czesc uwag recenzenta:

- mamy wyniki dla domeny produkcyjnej `Lin = 2D`, `Lout = 8D`;
- mamy testy czulosci wlotu i wylotu;
- mamy testy `maxCo = 0.4 / 0.8 / 1.0` w kampanii V4b;
- mamy audyt samplingu i okien czasowych, wlacznie z `Cl_rms` i `St`;
- mamy walidacje cieplna V2 dla `Nu` z bledami okolo `0.07-1.13%`;
- mamy hydrodynamiczna weryfikacje V1 oraz przypadki obejmujace `beta = 0.375`;
- mamy DMD jako sanity check dla czestotliwosci;
- mamy analize POD/EPOD/coherence/TE, ale jej jezyk musi byc ostrozny;
- mamy diagnostyke variable-property `run007a`, ale nie mamy zamknietego produkcyjnego porownania variable-property.
- mamy produkcyjny grid convergence / GCI check dla V4b force coefficients na trzech siatkach: `196,938`, `407,440`, `829,761` cells.
- mamy produkcyjny thermal GCI check w oknie wspolnym `2-3 s` dla `Nu_EB`, `Nu_wall`, `Q_wall` i `T_out`.

Najwieksze braki:

- nie mamy jeszcze robust `St` grid study z dluzszego okna dla coarse/fine;
- nie mamy eksperymentu dla tej dokladnej geometrii produkcyjnej;
- nie mamy produkcyjnego skanu Re pokazujacego `before and after Hopf`;
- nie mamy korekty wielokrotnych porownan dla TE fin bins;
- nie mamy confidence intervals dla wyzszych modow POD;
- nie mamy pelnego raportu rozkladu Couranta typu `Co_mean`, `Co_p95`;
- nie mamy opisanych przedzialow ufnosci dla estymacji koherencji Welcha.

## 2. Odpowiedz na fundamentalny zarzut

Recenzent ma racje, ze sama sciezka narracyjna `narzedzie sprawdzone -> narzedzie zastosowane` nie zamyka wszystkich wymagan publikacyjnych Q1. Po wykonaniu nowego GCI dla force coefficients oraz metryk cieplnych sytuacja jest mocniejsza, ale dwa elementy pozostaja niepelne:

1. dluzszy grid study dla `St` / statystyk czestotliwosciowych coarse-fine,
2. zewnetrzna walidacja eksperymentalna albo bardzo dobrze dobrana korelacja dla podobnej geometrii.

Jednoczesnie repo nie jest puste metodologicznie. Mamy kompletna warstwe:

- `V1`: weryfikacja hydrodynamiczna solvera,
- `V2`: walidacja cieplna liczby Nusselta,
- `V4b`: produkcyjny run z audytem domeny, czasu, samplingu, bilansu energii i modalnej analizy sprzezenia aero-termicznego.

Najuczciwsza odpowiedz:

`Na seminarium wewnetrzne sciezka V1/V2/V4b jest obronna, o ile jasno powiemy, ze V4b ma juz produkcyjny GCI check dla force coefficients oraz dla Nu_EB/Nu_wall w oknie wspolnym 2-3 s, ale nie jest jeszcze pelnym ASME-style validation package. Do publikacji Q1 potrzebujemy dluzszego potwierdzenia St/statystyk czestotliwosciowych i najlepiej zewnetrznej walidacji albo dodatkowej korelacyjnej kontroli rzedu wielkosci.`

## 3. Blokery recenzenta

### 3.1 Window sensitivity pomija `Cl_rms` i `St`

Status: mamy dane, nalezy pokazac.

Recenzent zarzuca, ze tabela pokazuje tylko stabilne metryki `Cd`, `Nu_EB` i closure, a pomija bardziej wrazliwe `Cl_rms` i `St`.

Dane z kampanii V4b:

| Run | Rola | Window | Cd_mean | Cl_rms | St | Nu | Uwagi |
|---|---|---:|---:|---:|---:|---:|---|
| run004b | accepted domain baseline | 3..6 s | 3.361490 | 0.184056 | 0.15517 | 7.777953 | baseline domeny |
| run005 | inlet sensitivity | 3..6 s | 3.359275 | 0.184616 | 0.15519 | 7.775975 | test wlotu |
| run007c | Cp-capacity smoke | 0.5..2 s | 3.361209 | 0.176698 | brak | 7.821736 | krotki smoke |
| run008 | production reference | 2..10 s | 3.361014 | 0.176441 | 0.15426 | 7.770004 | finalny run |

Roznice wzgledem run008:

| Run | Cd diff | Cl_rms diff | Nu diff |
|---|---:|---:|---:|
| run004b | +0.014% | +4.315% | +0.102% |
| run005 | -0.052% | +4.633% | +0.077% |
| run007c smoke | +0.006% | +0.145% | +0.666% |

Wniosek:

Mamy odpowiedz na zarzut cherry-pickingu. Nalezy pokazac `Cl_rms` i `St` jawnie. Trzeba tez uczciwie powiedziec, ze `Cl_rms` jest bardziej wrazliwe na okno czasowe niz `Cd` i `Nu`.

Proponowana odpowiedz:

`Uzupelnilismy tabele o Cl_rms i St. Cd, St i Nu sa stabilne miedzy wariantami domeny/wlotu, natomiast Cl_rms wykazuje kilka procent roznicy i traktujemy go ostrozniej jako metryke amplitudy niestacjonarnosci, a nie jako podstawowe kryterium akceptacji cieplnej.`

### 3.2 Grid convergence / GCI dla domeny produkcyjnej

Status: mamy nowy produkcyjny GCI check dla wspolczynnikow sil oraz metryk cieplnych w oknie wspolnym `2-3 s`.

Wykonane siatki:

| Level | Cells | Rola |
|---|---:|---|
| coarse | 196,938 | nowa siatka V4b GCI |
| medium | 407,440 | produkcyjny `run008` |
| fine | 829,761 | nowa siatka V4b GCI |

Wspolczynniki przy `t = 3 s`:

| Level | Cd | Cl | Cm |
|---|---:|---:|---:|
| coarse | 3.325969 | 2.320129 | 0.0103007 |
| medium | 3.352175 | 2.322302 | 0.0104446 |
| fine | 3.365623 | 2.332751 | 0.0104589 |

Srednie w oknie wspolnym `2-3 s`:

| Level | Cd_mean | Cl_mean | Cl_rms |
|---|---:|---:|---:|
| coarse | 3.337671 | 2.531947 | 2.541191 |
| medium | 3.364467 | 2.539078 | 2.548479 |
| fine | 3.377946 | 2.539904 | 2.549094 |

GCI:

| Metryka | Zrodlo | p | GCI fine/medium | GCI medium/coarse | Status |
|---|---|---:|---:|---:|---|
| Cd | `t=3 s` | 2.6888 | 0.560% | 1.064% | monotonic |
| Cl | `t=3 s` | 6.8128 | 0.139% | 0.0278% | monotonic |
| Cm | `t=3 s` | 9.5199 | 0.0199% | 0.1905% | monotonic |
| Cd | mean `2-3 s` | 2.7715 | 0.537% | 1.040% | monotonic |
| Cl | mean `2-3 s` | 8.8673 | 0.00566% | 0.0463% | monotonic |
| Cm | mean `2-3 s` | n/a | n/a | n/a | non-monotonic |

Metryki cieplne, srednie w oknie wspolnym `2-3 s`:

| Level | Nu_EB | Nu_wall | closure ratio | Q_air [W] | Q_wall [W] | T_out [K] |
|---|---:|---:|---:|---:|---:|---:|
| coarse | 7.719756 | 7.990602 | 3.5799% | 1.462810 | 1.515177 | 305.5837 |
| medium | 7.488820 | 7.795708 | 4.1994% | 1.424487 | 1.484307 | 305.2559 |
| fine | 7.417241 | 7.740256 | 4.4991% | 1.412095 | 1.475626 | 305.1507 |

Thermal GCI:

| Metryka | Zrodlo | p | GCI fine/medium | GCI medium/coarse | Status |
|---|---|---:|---:|---:|---|
| Nu_EB | mean `2-3 s` | 4.7853 | 0.572% | 1.761% | monotonic |
| Nu_wall | mean `2-3 s` | 5.1409 | 0.376% | 1.262% | monotonic |
| Q_wall | mean `2-3 s` | 5.1897 | 0.304% | 1.033% | monotonic |
| T_out | mean `2-3 s` | 4.6413 | 0.0215% | 0.0645% | monotonic |

Interpretacja:

- `Cd` ma dobra, monotoniczna zbieznosc; fine/medium GCI wynosi okolo `0.54-0.56%`.
- `Cl` jest bardzo blisko na trzech siatkach; wysoki rzad pozorny wynika z bardzo malej roznicy medium-fine, wiec traktujemy go jako wskazanie malej wrazliwosci siatkowej, a nie jako mocny dowod wysokiego rzedu metody.
- `Cm` jest mala metryka pomocnicza; chwilowe `t=3 s` jest monotoniczne, ale srednia `2-3 s` jest non-monotonic, wiec nie raportujemy dla niej formalnego GCI.
- `Nu_EB` i `Nu_wall` maja monotoniczna zbieznosc; medium jest w okolicach `1%` od fine dla obu niezaleznych definicji wymiany ciepla.
- `closure ratio` w oknie `2-3 s` jest wieksze niz pelne produkcyjne closure `+0.706%` z okna `2-10 s`, bo krotkie okno nadal lapie transport lag na outlecie; dlatego closure traktujemy jako diagnostyke spojnosci, a nie glowna metryke GCI.
- To zamyka najwazniejszy zarzut grid sensitivity dla wspolczynnikow sil i globalnych metryk cieplnych w produkcyjnej geometrii. Do pelnego pakietu publikacyjnego zostaje glownie dluzsze potwierdzenie `St`/statystyk czestotliwosciowych i zewnetrzna walidacja/korelacja.

Proponowana odpowiedz:

`Uzupelnilismy produkcyjny grid study dla V4b o trzy siatki: 196,938 / 407,440 / 829,761 cells. Dla Cd otrzymalismy monotoniczna zbieznosc i GCI fine/medium okolo 0.54-0.56%, a dla Nu_EB i Nu_wall odpowiednio okolo 0.57% i 0.38% w oknie wspolnym 2-3 s. Medium mesh jest wiec wystarczajaco blisko fine dla podstawowych metryk aerodynamicznych i cieplnych. Nie przedstawiamy tego jako pelnej walidacji eksperymentalnej; jest to verification / grid sensitivity. Do pelnego pakietu publikacyjnego pozostaje dluzsze potwierdzenie St oraz zewnetrzna walidacja lub korelacyjny order-of-magnitude check.`

### 3.3 Schemat geometrii z blednym `Lin/Lout`

Status: dane mamy, trzeba dopilnowac rysunku.

Poprawne parametry domeny produkcyjnej:

| Parametr | Wartosc |
|---|---:|
| D | 12 mm |
| Lin | 2D = 24 mm |
| Lout | 8D = 96 mm |
| Lf | 2.309D |
| H | 2.667D |
| Lz | 1D = 12 mm |
| liczba komorek run008 | 407,440 |

Domena produkcyjna nie jest szeroka domena izolowanego cylindra. Jest kompaktowa komorka wymiennika.

Proponowana odpowiedz:

`Rysunek musi zostac poprawiony na Lin=2D i Lout=8D. To nie jest zmiana wyniku, tylko korekta prezentacyjna. Dane i opis run008 sa zgodne z Lin=2D, Lout=8D, Lz=1D.`

## 4. Uwagi powazne

### 4.1 Abstrakt obiecuje `before and after Hopf`, ale V4b pokazuje tylko Re = 200

Status: nie mamy pelnego produkcyjnego Re-scan.

Co mamy:

- `V1` obejmuje onset/shedding w benchmarkach.
- `V4b run008` jest finalnym produkcyjnym runem przy `Re = 200`.
- W run logu V4b mamy:

| Run | Re | Status | Cd_mean | Cl_rms | St | Nu_EB |
|---|---:|---|---:|---:|---:|---:|
| run001 | 100 | STEADY | 4.00 | 0 | N/A | 7.054 |
| run002 | 100 | STEADY | 3.9974 | 0 | N/A | 6.955 |
| run003 | 200 | PERIODIC | 3.161 | 0.187 | 0.1484 | 7.476 |
| run004b | 200 | PERIODIC | 3.361 | 0.184 | 0.1552 | 7.778 |
| run008 | 200 | ANALYZED | 3.361 | 0.176 | 0.1543 | 7.770 |

Interpretacja:

Mamy dowod, ze `Re=100` w V4b bylo steady, a `Re=200` periodic. Nie mamy jednak produkcyjnego, uporzadkowanego skanu `Re` przez prog Hopfa.

Proponowana odpowiedz:

`Dla obecnej prezentacji nalezy zmienic claim z "before and after Hopf" na "post-Hopf production reference at Re=200, with preliminary steady Re=100 context". Pelny Re-scan V4b przez onset jest praca do wykonania. Minimalna macierz: Re=120, 140, 160, 180, 200.`

### 4.2 POD mode 1 vs Cl = okolo -0.99 moze byc tautologiczne

Status: mamy dane, trzeba zmienic interpretacje.

Dane:

| Metryka | Wartosc |
|---|---:|
| n_snapshots POD | 401 |
| n_points midspan | 13,524 |
| U mode 1 energy | 40.696607% |
| U mode 2 energy | 40.522935% |
| T mode 1 energy | 39.703996% |
| T mode 2 energy | 38.273113% |
| joint U+T mode 1 energy | 40.220773% |
| joint U+T mode 2 energy | 39.757562% |
| T POD mode 1 correlation with Cl | -0.9865 |
| joint POD mode 1 correlation with Cl | -0.9781 |
| U POD mode 1 correlation with Cd | -0.8503 |
| DMD near f_shed | 3.357668 Hz |
| DMD near 2f_shed | 6.569508 Hz |

Wniosek:

Recenzent ma racje, ze korelacja `T POD mode 1` z `Cl` nie powinna byc sprzedawana jako odkrycie przyczynowe. To jest sanity check, ze POD uchwycil dominujacy oscillator sheddingowy.

Proponowana odpowiedz:

`Korelacje POD-Cl traktujemy jako sanity check, a nie jako glowny wynik. Glownym wynikiem jest EPOD/coherence/local Nu: pokazanie, gdzie i z jaka faza struktury aerodynamiczne organizuja lokalna wymiane ciepla.`

### 4.3 Phase-averaged Nu na rurze pokazuje mala modulacje

Status: mamy liczby, nalezy oslabic claim.

Dane dla lokalnego Nu na rurze:

| Metryka | Wartosc |
|---|---:|
| n_times | 1601 |
| n_theta_bins | 96 |
| n_z_bins | 30 |
| Nu_mean_area_proxy | 8.588057 |
| Nu_rms_area_proxy | 0.097830 |
| A1_mean | 0.025266 |
| A1_max | 0.062989 |
| A2_mean | 0.021483 |
| A2_max | 0.059636 |
| asym_abs_mean | 0.290857 |
| asym_abs_max | 1.325308 |
| theta_profile_max_deg | 155.625 |
| theta_profile_min_deg | 35.625 |
| upper-lower asymmetry corr with Cl | 0.900067 |
| best short-lag corr | 0.922201 at -0.005 s |

Wniosek:

Srednia modulacja pierwszej harmonicznej na rurze jest mala: `A1_mean = 0.025`, czyli okolo 2.5% w przyjetej metryce. Lokalne piki dochodza do `A1_max = 0.063`. Rurka pokazuje wyrazna asymetrie skorelowana z `Cl`, ale nie nalezy twierdzic, ze caly profil Nu na rurze jest silnie modulowany fazowo.

Proponowana odpowiedz:

`Na rurze modulacja fazowa Nu jest skromna srednio, A1_mean okolo 0.025, z lokalnymi pikami do 0.063. Silniejszy i bardziej globalny kanal sprzezenia widzimy na finach i przy drugiej harmonicznej.`

### 4.4 Weryfikacja V1 przy innym blockage ratio niz produkcja

Status: mamy czesciowa odpowiedz.

Produkcja V4b ma `beta = 0.375`.

W kampanii V1 istnieja przypadki obejmujace zakres:

| beta | Przyklady Re |
|---:|---|
| 0.300 | Re 80, 90, 95, 100, 120 |
| 0.375 | Re 90, 105, 110, 120, 135 |
| 0.500 | Re 100, 120, 125, 130, 135, 140, 150 |
| 0.600 | Re 120, 125, 135 |

Dodatkowo jeden dobrze udokumentowany punkt porownawczy:

| case | beta | Re | cells | regime | Cd_mean | Cl_rms | f [Hz] | St_sim | St_ref | dSt [%] |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| b060_medium_Re135 | 0.6 | 135 | 33,268 | periodic | 4.608416 | 0.001323 | 5.824384 | 0.409807 | 0.4073 | 0.616 |

Wniosek:

Mozemy powiedziec, ze kampania V1 obejmuje `beta = 0.375`, czyli wartosc zgodna z produkcja. Jednak najbardziej uporzadkowana tabela porownawcza do literatury w repo jest nadal mocniejsza dla `beta = 0.6` niz dla calej matrycy.

Proponowana odpowiedz:

`Production beta=0.375 nie lezy poza zakresem V1. W V1 mamy przypadki beta=0.30-0.60, w tym beta=0.375. Najmocniejszy pokazany punkt literaturowy to beta=0.6, ale transfer zaufania nie opiera sie na jednym beta; beta=0.375 bylo rowniez uruchamiane w kampanii onset/consistency.`

### 4.5 `maxCo = 0.8` moze byc agresywne

Status: mamy czesciowa odpowiedz, brakuje pelnego rozkladu Co.

Co mamy:

| Run | Re | Mesh | maxCo/test | Status | Cd_mean | Cl_rms | St | Nu_EB | Uwagi |
|---|---:|---|---|---|---:|---:|---:|---:|---|
| run006a | 200 | BL lvl-2 | maxCo=0.4 | PARTIAL | 3.362 | 0.190 | 0.1541 | 7.723 | partial 0.5..2.6 s |
| run006b | 200 | BL lvl-2 | maxCo=1.0 | SHORT | 3.361 | 0.177 | 0.1546 | 7.734 | short smoke |
| run008 | 200 | BL lvl-2 | maxCo=0.8 | ANALYZED | 3.361 | 0.176 | 0.1543 | 7.770 | production |

Dodatkowo:

- poczatkowe `Co_max` w run008 pozostalo ponizej `0.8`;
- residuals i continuity errors byly skonczone;
- run008 zakonczyl sie poprawnie do `t_end = 10 s`.

Czego brakuje:

- `Co_mean` dla run008;
- `Co_p95` albo histogram Couranta;
- informacja, jaki procent komorek ma `Co < 0.3`.

Proponowana odpowiedz:

`Mamy testy maxCo=0.4 i maxCo=1.0, ktore wspieraja wybor maxCo=0.8 jako produkcyjnego kompromisu, ale nie mamy jeszcze pelnego rozkladu Co_mean/p95 dla run008. Do publikacji nalezy wyciagnac histogram Couranta z logow lub pol i dodac Co_mean, Co_p95 oraz Co_max.`

### 4.6 Boussinesq przy DeltaT = 50 K

Status: mamy diagnostyke, ale nie pelne zamkniecie.

Dane:

- `T_wall = 343.15 K`
- `T_in = 293.15 K`
- `DeltaT = 50 K`
- `betaT * DeltaT` okolo `0.17`

Kampania:

| Run | Model | Cd | Cl_rms | Q_wall [W] | Q_air case [W] | Nu_wall case-k | wall-air diff |
|---|---|---:|---:|---:|---:|---:|---:|
| run004b | baseline eConst/Boussinesq Cv=718 | 3.361209 | 0.176698 | 1.0591 | 1.0445 | 7.8217 | +1.4% |
| run007a | variable props: incompressiblePerfectGas + Sutherland | 3.473619 | 0.178979 | 1.3396 | 1.8450 | 7.3786 | -27.4% |
| run007c | constant props: eConst/Boussinesq capacity=1005 | 3.361209 | 0.176698 | 1.4824 | 1.4621 | 7.8217 | +1.4% |

Wniosek:

Boussinesq jest fizycznym zalozeniem granicznym, a nie oczywistoscia. Mamy diagnostyke variable-property, ale `run007a` nie domyka bilansu energii. Nie powinien definiowac produkcji, dopoki nie zostanie zdiagnozowany.

Proponowana odpowiedz:

`Boussinesq przy betaT*DeltaT okolo 0.17 traktujemy jako marginalne, ale spojne zalozenie bazowe. Variable-property run007a zmienil Cd i odpowiedz cieplna, ale mial wall-air closure -27.4%, wiec nie moze byc produkcyjnym odniesieniem bez dalszej diagnostyki.`

### 4.7 `Lz/D = 1` i quasi-2D

Status: mamy parametry geometrii, trzeba doprecyzowac jezyk.

Dane:

- `D = 12 mm`
- `Lz = 12 mm`
- `Lz/D = 1`
- span: `0 <= z <= 12 mm`
- plaszczyzny `z = 0/Lz` sa traktowane jako `symmetryPlane` w baseline
- fin pitch odpowiada fizycznej komorce wymiennika

Wniosek:

Nie nalezy mowic o pelnym, nieograniczonym 3D wake jak dla dlugiego cylindra. Nalezy mowic o fizycznej komorce fin-and-tube o `Lz/D = 1`, ktora z definicji ogranicza dlugofalowe tryby spanwise.

Proponowana odpowiedz:

`Lz/D=1 nie jest arbitralnym skroceniem domeny, tylko odpowiada fizycznemu pitchowi komorki wymiennika. Symulacja nie ma odtwarzac pelnego nieograniczonego wake cylindra z dlugofalowymi modami spanwise; ma odtwarzac ograniczona komorke fin-and-tube.`

### 4.8 Transfer entropy i korekta wielokrotnych porownan

Status: mamy TE i surrogate test, ale nie mamy Bonferroni/FDR.

Dane TE:

- window: `2.0..10.0 s`
- sampling: `200 Hz`
- samples: `1601`
- discretization: `4` quantile bins
- global lags: `0.005, 0.010, 0.020, 0.040, 0.060, 0.080, 0.120, 0.160, 0.240, 0.320, 0.480 s`
- surrogates: `250` for global/modal signals
- surrogates: `160` for reduced fin x-bins

Najmocniejsze globalne kierunki:

| Direction | lag [s] | TE [bits] | surrogate95 | surrogate99 | p_emp | significant95 |
|---|---:|---:|---:|---:|---:|---|
| Cl -> Q_wall | 0.240 | 0.2368 | 0.1345 | 0.1448 | 0.004 | True |
| Cl -> Q_tube | 0.080 | 0.3769 | 0.1922 | 0.2234 | 0.004 | True |
| Cl -> Q_fins | 0.240 | 0.4519 | 0.1810 | 0.2014 | 0.004 | True |
| Cl -> Nu_tube | 0.240 | 0.1413 | 0.0671 | 0.0711 | 0.004 | True |
| Cl -> Nu_fins | 0.240 | 0.1739 | 0.0639 | 0.0710 | 0.004 | True |
| Cl -> Nu_EB | 0.060 | 0.2602 | 0.1484 | 0.1751 | 0.004 | True |

Reduced fin-bin TE:

- `z_min`: significant x-bins `16/16`
- `z_max`: significant x-bins `16/16`

Czego brakuje:

- Bonferroni correction dla 16 binow;
- FDR;
- jawny family-wise error rate;
- p-values po korekcie.

Proponowana odpowiedz:

`TE jest traktowane jako exploratory directionality screen, nie jako dowod przyczynowy. Mamy circular-shift surrogate test, ale nie mamy jeszcze korekty wielokrotnych porownan dla 16 binow finow. Do publikacji nalezy dodac Bonferroni albo FDR i odpowiednio oslabic claim, jesli czesc binow nie przetrwa korekty.`

### 4.9 POD: 401 snapshotow i brak CI dla wyzszych modow

Status: mamy dane podstawowe, nie mamy niepewnosci modow 3-8.

Dane:

- snapshots: `401`
- window: `2.0..10.0 s`
- midspan points: `13,524`
- U modes 1+2: okolo `81.22%` calkowitej energii pierwszych dwoch modow liczonych osobno jako `40.70% + 40.52%`
- T modes 1+2: okolo `77.98%`
- joint U+T modes 1+2: okolo `79.98%`
- U pair 1/2 share of first 8 modes: `0.874521`
- T pair 1/2 share of first 8 modes: `0.840013`

Wniosek:

Pary 1-2 sa mocne i wiarygodne jako shedding pair. Wyzej polozone mody powinny byc traktowane ostrozniej.

Proponowana odpowiedz:

`POD modes 1-2 sa dominujaca para sheddingowa i sa wspierane przez DMD. Mody 3-8 traktujemy jako indicative, dopoki nie dodamy bootstrap confidence intervals dla energii modalnej.`

### 4.10 Slowko `mechanistic`

Status: mamy czesciowe wsparcie, ale slowo trzeba uzyc ostroznie.

Co mamy:

- POD: identyfikuje dominujace struktury na midspan;
- DMD: potwierdza `f_shed` i `2*f_shed`;
- EPOD/SPOD: pokazuje pola regresji i amplitudy single-frequency;
- coherence: lokalizuje sprzezenie `Cl` z lokalnym `Nu`;
- phase averaging: pokazuje organizacje w fazie cyklu;
- Q/Lambda2: istnieja warstwy strukturalne dla wirnosci i vortex cores;
- TE: exploratory directionality screen.

Najwazniejsze liczby coherence:

| Signal | coherence at f_shed | coherence at 2f_shed |
|---|---:|---:|
| Q_wall | 0.571 | 0.906 |
| Q_tube | 0.736 | 0.945 |
| Q_fins | 0.376 | 0.922 |
| Nu_tube | 0.561 | 0.950 |
| Nu_fins | 0.436 | 0.991 |
| tube mean spatial coherence | 0.454 | 0.977 |
| fin z_min mean coherence | 0.393 | 0.967 |
| fin z_max mean coherence | 0.430 | 0.980 |

Wniosek:

`Mechanistic` jest ryzykowne, jesli rozumiec to jako pelny lancuch przyczynowy. Bezpieczniej mowic `structural/modal coupling analysis` albo `mechanism-oriented analysis`.

Proponowana odpowiedz:

`Nie twierdzimy, ze POD sam w sobie dowodzi mechanizmu. Mechanizm opisujemy jako spojna interpretacje: shedding -> organizacja wake -> lokalna redystrybucja Nu -> zamkniety bilans ciepla. Formalnie narzedzia pokazuja struktury, koherencje i fazowanie, a nie pelny causal budget.`

### 4.11 Koherencja Cl-Nu i brak metadanych Welcha

Status: mamy wyniki koherencji, nie mamy pelnych przedzialow ufnosci.

Dane:

Global coherence:

| Signal | band | f [Hz] | coherence | cross phase | phase lag [s] |
|---|---|---:|---:|---:|---:|
| Q_wall | f_shed | 3.1250 | 0.5713 | -55.66 deg | -0.0472 |
| Q_wall | 2f_shed | 6.6406 | 0.9058 | -24.44 deg | -0.0104 |
| Q_tube | f_shed | 3.1250 | 0.7358 | -55.92 deg | -0.0474 |
| Q_tube | 2f_shed | 6.6406 | 0.9445 | +165.35 deg | +0.0700 |
| Q_fins | f_shed | 3.1250 | 0.3761 | -55.45 deg | -0.0470 |
| Q_fins | 2f_shed | 6.6406 | 0.9216 | -21.90 deg | -0.0093 |
| Nu_tube | f_shed | 3.1250 | 0.5608 | -100.52 deg | -0.0852 |
| Nu_tube | 2f_shed | 6.6406 | 0.9495 | +15.19 deg | +0.0064 |
| Nu_fins | f_shed | 3.1250 | 0.4361 | -109.51 deg | -0.0928 |
| Nu_fins | 2f_shed | 6.6406 | 0.9906 | +0.43 deg | +0.0002 |

Czego brakuje:

- liczba segmentow Welcha;
- confidence band na coherence;
- formalny opis wariancji estymatora.

Proponowana odpowiedz:

`Wyniki coherence sa mocne, zwlaszcza przy 2f_shed, ale do publikacji nalezy dopisac metadane estymacji: liczbe segmentow Welcha, okno, overlap i confidence interval. Na seminarium mozna pokazac je jako evidence of phase-locked coupling, nie jako precyzyjna metryke z zamknieta niepewnoscia.`

### 4.12 Definicja Nu w V2 i V4b

Status: mamy dane, trzeba wyjasnic transfer zaufania.

V2:

- waliduje ogrzewany cylinder w kontrolowanej geometrii O-grid;
- `Nu` jest porownywany do referencji;
- zakres Re: `10, 20, 40, 45, 60, 100, 200`;
- Re200 jest oznaczony jako diagnostic.

Tabela V2:

| Re | Nu present | Nu ref | err % | Cd | St | status |
|---:|---:|---:|---:|---:|---:|---|
| 10 | 1.880652 | 1.8623 | 0.985 | 2.925892 | brak | candidate |
| 20 | 2.482930 | 2.4653 | 0.715 | 2.103106 | brak | candidate |
| 40 | 3.304541 | 3.2825 | 0.671 | 1.571253 | brak | candidate |
| 45 | 3.473561 | 3.465658 | 0.228 | 1.500667 | brak | candidate |
| 60 | 3.977770 | 3.975156 | 0.066 | 1.408613 | 0.126860 | candidate |
| 100 | 5.171961 | 5.127775 | 0.862 | 1.332901 | 0.153915 | candidate |
| 200 | 7.503991 | 7.420205 | 1.129 | 1.323359 | 0.183117 | diagnostic |

V4b:

- `Nu_wall` pochodzi z powierzchni rury i finow;
- `Nu_EB` jest kontrola energy balance z rekonstrukcja outlet `T/phi`;
- lokalne `Nu(theta,z,t)` uzywa `q'' D / (k LMTD(t))`.

V4b global heat numbers:

| Metryka | Wartosc |
|---|---:|
| Nu_EB | 7.770004 +/- 0.091573 |
| Nu_wall | 7.816521 +/- 0.012286 |
| wall-air closure | +0.706 +/- 1.075% |
| Q_air | 1.4703 W |
| Q_wall | 1.4807 W |
| Q_tube | 0.3618 W |
| Q_fins | 1.1189 W |
| heat share tube/fins | 24.43% / 75.57% |
| Nu_tube_wall | 8.4344 |
| Nu_fins_wall | 7.6357 |

Wniosek:

V2 nie waliduje bezposrednio V4b, bo geometria i definicja globalnego Nu sa inne. V2 waliduje sciezke cieplna i ekstrakcje ciepla na problemie kanonicznym. V4b dodaje energy-balance cross-check.

Proponowana odpowiedz:

`V2 waliduje thermal solver path i ekstrakcje Nu na kanonicznym ogrzewanym cylindrze. V4b stosuje lokalny wall-flux Nu oraz niezalezny energy-balance cross-check. Zaufanie nie jest przeniesione przez identyczna wartosc Nu, tylko przez sprawdzona fizyke cieplna plus domkniecie bilansu energii w produkcji.`

## 5. Uwagi drobne

### 5.1 PSD dominowane przez `2*f_shed`

Status: mamy dane, trzeba nie oversellowac.

Dane:

- `f_shed` z every-second `Cl` peak: `3.2787 Hz`;
- `St = 0.15572`;
- DMD near `f_shed`: `3.3577 Hz`;
- DMD near `2*f_shed`: `6.5695 Hz`;
- PSD jest silnie zwiazane z druga harmoniczna.

Proponowana odpowiedz:

`Dominacja 2f_shed jest oczekiwana dla komponentu oporu i symetrycznej odpowiedzi cieplnej. Traktujemy ja jako zgodnosc fizyczna, nie jako nowe odkrycie.`

### 5.2 DMD sanity check

Status: mamy.

Liczby:

- `DMD_near_f_shed_hz = 3.357668`
- `DMD_near_2f_shed_hz = 6.569508`

Proponowana odpowiedz:

`DMD potwierdza czestotliwosci identyfikowane przez sily i POD: okolo 3.36 Hz oraz 6.57 Hz. To bedzie dobry backup slide.`

### 5.3 EPOD skale jako regression coefficients

Status: mamy interpretacje, trzeba opisac na slajdzie.

Proponowana odpowiedz:

`Mapy EPOD nalezy podpisac jako pola regresji, np. regression coefficient, a nie jako bezposrednie temperatury. To zapobiega blednemu odczytaniu skali.`

### 5.4 `Mesh OK` nie jest grid independence

Status: zgoda z recenzentem.

Proponowana odpowiedz:

`checkMesh passed oznacza poprawnosc topologiczna i jakosciowa siatki, ale nie niezaleznosc wyniku od dyskretyzacji. Nie bedziemy uzywac Mesh OK jako zamiennika grid convergence.`

### 5.5 Closure +0.706 +/- 1.075%

Status: mamy liczby, trzeba precyzyjnie interpretowac.

Dane:

- closure central: `+0.706%`
- 95% half-width: `1.075%`
- przyblizony przedzial: `[-0.369%, +1.781%]`

Proponowana odpowiedz:

`Bilans ciepla zamyka sie w tolerancji inzynierskiej okolo +/-2%, a przedzial bootstrap obejmuje zero. To jest argument za spojnoscia wewnetrzna, nie dowod zewnetrznej walidacji.`

### 5.6 Re = 200 w V2 jest diagnostic

Status: mamy, trzeba pokazac.

Proponowana odpowiedz:

`W V2 Re=200 ma status diagnostic. Glowna walidacja cieplna opiera sie na niskim i umiarkowanym Re, gdzie przypadki sa candidate; Re=200 pokazuje zgodnosc rzedu 1.13%, ale nie powinien byc przedstawiany jako najmocniejszy punkt walidacyjny.`

### 5.7 Trzy geometrie w narracji

Status: trzeba powiedziec wprost.

Proponowana odpowiedz:

`V1, V2 i V4b sa celowo roznymi geometriami. V1 testuje hydrodynamike, V2 testuje cieplo, V4b jest aplikacja produkcyjna. To nie jest jedna geometria rozwijana krok po kroku, tylko lancuch testow komponentow modelu.`

## 6. Pytania, ktore moga pasc, i gotowe odpowiedzi

### Q1. Jaki jest mesh-independence index / GCI dla 407k cells?

Odpowiedz:

`Mamy produkcyjny coarse/medium/fine GCI check dla 196,938 / 407,440 / 829,761 cells. Dla Cd GCI fine/medium wynosi okolo 0.54-0.56%, a dla metryk cieplnych w oknie wspolnym 2-3 s: Nu_EB okolo 0.57%, Nu_wall okolo 0.38%, Q_wall okolo 0.30%. To jest mocny verification argument, ze medium mesh 407k jest wystarczajaco blisko fine dla podstawowych metryk aerodynamicznych i cieplnych. Caveat: closure w krotkim oknie 2-3 s jest diagnostyczne przez outlet lag; finalne closure raportujemy z pelnego run008 2-10 s jako +0.706%.`

### Q2. Dlaczego V1 jest przy innym beta niz produkcja?

Odpowiedz:

`Produkcja ma beta=0.375 i ten beta jest obecny w kampanii V1. V1 obejmuje beta od 0.30 do 0.60, w tym przypadki beta=0.375 przy Re 90-135. Najmocniej udokumentowany punkt literaturowy w tabeli to beta=0.6, ale zakres V1 nie omija beta produkcyjnego.`

### Q3. Czy Lz/D=1 z symmetryPlane uchwyci pelne tryby 3D?

Odpowiedz:

`Nie udajemy dlugiego, nieograniczonego cylindra. Lz/D=1 odpowiada fizycznemu pitchowi komorki wymiennika i ogranicza dlugofalowe tryby spanwise. To jest cecha produkcyjnej geometrii, nie blad benchmarku.`

### Q4. Korelacja POD mode 1 z Cl = -0.9865, czy to tautologia?

Odpowiedz:

`Traktujemy to jako sanity check, ze POD uchwycil shedding oscillator. Glowny wynik to nie sama korelacja POD-Cl, tylko lokalne mapy Nu, coherence i EPOD pokazujace, gdzie odpowiedz cieplna jest powiazana z cyklem aerodynamicznym.`

### Q5. Co dokladnie jest mechanizmem?

Odpowiedz:

`Mechanizm opisujemy ostroznie: shedding organizuje wake, wake fazowo organizuje lokalne Nu, a finy przenosza wiekszosc ciepla. Narzedzia POD/DMD/EPOD/coherence/phase averaging pokazuja strukture i fazowanie tego procesu. Pelny causal budget to kolejny krok, wiec w publikacji lepsze jest okreslenie structural/modal coupling analysis niz mocne mechanistic claim.`

### Q6. Czemu Boussinesq przy betaT DeltaT okolo 0.17?

Odpowiedz:

`To jest marginalne zalozenie fizyczne. Sprawdzilismy variable-property diagnostic run007a, ale nie zamknal bilansu energii: wall-air diff -27.4%. Cp-consistent constant-property run007c zamyka sie na +1.4%, a run008 na +0.706 +/- 1.075%. Dlatego run008 jest spojnym baseline, ale variable-property comparison pozostaje zaplanowanym krokiem.`

### Q7. Czy 25.98 cykli wystarczy?

Odpowiedz:

`Dla srednich, RMS, PSD i podstawowej koherencji to jest wiarygodny minimalny rekord produkcyjny, przekraczajacy planowane 20 cykli. Dla TE i wyzszych modow POD traktujemy wyniki ostrozniej jako exploratory/indicative.`

### Q8. Czemu nie porownujecie Nu z korelacjami dla bankow rur?

Odpowiedz:

`Korelacje dla bankow rur nie odpowiadaja dokladnie tej pojedynczej, ograniczonej komorce fin-and-tube, ale warto je dodac jako order-of-magnitude check. Obecny wynik V4b to Nu okolo 7.77-7.82, a taka kontrola korelacyjna bylaby dobrym dodatkowym argumentem przed publikacja.`

### Q9. Czy TE jest dowodem przyczynowosci?

Odpowiedz:

`Nie. TE traktujemy jako exploratory directionality screen. Najbezpieczniejszym dowodem coupling sa coherence, cross-phase, phase averaging i lokalne mapy Nu. TE pomaga, ale nie jest samodzielnym causal proof.`

### Q10. Czy mamy pelna walidacje V4b?

Odpowiedz:

`Nie mamy zewnetrznej walidacji eksperymentalnej tej dokladnej geometrii. Mamy verification/validation narzedzia na V1/V2 oraz bardzo mocna spojnosc wewnetrzna V4b: zamkniety bilans energii, stabilne Cd/St/Nu, kompletne probkowanie i kontrolowane domeny wlotu/wylotu.`

## 7. Co trzeba zrobic przed seminarium

Priorytet 1:

- poprawic rysunek domeny na `Lin=2D`, `Lout=8D`, `Lz=1D`;
- pokazac w tabeli window/domain sensitivity `Cl_rms` i `St`;
- zmienic narracje POD-Cl z `finding` na `sanity check`;
- powiedziec wprost, ze modulacja Nu na rurze jest mala srednio: `A1_mean = 0.025`;
- oslabic slowo `mechanistic` albo zdefiniowac je ostroznie;
- zaznaczyc, ze `Mesh OK` nie jest grid convergence;
- zaznaczyc, ze `V2 Re=200` jest diagnostic.

Priorytet 2:

- dodac backup slide z domain sensitivity: `Lout=8D vs 16D`, `Lin=2D vs 4D`;
- dodac backup slide z DMD frequencies `3.3577 Hz` i `6.5695 Hz`;
- dodac backup slide o `run007a` i ograniczeniu Boussinesq;
- dodac slajd z nowym GCI force coefficients i thermal GCI oraz lista brakow uczciwie: `St long-window check planned`, `experiment/correlation planned`, `Re-scan planned`.

## 8. Co trzeba zrobic przed publikacja

Minimalny pakiet publikacyjny:

1. Domkniecie grid convergence dla V4b przy `Re=200`:
   - force coefficients oraz `Nu_EB`/`Nu_wall` sa juz policzone dla coarse / medium / fine;
   - do zrobienia: dluzszy `St`/frequency check dla coarse/fine;
   - closure traktowac jako diagnostyke transport-lag; finalne closure zostaje z pelnego `run008` 2-10 s.

2. Production Re-scan:
   - minimum: `Re = 120, 140, 160, 180, 200`;
   - cel: pokazac onset i odpowiedz cieplna przed/po Hopf;
   - wynik: `Nu(Re)`, `St(Re)`, `Cl_rms(Re)`.

3. Variable-property diagnostic:
   - ponowic lub dokonczyc model variable properties z domknietym bilansem energii;
   - sprawdzic, czy roznica Nu/Cd jest fizyczna czy implementacyjna.

4. Statystyka TE/coherence/POD:
   - Bonferroni albo FDR dla fin bins;
   - confidence bands dla coherence;
   - bootstrap confidence interval dla energii modow POD 3-8;
   - jawny opis liczby segmentow Welcha.

5. Zewnetrzna kontrola V4b:
   - eksperyment dla geometrii produkcyjnej, jesli dostepny;
   - albo order-of-magnitude comparison z korelacjami dla podobnych kanalow/fin-and-tube, z jasnym caveatem geometrycznym.

## 9. Finalna rekomendacja narracyjna

Najbezpieczniejsza wersja prezentacji:

`V1 i V2 potwierdzaja, ze solver i model cieplny dzialaja na przypadkach kanonicznych. V4b jest produkcyjnym zastosowaniem tej metody do zwartej komorki wymiennika. V4b nie jest bezposrednio walidowane wzgledem izolowanego cylindra, ale jest wewnetrznie spojne: domena wlot/wylot zostala sprawdzona, bilans energii zamyka sie w tolerancji inzynierskiej, sampling jest kompletny, aerodynamika i globalna termika maja produkcyjny GCI check, a lokalna termika wykazuje spojne fazowe sprzezenie. Glowne luki przed publikacja to dluzszy St/frequency check oraz zewnetrzna walidacja lub korelacyjny order-of-magnitude check.`
