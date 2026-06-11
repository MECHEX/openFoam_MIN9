# Obrona metodologii: V1/V2 jako benchmarki, V4b jako przypadek produkcyjny

Data: 2026-06-03

## Decyzja metodologiczna

Nie przenosimy `V1` i `V2` na geometrię produkcyjną jako głównej walidacji.

`V1` i `V2` powinny pozostać na geometriach benchmarkowych, bo tylko wtedy
porównanie z literaturą jest porównaniem tego samego problemu fizycznego. Po
zmianie domeny, ograniczenia w osi `y`, topologii siatki i warunków brzegowych
nie sprawdzamy już zgodności z artykułem, tylko odpowiedź innego układu.

`V4b` jest przypadkiem zastosowania zweryfikowanego i zwalidowanego narzędzia
do geometrii produkcyjnej wymiennika. W tej geometrii oczekujemy innych wartości
`Cd`, `St`, `Nu` i czasem innego zachowania onset/shedding, ponieważ przepływ
jest celowo zawężony i odtwarza realne warunki w kanale wymiennika.

## Główna narracja

Projekt ma trzy warstwy:

1. `V1`: weryfikacja hydrodynamiczna.
2. `V2`: walidacja cieplna.
3. `V4b`: zastosowanie produkcyjne.

To jest mocniejsza narracja niż próba wymuszenia zgodności wartości
benchmarkowych na geometrii produkcyjnej. Benchmark ma potwierdzić narzędzie,
a przypadek produkcyjny ma odpowiedzieć na pytanie inżynierskie dla innej
geometrii.

## Najważniejsze zdanie do powiedzenia profesorowi

Zgodności z literaturą oczekujemy dla `V1` i `V2`, ponieważ tam zachowujemy
geometrie benchmarkowe. Dla `V4b` nie oczekujemy tych samych wartości, bo jest
to już geometria rzeczywistego elementu wymiennika, z innym confinement,
innym polem prędkości i inną wymianą ciepła.

## Dlaczego wyniki production-like nie muszą zgadzać się z artykułem

Smoke testy `production-like` pokazały dokładnie to, czego fizycznie należało
się spodziewać:

- po zawężeniu domeny i przejściu na geometrię typu `V4b`, wartości `Cd` i
  `Nu` zmieniają się istotnie,
- dla `V1` zachowanie periodyczne/onset może przesunąć się lub osłabić,
- dla `V2` kompaktowa domena zwiększa wpływ ograniczenia przepływu i daje inne
  `Nu` niż unconfined/benchmark O-grid.

To nie obala walidacji. To pokazuje, że zmieniliśmy problem fizyczny.

## Jak pokazać to na slajdach

### Slajd 1: Cel projektu

Tytuł:
`Od benchmarków CFD do przypadku produkcyjnego wymiennika`

Teza:
Najpierw sprawdzamy narzędzie na znanych przypadkach, potem stosujemy je do
rzeczywistej geometrii, gdzie nie oczekujemy już wartości 1:1 z artykułu.

Co pokazać:

- schemat `V1 -> V2 -> V4b`,
- krótki opis roli każdego etapu.

### Slajd 2: V1 jako weryfikacja hydrodynamiczna

Tytuł:
`V1: hydrodynamic verification`

Przekaz:
`V1` sprawdza, czy solver odtwarza onset shedding i liczbę Strouhala dla
znanego układu cylindra w kanale.

Co pokazać:

- `St` vs literatura,
- onset/periodic classification,
- siatka/domena benchmarkowa.

Zdanie:
Tutaj porównanie z artykułem jest ilościowe, ponieważ geometria i warunki
problemu odpowiadają benchmarkowi.

### Slajd 3: V2 jako walidacja cieplna

Tytuł:
`V2: thermal validation`

Przekaz:
`V2` sprawdza ścieżkę cieplną i ekstrakcję `Nu` na benchmarku ogrzewanego
cylindra.

Co pokazać:

- `Nu` vs reference,
- O-grid,
- boundedness temperatury,
- `snGrad(T)` jako definicję `Nu`.

Zdanie:
Tutaj walidujemy model cieplny i sposób obliczania `Nu`, a nie jeszcze geometrię
wymiennika.

### Slajd 4: Dlaczego nie walidujemy V4b liczbami z V1/V2

Tytuł:
`Benchmark geometry vs production geometry`

Przekaz:
Zmiana domeny i confinement zmienia fizykę przepływu, więc inne wartości są
oczekiwane.

Co pokazać:

- porównanie geometrii benchmarkowej i `V4b`,
- krótką tabelę:
  `benchmark = validation target`,
  `V4b = engineering application`.

Zdanie:
Gdyby produkcyjna geometria dawała te same wartości co unconfined cylinder,
byłoby to mniej przekonujące fizycznie niż obserwacja wpływu confinement.

### Slajd 5: V4b jako przypadek produkcyjny

Tytuł:
`V4b: production application`

Przekaz:
`V4b` używa sprawdzonego solvera i zwalidowanej ścieżki cieplnej do geometrii
elementu wymiennika.

Co pokazać:

- geometria,
- setup fizyczny,
- sensitivity checks,
- heat-balance closure.

Zdanie:
Dla `V4b` głównym kryterium jakości nie jest zgodność z benchmarkiem 1:1, tylko
spójność numeryczna, bilans ciepła i stabilność metryk w geometrii docelowej.

### Slajd 6: Wyniki V4b

Tytuł:
`V4b: quality and physics`

Przekaz:
Wynik produkcyjny jest wiarygodny, bo przechodzi niezależne kontrole jakości.

Co pokazać:

