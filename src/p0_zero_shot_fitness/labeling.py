from __future__ import annotations

from p0_zero_shot_fitness.models import Mutation


def is_catalytic_mutation(mutation: Mutation, catalytic_residues: set[int]) -> bool:
    return mutation.position in catalytic_residues
