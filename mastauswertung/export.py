from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def export_json(path: str | Path, payload: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
