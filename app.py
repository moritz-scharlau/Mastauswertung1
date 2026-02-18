from __future__ import annotations

import json

import streamlit as st

from mastauswertung.calculator import build_mastauswertung
from mastauswertung.io import input_from_dict

st.set_page_config(page_title="Mastauswertung", layout="wide")
st.title("Mastauswertung – JSON zu Ergebnis")

st.markdown("""
Füge eure strukturierten Betriebsdaten als JSON ein. Das Tool berechnet automatisch:
- Verluste
- DB pro Schwein / gesamt
- Gruppen- und Futterdetails
- Validierungswarnungen
""")

example = {
    "location": "Natrup 1",
    "market_prices": {"weizen": 26.09, "gerste": 25.09},
    "lagerkosten_dt": 1.2,
    "lagerbestand": {"start": {"weizen": 500, "gerste": 300}, "end": {"weizen": 100, "gerste": 50}},
    "sonstige_kosten_pro_schwein": 6.0,
    "eingestallt": 540,
    "geschlachtet": 529,
    "transport_count": 529,
    "ferkel": [{"date": "2025-01-02", "quantity": 540, "avg_weight": 30.0, "price_per_head": 95.0, "net_total": 51300}],
    "slaughter_groups": [{"date": "2025-05-15", "slaughterhouse": "Musterhof", "count": 529, "sg_total": 100000, "sg_avg": 189.0, "model": "INDEX", "magerfleisch": None, "index_per_kg": 1.2, "leberbefund": 4, "bonus_count": 20, "net_revenue": 100000}],
    "feed_invoices": [{"supplier": "Futter GmbH", "article": "Mastmix", "quantity_kg": 20000, "net_total": 12000, "category": "Endmast"}],
    "vet_invoices": [{"date": "2025-03-02", "net_total": 1700, "treatments": ["Impfung", "Wurmkur"]}],
    "disposal_invoices": [{"net_total": 550, "count": 11, "location": "Natrup 1"}],
}

raw = st.text_area("Input JSON", value=json.dumps(example, ensure_ascii=False, indent=2), height=420)

if st.button("Auswertung berechnen"):
    try:
        data = input_from_dict(json.loads(raw))
        result = build_mastauswertung(data).to_dict()
    except Exception as exc:
        st.error(f"Fehler: {exc}")
    else:
        st.success("Auswertung erfolgreich berechnet")
        st.json(result)
        st.download_button(
            "📥 Ergebnis als JSON herunterladen",
            data=json.dumps(result, ensure_ascii=False, indent=2),
            file_name="mastauswertung_result.json",
            mime="application/json",
        )
