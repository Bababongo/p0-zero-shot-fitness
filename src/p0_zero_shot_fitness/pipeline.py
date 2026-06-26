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
from p0_zero_shot_fitness.labeling import is_catalytic_mutation
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
    variant_column: str = "variant",
    fitness_column: str = "fitness",
    single_only: bool = True,
) -> list[VariantRecord]:
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
            )
        )
    return records


def run_fixture_benchmark(output_dir: Path, scorer: VariantScorer | None = None) -> JsonDict:
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
    metrics = summarize_records(records)
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
    variant_column: str = "mutant",
    fitness_column: str = "DMS_score",
    single_only: bool = True,
) -> JsonDict:
    scorer = scorer or PlaceholderConservationScorer()
    wild_type_sequence = read_fasta_sequence(wild_type_fasta.read_text(encoding="utf-8"))
    catalytic_payload = load_external_json(catalytic_json)
    catalytic_residues = set(catalytic_payload["catalytic_residues"])
    dms_rows = load_dms_csv_path(dms_csv)

    records = build_variant_records(
        dms_rows=dms_rows,
        wild_type_sequence=wild_type_sequence,
        catalytic_residues=catalytic_residues,
        scorer=scorer,
        variant_column=variant_column,
        fitness_column=fitness_column,
        single_only=single_only,
    )
    metrics = summarize_records(records)
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


def run_proteingym_blat_benchmark(output_dir: Path, scorer: VariantScorer | None = None) -> JsonDict:
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "data" / "proteingym"
    return run_external_benchmark(
        output_dir=output_dir,
        dms_csv=data_dir / "BLAT_ECOLX_Firnberg_2014.csv",
        wild_type_fasta=data_dir / "BLAT_ECOLX.fasta",
        catalytic_json=data_dir / "BLAT_ECOLX_catalytic_residues.json",
        dataset_name="ProteinGym BLAT_ECOLX_Firnberg_2014",
        scorer=scorer,
        variant_column="mutant",
        fitness_column="DMS_score",
        single_only=True,
    )
