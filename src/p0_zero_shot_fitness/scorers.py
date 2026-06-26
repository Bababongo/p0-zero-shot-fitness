from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache

from p0_zero_shot_fitness.models import Mutation


class VariantScorer(ABC):
    """Interface for zero-shot variant scorers such as ESM log-likelihood ratios."""

    @abstractmethod
    def score(self, mutation: Mutation, wild_type_sequence: str) -> float:
        """Return a model score where higher should mean more fit."""


class PlaceholderConservationScorer(VariantScorer):
    """Deterministic scorer used to test the pipeline before ESM is integrated."""

    def score(self, mutation: Mutation, wild_type_sequence: str) -> float:
        del wild_type_sequence
        substitution_penalty = 0.25
        if mutation.mutation_class.endswith("preserving"):
            substitution_penalty = 0.12
        if mutation.mutation_class == "class_changing":
            substitution_penalty = 0.35

        position_penalty = 0.02 * (mutation.position % 5)
        return round(1.0 - substitution_penalty - position_penalty, 6)


class ESM2MaskedMarginalScorer(VariantScorer):
    """ESM-2 masked-marginal single-substitution scorer.

    This scorer is optional because it requires PyTorch, fair-esm, and model
    weights. It is intentionally lazy-imported so the rest of the benchmark
    remains runnable in lightweight environments.
    """

    def __init__(self, model_name: str = "esm2_t6_8M_UR50D", device: str = "cpu") -> None:
        try:
            import esm  # type: ignore
            import torch  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "ESM scoring requires optional dependencies. Install with "
                "`python -m pip install -e .[esm]` in an environment with a "
                "supported PyTorch build."
            ) from exc

        if not hasattr(esm.pretrained, model_name):
            raise ValueError(f"Unsupported ESM model name: {model_name}")

        self._torch = torch
        self.model_name = model_name
        self.device = device
        self.model, self.alphabet = getattr(esm.pretrained, model_name)()
        self.model.eval()
        self.model.to(device)
        self.batch_converter = self.alphabet.get_batch_converter()
        self.mask_idx = self.alphabet.mask_idx

    @lru_cache(maxsize=4096)
    def _position_log_probs(self, wild_type_sequence: str, position: int):
        _, _, tokens = self.batch_converter([("wild_type", wild_type_sequence)])
        token_position = position
        tokens[0, token_position] = self.mask_idx
        tokens = tokens.to(self.device)
        with self._torch.no_grad():
            logits = self.model(tokens)["logits"][0, token_position]
            return self._torch.log_softmax(logits, dim=-1).cpu()

    def score(self, mutation: Mutation, wild_type_sequence: str) -> float:
        log_probs = self._position_log_probs(wild_type_sequence, mutation.position)
        wild_type_idx = self.alphabet.get_idx(mutation.wild_type)
        mutant_idx = self.alphabet.get_idx(mutation.mutant)
        return float(log_probs[mutant_idx] - log_probs[wild_type_idx])
