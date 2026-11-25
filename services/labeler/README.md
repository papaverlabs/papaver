# Labeler

Serwis, który ocenia sprawę zakupową (pliki RFP, memo, ofert, zamówień) według katalogu flag. Na razie zawiera format katalogu i jego walidację; ocena spraw jest następnym krokiem ([plan labelera](../../docs/architecture/plan-labeler.md)).

## Uruchomienie

```sh
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python -m pytest
venv/bin/python -m app catalog check tests/fixtures/catalog     # walidacja katalogu i podsumowanie zestawów
venv/bin/python -m app catalog set tests/fixtures/catalog telco # flagi zestawu po rozwinięciu
venv/bin/python -m app schema --out ../../schemas               # JSON Schema formatu katalogu
```

Schematy w [`schemas/`](../../schemas/) w korzeniu repo są generowane z modeli w `app/catalog.py`. Po zmianie modeli trzeba je wygenerować ponownie.
