# Papaver

Papaver sprawdza zakupy: planowane (analiza ciągła) i zrealizowane (analiza wsteczna). Bierze pliki sprawy (RFP, memo, oferty, zamówienia, faktury) i kontekst firmy, a zwraca flagi zdefiniowane w katalogu flag. Każda flaga ma dowód, czyli plik i cytat, albo status „nie da się ocenić” z powodem.

Narzędzie nie oskarża. Zbiera sygnały i dowody, a decyzję podejmuje człowiek.

Projekt jest na etapie specyfikacji. Z kodu istnieje na razie format katalogu flag z walidacją (`services/labeler`).

## Dokumentacja

Mapa i zasady statusu dokumentów: [`docs/README.md`](docs/README.md).

| Dokument | O czym |
| --- | --- |
| [Specyfikacja](docs/product/specyfikacja.md) | **zacznij tu**: cel, tryby działania, flagi, scoring, dane, wdrożenie |
| [Zakres MVP](docs/product/zakres-mvp.md) | hipotezy, zakres i kryteria akceptacji pierwszej fazy |
| [Roadmapa](docs/product/roadmapa.md) | fazy, kamienie milowe, bramki |
| [Architektura](docs/architecture/architektura.md) | komponenty, przepływ sprawy, wdrożenie na Kubernetesie z Knative |
| [Format katalogu flag](docs/architecture/format-katalogu.md) | definicja flagi, indeks, zestawy branżowe, jak pisać instrukcje |
| [Plan labelera](docs/architecture/plan-labeler.md) | wejście wywołania modelu, funkcje kontekstu, wynik, kolejność prac |

Zasady pracy w repo (dla ludzi i agentów): [`CLAUDE.md`](CLAUDE.md).

## Struktura repo

Repo jest monorepo publicznej części systemu. Katalog flag jest zamknięty i nie jest częścią tego repo; silnik dostaje go przy wdrożeniu.

```
services/              serwisy backendowe (Python, Knative)
  labeler/               ocena spraw według katalogu flag; na razie format katalogu i walidacja
infrastructure/        Helm chart i Terraform (na razie plan układu)
apps/                  aplikacje mobilne (na razie pusto)
web/                   aplikacje webowe (na razie pusto)
site/                  strona papaverlabs.com
schemas/               JSON Schema formatu katalogu flag i kontrakty zdarzeń
libs/                  biblioteka współdzielona przez serwisy (na razie pusto)
docs/                  dokumentacja: product/, architecture/
.github/workflows/     CI/CD
```

Każdy serwis i aplikacja ma własny katalog z README i instrukcją uruchomienia. Serwisy w Pythonie używają `requirements.txt` i lokalnego `venv` w swoim katalogu.

## CI/CD

GitHub Actions, workflowy w [`.github/workflows/`](.github/workflows/). Każdy workflow uruchamia się tylko przy zmianach w ścieżkach swojego komponentu.

| Workflow | Kiedy | Co robi |
| --- | --- | --- |
| [`pages.yml`](.github/workflows/pages.yml) | push na `main` ze zmianą w `site/`, albo ręcznie | publikuje `site/` na GitHub Pages pod papaverlabs.com |

Workflowy testów i budowania obrazów dodamy, gdy powstanie implementacja serwisów. Do tego czasu testy uruchamiamy lokalnie, żeby nie zużywać minut GitHub Actions. Docelowo każdy serwis dostanie workflow: testy, budowa obrazu, publikacja do rejestru; wdrożenie przez Helm opisuje [architektura](docs/architecture/architektura.md).

## Licencja

[Apache 2.0](LICENSE)
