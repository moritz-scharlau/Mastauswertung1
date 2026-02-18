# Mastauswertung-Tool (extern)

Dieses Tool ist auf eure gewünschte **Systemarchitektur** ausgerichtet und erzeugt aus strukturierten Eingabedaten eine Mastauswertung als JSON.

## Enthaltene Kernlogik

- Datenmodelle für:
  - `Batch`
  - `FerkelInvoice`
  - `SlaughterGroup`
  - `FeedInvoice`
  - `VetInvoice`
  - `DisposalInvoice`
- Kernfunktionen:
  - `calculate_losses(eingestallt, geschlachtet)`
  - `calculate_db(batch)`
  - `build_mastauswertung(input_data)`
- Validierungen:
  - `Verluste == SecAnim_count`
  - `Transport_count == geschlachtet`
  - `Netto = Brutto / (1 + MwSt)` (wenn nur Brutto vorhanden)
  - Keine negativen Lagerverbräuche
- Output-JSON gemäß gewünschter Struktur:
  - `summary`
  - `groups`
  - `feed_detail`
  - `vet_treatments`
  - `warnings`

## CLI-Nutzung

```bash
python -m mastauswertung.cli input.json -o output.json
```

Ohne `-o` wird das Ergebnis auf stdout ausgegeben.

## Streamlit UI

```bash
streamlit run app.py
```

Die UI nimmt JSON entgegen und zeigt das Ergebnis direkt an.

## Dokumente (PDF/Bild)

In `mastauswertung/processor.py` ist eine leichte Dokument-Erkennung enthalten (`parse_document`), die pro Datei Typ-, Datums- und Betragskandidaten extrahiert. Diese Daten können dann in das strukturierte Input-JSON überführt werden.

## Tests

```bash
pytest -q
```
