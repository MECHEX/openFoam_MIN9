# Plan po recenzji zewnetrznej

Data: 2026-06-04

Cel: uporzadkowac najwazniejsze kroki po krytycznej recenzji prezentacji i wynikow. Plan rozdziela trzy poziomy:

- co trzeba poprawic przed spotkaniem z profesorem;
- co trzeba wykonac, zeby wyniki byly mocniejsze publikacyjnie;
- co jest dalszym rozwojem projektu, a nie warunkiem najblizszej prezentacji.

## 1. Najwazniejsza decyzja strategiczna

Obecna sciezka `V1 -> V2 -> V4b` moze sie obronic na spotkaniu, ale tylko jako:

`verification/validation narzedzia + production reference case`

a nie jako:

`pelna walidacja produkcyjnej geometrii`.

To rozroznienie musi byc jawne. Najwieksza luka po recenzji to nie brak wynikow w ogole, tylko brak dwoch formalnych elementow dla publikacji Q1:

1. grid convergence / GCI dla produkcyjnego `V4b run008`;
2. zewnetrzna walidacja albo przynajmniej order-of-magnitude check dla produkcyjnej geometrii.

## 2. Priorytet A: poprawki przed spotkaniem z profesorem

Termin: natychmiast, przed pokazaniem prezentacji.

### A1. Poprawic narracje prezentacji

Zmienic glowna teze:

`V1/V2 waliduja narzedzie na przypadkach kanonicznych, V4b jest zastosowaniem produkcyjnym.`

Nie mowic:

- `V4b jest zwalidowane wzgledem izolowanego cylindra`;
- `Mesh OK oznacza niezaleznosc od siatki`;
- `POD-Cl correlation jest odkryciem mechanistycznym`;
- `TE dowodzi przyczynowosci`;
- `before and after Hopf` dla produkcji, jesli pokazujemy tylko `Re=200` jako finalny run.

Mowic:

- `V4b jest internally consistent production reference`;
- `bilans energii zamyka sie w tolerancji inzynierskiej`;
- `domain/inlet/outlet sensitivity zostaly sprawdzone`;
- `grid convergence jest zaplanowanym kolejnym krokiem`.

### A2. Poprawic slajd domeny produkcyjnej

Wymagane parametry na rysunku:

| Parametr | Wartosc |
|---|---:|
| `D` | `12 mm` |
| `Lin` | `2D = 24 mm` |
| `Lout` | `8D = 96 mm` |
| `Lz` | `1D = 12 mm` |
| `H` | `2.667D` |
| cells | `407,440` |

Powod:

Recenzent slusznie wskazal, ze bledny schemat z `Lin=1D / Lout=2D` podwaza zaufanie. To jest prosta poprawka o bardzo duzym znaczeniu.

### A3. Dodac jawna tabele `Cl_rms` i `St`

Tabela do pokazania:

| Run | Role | Window | Cd_mean | Cl_rms | St | Nu |
|---|---|---:|---:|---:|---:|---:|
| run004b | accepted domain baseline | 3..6 s | 3.361490 | 0.184056 | 0.15517 | 7.777953 |
| run005 | inlet sensitivity | 3..6 s | 3.359275 | 0.184616 | 0.15519 | 7.775975 |
| run008 | production reference | 2..10 s | 3.361014 | 0.176441 | 0.15426 | 7.770004 |

Komentarz:

`Cd`, `St` i `Nu` sa stabilne. `Cl_rms` jest bardziej wrazliwe na okno i traktujemy je jako amplitude niestacjonarnosci, nie jako podstawowe kryterium bilansu cieplnego.

### A4. Uczciwie opisac modulacje Nu na rurze

Liczby:

| Metryka | Wartosc |
|---|---:|
| `A1_mean` | `0.025266` |
| `A1_max` | `0.062989` |
| `A2_mean` | `0.021483` |
| `A2_max` | `0.059636` |
| asymmetry corr with `Cl` | `0.900067` |

Nowy przekaz:

