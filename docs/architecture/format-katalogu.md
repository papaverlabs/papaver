# Papaver — format katalogu flag

Powiązane: [Specyfikacja](../product/specyfikacja.md) (sekcje 5 i 6) · [Plan labelera](plan-labeler.md)

Katalog flag to katalog z plikami YAML: jedna flaga na plik i indeks, który składa flagi w zestawy. Silnik nie zawiera żadnego katalogu; dostaje ścieżkę przy uruchomieniu.

```
<katalog>/
├── index.yaml                  wersja katalogu i zestawy
├── PRZYKLADOWA_FLAGA.yaml      nazwa pliku = kod flagi
└── ...
```

Klucze formatu są po angielsku, jak cały kod. Kody flag, nazwy zestawów i treść (`flag_when`, `instructions`, `description`) są na razie po polsku; lokalizację katalogu dodamy, gdy będzie potrzebna.

## Definicja flagi

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/papaverlabs/papaver/main/schemas/flag-definition.schema.json
code: PRZYKLADOWA_FLAGA
version: 1
flag_when: jednozdaniowy opis, kiedy flaga się zapala
severity: high
instructions: |
  Instrukcja dla modelu.
```

| Pole | Wymagane | Znaczenie |
| --- | --- | --- |
| `code` | tak | wielkie litery i `_`, równy nazwie pliku; stały identyfikator w wynikach i raportach |
| `version` | tak | liczba całkowita, podbijana przy zmianie tego, co flaga wykrywa |
| `flag_when` | tak | jednozdaniowy opis dla człowieka, kiedy flaga się zapala |
| `severity` | tak | `low`, `medium`, `high`, `critical` (krytyczność w profilu domyślnym) |
| `instructions` | nie | instrukcja dla modelu; flaga bez niej nie jest jeszcze wykonywana |

Nieznane pola są błędem, żeby literówka nie przeszła po cichu.

Definicja celowo nie mówi, na jakim etapie flaga działa ani jakich danych potrzebuje (decyzja z 24.11.2026, zob. [plan labelera](plan-labeler.md)):

- **Etap** (przed zakupem albo po zakupie) to parametr przebiegu. Każdą flagę da się policzyć na każdym etapie.
- **Dane** model pobiera sam przez narzędzia. Gdy narzędzia nie dają tego, czego flaga potrzebuje, wynik to „nie da się ocenić” z powodem.

### Instrukcja

`flag_when` mówi człowiekowi, co flaga oznacza. `instructions` mówi modelowi, jak sprawdzić, czy flaga występuje. Dobra instrukcja ma:

1. **Cel** w jednym zdaniu.
2. **Kroki sprawdzenia:** co wypisać z dokumentów, z czym porównać i skąd wziąć dane, od najmocniejszego źródła.
3. **Kiedy flaga się zapala** i jak ocenić siłę sygnału (słaby, umiarkowany, silny). Liczbowe progi oznaczamy jako do kalibracji.
4. **Kiedy nie zapalać:** uzasadnione wyjątki, które dają fałszywe alarmy.
5. **Kiedy „nie da się ocenić”:** czego brak, żeby wynik był wiarygodny.
6. **Dowody:** jakie cytaty i referencje mają trafić do wyniku.

Instrukcja nigdy nie każe szukać w treści korespondencji.

Instrukcja opisuje dane słowami, a nie nazwami narzędzi. Model sam dobiera narzędzie. Gdy go nie ma, zwraca „nie da się ocenić”. Dzięki temu nowe narzędzie nie wymaga zmian w katalogu.

Zmiana instrukcji nie wymaga podbicia `version`, bo wynik zapisuje skrót instrukcji. `version` podbijamy, gdy zmienia się to, co flaga wykrywa.

Oś jakość/integralność, typ rdzeń/warstwa i flagi twarde z pierwszej wersji specyfikacji usunęliśmy. Jeśli wrócą, to w profilu scoringu, nie w definicji flagi (otwarte pytania w specyfikacji, sekcja 23).

## Indeks i zestawy

Zestaw to oferta branżowa, np. telekomunikacja, produkcja stali albo handel. Analiza dla klienta używa jednego zestawu w całości. Flagi wspólne dla kilku branż trzymamy w zestawie bazowym, który zestawy branżowe włączają przez `includes`.

```yaml
catalog_version: "2026.11"   # w cudzysłowie, inaczej YAML wczyta liczbę
sets:
  wspolne:
    description: Flagi wspólne dla wszystkich branż
    flags: [FLAGA_A, FLAGA_B]
  telco:
    description: Telekomunikacja
    includes: [wspolne]   # zestaw może włączać inne zestawy
    flags: [FLAGA_C]
```

Zestaw rozwija się do listy flag w kolejności z indeksu, bez powtórzeń. Cykl między zestawami jest błędem. Flaga, której nie ma w żadnym zestawie, jest zgłaszana jako ostrzeżenie.

## Wersja katalogu w wynikach

Silnik zapisuje w wyniku `catalog_version` z indeksu i skrót SHA-256 z treści wszystkich plików, np. `2026.11+7cfb1bc695dd`. Każda zmiana w katalogu zmienia skrót, nawet jeśli nikt nie podbił wersji.

## Polecenia

Z katalogu `services/labeler`, z `venv` utworzonym według jego README:

```sh
venv/bin/python -m app catalog check <katalog>         # walidacja i podsumowanie zestawów
venv/bin/python -m app catalog set <katalog> <nazwa>   # flagi zestawu po rozwinięciu
venv/bin/python -m app schema --out ../../schemas      # JSON Schema do podpowiedzi w edytorze
```

Schematy w `schemas/` w korzeniu repo są generowane z modeli w `services/labeler/app/catalog.py`. Po zmianie modeli trzeba je wygenerować ponownie.
