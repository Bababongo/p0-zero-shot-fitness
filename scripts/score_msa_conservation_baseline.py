from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p0_zero_shot_fitness.conservation import conservation_log_odds_score, load_conservation_profile
from p0_zero_shot_fitness.io import write_json, write_scored_variants
from p0_zero_shot_fitness.metrics import summarize_records
from p0_zero_shot_fitness.models import Mutation, VariantRecord
from p0_zero_shot_fitness.plotting.svg import write_scatter_svg


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes"}


def load_scored_variants_with_conservation_scores(
    scored_variants_csv: Path,
    conservation_profile: dict[str, object],
) -> list[VariantRecord]:
    records: list[VariantRecord] = []
    with scored_variants_csv.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            mutation = Mutation(
                raw=row["variant"],
                wild_type=row["wild_type"],
                position=int(row["position"]),
                mutant=row["mutant"],
            )
            residue_groups = frozenset(
                group_name
                for group_name in row.get("residue_groups", "").split(";")
                if group_name
            )
            records.append(
                VariantRecord(
                    mutation=mutation,
                    fitness=float(row["fitness"]),
                    is_catalytic=parse_bool(row["is_catalytic"]),
                    model_score=conservation_log_odds_score(mutation, conservation_profile),
                    residue_groups=residue_groups,
                )
            )
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a P0 run with an MSA conservation baseline.")
    parser.add_argument("--scored-variants-csv", type=Path, required=True)
    parser.add_argument("--conservation-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--bootstrap-iterations", type=int, default=0)
    parser.add_argument("--null-iterations", type=int, default=0)
    args = parser.parse_args()

    profile = load_conservation_profile(args.conservation_json)
    records = load_scored_variants_with_conservation_scores(args.scored_variants_csv, profile)
    metrics = summarize_records(
        records,
        bootstrap_iterations=args.bootstrap_iterations,
        null_iterations=args.null_iterations,
    )
    payload = {
        "benchmark": "P0 - Zero-Shot Fitness",
        "question": "Do protein language models fail differently on catalytic residues than on the rest of the protein?",
        "dataset": args.dataset_name,
        "scorer": "MSAConservationLogOddsScorer",
        "data_scope": "MSA-derived conservation baseline scored on an existing P0 variant table",
        "input_files": {
            "scored_variants_csv": str(args.scored_variants_csv),
            "conservation_json": str(args.conservation_json),
        },
        "metrics": metrics,
        "artifacts": {
            "scored_variants_csv": "scored_variants.csv",
            "fitness_scatter_svg": "fitness_scatter.svg",
        },
    }

    write_json(args.output_dir / "metrics.json", payload)
    write_scored_variants(args.output_dir / "scored_variants.csv", records)
    write_scatter_svg(args.output_dir / "fitness_scatter.svg", records)
    print(f"Wrote MSA conservation baseline to {args.output_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