`Na rurze srednia modulacja fazowa Nu jest mala, ale lokalna asymetria Nu jest silnie skorelowana z Cl. Silniejsza organizacja globalna pojawia sie przez finy i druga harmoniczna.`

### A5. Przestawic POD/DMD/EPOD jako sanity + struktura, nie przyczynowosc

Pokazac:

| Metryka | Wartosc |
|---|---:|
| POD snapshots | `401` |
| U modes 1/2 | `40.70% / 40.52%` |
| T modes 1/2 | `39.70% / 38.27%` |
| T mode 1 corr with Cl | `-0.9865` |
| DMD near `f_shed` | `3.357668 Hz` |
| DMD near `2f_shed` | `6.569508 Hz` |

Komentarz:

`Korelacja POD-Cl to sanity check. Glowny wynik to lokalne Nu, coherence, EPOD i phase averaging.`

### A6. Dodac slajd "limitations and next steps"

Musi zawierac:

- brak formalnego GCI dla `run008`;
- brak eksperymentu dla tej geometrii;
- `run007a` variable-property nie domyka bilansu;
- TE jest exploratory;
- Re-scan produkcyjny przez Hopf jest planowany.

Ten slajd dziala na nasza korzysc, bo pokazuje, ze znamy ograniczenia i nie udajemy pelnej walidacji.

## 3. Priorytet B: minimum przed publikacja

Termin: po spotkaniu, jesli profesor zaakceptuje kierunek.

### B1. Grid convergence / GCI dla V4b

To jest najwazniejszy brak techniczny.

Minimalna macierz:

| Mesh | Cel | Uwagi |
|---|---|---|
| coarse | tanszy punkt GCI | zachowac te sama geometrie i BC |
| medium | obecny `run008`, 407,440 cells | production reference |
| fine | punkt do ekstrapolacji | lokalne zagęszczenie BL/wake/fin junction |

Metryki:

- `Cd_mean`;
- `Cl_rms`;
- `St`;
- `Nu_EB`;
- `Nu_wall`;
- closure wall-air;
- heat share tube/fins.

Wynik:

- Richardson extrapolation;
- GCI;
- tabela niepewnosci dyskretyzacji.

### B2. Production Re-scan przez Hopf

Powod:

Obecnie finalny wynik jest dla `Re=200`. Jesli abstrakt lub narracja mowi `before and after Hopf`, trzeba miec produkcyjna macierz Re.

Minimalna macierz:

| Re | Cel |
|---:|---|
| 100 | steady baseline, juz mamy kontekst |
| 120 | okolice onset |
| 140 | okolice onset / weak periodic |
| 160 | periodic growth |
| 180 | pre-production periodic |
| 200 | production reference |

Metryki:

- `Cl_rms(Re)`;
- `St(Re)`;
- `Nu_EB(Re)`;
- `Nu_wall(Re)`;
- heat share tube/fins;
- ewentualnie `A1/A2` dla lokalnego Nu.

Wynik:

Slajd/paper figure: `Nu(Re)` i `Cl_rms(Re)` z zaznaczonym onset.

### B3. Variable-property production comparison

Powod:

Boussinesq przy `betaT * DeltaT ~ 0.17` jest marginalne. Obecny `run007a` jest diagnostyczny, ale nie zamyka bilansu.

Do wykonania:

- przygotowac poprawny variable-property run z domknietym heat balance;
- sprawdzic, czy roznica `Cd` i `Nu` jest fizyczna czy implementacyjna;
- porownac z `run008` w tym samym oknie.

Obecne liczby ostrzegawcze:

| Run | Model | Cd | Nu_wall case-k | wall-air diff |
|---|---|---:|---:|---:|
| run007a | variable props | 3.473619 | 7.3786 | -27.4% |
| run007c | Cp-consistent constant props | 3.361209 | 7.8217 | +1.4% |
| run008 | production constant props | 3.361014 | 7.816521 | +0.706 +/- 1.075% |

### B4. Statystyka TE/coherence/POD

Do wykonania:

