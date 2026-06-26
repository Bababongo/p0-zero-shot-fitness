from __future__ import annotations

from dataclasses import dataclass
from typing import Any


JsonDict = dict[str, Any]


@dataclass(frozen=True)
class Mutation:
    raw: str
    wild_type: str
    position: int
    mutant: str

    @property
    def mutation_class(self) -> str:
        if self.wild_type == self.mutant:
            return "synonymous"
        if self.wild_type in "DEKRH" and self.mutant in "DEKRH":
            return "charge_preserving"
        if self.wild_type in "STNQCY" and self.mutant in "STNQCY":
            return "polar_preserving"
        if self.wild_type in "AVILMFWYPG" and self.mutant in "AVILMFWYPG":
            return "hydrophobic_or_special_preserving"
        return "class_changing"


@dataclass(frozen=True)
class VariantRecord:
    mutation: Mutation
    fitness: float
    is_catalytic: bool
    model_score: float

    def to_row(self) -> dict[str, str]:
        return {
            "variant": self.mutation.raw,
            "wild_type": self.mutation.wild_type,
            "position": str(self.mutation.position),
            "mutant": self.mutation.mutant,
            "fitness": f"{self.fitness:.6g}",
            "is_catalytic": str(self.is_catalytic).lower(),
            "mutation_class": self.mutation.mutation_class,
            "model_score": f"{self.model_score:.6g}",
        }
