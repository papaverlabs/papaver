# Papaver — plan labelera

Powiązane: [Specyfikacja](../product/specyfikacja.md) · [Zakres MVP](../product/zakres-mvp.md) · [Format katalogu](format-katalogu.md)

Labeler bierze manifest i pliki jednej sprawy (zakupu), zestaw flag i etap oceny, robi jedno wywołanie modelu przez `ai-engine` i publikuje wynik w zdarzeniu `case.labeled`: dla każdej flagi stan z dowodami zweryfikowanymi w pliku. Labeler jest bezstanowy; wynik zapisuje `case-manager` ([architektura](architektura.md)).

## Tryby działania (25.11.2026)

| Tryb | Co robi | Labeler |
| --- | --- | --- |
| Analiza ciągła | ocenia nadchodzące zakupy | tak, to budujemy teraz |
| Analiza wsteczna | ocenia historię zrealizowanych zakupów, najczęściej przy uruchomieniu u klienta | tak, ten sam labeler wsadowo, etap „po zakupie” |
| Analiza kontekstu | cyklicznie zbiera i łączy dane dla trybów 1 i 2: katalogi, stany, telemetria, inwentarz sieci, rejestry, graf powiązań, agregacja | nie; daje dane narzędziom labelera |
| Śledztwo | ad hoc, półautomatycznie, prowadzi człowiek | poza zakresem; labeler daje tylko informację dla compliance |

## Decyzje

- **Weryfikacja zakupu (24.11).** Czy to, co kupujemy (RFP, oferty), odpowiada potrzebie (memo, uzasadnienie). Wejściem jest paczka dokumentów zakupu: RFP, memo, oferty. Rzadko jest kompletna, więc każda flaga działa na tym, co jest, a brak danych to „nie da się ocenić” z powodem.
- **Dwa etapy oceny (24.11).** Przed zakupem i po zakupie. Etap to parametr przebiegu, a nie cecha flagi. Etap mówi modelowi tylko, jakich dokumentów może się spodziewać: przed zakupem brak zamówienia czy faktury nie jest niczym podejrzanym.
- **Dane przez narzędzia (24.11).** Definicja flagi nie deklaruje wymaganych danych. Model dostaje narzędzia (function calling) i sam dobiera informacje.
- **Definicja flagi jest minimalna (24.11):** `code`, `version`, `flag_when`, `severity`, `instructions`.
- **Bez enkodera, jedno wywołanie na sprawę (25.11).** Model dostaje pliki sprawy w całości, metadane jako tekst, zestaw flag i funkcje kontekstu. Dowód flagi to plik i krótki cytat, bez strony i akapitu. Bez bazy wektorowej i RAG na plikach sprawy.
- **Bez treści korespondencji (25.11).** Treść maili i komunikatorów nie trafia do modelu. Pliki korespondencji pomijamy przed wywołaniem modelu. Z komunikacji dostępne są tylko metadane w grafie komunikacji, bez treści.
- **Informacja dla compliance (25.11).** Gdy flaga krytyczna ma silny sygnał albo wokół tego samego oferenta, zespołu lub osoby zbiera się kilka flag, wynik zakupu zawiera krótką informację „oferent | zespół | osoby wymagają analizy”, bez ocen i wniosków.
- **Język (24.11).** Kod, klucze formatu i nazwy narzędzi po angielsku. Kody flag i ich treść na razie po polsku.

## Wejście wywołania

| Element | Skąd |
| --- | --- |
| pliki sprawy w całości | folder sprawy; DOCX i XLSX skonwertowane, gdy API ich nie przyjmuje; dla modeli tekstowych czysty tekst |
| metadane plików jako tekst | odczyt z oryginału: autor, firma, ostatni edytujący, daty, szablon, śledzone zmiany, komentarze, hash |
| opis sprawy | tryb, etap, kategoria, osoby i role, jeśli są znane |
| zestaw flag z instrukcjami | katalog flag |
| funkcje kontekstu | niżej |

Gdy pliki nie mieszczą się w kontekście modelu (mały model lokalny), zestaw flag dzielimy na kilka wywołań na tych samych plikach. To wyjątek.

Czysty tekst każdego pliku zostaje też po stronie silnika: służy do sprawdzenia, czy cytat z flagi jest we wskazanym pliku.