- Bonferroni albo FDR dla `16` fin bins;
- confidence band dla coherence;
- liczba segmentow Welcha, okno, overlap;
- bootstrap CI dla energii modow POD `3-8`;
- jasny opis, ze TE jest screeningiem, nie dowodem przyczynowosci.

### B5. Zewnetrzna kontrola `Nu`

Opcje:

1. Eksperyment dla tej geometrii.
2. Korelacje dla podobnych fin-and-tube / confined cylinder jako order-of-magnitude check.
3. Porownanie z literatura confined-cylinder dla `Cd`, `St`, `Nu`, jesli geometrie sa wystarczajaco podobne.

Minimalny cel:

Pokazac, ze `Nu ~ 7.77-7.82` jest fizycznie sensowne dla `Re=200` w ograniczonej geometrii z finami.

## 4. Priorytet C: rozszerzenie naukowe

To nie jest wymagane na najblizsze spotkanie, ale moze zbudowac mocny artykul lub grant.

### C1. Skan `Lz/D`

Cel:

Oddzielic wplyw pitchu finow od samego shedding.

Propozycja:

| Lz/D | Cel |
|---:|---|
| 0.5 | silnie ograniczony span |
| 1.0 | obecny przypadek produkcyjny |
| 2.0 | bardziej przestrzenny wake |
| 4.0 | porownanie z dluzszym cylindrem |

### C2. Q/Lambda2 + local Nu jako mechanistyczna figura

Mamy juz warstwy Q/Lambda2, ale warto zrobic jedna mocna figure:

- iso-surfaces Q albo Lambda2;
- kolor/overlay temperatury albo local Nu;
- fazy: max `Cl`, zero crossing, min `Cl`;
- podpis: struktura wirowa -> lokalna odpowiedz cieplna.

To bylaby najmocniejsza odpowiedz na pytanie o "mechanism".

### C3. Local-Nu conditioned EPOD

Zamiast kondycjonowac tylko na globalnym `Cl`, mozna kondycjonowac na lokalnym `Nu` w wybranych strefach:

- tube front/stagnation;
- tube rear/separation;
- fin near wake;
- fin downstream high-coherence bins.

Cel:

Pokazac, jaka struktura przeplywu odpowiada za lokalne wzmocnienie ciepla.

## 5. Kolejnosc wykonania

### Etap 1: wersja na spotkanie

Szacowany czas: 1 dzien roboczy.

1. Poprawic slajd domeny `Lin=2D`, `Lout=8D`, `Lz=1D`.
2. Dodac tabele z `Cl_rms` i `St`.
3. Oslabic claimy POD/TE/mechanistic.
4. Dodac limitation slide.
5. Dodac backup slides: DMD, Boussinesq/run007a, domain sensitivity.

### Etap 2: pakiet po spotkaniu

Szacowany czas: kilka dni do 1-2 tygodni, zaleznie od kosztu obliczen.

1. Zaprojektowac coarse/fine mesh dla V4b.
2. Uruchomic grid study.
3. Przygotowac skrypt GCI.
4. Przeliczyc TE z Bonferroni/FDR.
5. Uzupelnic coherence o confidence bands.

### Etap 3: pakiet publikacyjny

Szacowany czas: wieksza kampania.

1. Re-scan produkcyjny `100-200`.
2. Poprawny variable-property comparison.
3. Zewnetrzna kontrola Nu.
4. Jedna mechanistyczna figura Q/Lambda2 + local Nu.
5. Finalny manuskrypt z jasnym rozdzialem limitations.

## 6. Najlepsza odpowiedz dla profesora

`Po recenzji widzimy, ze nasze wyniki sa mocne jako production reference po V1/V2, ale nie sa jeszcze pelnym pakietem walidacyjnym do publikacji Q1. Na najblizsze spotkanie poprawiamy narracje i pokazujemy uczciwie domain sensitivity, bilans energii, St/Cl_rms oraz ograniczenia. Najwazniejsza praca po spotkaniu to grid convergence/GCI dla V4b oraz produkcyjny Re-scan przez onset.`

