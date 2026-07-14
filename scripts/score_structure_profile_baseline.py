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
from p0_zero_shot_fitness.pipeline import load_position_covariates
from p0_zero_shot_fitness.plotting.svg import write_scatter_svg
from p0_zero_shot_fitness.structure_profiles import (
    load_structure_log_probability_profile,
    structure_profile_log_odds_score,
)


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes"}


def load_scored_variants_with_structure_profile_scores(
    scored_variants_csv: Path,
    structure_profile: dict[str, object],
    drop_missing_profile_positions: bool = False,
) -> tuple[list[VariantRecord], list[dict[str, object]]]:
    records: list[VariantRecord] = []
    skipped: list[dict[str, object]] = []
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
            try:
                model_score = structure_profile_log_odds_score(mutation, structure_profile)
            except ValueError as error:
                if drop_missing_profile_positions and "missing position" in str(error):
                    skipped.append(
                        {
                            "variant": mutation.raw,
                            "position": mutation.position,
                            "reason": str(error),
                        }
                    )
                    continue
                raise
            records.append(
                VariantRecord(
                    mutation=mutation,
                    fitness=float(row["fitness"]),
                    is_catalytic=parse_bool(row["is_catalytic"]),
                    model_score=model_score,
                    residue_groups=residue_groups,
                )
            )
    return records, skipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Score a P0 run with a structure-conditioned amino-acid log-probability "
            "profile, such as a ProteinMPNN fixed-backbone profile."
        )
    )
    parser.add_argument("--scored-variants-csv", type=Path, required=True)
    parser.add_argument("--structure-profile-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--scorer-name", default=None)
    parser.add_argument("--position-covariates-json", type=Path, default=None)
    parser.add_argument("--bootstrap-iterations", type=int, default=0)
    parser.add_argument("--bootstrap-seed", type=int, default=13)
    parser.add_argument("--null-iterations", type=int, default=0)
    parser.add_argument("--null-seed", type=int, default=2026)
    parser.add_argument("--covariate-null-iterations", type=int, default=0)
    parser.add_argument("--covariate-null-seed", type=int, default=707)
    parser.add_argument(
        "--drop-missing-profile-positions",
        action="store_true",
        help=(
            "Skip variants whose target position is absent from the structure profile. "
            "Use only for structures with known missing termini or unresolved residues."
        ),
    )
    args = parser.parse_args()

    structure_profile = load_structure_log_probability_profile(args.structure_profile_json)
    scorer_name = args.scorer_name or str(
        structure_profile.get("scorer", "StructureLogProbabilityProfileScorer")
    )
    records, skipped_variants = load_scored_variants_with_structure_profile_scores(
        args.scored_variants_csv,
        structure_profile,
        drop_missing_profile_positions=args.drop_missing_profile_positions,
    )
    position_covariates = load_position_covariates(args.position_covariates_json)
    metrics = summarize_records(
        records,
        bootstrap_iterations=args.bootstrap_iterations,
        bootstrap_seed=args.bootstrap_seed,
        null_iterations=args.null_iterations,
        null_seed=args.null_seed,
        position_covariates=position_covariates,
        covariate_null_iterations=args.covariate_null_iterations,
        covariate_null_seed=args.covariate_null_seed,
    )
    payload = {
        "benchmark": "P0 - Zero-Shot Fitness",
        "question": "Do protein language models fail differently on catalytic residues than on the rest of the protein?",
        "dataset": args.dataset_name,
        "scorer": scorer_name,
        "data_scope": (
            "Structure-conditioned amino-acid log-probability baseline scored "
            "on an existing P0 variant table"
        ),
        "score_definition": "log P(mutant amino acid | backbone) - log P(wild type amino acid | backbone)",
        "input_files": {
            "scored_variants_csv": str(args.scored_variants_csv),
            "structure_profile_json": str(args.structure_profile_json),
            "position_covariates_json": str(args.position_covariates_json)
            if args.position_covariates_json
            else None,
        },
        "skipped_variants": {
            "n": len(skipped_variants),
            "reason": "missing structure-profile positions"
            if skipped_variants
            else None,
            "variants": skipped_variants,
        },
        "structure_profile_metadata": {
            key: value
            for key, value in structure_profile.items()
            if key not in {"positions"}
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
    print(f"Wrote structure-profile baseline to {args.output_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
