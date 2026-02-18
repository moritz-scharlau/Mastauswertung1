from __future__ import annotations

import re
from datetime import date
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None

try:
    import pytesseract
    from PIL import Image
except ImportError:  # pragma: no cover
    pytesseract = None
    Image = None

_AMOUNT = re.compile(r"(\d{1,3}(?:[\.\s]\d{3})*(?:,\d{2})|\d+,\d{2})")
_DATE = re.compile(r"\b(\d{2}\.\d{2}\.\d{4})\b")


def _to_eur(value: str) -> float:
    normalized = value.replace(" ", "").replace(".", "").replace(",", ".")
    return round(float(normalized), 2)


def _to_date_or_none(text: str) -> date | None:
    hit = _DATE.search(text)
    if not hit:
        return None
    d, m, y = hit.group(1).split(".")
    return date(int(y), int(m), int(d))


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        if PdfReader is None:
            raise RuntimeError("PDF-Verarbeitung nicht möglich: pypdf fehlt")
        return "\n".join((page.extract_text() or "") for page in PdfReader(str(path)).pages)

    if suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}:
        if pytesseract is None or Image is None:
            raise RuntimeError("Bild-OCR nicht möglich: pytesseract/Pillow fehlen")
        return pytesseract.image_to_string(Image.open(path), lang="deu+eng")

    raise ValueError(f"Nicht unterstütztes Dateiformat: {path.suffix}")


def infer_document_type(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["schlachthof", "schlacht", "auszahlung"]):
        return "slaughter"
    if any(k in t for k in ["ferkel", "piglet"]):
        return "ferkel"
    if any(k in t for k in ["tierarzt", "impfung", "medizin"]):
        return "vet"
    if any(k in t for k in ["secanim", "entsorgung", "kadaver"]):
        return "disposal"
    if any(k in t for k in ["futter", "mischfutter", "mast"]):
        return "feed"
    return "unknown"


def extract_amounts(text: str) -> list[float]:
    return [_to_eur(m.group(1)) for m in _AMOUNT.finditer(text)]


def parse_document(path: Path) -> dict[str, object]:
    text = extract_text(path)
    return {
        "file": path.name,
        "date": _to_date_or_none(text).isoformat() if _to_date_or_none(text) else None,
        "document_type": infer_document_type(text),
        "amount_candidates": extract_amounts(text),
        "text_preview": text[:200].replace("\n", " "),
    }
