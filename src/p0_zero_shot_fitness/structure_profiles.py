from __future__ import annotations

import json
import math
from pathlib import Path

from p0_zero_shot_fitness.models import Mutation


AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"


def load_structure_log_probability_profile(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _position_profile(profile: dict[str, object], position: int) -> dict[str, object]:
    raw_positions = profile.get("positions")
    if not isinstance(raw_positions, dict):
        raise ValueError("Structure profile is missing a 'positions' object.")
    raw_position = raw_positions.get(str(position))
    if not isinstance(raw_position, dict):
        raise ValueError(f"Structure profile is missing position {position}.")
    return raw_position


def _log_probabilities(position_profile: dict[str, object]) -> dict[str, float]:
    raw_log_probabilities = position_profile.get("log_probabilities")
    if isinstance(raw_log_probabilities, dict):
        return {
            amino_acid: float(raw_log_probabilities[amino_acid])
            for amino_acid in AMINO_ACIDS
            if amino_acid in raw_log_probabilities
        }

    raw_probabilities = position_profile.get("probabilities")
    if isinstance(raw_probabilities, dict):
        return {
            amino_acid: math.log(float(raw_probabilities[amino_acid]))
            for amino_acid in AMINO_ACIDS
            if amino_acid in raw_probabilities and float(raw_probabilities[amino_acid]) > 0
        }

    raise ValueError("Each structure-profile position needs 'log_probabilities' or 'probabilities'.")


def structure_profile_log_odds_score(mutation: Mutation, profile: dict[str, object]) -> float:
    """Score a mutation as log P(mutant | structure) - log P(wild type | structure).

    This is useful for ProteinMPNN-style fixed-backbone profiles. Higher scores
    mean the mutant residue is more compatible with the backbone relative to the
    wild-type residue under the structure-conditioned model.
    """
    position_profile = _position_profile(profile, mutation.position)
    expected_wild_type = position_profile.get("wild_type")
    if expected_wild_type is not None and str(expected_wild_type) != mutation.wild_type:
        raise ValueError(
            "Structure profile wild type mismatch at "
            f"position {mutation.position}: expected {expected_wild_type}, "
            f"mutation has {mutation.wild_type}."
        )

    log_probabilities = _log_probabilities(position_profile)
    missing = [
        amino_acid
        for amino_acid in (mutation.wild_type, mutation.mutant)
        if amino_acid not in log_probabilities
    ]
    if missing:
        missing_list = ", ".join(sorted(set(missing)))
        raise ValueError(
            f"Structure profile is missing log probabilities for {missing_list} "
            f"at position {mutation.position}."
        )

    return log_probabilities[mutation.mutant] - log_probabilities[mutation.wild_type]
