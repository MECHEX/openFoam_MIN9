# Presentation Handoff for Claude Opus 4.8

Cel paczki: przygotowanie prezentacji na spotkanie z profesorem oceniającym jakosc wynikow projektu CFD/OpenFOAM.

Glowna narracja:

1. V1 sprawdza solver aerodynamicznie na kanonicznym benchmarku cylindra.
2. V2 sprawdza model cieplny na kanonicznym benchmarku wymiany ciepla.
3. V4b nie jest kolejnym benchmarkiem cylindra. To produkcyjna geometria elementu wymiennika, w ktorej ograniczenie domeny, finy i rzeczywisty przeplyw zmieniaja fizyke.
4. Dlatego V4b ma byc oceniane przez bilans energii, stabilnosc, spojna metodyke, konwergencje/niepewnosc i sens fizyczny, a nie przez wymuszanie zgodnosci 1:1 z literatura dla izolowanego cylindra.

Najwazniejsze pliki dla Claude:

- `CLAUDE_PROMPT.md` - gotowy prompt do wklejenia w Claude Opus 4.8.
- `SLIDE_PLAN.md` - plan slajdow i przypisane figury.
- `KEY_NUMBERS.md` - liczby, ktore powinny trafic do prezentacji.
- `PRODUCTION_DOMAIN_AND_NUMERICS.md` - gotowa sciaga o wlocie, wylocie, siatce, samplingu i stabilnosci `V4b`.
- `ASSET_MANIFEST.md` - lista obrazow i ich rola.
- `source_refs/` - dokumenty zrodlowe, z ktorych Claude moze brac szczegoly.
- `assets/` - wykresy do uzycia w prezentacji.

Rekomendowany styl prezentacji:

- akademicki, spokojny, techniczny;
- jasne rozdzielenie `verification`, `validation`, `production application`;
- maksymalnie 1 glowna teza na slajd;
- niewiele tekstu na slajdach, wiecej w notatkach prelegenta;
- bez obietnicy, ze V4b ma odtwarzac wartosci benchmarkowe V1/V2.

Najwazniejsza zasada:

Nie porownywac bezposrednio wartosci `Cd`, `St` i `Nu` z V4b do benchmarkow V1/V2 jako kryterium bledu. To sa rozne geometrie i rozne warunki przeplywu. Porownanie ma byc metodologiczne: czy solver i model fizyczny zostaly sprawdzone na benchmarkach, a potem zastosowane do geometrii produkcyjnej.
