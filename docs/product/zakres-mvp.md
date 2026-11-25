# Papaver — zakres MVP

Powiązane: [Specyfikacja](specyfikacja.md) · [Roadmapa](roadmapa.md) (etap 1) · [Plan labelera](../architecture/plan-labeler.md)

MVP ma pokazać, że labeler w **analizie ciągłej** (nadchodzące zakupy) i **analizie wstecznej** (zrealizowane zakupy) znajduje flagi z weryfikowalnym dowodem. Wejściem jest paczka dokumentów zakupu, zwykle niekompletna, plus kontekst: historia spraw i zakupów, katalog urządzeń, stany magazynowe i rejestry publiczne. Wszystko na syntetycznej firmie telco, bez danych klienta.

## Hipotezy

| # | Hipoteza | Jak sprawdzamy |
| --- | --- | --- |
| H1 | Labeler znajduje flagi z dowodem, który da się zweryfikować w źródle, także na niekompletnych paczkach | precyzja na zestawie ewaluacyjnym, 100% dowodów zweryfikowanych, „nie da się ocenić” z poprawnym powodem |
| H2 | Kontekst daje sygnały, których nie widać w samych dokumentach | porównanie przebiegu bez funkcji kontekstu i z nimi na tych samych zakupach |
| H3 | Przypadki z zestawu testowego da się wykryć przed decyzją, bez czytania korespondencji | wykrycie przypadków zaszytych w firmie syntetycznej na etapie „przed zakupem” |
| H4 | Raport jest zrozumiały bez naszego komentarza | ocena 2–3 osób spoza zespołu |

## Użytkownicy MVP

- **Analityk (my):** uruchamia analizę, przegląda flagi, oznacza zestaw ewaluacyjny.
- **Odbiorca raportu (compliance, finanse):** czyta raport zakupu, zestawienie analizy wstecznej i informację dla compliance.

Role, SSO i dwa tryby widoku wchodzą w etapie 2.

## W zakresie

### Wejście

- Analiza ciągła jednego zakupu z folderu z paczką dokumentów (CLI), na etapie „przed zakupem” albo „po zakupie”.
- Analiza wsteczna: ten sam przebieg wsadowo dla całej historii zakupów firmy syntetycznej.

### Przygotowanie plików

Osobnego enkodera nie budujemy. Przed wywołaniem modelu działają małe funkcje pomocnicze:

- metadane z oryginału: autor, firma, ostatni edytujący, daty, szablon, śledzone zmiany, komentarze, hash SHA-256; przekazywane modelowi jako tekst,
- czysty tekst z PDF, DOCX i XLSX: do weryfikacji cytatów i jako wejście dla modeli tekstowych,
- konwersja DOCX i XLSX, gdy API modelu ich nie przyjmuje,
- pomijanie plików korespondencji.

Skany czyta model z obsługą obrazu; OCR dla modeli tekstowych tylko wtedy, gdy okaże się potrzebny.

### Labeler

- Katalog flag w YAML, z katalogu zamkniętego, poza tym repo. Format: [Format katalogu](../architecture/format-katalogu.md).
- Jedno wywołanie modelu na sprawę: pliki w całości, metadane jako tekst, zestaw flag z instrukcjami i funkcje kontekstu: historia spraw, historia zakupów, katalog urządzeń, stany magazynowe, rejestry publiczne, ceny referencyjne, zlecenia prac, budżety i progi akceptacji, struktura firmy (plan labelera).
- `ai-engine` z adapterami Anthropic, Gemini i API zgodnego z OpenAI; domyślnie aktywny jeden silnik. Labeler jest bezstanowy i publikuje wynik zdarzeniem; zapisuje go `case-manager`.
- Structured output: stan (wykryto, nie wykryto, nie da się ocenić z powodem), siła sygnału, dowody (plik i krótki cytat albo referencja z funkcji kontekstu), osoby i podmioty, których dotyczy, wyjaśnienie, proponowana poprawka.
- Weryfikacja dowodów: cytat musi występować w czystym tekście wskazanego pliku, wartość z kontekstu w rekordzie dowodowym, czyli zapisanej odpowiedzi funkcji ze stanem na dzień; flaga bez potwierdzonego dowodu jest odrzucana i logowana.
- Pewność bazowa ze stałych startowych (słaby 0,3, umiarkowany 0,6, silny 0,85), limit 0,5 dla podpowiedzi bez potwierdzenia.
- Pełne wersjonowanie wyniku: katalog, definicja, hash instrukcji, model, wersja przygotowania plików, tryb, etap, data.

### Flagi w MVP

Labeler wykonuje cały zestaw flag z katalogu zamkniętego. Flagi, które potrzebują danych spoza MVP (graf komunikacji, telemetria, rejestry producentów), zwracają „nie da się ocenić” z powodem.

### Katalog urządzeń

- Jedna kategoria, 5–10 producentów, płaska tabela modeli i parametrów z kart katalogowych, z mapowaniem part numberów.
- Zamienniki, EOL i EOS, autoryzowani partnerzy producenta.
- Wyszukiwanie dla labelera przez funkcje kontekstu.

### Firma syntetyczna

- 15–20 zakupów w kategorii katalogu z paczkami: RFP i ich wersje, memo, oferty, wnioski. Część paczek celowo niekompletna.
- Część zakupów zrealizowana: zamówienia, faktury, protokoły odbioru, aneksy (do analizy wstecznej).
- Historia zakupów z 24 miesięcy, stany magazynowe i zużycie, budżety i progi akceptacji, zlecenia prac, struktura firmy z minimum danych o osobach, fikcyjne podmioty oferentów z danymi „rejestrowymi”.
- Zaszyte przypadki z zamkniętego zestawu testowego, bez danych z prawdziwych spraw, oraz kilka czystych zakupów jako kontrola.
- Wersja demo (czysta) i wersja zabłocona (duplikaty SKU, różne nazwy tego samego produktu, brakujące pola, skany).

