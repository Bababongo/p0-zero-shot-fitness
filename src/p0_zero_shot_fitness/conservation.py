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
    sequences = normalized_alignment_sequences(alignment_text)
    query_sequence = sequences[0]
    ungapped_query_length = sum(character != "-" for character in query_sequence)
    if ungapped_query_length != len(wild_type_sequence):
        raise ValueError(
            "The first MSA sequence must align to the wild-type sequence length "
            f"after removing gaps: got {ungapped_query_length}, expected {len(wild_type_sequence)}."
        )

    covariates: dict[str, dict[str, float]] = {}
    aa_frequencies: dict[str, dict[str, float]] = {}
    wild_type_position = 0
    for column_index, query_residue in enumerate(query_sequence):
        if query_residue == "-":
            continue
        wild_type_position += 1
        column = [sequence[column_index] for sequence in sequences]
        frequencies = amino_acid_frequencies(column, pseudocount=pseudocount)
        entropy = normalized_entropy(frequencies)
        wild_type_residue = wild_type_sequence[wild_type_position - 1]
        wild_type_frequency = frequencies.get(wild_type_residue, 0.0)
        covariates[str(wild_type_position)] = {
            "msa_wild_type_frequency": wild_type_frequency,
            "msa_normalized_entropy": entropy,
            "msa_conservation": 1.0 - entropy,
        }
        aa_frequencies[str(wild_type_position)] = frequencies

    return {
        "alignment_records": len(sequences),
        "alignment_length": len(query_sequence),
        "wild_type_length": len(wild_type_sequence),
        "pseudocount": pseudocount,
        "notes": {
            "msa_wild_type_frequency": "Frequency of the wild-type amino acid at this alignment column.",
            "msa_normalized_entropy": "Shannon entropy over amino-acid frequencies, normalized by log(20).",
            "msa_conservation": "One minus normalized entropy; higher means more conserved.",
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
