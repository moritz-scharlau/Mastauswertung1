from __future__ import annotations

from collections import defaultdict

from .models import Batch, InputData, OutputData


def calculate_losses(eingestallt: int, geschlachtet: int) -> int:
    return eingestallt - geschlachtet


def calculate_db(batch: Batch) -> float:
    return (
        batch.revenue_per_head
        - batch.ferkel_per_head
        - batch.feed_per_head
        - batch.vet_per_head
        - batch.disposal_per_head
        - batch.transport_per_head
        - batch.sonstige_per_head
    )


def _safe_per_head(total: float, geschlachtet: int) -> float:
    if geschlachtet <= 0:
        return 0.0
    return total / geschlachtet


def _feed_consumption_dt_and_cost(input_data: InputData) -> tuple[dict[str, float], float, list[str]]:
    warnings: list[str] = []
    details: dict[str, float] = {}
    total_cost = 0.0

    start = input_data.lagerbestand.get("start", {})
    end = input_data.lagerbestand.get("end", {})

    for artikel in sorted(set(start) | set(end)):
        start_val = float(start.get(artikel, 0.0))
        end_val = float(end.get(artikel, 0.0))
        consumption = start_val - end_val
        if consumption < 0:
            warnings.append(f"Negativer Lagerverbrauch für {artikel}: {consumption:.2f} dt")
            consumption = 0.0

        preis = float(input_data.market_prices.get(artikel, 0.0))
        value = consumption * (preis + input_data.lagerkosten_dt)
        details[artikel] = consumption
        total_cost += value

    return details, round(total_cost, 2), warnings


def build_mastauswertung(input_data: InputData) -> OutputData:
    warnings: list[str] = []

    losses = calculate_losses(input_data.eingestallt, input_data.geschlachtet)
    loss_pct = (losses / input_data.eingestallt * 100.0) if input_data.eingestallt else 0.0

    secanim_count = sum(x.count for x in input_data.disposal_invoices)
    if secanim_count != losses:
        warnings.append(
            f"Validierung: Verluste ({losses}) stimmen nicht mit SecAnim_count ({secanim_count}) überein."
        )

    if input_data.transport_count != input_data.geschlachtet:
        warnings.append(
            f"Validierung: Transport_count ({input_data.transport_count}) stimmt nicht mit geschlachtet ({input_data.geschlachtet}) überein."
        )

    feed_consumption, feed_stock_cost, feed_warnings = _feed_consumption_dt_and_cost(input_data)
    warnings.extend(feed_warnings)

    feed_invoice_total = sum(x.net_total for x in input_data.feed_invoices)
    feed_total = round(feed_invoice_total + feed_stock_cost, 2)

    ferkel_total = round(sum(x.net_total for x in input_data.ferkel), 2)
    revenue_total = round(sum(x.net_revenue for x in input_data.slaughter_groups), 2)
    vet_total = round(sum(x.net_total for x in input_data.vet_invoices), 2)
    disposal_total = round(sum(x.net_total for x in input_data.disposal_invoices), 2)

    batch = Batch(
        location=input_data.location,
        eingestallt=input_data.eingestallt,
        geschlachtet=input_data.geschlachtet,
        verluste=losses,
        verluste_prozent=round(loss_pct, 2),
        revenue_per_head=_safe_per_head(revenue_total, input_data.geschlachtet),
        ferkel_per_head=_safe_per_head(ferkel_total, input_data.geschlachtet),
        feed_per_head=_safe_per_head(feed_total, input_data.geschlachtet),
        vet_per_head=_safe_per_head(vet_total, input_data.geschlachtet),
        disposal_per_head=_safe_per_head(disposal_total, input_data.geschlachtet),
        transport_per_head=0.0,
        sonstige_per_head=float(input_data.sonstige_kosten_pro_schwein),
    )

    db_pro_schwein = round(calculate_db(batch), 2)
    db_gesamt = round(db_pro_schwein * input_data.geschlachtet, 2)

    treatments = sorted({t for v in input_data.vet_invoices for t in v.treatments})

    grouped_feed_costs: dict[str, float] = defaultdict(float)
    for item in input_data.feed_invoices:
        grouped_feed_costs[item.category] += item.net_total

    feed_detail = [
        {
            "article": art,
            "consumption_dt": round(cons, 2),
            "market_price": input_data.market_prices.get(art, 0.0),
        }
        for art, cons in sorted(feed_consumption.items())
    ]
    for cat, total in sorted(grouped_feed_costs.items()):
        feed_detail.append({"category": cat, "invoice_net_total": round(total, 2)})

    summary = {
        "eingestallt": input_data.eingestallt,
        "geschlachtet": input_data.geschlachtet,
        "verluste": losses,
        "db_pro_schwein": db_pro_schwein,
        "db_gesamt": db_gesamt,
    }

    groups = [
        {
            "date": g.date.isoformat(),
            "slaughterhouse": g.slaughterhouse,
            "count": g.count,
            "model": g.model,
            "net_revenue": g.net_revenue,
            "sg_avg": g.sg_avg,
        }
        for g in input_data.slaughter_groups
    ]

    return OutputData(
        summary=summary,
        groups=groups,
        feed_detail=feed_detail,
        vet_treatments=treatments,
        warnings=warnings,
    )