### Scoring i raport

- Ryzyko R i kategorie A–D według jawnych reguł ze specyfikacji.
- Informacja dla compliance: „oferent | zespół | osoby wymagają analizy”, bez ocen i wniosków.
- JSON zakupu w schemacie 2.0.
- Raport HTML dla jednego zakupu: kategoria i R, flagi z rozbiciem pewności, dowody z cytatem i odnośnikiem do pliku, proponowane poprawki, lista „nie da się ocenić” z powodami, pokrycie kontekstu.
- Zestawienie analizy wstecznej: rozkład A–D, najczęstsze flagi, zakupy z informacją dla compliance.

### Uruchomienie

- Lokalnie przez Docker Compose, te same obrazy co docelowo; PostgreSQL i S3 (MinIO) jako zamienniki dostarczanych przez klienta. Knative i k3d wchodzą w etapie 2.
- Testy na danych syntetycznych mogą korzystać z modelu w chmurze. Jeden pełny przebieg na modelu open-weight dostępnym przez API zgodne z OpenAI (np. gpt-oss-120b) pokazuje, że działa bez chmury.

## Poza zakresem MVP

| Element | Kiedy |
| --- | --- |
| Konektory do systemów klienta: ERP, historia spraw, faktury | etap 3 |
| Telemetria i inwentarz sieci (urządzenia poza siecią, OLT i CMTS, EOL w lokalizacji) | etap 3 |
| Graf powiązań | etap 4 |
| Agregacja po osobach, zespołach i dostawcach | etap 3 |
| Dwa tryby widoku, role, SSO, rejestr decyzji w interfejsie | etap 2 |
| Rejestry producentów (S/N) | etap 5 |
| Moduł zakupowy | etap 5 |
| Helm, Knative, kolejka zdarzeń, object lock | etap 2 |
| Etykiety kosztów i model kosztów firmy | etap 6 |
| Śledztwo | nigdy w narzędziu |
| Fine-tuning modeli | nie planujemy |

Przetargi publiczne (e-Zamówienia, TED) służą tylko do testów przygotowania plików. Nie mają memo, ofert konkurencyjnych ani historii zakupów, więc nie są głównym korpusem.

## Kryteria akceptacji

Progi są propozycją do potwierdzenia przed startem fazy.

| Kryterium | Próg |
| --- | --- |
| Zakupy firmy syntetycznej przetworzone end-to-end bez ręcznej ingerencji | 100% |
| Dowody w raporcie zweryfikowane w pliku lub w rekordzie dowodowym | 100% |
| Przypadki zaszyte w firmie syntetycznej wykryte: wersja demo / zabłocona | 100% / ≥ 80% |
| Przypadki wykryte na etapie „przed zakupem” (H3), spośród tych, które da się wykryć przed zakupem | ≥ 80% |
| Czyste zakupy: kategoria | A lub B |
| Precyzja flag opartych na samych plikach sprawy | ≥ 0,8 |
| Precyzja flag korzystających z kontekstu | ≥ 0,7 |
| Flagi w stanie „nie da się ocenić” z powodu nieczytelnego pliku (nie braku dokumentów) | ≤ 10% |
| Powtarzalność: ten sam stan flagi przy dwóch przebiegach na tej samej wersji | ≥ 95% |
| Czas analizy jednego zakupu na modelu w chmurze | ≤ 10 min |
| Raport oceniony przez osoby spoza zespołu | co najmniej 2, rozumieją go bez komentarza |

## Rezultaty

- Repo silnika z labelerem i schematami.
- Poza tym repo: katalog flag, katalog urządzeń jednej kategorii, firma syntetyczna i zestaw ewaluacyjny.
- Wyniki JSON i raporty HTML dla wszystkich zakupów firmy syntetycznej oraz zestawienie analizy wstecznej.
- Raport przykładowy.
- Notatka z ewaluacji: precyzja per flaga, wpływ kontekstu (H2), porównanie modelu chmurowego i lokalnego, główne problemy z plikami.

## Decyzje przed startem

- [ ] Pierwsza kategoria katalogu urządzeń: serwery, transceivery czy sprzęt abonencki.
- [ ] Model chmurowy do testów i model lokalny do jednego przebiegu.
- [ ] Skąd dane rejestrowe do firmy syntetycznej: fikcyjne podmioty czy prawdziwe rejestry na przykładach publicznych.
- [ ] Progi kryteriów akceptacji.

## Ryzyka MVP

- **Realizm firmy syntetycznej.** Przypadki zaszyte przez nas samych łatwo wykryć. Zestaw ewaluacyjny powinna przygotować inna osoba niż ta, która pisze instrukcje flag, a wersja zabłocona musi przypominać prawdziwe dokumenty.
- **Niekompletne paczki.** U klienta rzadko będzie komplet dokumentów. Flagi muszą dawać „nie da się ocenić” z poprawnym powodem, a nie zgadywać.
- **Katalog urządzeń** to praca ręczna przy kartach katalogowych; zakres jednej kategorii trzeba utrzymać.
- **Dopasowanie osób do rejestrów publicznych** dotyka danych osobowych i łatwo o fałszywe dopasowanie po nazwisku; w MVP wynik zawsze potwierdza analityk.
