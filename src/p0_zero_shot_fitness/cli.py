from __future__ import annotations

import argparse
import json
from pathlib import Path

from p0_zero_shot_fitness.pipeline import (
    run_external_benchmark,
    run_fixture_benchmark,
    run_proteingym_amie_benchmark,
    run_proteingym_bgly_benchmark,
    run_proteingym_blat_benchmark,
    run_proteingym_vim2_benchmark,
)
from p0_zero_shot_fitness.scorers import ESM2MaskedMarginalScorer, PlaceholderConservationScorer, VariantScorer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the P0 zero-shot protein fitness benchmark fixture pipeline."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results"),
        help="Directory for metrics, scored variants, and plots.",
    )
    parser.add_argument(
        "--preset",
        choices=[
            "fixture",
            "proteingym-blat",
            "proteingym-vim2",
            "proteingym-amie",
            "proteingym-bgly",
            "external",
        ],
        default="fixture",
        help="Benchmark preset to run.",
    )
    parser.add_argument("--dms-csv", type=Path, default=None, help="External DMS CSV path.")
    parser.add_argument("--wild-type-fasta", type=Path, default=None, help="External FASTA path.")
    parser.add_argument("--catalytic-json", type=Path, default=None, help="External catalytic-residue JSON path.")
    parser.add_argument("--residue-groups-json", type=Path, default=None, help="Optional external residue-group JSON path.")
    parser.add_argument("--position-covariates-json", type=Path, default=None, help="Optional per-position covariate JSON path.")
    parser.add_argument("--dataset-name", default="external dataset", help="Name for external dataset metadata.")
    parser.add_argument("--variant-column", default="mutant", help="Variant column for external CSV.")
    parser.add_argument("--fitness-column", default="DMS_score", help="Fitness column for external CSV.")
    parser.add_argument("--include-multiple-mutants", action="store_true", help="Do not filter variants containing ':'.")
    parser.add_argument(
        "--scorer",
        choices=["placeholder", "esm2"],
        default="placeholder",
        help="Variant scorer to use.",
    )
    parser.add_argument("--esm-model", default="esm2_t6_8M_UR50D", help="fair-esm pretrained model function name.")
    parser.add_argument("--device", default="cpu", help="Torch device for ESM scoring.")
    parser.add_argument(
        "--bootstrap-iterations",
        type=int,
        default=0,
        help="Add bootstrap confidence intervals for Spearman metrics.",
    )
    parser.add_argument("--bootstrap-seed", type=int, default=13, help="Random seed for bootstrap intervals.")
    parser.add_argument(
        "--null-iterations",
        type=int,
        default=0,
        help="Add residue-position-matched null controls for catalytic and residue-group slices.",
    )
    parser.add_argument("--null-seed", type=int, default=2026, help="Random seed for matched-position null controls.")
    parser.add_argument(
        "--covariate-null-iterations",
        type=int,
        default=0,
        help="Add covariate-matched null controls for catalytic and residue-group slices.",
    )
    parser.add_argument("--covariate-null-seed", type=int, default=707, help="Random seed for covariate-matched controls.")
    return parser


def build_scorer(args: argparse.Namespace) -> VariantScorer:
    if args.scorer == "placeholder":
        return PlaceholderConservationScorer()
    return ESM2MaskedMarginalScorer(model_name=args.esm_model, device=args.device)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    scorer = build_scorer(args)
    if args.preset == "fixture":
        payload = run_fixture_benchmark(
            args.output_dir,
            scorer=scorer,
            null_iterations=args.null_iterations,
            null_seed=args.null_seed,
            position_covariates_json=args.position_covariates_json,
            covariate_null_iterations=args.covariate_null_iterations,
            covariate_null_seed=args.covariate_null_seed,
        )
    elif args.preset == "proteingym-blat":
        payload = run_proteingym_blat_benchmark(
            args.output_dir,
            scorer=scorer,
            bootstrap_iterations=args.bootstrap_iterations,
            bootstrap_seed=args.bootstrap_seed,
            null_iterations=args.null_iterations,
            null_seed=args.null_seed,
            position_covariates_json=args.position_covariates_json,
            covariate_null_iterations=args.covariate_null_iterations,
            covariate_null_seed=args.covariate_null_seed,
        )
    elif args.preset == "proteingym-vim2":
        payload = run_proteingym_vim2_benchmark(
            args.output_dir,
            scorer=scorer,
            bootstrap_iterations=args.bootstrap_iterations,
            bootstrap_seed=args.bootstrap_seed,
            null_iterations=args.null_iterations,
            null_seed=args.null_seed,
            position_covariates_json=args.position_covariates_json,
            covariate_null_iterations=args.covariate_null_iterations,
            covariate_null_seed=args.covariate_null_seed,
        )
    elif args.preset == "proteingym-amie":
        payload = run_proteingym_amie_benchmark(
            args.output_dir,
            scorer=scorer,
            bootstrap_iterations=args.bootstrap_iterations,
            bootstrap_seed=args.bootstrap_seed,
            null_iterations=args.null_iterations,
            null_seed=args.null_seed,
            position_covariates_json=args.position_covariates_json,
            covariate_null_iterations=args.covariate_null_iterations,
            covariate_null_seed=args.covariate_null_seed,
        )
    elif args.preset == "proteingym-bgly":
        payload = run_proteingym_bgly_benchmark(
            args.output_dir,
            scorer=scorer,
            bootstrap_iterations=args.bootstrap_iterations,
            bootstrap_seed=args.bootstrap_seed,
            null_iterations=args.null_iterations,
            null_seed=args.null_seed,
            position_covariates_json=args.position_covariates_json,
            covariate_null_iterations=args.covariate_null_iterations,
            covariate_null_seed=args.covariate_null_seed,
        )
    else:
        required = [args.dms_csv, args.wild_type_fasta, args.catalytic_json]
        if any(path is None for path in required):
            parser.error("--preset external requires --dms-csv, --wild-type-fasta, and --catalytic-json")
        payload = run_external_benchmark(
            output_dir=args.output_dir,
            dms_csv=args.dms_csv,
            wild_type_fasta=args.wild_type_fasta,
            catalytic_json=args.catalytic_json,
            residue_groups_json=args.residue_groups_json,
            dataset_name=args.dataset_name,
            scorer=scorer,
            variant_column=args.variant_column,
            fitness_column=args.fitness_column,
            single_only=not args.include_multiple_mutants,
            bootstrap_iterations=args.bootstrap_iterations,
            bootstrap_seed=args.bootstrap_seed,
            null_iterations=args.null_iterations,
            null_seed=args.null_seed,
            position_covariates_json=args.position_covariates_json,
            covariate_null_iterations=args.covariate_null_iterations,
            covariate_null_seed=args.covariate_null_seed,
        )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
