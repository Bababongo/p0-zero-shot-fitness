"""Follow one TEM-1 mutation through the P0 analysis pipeline.

Run from the repository root:

    PYTHONPATH=src python examples/beginner_walkthrough.py

This example uses the fast placeholder scorer so it does not need PyTorch or
ESM model weights. The production pipeline can swap in ESM-2 without changing
the data-loading, labeling, or metrics code.
"""

from pathlib import Path

from p0_zero_shot_fitness.io import load_dms_csv_path, read_fasta_sequence
from p0_zero_shot_fitness.labeling import (
    is_catalytic_mutation,
    residue_groups_for_mutation,
)
from p0_zero_shot_fitness.metrics import summarize_records
from p0_zero_shot_fitness.mutations import parse_mutation
from p0_zero_shot_fitness.pipeline import (
    build_variant_records,
    load_external_json,
    load_residue_groups,
)
from p0_zero_shot_fitness.scorers import PlaceholderConservationScorer


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "proteingym"


def main() -> None:
    # Step 1: load the wild-type sequence and experimental DMS table.
    fasta_text = (DATA_DIR / "BLAT_ECOLX.fasta").read_text(encoding="utf-8")
    wild_type_sequence = read_fasta_sequence(fasta_text)
    dms_rows = load_dms_csv_path(DATA_DIR / "BLAT_ECOLX_Firnberg_2014.csv")

    # Step 2: load biological labels derived from UniProt and PDB.
    catalytic_payload = load_external_json(
        DATA_DIR / "BLAT_ECOLX_catalytic_residues.json"
    )
    catalytic_residues = set(catalytic_payload["catalytic_residues"])
    residue_groups = load_residue_groups(
        DATA_DIR / "BLAT_ECOLX_residue_groups.json"
    )

    # Step 3: inspect one catalytic mutation by hand.
    row = next(row for row in dms_rows if row["mutant"] == "H24S")
    mutation = parse_mutation(row["mutant"], wild_type_sequence)
    scorer = PlaceholderConservationScorer()
    model_score = scorer.score(mutation, wild_type_sequence)
    groups = residue_groups_for_mutation(mutation, residue_groups)

    print("ONE MUTATION")
    print(f"Mutation: {mutation.raw}")
    print(f"Experimental fitness: {float(row['DMS_score'])}")
    print(f"Placeholder model score: {model_score}")
    print(f"Is catalytic: {is_catalytic_mutation(mutation, catalytic_residues)}")
    print(f"Residue groups: {', '.join(sorted(groups))}")

    # Step 4: let the real pipeline repeat those operations for all variants.
    records = build_variant_records(
        dms_rows=dms_rows,
        wild_type_sequence=wild_type_sequence,
        catalytic_residues=catalytic_residues,
        scorer=scorer,
        residue_groups=residue_groups,
        variant_column="mutant",
        fitness_column="DMS_score",
    )

    # Step 5: summarize agreement between model rankings and experiment.
    metrics = summarize_records(records)
    print("\nWHOLE DATASET")
    print(f"Variants analyzed: {metrics['n_variants']}")
    print(f"Catalytic variants: {metrics['n_catalytic']}")
    print(f"Overall Spearman: {metrics['spearman_overall']:.4f}")
    print(f"Catalytic Spearman: {metrics['spearman_catalytic']:.4f}")
    print(f"Non-catalytic Spearman: {metrics['spearman_non_catalytic']:.4f}")


if __name__ == "__main__":
    main()
