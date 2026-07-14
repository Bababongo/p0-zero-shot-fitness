from __future__ import annotations

from pathlib import Path

from p0_zero_shot_fitness.io import (
    load_dms_csv_path,
    load_dms_csv_text,
    load_fixture_json,
    load_fixture_text,
    read_fasta_sequence,
    write_json,
    write_scored_variants,
)
from p0_zero_shot_fitness.labeling import is_catalytic_mutation, residue_groups_for_mutation
from p0_zero_shot_fitness.metrics import summarize_records
from p0_zero_shot_fitness.models import JsonDict, VariantRecord
from p0_zero_shot_fitness.mutations import parse_mutation
from p0_zero_shot_fitness.plotting.svg import write_scatter_svg
from p0_zero_shot_fitness.scorers import PlaceholderConservationScorer, VariantScorer


def build_variant_records(
    dms_rows: list[dict[str, str]],
    wild_type_sequence: str,
    catalytic_residues: set[int],
    scorer: VariantScorer,
    residue_groups: dict[str, set[int]] | None = None,
    variant_column: str = "variant",
    fitness_column: str = "fitness",
    single_only: bool = True,
) -> list[VariantRecord]:
    residue_groups = residue_groups or {}
    records = []
    for row in dms_rows:
        variant = row[variant_column]
        if single_only and ":" in variant:
            continue
        mutation = parse_mutation(variant, wild_type_sequence)
        records.append(
            VariantRecord(
                mutation=mutation,
                fitness=float(row[fitness_column]),
                is_catalytic=is_catalytic_mutation(mutation, catalytic_residues),
                model_score=scorer.score(mutation, wild_type_sequence),
                residue_groups=residue_groups_for_mutation(mutation, residue_groups),
            )
        )
    return records


def run_fixture_benchmark(
    output_dir: Path,
    scorer: VariantScorer | None = None,
    null_iterations: int = 0,
    null_seed: int = 2026,
) -> JsonDict:
    scorer = scorer or PlaceholderConservationScorer()
    wild_type_sequence = read_fasta_sequence(load_fixture_text("wild_type.fasta"))
    catalytic_payload = load_fixture_json("catalytic_residues.json")
    catalytic_residues = set(catalytic_payload["catalytic_residues"])
    dms_rows = load_dms_csv_text(load_fixture_text("dms_fixture.csv"))

    records = build_variant_records(
        dms_rows=dms_rows,
        wild_type_sequence=wild_type_sequence,
        catalytic_residues=catalytic_residues,
        scorer=scorer,
    )
    metrics = summarize_records(records, null_iterations=null_iterations, null_seed=null_seed)
    payload = {
        "benchmark": "P0 - Zero-Shot Fitness",
        "question": "Do protein language models fail differently on catalytic residues than on the rest of the protein?",
        "scorer": scorer.__class__.__name__,
        "data_scope": "Synthetic fixture data for pipeline development",
        "metrics": metrics,
        "artifacts": {
            "scored_variants_csv": "scored_variants.csv",
            "fitness_scatter_svg": "fitness_scatter.svg",
        },
    }

    write_json(output_dir / "metrics.json", payload)
    write_scored_variants(output_dir / "scored_variants.csv", records)
    write_scatter_svg(output_dir / "fitness_scatter.svg", records)
    return payload


def run_external_benchmark(
    output_dir: Path,
    dms_csv: Path,
    wild_type_fasta: Path,
    catalytic_json: Path,
    dataset_name: str,
    scorer: VariantScorer | None = None,
    residue_groups_json: Path | None = None,
    variant_column: str = "mutant",
    fitness_column: str = "DMS_score",
    single_only: bool = True,
    bootstrap_iterations: int = 0,
    bootstrap_seed: int = 13,
    null_iterations: int = 0,
    null_seed: int = 2026,
) -> JsonDict:
    scorer = scorer or PlaceholderConservationScorer()
    wild_type_sequence = read_fasta_sequence(wild_type_fasta.read_text(encoding="utf-8"))
    catalytic_payload = load_external_json(catalytic_json)
    catalytic_residues = set(catalytic_payload["catalytic_residues"])
    residue_groups = load_residue_groups(residue_groups_json)
    dms_rows = load_dms_csv_path(dms_csv)

    records = build_variant_records(
        dms_rows=dms_rows,
        wild_type_sequence=wild_type_sequence,
        catalytic_residues=catalytic_residues,
        scorer=scorer,
        residue_groups=residue_groups,
        variant_column=variant_column,
        fitness_column=fitness_column,
        single_only=single_only,
    )
    metrics = summarize_records(
        records,
        bootstrap_iterations=bootstrap_iterations,
        bootstrap_seed=bootstrap_seed,
        null_iterations=null_iterations,
        null_seed=null_seed,
    )
    payload = {
        "benchmark": "P0 - Zero-Shot Fitness",
        "question": "Do protein language models fail differently on catalytic residues than on the rest of the protein?",
        "dataset": dataset_name,
        "scorer": scorer.__class__.__name__,
        "data_scope": "External DMS dataset",
        "input_files": {
            "dms_csv": str(dms_csv),
            "wild_type_fasta": str(wild_type_fasta),
            "catalytic_json": str(catalytic_json),
            "residue_groups_json": str(residue_groups_json) if residue_groups_json else None,
        },
        "metrics": metrics,
        "artifacts": {
            "scored_variants_csv": "scored_variants.csv",
            "fitness_scatter_svg": "fitness_scatter.svg",
        },
    }

    write_json(output_dir / "metrics.json", payload)
    write_scored_variants(output_dir / "scored_variants.csv", records)
    write_scatter_svg(output_dir / "fitness_scatter.svg", records)
    return payload


