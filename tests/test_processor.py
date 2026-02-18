from mastauswertung.calculator import build_mastauswertung, calculate_db, calculate_losses
from mastauswertung.io import input_from_dict, netto_from_brutto
from mastauswertung.models import Batch


def test_calculate_losses():
    assert calculate_losses(540, 529) == 11


def test_calculate_db():
    batch = Batch(
        location="Natrup 1",
        eingestallt=540,
        geschlachtet=529,
        revenue_per_head=190,
        ferkel_per_head=95,
        feed_per_head=70,
        vet_per_head=8,
        disposal_per_head=2,
        transport_per_head=3,
        sonstige_per_head=6,
    )
    assert calculate_db(batch) == 6


def test_nett_from_brutto():
    assert netto_from_brutto(119.0, 0.19) == 100.0


def test_build_mastauswertung_with_validations():
    payload = {
        "location": "Natrup 1",
        "market_prices": {"weizen": 26.09, "gerste": 25.09},
        "lagerkosten_dt": 1.2,
        "lagerbestand": {"start": {"weizen": 500, "gerste": 300}, "end": {"weizen": 100, "gerste": 50}},
        "sonstige_kosten_pro_schwein": 6.0,
        "eingestallt": 540,
        "geschlachtet": 529,
        "transport_count": 520,
        "ferkel": [{"date": "2025-01-02", "quantity": 540, "avg_weight": 30, "price_per_head": 95, "net_total": 51300}],
        "slaughter_groups": [{"date": "2025-05-15", "slaughterhouse": "Musterhof", "count": 529, "sg_total": 100000, "sg_avg": 189, "model": "INDEX", "magerfleisch": None, "index_per_kg": 1.2, "leberbefund": 4, "bonus_count": 20, "net_revenue": 100000}],
        "feed_invoices": [{"supplier": "Futter GmbH", "article": "Mastmix", "quantity_kg": 20000, "net_total": 12000, "category": "Endmast"}],
        "vet_invoices": [{"date": "2025-03-02", "net_total": 1700, "treatments": ["Impfung", "Wurmkur"]}],
        "disposal_invoices": [{"net_total": 550, "count": 11, "location": "Natrup 1"}],
    }

    data = input_from_dict(payload)
    result = build_mastauswertung(data)

    assert result.summary["verluste"] == 11
    assert result.summary["eingestallt"] == 540
    assert any("Transport_count" in w for w in result.warnings)
    assert isinstance(result.feed_detail, list)
    assert sorted(result.vet_treatments) == ["Impfung", "Wurmkur"]
