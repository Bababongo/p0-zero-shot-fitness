import pytest

from p0_zero_shot_fitness.metrics import spearman, top_k_enrichment
from p0_zero_shot_fitness.models import Mutation, VariantRecord


def test_spearman_identifies_perfect_rank_correlation() -> None:
    assert spearman([1, 2, 3], [10, 20, 30]) == pytest.approx(1.0)
    assert spearman([1, 2, 3], [30, 20, 10]) == pytest.approx(-1.0)


def test_top_k_enrichment_returns_ratio_over_background() -> None:
    records = [
        VariantRecord(Mutation("A1V", "A", 1, "V"), 0.9, False, 0.9),
        VariantRecord(Mutation("C2S", "C", 2, "S"), 0.8, False, 0.8),
        VariantRecord(Mutation("D3E", "D", 3, "E"), 0.1, False, 0.7),
        VariantRecord(Mutation("F4Y", "F", 4, "Y"), 0.2, False, 0.6),
    ]

    assert top_k_enrichment(records, k=2, fitness_threshold=0.7) == 2.0
