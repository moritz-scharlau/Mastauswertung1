from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any


@dataclass
class Batch:
    location: str
    eingestallt: int
    geschlachtet: int
    verluste: int = 0
    verluste_prozent: float = 0.0
    revenue_per_head: float = 0.0
    ferkel_per_head: float = 0.0
    feed_per_head: float = 0.0
    vet_per_head: float = 0.0
    disposal_per_head: float = 0.0
    transport_per_head: float = 0.0
    sonstige_per_head: float = 0.0


@dataclass
class FerkelInvoice:
    date: date
    quantity: int
    avg_weight: float
    price_per_head: float
    net_total: float


@dataclass
class SlaughterGroup:
    date: date
    slaughterhouse: str
    count: int
    sg_total: float
    sg_avg: float
    model: str  # MFL / INDEX
    magerfleisch: float | None
    index_per_kg: float | None
    leberbefund: int
    bonus_count: int
    net_revenue: float


@dataclass
class FeedInvoice:
    supplier: str
    article: str
    quantity_kg: float
    net_total: float
    category: str  # Vormast / Endmast / Sonst


@dataclass
class VetInvoice:
    date: date
    net_total: float
    treatments: list[str]


@dataclass
class DisposalInvoice:
    net_total: float
    count: int
    location: str


@dataclass
class InputData:
    location: str
    market_prices: dict[str, float]
    lagerkosten_dt: float
    lagerbestand: dict[str, dict[str, float]]
    sonstige_kosten_pro_schwein: float
    eingestallt: int
    geschlachtet: int
    transport_count: int
    ferkel: list[FerkelInvoice] = field(default_factory=list)
    slaughter_groups: list[SlaughterGroup] = field(default_factory=list)
    feed_invoices: list[FeedInvoice] = field(default_factory=list)
    vet_invoices: list[VetInvoice] = field(default_factory=list)
    disposal_invoices: list[DisposalInvoice] = field(default_factory=list)


@dataclass
class OutputData:
    summary: dict[str, float | int]
    groups: list[dict[str, Any]]
    feed_detail: list[dict[str, Any]]
    vet_treatments: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
