from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .models import DisposalInvoice, FeedInvoice, FerkelInvoice, InputData, SlaughterGroup, VetInvoice


def netto_from_brutto(brutto: float, mwst: float) -> float:
    return round(brutto / (1.0 + mwst), 2)


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _ensure_netto(record: dict[str, Any]) -> float:
    if "net_total" in record:
        return float(record["net_total"])
    if "brutto_total" in record and "mwst" in record:
        return netto_from_brutto(float(record["brutto_total"]), float(record["mwst"]))
    raise ValueError(f"Datensatz hat weder net_total noch brutto_total+mwst: {record}")


def input_from_dict(raw: dict[str, Any]) -> InputData:
    ferkel = [
        FerkelInvoice(
            date=_parse_date(item["date"]),
            quantity=int(item["quantity"]),
            avg_weight=float(item["avg_weight"]),
            price_per_head=float(item["price_per_head"]),
            net_total=_ensure_netto(item),
        )
        for item in raw.get("ferkel", [])
    ]

    slaughter_groups = [
        SlaughterGroup(
            date=_parse_date(item["date"]),
            slaughterhouse=str(item["slaughterhouse"]),
            count=int(item["count"]),
            sg_total=float(item["sg_total"]),
            sg_avg=float(item["sg_avg"]),
            model=str(item["model"]),
            magerfleisch=float(item["magerfleisch"]) if item.get("magerfleisch") is not None else None,
            index_per_kg=float(item["index_per_kg"]) if item.get("index_per_kg") is not None else None,
            leberbefund=int(item.get("leberbefund", 0)),
            bonus_count=int(item.get("bonus_count", 0)),
            net_revenue=_ensure_netto(item) if "net_total" in item or "brutto_total" in item else float(item["net_revenue"]),
        )
        for item in raw.get("slaughter_groups", [])
    ]

    feed_invoices = [
        FeedInvoice(
            supplier=str(item.get("supplier", "unbekannt")),
            article=str(item.get("article", "unbekannt")),
            quantity_kg=float(item.get("quantity_kg", 0.0)),
            net_total=_ensure_netto(item),
            category=str(item.get("category", "Sonst")),
        )
        for item in raw.get("feed_invoices", [])
    ]

    vet_invoices = [
        VetInvoice(
            date=_parse_date(item["date"]),
            net_total=_ensure_netto(item),
            treatments=[str(x) for x in item.get("treatments", [])],
        )
        for item in raw.get("vet_invoices", [])
    ]

    disposal_invoices = [
        DisposalInvoice(
            net_total=_ensure_netto(item),
            count=int(item.get("count", 0)),
            location=str(item.get("location", raw.get("location", ""))),
        )
        for item in raw.get("disposal_invoices", [])
    ]

    return InputData(
        location=str(raw["location"]),
        market_prices={str(k): float(v) for k, v in raw.get("market_prices", {}).items()},
        lagerkosten_dt=float(raw.get("lagerkosten_dt", 0.0)),
        lagerbestand=raw.get("lagerbestand", {"start": {}, "end": {}}),
        sonstige_kosten_pro_schwein=float(raw.get("sonstige_kosten_pro_schwein", 0.0)),
        eingestallt=int(raw["eingestallt"]),
        geschlachtet=int(raw["geschlachtet"]),
        transport_count=int(raw.get("transport_count", raw["geschlachtet"])),
        ferkel=ferkel,
        slaughter_groups=slaughter_groups,
        feed_invoices=feed_invoices,
        vet_invoices=vet_invoices,
        disposal_invoices=disposal_invoices,
    )


def load_input(path: str | Path) -> InputData:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return input_from_dict(raw)
