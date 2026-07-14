from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p0_zero_shot_fitness.io import read_fasta_sequence, write_json


PROTEINMPNN_ALPHABET = "ACDEFGHIKLMNPQRSTVWYX"
P0_AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"


def log_mean_exp(values: np.ndarray, axis: int = 0) -> np.ndarray:
    max_values = np.max(values, axis=axis, keepdims=True)
    return np.squeeze(max_values, axis=axis) + np.log(
        np.mean(np.exp(values - max_values), axis=axis)
    )


def sequence_from_indices(indices: np.ndarray) -> str:
    return "".join(PROTEINMPNN_ALPHABET[int(index)] for index in indices)


def load_log_probabilities(npz: np.lib.npyio.NpzFile) -> tuple[np.ndarray, str]:
    if "log_p" in npz:
        return np.asarray(npz["log_p"], dtype=float), "log_p"
    if "log_probs" in npz:
        return np.asarray(npz["log_probs"], dtype=float), "log_probs"
    if "probs" in npz:
        probabilities = np.asarray(npz["probs"], dtype=float)
        if np.any(probabilities <= 0):
            raise ValueError("ProteinMPNN probs array contains non-positive values.")
        return np.log(probabilities), "probs"
    raise ValueError("ProteinMPNN NPZ must contain one of: log_p, log_probs, probs.")


def build_profile(
    proteinmpnn_npz: Path,
    wild_type_fasta: Path,
    scorer_name: str,
    protein: str | None,
    structure: str | None,
    chain: str,
    source_mode: str,
    allow_sequence_mismatch: bool = False,
) -> dict[str, object]:
    wild_type_sequence = read_fasta_sequence(wild_type_fasta.read_text(encoding="utf-8"))
    with np.load(proteinmpnn_npz, allow_pickle=True) as npz:
        log_probabilities, source_key = load_log_probabilities(npz)
        if log_probabilities.ndim == 2:
            log_probabilities = log_probabilities[None, :, :]
        if log_probabilities.ndim != 3:
            raise ValueError(
                "ProteinMPNN log probability array must have shape [batch, length, alphabet]."
            )
        if log_probabilities.shape[2] < len(P0_AMINO_ACIDS):
            raise ValueError("ProteinMPNN alphabet dimension is smaller than 20 amino acids.")

        batch_count, structure_length, alphabet_size = log_probabilities.shape
        if structure_length != len(wild_type_sequence):
            raise ValueError(
                "ProteinMPNN profile length does not match FASTA length: "
                f"{structure_length} vs {len(wild_type_sequence)}."
            )

        sequence_from_npz = None
        if "S" in npz:
            raw_sequence_indices = np.asarray(npz["S"])
            if raw_sequence_indices.ndim > 1:
                raw_sequence_indices = raw_sequence_indices[0]
            sequence_from_npz = sequence_from_indices(raw_sequence_indices[:structure_length])
            if sequence_from_npz != wild_type_sequence and not allow_sequence_mismatch:
                raise ValueError(
                    "ProteinMPNN native sequence in NPZ does not match FASTA sequence. "
                    "Use --allow-sequence-mismatch only after confirming the profile is correctly remapped."
                )

        design_mask = None
        if "design_mask" in npz:
            design_mask = np.asarray(npz["design_mask"]).astype(float).tolist()

        mean_log_probabilities = log_mean_exp(log_probabilities, axis=0)
        positions = {}
        for position, wild_type_residue in enumerate(wild_type_sequence, start=1):
            positions[str(position)] = {
                "wild_type": wild_type_residue,
                "log_probabilities": {
                    amino_acid: float(mean_log_probabilities[position - 1, aa_index])
                    for aa_index, amino_acid in enumerate(P0_AMINO_ACIDS)
                },
            }

    return {
        "format": "p0_structure_log_probability_profile.v1",
        "scorer": scorer_name,
        "protein": protein,
        "structure": structure,
        "chain": chain,
        "source": "ProteinMPNN NPZ",
        "source_mode": source_mode,
        "source_npz": str(proteinmpnn_npz),
        "source_key": source_key,
        "wild_type_fasta": str(wild_type_fasta),
        "wild_type_length": len(wild_type_sequence),
        "proteinmpnn_alphabet": PROTEINMPNN_ALPHABET,
        "p0_amino_acids": P0_AMINO_ACIDS,
        "aggregation": "log-mean-exp across ProteinMPNN batches",
        "batch_count": int(batch_count),
        "structure_length": int(structure_length),
        "alphabet_size": int(alphabet_size),
        "sequence_from_npz_matches_fasta": sequence_from_npz == wild_type_sequence
        if sequence_from_npz is not None
        else None,
        "design_mask": design_mask,
        "positions": positions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert ProteinMPNN probability NPZ output into a P0 structure-profile JSON."
    )
    parser.add_argument("--proteinmpnn-npz", type=Path, required=True)
    parser.add_argument("--wild-type-fasta", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--scorer-name", default="ProteinMPNNProfileScorer")
    parser.add_argument("--protein", default=None)
    parser.add_argument("--structure", default=None)
    parser.add_argument("--chain", default="A")
    parser.add_argument(
        "--source-mode",
        choices=["unconditional_probs_only", "conditional_probs_only", "save_probs"],
        default="unconditional_probs_only",
    )
    parser.add_argument(
        "--allow-sequence-mismatch",
        action="store_true",
        help="Allow NPZ S indices to disagree with FASTA after an external remapping check.",
    )
    args = parser.parse_args()

    profile = build_profile(
        proteinmpnn_npz=args.proteinmpnn_npz,
        wild_type_fasta=args.wild_type_fasta,
        scorer_name=args.scorer_name,
        protein=args.protein,
        structure=args.structure,
        chain=args.chain,
        source_mode=args.source_mode,
        allow_sequence_mismatch=args.allow_sequence_mismatch,
    )
    write_json(args.output_json, profile)
    print(
        json.dumps(
            {
                "output_json": str(args.output_json),
                "positions": len(profile["positions"]),
                "batch_count": profile["batch_count"],
                "sequence_from_npz_matches_fasta": profile["sequence_from_npz_matches_fasta"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