- `Cd`, `Cl_rms`, `St`,
- `Nu_EB` i `Nu_wall`,
- closure wall-air,
- udział rurki i płetw,
- wybrane mapy lokalnego `Nu`/POD/coherence.

Zdanie:
Ten etap nie jest prostą walidacją literaturową, tylko demonstracją jakości
wyniku w docelowej geometrii.

### Slajd 7: Uczciwe ograniczenia

Tytuł:
`Scope and limitations`

Przekaz:
Wiemy dokładnie, co zostało zwalidowane, a co jest już zastosowaniem.

Co powiedzieć:

- `V1` waliduje hydrodynamiczny benchmark.
- `V2` waliduje cieplny benchmark.
- `V4b` jest produkcyjną aplikacją, wspartą przez V1/V2 i kontrole wewnętrzne.
- Bezpośrednia walidacja literaturowa geometrii `V4b` nie jest dostępna.

## Sformułowania, których warto użyć

- `V1 i V2 są warstwą verification/validation, a V4b jest warstwą application.`
- `Nie oczekujemy identycznych wartości w V4b, ponieważ zmienia się geometria i confinement.`
- `Porównanie z literaturą wykonujemy tam, gdzie zachowany jest problem literaturowy.`
- `V4b korzysta z narzędzia sprawdzonego na benchmarkach, ale odpowiada na inne pytanie fizyczne.`
- `Production geometry ma odtwarzać realny przepływ w wymienniku, a nie liczby z izolowanego benchmarku.`
- `Różnica między benchmarkiem i V4b jest wynikiem zmiany problemu, nie dowodem błędu solvera.`
- `Dla V4b pokazujemy jakość przez sensitivity checks, bilans ciepła, stabilność sygnałów i spójność mechanistyczną.`

## Czego nie mówić

- Nie mówić:
  `V4b jest zwalidowane literaturowo przez V1/V2.`

  Lepiej:
  `V4b jest wsparte przez walidację V1/V2 oraz przez kontrole wewnętrzne.`

- Nie mówić:
  `Wartości V4b powinny zgadzać się z artykułem.`

  Lepiej:
  `Wartości V4b powinny być fizycznie spójne dla geometrii produkcyjnej.`

- Nie mówić:
  `Production-like V1/V2 nie wyszły, więc są problemem.`

  Lepiej:
  `Production-like test potwierdził, że zmiana geometrii istotnie zmienia fizykę, więc nie może zastąpić benchmarku.`

- Nie mówić:
  `V1 i V2 walidują cały projekt bezpośrednio.`

  Lepiej:
  `V1 i V2 walidują kluczowe komponenty modelu, które następnie stosujemy w V4b.`

- Nie mówić:
  `Nie mamy walidacji V4b.`

  Lepiej:
  `Nie mamy bezpośredniego benchmarku 1:1 dla V4b; mamy za to walidację komponentową i rozbudowane kontrole jakości przypadku produkcyjnego.`

## Odpowiedzi na możliwe pytania profesora

### Dlaczego V4b nie zgadza się z wartościami z benchmarku?

Bo V4b nie jest tym samym problemem. Benchmarkowy cylinder ma inną domenę,
inne ograniczenie przepływu i inną geometrię cieplną. W V4b przepływ jest
celowo zawężony, bo taki jest realny kanał wymiennika. Dlatego zmiana `Cd`,
`St` i `Nu` jest oczekiwana.

### Czy to znaczy, że solver nie jest zwalidowany?

Nie. Solver i ścieżka obliczeniowa są sprawdzane na przypadkach, gdzie istnieje
referencja literaturowa. `V1` sprawdza hydrodynamikę, a `V2` sprawdza wymianę
ciepła. `V4b` jest zastosowaniem tej sprawdzonej ścieżki w geometrii bez
bezpośredniego odpowiednika literaturowego.

### Czy production-like testy są bezużyteczne?

Nie. One są diagnostyczne. Pokazały, że przejście do geometrii produkcyjnej
zmienia odpowiedź układu. To pomaga wyjaśnić, dlaczego benchmarki muszą
pozostać benchmarkami, a `V4b` trzeba traktować jako osobną aplikację.

### Jaki jest główny dowód jakości V4b?

Nie jedna liczba z literatury, tylko łańcuch dowodów:

- solver zweryfikowany na `V1`,
- ścieżka cieplna zwalidowana na `V2`,
- geometria produkcyjna przeszła sensitivity checks,
- bilans ciepła jest domknięty,
- metryki integralne i lokalne są stabilne,
- analiza modalna i sygnałowa daje spójny obraz mechanizmu.

## Finalna struktura obrony

Najbezpieczniej powiedzieć to w tej kolejności:

1. `Najpierw sprawdziliśmy narzędzie na problemach, dla których istnieją referencje.`
2. `V1 potwierdza hydrodynamikę, V2 potwierdza transfer ciepła.`
3. `Następnie zastosowaliśmy to narzędzie do geometrii produkcyjnej V4b.`
4. `V4b nie ma być zgodne liczbowo z benchmarkiem, bo jest innym problemem fizycznym.`
5. `Jakość V4b oceniamy przez kontrole wewnętrzne, sensitivity checks i bilans energii.`

## Status ścieżki production-like

Ścieżka `production-like` pozostaje pomocniczym eksperymentem diagnostycznym.
Nie powinna zastępować głównych benchmarków `V1` i `V2` w prezentacji.

W prezentacji można ją wspomnieć tylko wtedy, gdy profesor zapyta, czy
sprawdzaliśmy wpływ geometrii produkcyjnej na benchmarkowe metryki. Wtedy
odpowiedź jest prosta: tak, i właśnie ten test pokazał, że zmiana geometrii
zmienia problem fizyczny, więc nie można wymagać zgodności 1:1 z literaturą.
