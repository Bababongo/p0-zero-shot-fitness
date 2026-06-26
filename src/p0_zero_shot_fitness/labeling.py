from __future__ import annotations

from p0_zero_shot_fitness.models import Mutation


def is_catalytic_mutation(mutation: Mutation, catalytic_residues: set[int]) -> bool:
    return mutation.position in catalytic_residues


def residue_groups_for_mutation(
    mutation: Mutation,
    residue_groups: dict[str, set[int]],
) -> frozenset[str]:
    return frozenset(
        group_name
        for group_name, positions in residue_groups.items()
        if mutation.position in positions
    )
