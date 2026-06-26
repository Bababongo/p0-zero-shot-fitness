from __future__ import annotations

import csv
import json
from importlib.resources import files
from pathlib import Path

from p0_zero_shot_fitness.models import JsonDict, VariantRecord


def fixture_path(filename: str):
    return files("p0_zero_shot_fitness.fixtures").joinpath(filename)


def load_fixture_text(filename: str) -> str:
    return fixture_path(filename).read_text(encoding="utf-8")


def load_fixture_json(filename: str) -> JsonDict:
    return json.loads(load_fixture_text(filename))


def read_fasta_sequence(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "".join(line for line in lines if not line.startswith(">")).upper()


def load_dms_csv_text(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(text.splitlines()))


def load_dms_csv_path(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_scored_variants(path: Path, records: list[VariantRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "variant",
        "wild_type",
        "position",
        "mutant",
        "fitness",
        "is_catalytic",
        "mutation_class",
        "model_score",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record.to_row())


def write_json(path: Path, payload: JsonDict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
