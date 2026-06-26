from __future__ import annotations

import re

from p0_zero_shot_fitness.models import Mutation

MUTATION_PATTERN = re.compile(r"^(?P<wt>[A-Z])(?P<position>[1-9][0-9]*)(?P<mutant>[A-Z])$")


def parse_mutation(raw_mutation: str, wild_type_sequence: str) -> Mutation:
    normalized = raw_mutation.strip().upper()
    sequence = wild_type_sequence.strip().upper()
    match = MUTATION_PATTERN.match(normalized)
    if not match:
        raise ValueError(f"Mutation must look like A23G: {raw_mutation}")

    wild_type = match.group("wt")
    position = int(match.group("position"))
    mutant = match.group("mutant")
    if position > len(sequence):
        raise ValueError(
            f"Mutation {raw_mutation} position {position} exceeds sequence length {len(sequence)}."
        )

    observed = sequence[position - 1]
    if observed != wild_type:
        raise ValueError(
            f"Mutation {raw_mutation} expects {wild_type} at position {position}, observed {observed}."
        )

    return Mutation(
        raw=normalized,
        wild_type=wild_type,
        position=position,
        mutant=mutant,
    )