def load_external_json(path: Path) -> JsonDict:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def load_residue_groups(path: Path | None) -> dict[str, set[int]]:
    if path is None:
        return {}
    payload = load_external_json(path)
    return {
        group_name: set(positions)
        for group_name, positions in payload.get("residue_groups", {}).items()
    }


def run_proteingym_blat_benchmark(
    output_dir: Path,
    scorer: VariantScorer | None = None,
    bootstrap_iterations: int = 0,
    bootstrap_seed: int = 13,
    null_iterations: int = 0,
    null_seed: int = 2026,
) -> JsonDict:
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "data" / "proteingym"
    return run_external_benchmark(
        output_dir=output_dir,
        dms_csv=data_dir / "BLAT_ECOLX_Firnberg_2014.csv",
        wild_type_fasta=data_dir / "BLAT_ECOLX.fasta",
        catalytic_json=data_dir / "BLAT_ECOLX_catalytic_residues.json",
        residue_groups_json=data_dir / "BLAT_ECOLX_residue_groups.json",
        dataset_name="ProteinGym BLAT_ECOLX_Firnberg_2014",
        scorer=scorer,
        variant_column="mutant",
        fitness_column="DMS_score",
        single_only=True,
        bootstrap_iterations=bootstrap_iterations,
        bootstrap_seed=bootstrap_seed,
        null_iterations=null_iterations,
        null_seed=null_seed,
    )


def run_proteingym_vim2_benchmark(
    output_dir: Path,
    scorer: VariantScorer | None = None,
    bootstrap_iterations: int = 0,
    bootstrap_seed: int = 13,
    null_iterations: int = 0,
    null_seed: int = 2026,
) -> JsonDict:
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "data" / "proteingym"
    return run_external_benchmark(
        output_dir=output_dir,
        dms_csv=data_dir / "A4GRB6_PSEAI_Chen_2020.csv",
        wild_type_fasta=data_dir / "A4GRB6_PSEAI.fasta",
        catalytic_json=data_dir / "A4GRB6_PSEAI_catalytic_residues.json",
        residue_groups_json=data_dir / "A4GRB6_PSEAI_residue_groups.json",
        dataset_name="ProteinGym A4GRB6_PSEAI_Chen_2020",
        scorer=scorer,
        variant_column="mutant",
        fitness_column="DMS_score",
        single_only=True,
        bootstrap_iterations=bootstrap_iterations,
        bootstrap_seed=bootstrap_seed,
        null_iterations=null_iterations,
        null_seed=null_seed,
    )


def run_proteingym_amie_benchmark(
    output_dir: Path,
    scorer: VariantScorer | None = None,
    bootstrap_iterations: int = 0,
    bootstrap_seed: int = 13,
    null_iterations: int = 0,
    null_seed: int = 2026,
) -> JsonDict:
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "data" / "proteingym"
    return run_external_benchmark(
        output_dir=output_dir,
        dms_csv=data_dir / "AMIE_PSEAE_Wrenbeck_2017.csv",
        wild_type_fasta=data_dir / "AMIE_PSEAE.fasta",
        catalytic_json=data_dir / "AMIE_PSEAE_catalytic_residues.json",
        residue_groups_json=data_dir / "AMIE_PSEAE_residue_groups.json",
        dataset_name="ProteinGym AMIE_PSEAE_Wrenbeck_2017",
        scorer=scorer,
        variant_column="mutant",
        fitness_column="DMS_score",
        single_only=True,
        bootstrap_iterations=bootstrap_iterations,
        bootstrap_seed=bootstrap_seed,
        null_iterations=null_iterations,
        null_seed=null_seed,
    )


def run_proteingym_bgly_benchmark(
    output_dir: Path,
    scorer: VariantScorer | None = None,
    bootstrap_iterations: int = 0,
    bootstrap_seed: int = 13,
    null_iterations: int = 0,
    null_seed: int = 2026,
) -> JsonDict:
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "data" / "proteingym"
    return run_external_benchmark(
        output_dir=output_dir,
        dms_csv=data_dir / "Q59976_STRSQ_Romero_2015.csv",
        wild_type_fasta=data_dir / "Q59976_STRSQ.fasta",
        catalytic_json=data_dir / "Q59976_STRSQ_catalytic_residues.json",
        residue_groups_json=data_dir / "Q59976_STRSQ_residue_groups.json",
        dataset_name="ProteinGym Q59976_STRSQ_Romero_2015",
        scorer=scorer,
        variant_column="mutant",
        fitness_column="DMS_score",
        single_only=True,
        bootstrap_iterations=bootstrap_iterations,
        bootstrap_seed=bootstrap_seed,
        null_iterations=null_iterations,
        null_seed=null_seed,
    )
