# Zasady pracy w repo

## Układ repo

```
services/          serwisy backendowe (Python), każdy w osobnym katalogu
infrastructure/    Helm chart i Terraform
apps/              aplikacje mobilne
web/               aplikacje webowe
site/              strona papaverlabs.com (GitHub Pages)
schemas/           JSON Schema formatu katalogu flag i kontrakty zdarzeń
libs/              biblioteka współdzielona przez serwisy
docs/              dokumentacja; mapa w docs/README.md
.github/workflows/ CI/CD
```

## Wspólne

- Kod, identyfikatory, klucze formatu, komunikaty błędów i commity po angielsku. Dokumentacja i treść flag po polsku.
- Każdy serwis ma `requirements.txt`. Do uruchomienia serwisu tworzymy `venv` w jego katalogu i używamy go; nigdy systemowego Pythona.
- Importy tylko na górze pliku.
- **NIE WOLNO umieszczać w tym repo NICZEGO z katalogu flag.** Ani kodów, ani nazw (także opisowych), ani treści `flag_when` i instrukcji, ani obszarów, mechanizmów czy przykładów tego, co wykrywamy, ani listy flag publicznych (nie ma flag publicznych). W kodzie, dokumentacji, testach, przykładach, schematach i na stronie wolno opisać wyłącznie strukturę definicji flagi i to, że flagi wykonuje labeler. W przykładach i testach tylko neutralne kody (`PRZYKLADOWA_FLAGA`, `FLAGA_A`, `TEST_FLAG_A`). Nie linkujemy do miejsca, gdzie katalog jest trzymany.
- Treść korespondencji nigdy nie jest źródłem flag i nie trafia do żadnego komponentu.
- **Biznes nie trafia do tego repo.** Sprzedaż, pitch, rynek i konkurencja, cennik, model biznesowy, klienci i wdrożenia u nich, organizacja i role w zespole są poza tym repo. Tutaj opisujemy wyłącznie system: jak działa, jak jest zbudowany i w jakich etapach się rozwija.

## Serwisy

- Python, pakiet `app/`, testy w `tests/`, README z instrukcją uruchomienia.
- Konteneryzowane; konfiguracja wyłącznie przez zmienne środowiskowe.
- Wdrażane jako usługi Knative na Kubernetesie ([architektura](docs/architecture/architektura.md)); bezstanowe, stan w S3 i PostgreSQL.

## CI/CD

- Workflowy są w `.github/workflows/`, jeden na komponent, uruchamiane tylko przy zmianach w jego ścieżkach.
- Nie dodajemy workflowów testowych, dopóki komponent nie ma realnej implementacji; testy uruchamiamy lokalnie. Minuty GitHub Actions są płatne.

## Dokumentacja

- `docs/README.md` jest mapą; status dokumentu wynika z folderu (`product/`, `architecture/` obowiązują, `archived/` nie).
