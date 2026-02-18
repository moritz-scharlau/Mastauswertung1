from __future__ import annotations

import argparse
import json

from .calculator import build_mastauswertung
from .io import load_input


def main() -> None:
    parser = argparse.ArgumentParser(description="Mastauswertung aus strukturierten Eingabedaten erzeugen")
    parser.add_argument("input", help="Pfad zur Input-JSON")
    parser.add_argument("-o", "--output", help="Optionaler Pfad für Output-JSON")
    args = parser.parse_args()

    input_data = load_input(args.input)
    result = build_mastauswertung(input_data).to_dict()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
