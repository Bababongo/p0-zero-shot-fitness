from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p0_zero_shot_fitness.io import write_json, write_scored_variants
from p0_zero_shot_fitness.metrics import summarize_records
from p0_zero_shot_fitness.models import Mutation, VariantRecord
from p0_zero_shot_fitness.pipeline import load_external_json, load_position_covariates, load_residue_groups


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes"}


def load_catalytic_residues(path: Path | None) -> set[int] | None:
    if path is None:
        return None
    payload = load_external_json(path)
    return set(payload["catalytic_residues"])


def load_scored_variants(
    path: Path,
    residue_groups: dict[str, set[int]],
    catalytic_residues: set[int] | None = None,
) -> list[VariantRecord]:
    records: list[VariantRecord] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            mutation = Mutation(
                raw=row["variant"],
                wild_type=row["wild_type"],
                position=int(row["position"]),
                mutant=row["mutant"],
            )
            row_groups = {
                group_name
                for group_name in row.get("residue_groups", "").split(";")
                if group_name
            }
            computed_groups = {
                group_name
                for group_name, positions in residue_groups.items()
                if mutation.position in positions
            }
            final_groups = computed_groups if residue_groups else row_groups
            records.append(
                VariantRecord(
                    mutation=mutation,
                    fitness=float(row["fitness"]),
                    is_catalytic=(
                        mutation.position in catalytic_residues
                        if catalytic_residues is not None
                        else parse_bool(row["is_catalytic"])
                    ),
                    model_score=float(row["model_score"]),
                    residue_groups=frozenset(final_groups),
                )
            )
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh P0 metrics from an existing scored_variants.csv.")
    parser.add_argument("--metrics-json", type=Path, required=True)
    parser.add_argument("--scored-variants-csv", type=Path, required=True)
    parser.add_argument("--catalytic-json", type=Path, default=None)
    parser.add_argument("--residue-groups-json", type=Path, default=None)
    parser.add_argument("--position-covariates-json", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--rewrite-scored-variants", action="store_true")
    parser.add_argument("--bootstrap-iterations", type=int, default=0)
    parser.add_argument("--bootstrap-seed", type=int, default=13)
    parser.add_argument("--null-iterations", type=int, default=0)
    parser.add_argument("--null-seed", type=int, default=2026)
    parser.add_argument("--covariate-null-iterations", type=int, default=0)
    parser.add_argument("--covariate-null-seed", type=int, default=707)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.metrics_json.read_text(encoding="utf-8"))
    residue_groups = load_residue_groups(args.residue_groups_json)
    position_covariates = load_position_covariates(args.position_covariates_json)
    catalytic_residues = load_catalytic_residues(args.catalytic_json)
    records = load_scored_variants(args.scored_variants_csv, residue_groups, catalytic_residues)
    payload["metrics"] = summarize_records(
        records,
        bootstrap_iterations=args.bootstrap_iterations,
        bootstrap_seed=args.bootstrap_seed,
        null_iterations=args.null_iterations,
        null_seed=args.null_seed,
        position_covariates=position_covariates,
        covariate_null_iterations=args.covariate_null_iterations,
        covariate_null_seed=args.covariate_null_seed,
    )
    payload.setdefault("input_files", {})["residue_groups_json"] = (
        str(args.residue_groups_json) if args.residue_groups_json else None
    )
    if args.catalytic_json:
        payload.setdefault("input_files", {})["catalytic_json"] = str(args.catalytic_json)
    if args.position_covariates_json:
        payload.setdefault("input_files", {})["position_covariates_json"] = str(args.position_covariates_json)

    output_json = args.output_json or args.metrics_json
    write_json(output_json, payload)
    if args.rewrite_scored_variants:
        write_scored_variants(args.scored_variants_csv, records)
    if not args.quiet:
        print(json.dumps(payload["metrics"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
