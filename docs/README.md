# Dokumentacja — co gdzie jest

Status dokumentu wynika z folderu, w którym leży.

| Folder | Znaczenie |
| --- | --- |
| `product/` | **Obowiązujące.** Co budujemy i po co: specyfikacja, zakres MVP, roadmapa. |
| `architecture/` | **Obowiązujące.** Jak to jest zbudowane: architektura i wdrożenie, format katalogu flag, plan labelera. |
| `archived/` | **Nieaktualne.** Porzucone koncepcje, trzymane dla uzasadnienia decyzji. Na razie pusto. |

Przeniesienie pliku do `archived/` oznacza, że przestał obowiązywać. Tego samego dnia dopisujemy na jego początku, gdzie jest aktualna wersja.

## `product/`

| Dokument | O czym |
| --- | --- |
| [Specyfikacja](product/specyfikacja.md) | **Zacznij tu.** Cel, tryby działania, flagi, scoring, dane, wdrożenie, otwarte pytania |
| [Zakres MVP](product/zakres-mvp.md) | hipotezy, zakres, kryteria akceptacji pierwszej fazy |
| [Roadmapa](product/roadmapa.md) | fazy, kamienie milowe, bramki |

## `architecture/`

| Dokument | O czym |
| --- | --- |
| [Architektura](architecture/architektura.md) | komponenty, przepływ sprawy, wdrożenie na Kubernetesie z Knative |
| [Format katalogu flag](architecture/format-katalogu.md) | definicja flagi, indeks, zestawy, jak pisać instrukcje |
| [Plan labelera](architecture/plan-labeler.md) | wejście wywołania modelu, funkcje kontekstu, wynik, kolejność prac |

## Zasady

- Dokumentacja jest po polsku; kod, klucze formatu i nazwy narzędzi po angielsku.
- Katalog flag jest zamknięty i nic z niego nie trafia do tego repo: ani kody, ani nazwy, ani opisy, obszary czy mechanizmy wykrywania. Dokumenty opisują wyłącznie strukturę definicji flagi i silnik, który flagi wykonuje.
