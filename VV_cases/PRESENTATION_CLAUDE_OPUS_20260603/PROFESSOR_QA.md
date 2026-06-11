# Expected Professor Questions

## Dlaczego V4b nie zgadza sie 1:1 z benchmarkiem cylindra?

Bo V4b nie jest benchmarkiem izolowanego cylindra. V4b ma inna geometrie, inne ograniczenie przeplywu, finy, inny inlet/outlet development i efekty 3D. Benchmark V1/V2 sprawdza narzedzie w znanych warunkach, a V4b wykorzystuje to narzedzie w rzeczywistszej konfiguracji.

## Czy to oznacza, ze walidacja nie dotyczy V4b?

Walidacja bezposrednia dotyczy kanonicznych przypadkow V1/V2. V4b jest aplikacja produkcyjna oparta na zweryfikowanym solverze i zwalidowanym modelu cieplnym. Dla V4b kryterium jakosci to bilans energii, stabilnosc, kompletna probka czasowa, sens fizyczny rozkladow i spojna odpowiedz aerodynamiczno-termiczna.

## Czy moglismy uruchomic V1/V2 na geometrii produkcyjnej?

Mozna to zrobic diagnostycznie, ale nie byloby to juz porownanie z literatura benchmarkowa. Jesli zmienimy geometrie benchmarku na produkcyjna, tracimy prawo oczekiwac tych samych wartosci referencyjnych. Dlatego glowna obrona zostaje przy czystych benchmarkach V1/V2, a V4b jest oddzielnie interpretowana jako przypadek produkcyjny.

## Jaki jest najmocniejszy argument za wiarygodnoscia V4b?

Najmocniejszy argument cieplny to domkniecie bilansu: `Nu_EB = 7.770004 +/- 0.091573`, `Nu_wall = 7.816521 +/- 0.012286`, wall-air closure `+0.706 +/- 1.075%`. Aerodynamicznie wynik ma spojny `St = 0.154261 +/- 0.009574` oraz okno analizy obejmujace `25.98` cykli zrzucania wirow.

## Co jest najwiekszym ograniczeniem?

Brak bezposredniego eksperymentu dla tej dokladnej geometrii produkcyjnej. Dlatego prezentujemy V4b jako wiarygodna aplikacje inzynierska po V&V, a nie jako eksperymentalnie zwalidowany model konkretnego wymiennika.

## Co byloby nastepnym krokiem?

Najlepszy nastepny krok to albo eksperyment dla geometrii produkcyjnej, albo dodatkowa analiza wrazliwosci: siatka, okno czasowe, warunki wlotu/wylotu oraz porownanie z korelacjami dla przeplywu ograniczonego/finow, jesli takie korelacje pasuja do geometrii.
