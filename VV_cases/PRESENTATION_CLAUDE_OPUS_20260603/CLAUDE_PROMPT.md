# Prompt do Claude Opus 4.8

Przygotuj prezentacje PowerPoint na spotkanie z profesorem oceniającym jakosc wynikow projektu CFD/OpenFOAM. Uzyj materialow z folderu `PRESENTATION_CLAUDE_OPUS_20260603`.

Cel prezentacji:

Pokazac projekt od poczatku: zalozenia, weryfikacja solvera, walidacja cieplna, a nastepnie zastosowanie w geometrii produkcyjnej V4b. Prezentacja ma byc techniczna, spokojna i obronna metodologicznie.

Najwazniejsza narracja:

1. `V1` to hydrodynamic solver verification na benchmarku cylindra. Pokazuje, ze solver poprawnie odtwarza dynamike przeplywu, prog niestacjonarnosci i `St(Re)`.
2. `V2` to thermal validation na benchmarku ogrzewanego cylindra. Pokazuje, ze model wymiany ciepla odtwarza liczbe Nusselta z bledem okolo `0.07-1.13%`.
3. `V4b` to production application, czyli realniejsza geometria elementu wymiennika. Nie nalezy jej oceniac przez bezposrednia zgodnosc `Cd`, `St` i `Nu` z izolowanym cylindrem z V1/V2.
4. Roznice V4b wzgledem benchmarkow sa oczekiwane, bo produkcyjna geometria zmienia fizyke: zwezenie domeny, finy, inlet/outlet development, lokalna akceleracja przeplywu i efekty 3D.
5. V4b nalezy bronic przez domkniecie bilansu energii, stabilnosc przebiegow, sens fizyczny rozkladow lokalnych, dlugosc probki czasowej i spojna analize aerodynamiczno-termiczna.

Utworz prezentacje po polsku, najlepiej 12-14 slajdow. Uzyj `SLIDE_PLAN.md` jako glownej struktury, `KEY_NUMBERS.md` jako zrodla liczb, `ASSET_MANIFEST.md` jako mapy obrazow i `source_refs/` jako dokumentow pomocniczych.
Koniecznie wykorzystaj tez `PRODUCTION_DOMAIN_AND_NUMERICS.md` do slajdu o metodologii `V4b`, zeby uwzglednic informacje o `Lin`, `Lout`, siatce, `maxCo`, cadence samplingu i oknie analizy.

Styl:

- akademicki, czytelny, nieprzegadany;
- 1 glowny przekaz na slajd;
- duze figury, malo tekstu;
- notatki prelegenta moga byc bardziej szczegolowe;
- unikaj marketingowego tonu;
- nie uzywaj sformulowan typu "V4b zostalo zwalidowane z literatura cylindra";
- uzywaj sformulowan typu "V1/V2 waliduja narzedzie na przypadkach kanonicznych, V4b jest zastosowaniem produkcyjnym".

Wymagany output:

1. Plik `.pptx`.
2. Krotki dokument z notatkami prelegenta.
3. Slajd lub sekcja "expected questions" z odpowiedziami na pytania profesora.
4. Jesli robisz wykresy lub tabele dodatkowe, zachowaj je w osobnym folderze `generated_assets`.

Pytania, na ktore prezentacja musi odpowiadac:

- Co bylo celem projektu?
- Jak sprawdzono solver?
- Jak sprawdzono model cieplny?
- Dlaczego V4b nie musi dawac identycznych wartosci jak benchmark cylindra?
- Jakie sa najwazniejsze wyniki V4b?
- Jak wiemy, ze bilans ciepla jest wiarygodny?
- Jakie sa ograniczenia i dalsze kroki?