## Funkcje kontekstu

Model wywołuje je przez function calling. Definicje i wykonanie wywołań zapewnia serwis `context`, który kieruje każde wywołanie do komponentu z danymi ([architektura](architektura.md)). Dopóki funkcji nie ma, flagi, które jej potrzebują, zwracają „nie da się ocenić”.

| Funkcja | Zwraca | Komponent |
| --- | --- | --- |
| `past_cases(query)` | poprzednie zakupy: RFP i ich wersje, memo, oferty, wynik, osoby i zespoły | `case-manager` |
| `find_orders(query, since)` | historyczne zamówienia i faktury: produkt, part number, ilość, cena jednostkowa, waluta, dostawca, data, warunki | `erp-view` |
| `market_prices(product)` | ceny referencyjne z rozstrzygnięć przetargów publicznych i od dystrybutorów, ze źródłem, datą, ilością i warunkami | `catalog` |
| `catalog(query)` | modele i materiały z parametrami, zamienniki, producent, autoryzowani partnerzy, EOL i EOS | `catalog` |
| `stock(product)` | stany tego samego modelu i zamienników: wolne, zarezerwowane (pod jaki projekt i od kiedy), w drodze, lokalizacja, zużycie | `erp-view` |
| `network(query)` | urządzenia w sieci po S/N i lokalizacji, wykorzystanie pojemności, urządzenia kupione i nieuruchomione | `asset-registry` |
| `registry(company_or_person)` | zarząd, wspólnicy, prokurenci, beneficjenci, działalność, adres, rachunki | `supplier-registry` |
| `contacts(person, counterpart, since)` | liczba kontaktów w czasie, bez treści | `comm-graph` |
| `work_orders(query)` | zlecenia instalacji i serwisu, raporty prac, zgłoszenia serwisowe: kto, gdzie, kiedy | `asset-registry` |
| `budget(query)` | pozycje budżetu, progi akceptacji, ścieżka akceptacji | `erp-view` |
| `org(person)` | rola, dział, przełożony, minimum danych osoby do dopasowania w rejestrach | `org` |
| `policies(query)` | pryncypia, standardy, roadmapa, plan wygaszania technologii, partnerzy strategiczni | `org` |
| `vendor_registry(serial)` | model, gwarancja i czy numer seryjny jest na koncie firmy u producenta | `asset-registry` (etap 5) |

Każda odpowiedź funkcji ma stan na dzień (`as_of`) i komponent źródłowy. `labeler` dołącza odpowiedzi do wyniku jako rekordy dowodowe, a dowód z kontekstu wskazuje rekord i miejsce w odpowiedzi; silnik sprawdza wartość w tym rekordzie, tak jak cytat w czystym tekście pliku.

## Wynik

Dla każdej flagi:

- stan: wykryto, nie wykryto, nie da się ocenić (z powodem),
- siła sygnału: słaby, umiarkowany, silny,
- dowody: plik (link, hash) i krótki dosłowny cytat albo rekord dowodowy z odpowiedzi funkcji kontekstu (stan na dzień); flaga bez potwierdzonego dowodu jest odrzucana i logowana,
- podmioty i osoby, których dotyczy (role w zakupie, bez ocen),
- wyjaśnienie i proponowana poprawka,
- wersje: katalog, definicja flagi, hash instrukcji, model, wersja przygotowania plików, tryb, etap, data.

Dla zakupu: ryzyko R, kategoria i informacja dla compliance, jeśli jest.

## Kolejność prac

1. Format katalogu i walidacja — zrobione.
2. Przygotowanie plików: metadane z oryginału, czysty tekst z PDF, DOCX i XLSX, konwersja dla API, pomijanie korespondencji.
3. Wywołanie modelu przez `ai-engine` (na start jeden silnik): pliki, metadane, zestaw flag, structured output wyniku.
4. Weryfikacja cytatów w czystym tekście, odrzucanie flag bez dowodu.
5. CLI: `labeler assess <folder> --catalog <dir> --set <name> --stage before|after` → JSON; analiza wsteczna to ten sam przebieg wsadowo.
6. Pierwsze porównanie z oceną ręczną na flagach, które działają na samych plikach.
7. Funkcje kontekstu, zaczynając od historii zakupów i katalogu urządzeń.
