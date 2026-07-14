from __future__ import annotations

import json
import math
from pathlib import Path

from p0_zero_shot_fitness.models import Mutation


AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"


def read_alignment_records(text: str) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    current_name: str | None = None
    current_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current_name is not None:
                records.append((current_name, "".join(current_lines)))
            current_name = line[1:].strip() or f"sequence_{len(records) + 1}"
            current_lines = []
        else:
            current_lines.append(line)
    if current_name is not None:
        records.append((current_name, "".join(current_lines)))
    return records


def normalize_a2m_sequence(sequence: str) -> str:
    """Remove A2M insert columns and keep match-state residues/gaps."""
    normalized = []
    for character in sequence:
        if character == "." or character.islower():
            continue
        normalized.append(character.upper())
    return "".join(normalized)


def normalized_alignment_sequences(alignment_text: str) -> list[str]:
    records = read_alignment_records(alignment_text)
    sequences = [normalize_a2m_sequence(sequence) for _, sequence in records]
    if not sequences:
        raise ValueError("MSA file did not contain any FASTA/A2M records.")
    lengths = {len(sequence) for sequence in sequences}
    if len(lengths) != 1:
        raise ValueError("Normalized alignment sequences must all have the same length.")
    return sequences


def amino_acid_frequencies(column: list[str], pseudocount: float = 0.5) -> dict[str, float]:
    counts = {amino_acid: 0 for amino_acid in AMINO_ACIDS}
    observed = 0
    for residue in column:
        if residue in counts:
            counts[residue] += 1
            observed += 1
    denominator = observed + pseudocount * len(AMINO_ACIDS)
    return {
        amino_acid: (counts[amino_acid] + pseudocount) / denominator
        for amino_acid in AMINO_ACIDS
    }


def normalized_entropy(frequencies: dict[str, float]) -> float:
    entropy = -sum(frequency * math.log(frequency) for frequency in frequencies.values() if frequency > 0)
    return entropy / math.log(len(AMINO_ACIDS))


def derive_conservation_profile(
    alignment_text: str,
    wild_type_sequence: str,
    pseudocount: float = 0.5,
) -> dict[str, object]:
    records = read_alignment_records(alignment_text)
    if not records:
        raise ValueError("MSA file did not contain any FASTA/A2M records.")
    sequences = [normalize_a2m_sequence(sequence) for _, sequence in records]
    lengths = {len(sequence) for sequence in sequences}
    if len(lengths) != 1:
        raise ValueError("Normalized alignment sequences must all have the same length.")
    query_record_sequence = records[0][1]
    query_sequence = sequences[0]
    ungapped_query = "".join(
        character.upper()
        for character in query_record_sequence
        if character not in {"-", "."}
    )
    if ungapped_query != wild_type_sequence:
        raise ValueError(
            "The first MSA sequence must match the wild-type sequence after removing gaps "
            "and A2M dot placeholders."
        )

    covariates: dict[str, dict[str, float]] = {}
    aa_frequencies: dict[str, dict[str, float]] = {}
    covered_positions = 0
    match_column_index = 0
    wild_type_position = 0
    for query_residue in query_record_sequence:
        if query_residue == ".":
            continue
        if query_residue == "-":
            match_column_index += 1
            continue

        wild_type_position += 1
        wild_type_residue = wild_type_sequence[wild_type_position - 1]
        if query_residue.islower():
            frequencies = amino_acid_frequencies([], pseudocount=pseudocount)
            match_state_coverage = 0.0
            match_column = None
        else:
            column = [sequence[match_column_index] for sequence in sequences]
            frequencies = amino_acid_frequencies(column, pseudocount=pseudocount)
            match_state_coverage = 1.0
            match_column = match_column_index + 1
            covered_positions += 1
            match_column_index += 1
        entropy = normalized_entropy(frequencies)
        wild_type_frequency = frequencies.get(wild_type_residue, 0.0)
        covariates[str(wild_type_position)] = {
            "msa_wild_type_frequency": wild_type_frequency,
            "msa_normalized_entropy": entropy,
            "msa_conservation": 1.0 - entropy,
            "msa_match_state_coverage": match_state_coverage,
        }
        if match_column is not None:
            covariates[str(wild_type_position)]["msa_match_column"] = float(match_column)
        aa_frequencies[str(wild_type_position)] = frequencies
    if wild_type_position != len(wild_type_sequence):
        raise ValueError(
            "The first MSA sequence did not map onto every wild-type position: "
            f"mapped {wild_type_position}, expected {len(wild_type_sequence)}."
        )
    if match_column_index != len(query_sequence):
        raise ValueError(
            "The first MSA sequence did not consume every normalized match column: "
            f"used {match_column_index}, expected {len(query_sequence)}."
        )

    return {
        "alignment_records": len(sequences),
        "alignment_length": len(query_sequence),
        "wild_type_length": len(wild_type_sequence),
        "covered_wild_type_positions": covered_positions,
        "uncovered_wild_type_positions": len(wild_type_sequence) - covered_positions,
        "match_state_coverage_fraction": covered_positions / len(wild_type_sequence),
        "pseudocount": pseudocount,
        "notes": {
            "msa_wild_type_frequency": "Frequency of the wild-type amino acid at this alignment column.",
            "msa_normalized_entropy": "Shannon entropy over amino-acid frequencies, normalized by log(20).",
            "msa_conservation": "One minus normalized entropy; higher means more conserved.",
            "msa_match_state_coverage": "1.0 if the wild-type residue is represented by an MSA match-state column; 0.0 if it is lowercase/query-only in the A2M and receives a neutral uniform baseline.",
        },
        "covariates": covariates,
        "aa_frequencies": aa_frequencies,
    }


def load_conservation_profile(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def conservation_log_odds_score(mutation: Mutation, profile: dict[str, object]) -> float:
    aa_frequencies = profile["aa_frequencies"]
    if not isinstance(aa_frequencies, dict):
        raise ValueError("Conservation profile is missing aa_frequencies.")
    position_frequencies = aa_frequencies[str(mutation.position)]
    if not isinstance(position_frequencies, dict):
        raise ValueError(f"Conservation profile is missing position {mutation.position}.")
    wild_type_frequency = float(position_frequencies.get(mutation.wild_type, 1e-12))
    mutant_frequency = float(position_frequencies.get(mutation.mutant, 1e-12))
    return math.log(mutant_frequency) - math.log(wild_type_frequency)
