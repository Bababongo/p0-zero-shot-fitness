import pytest

from p0_zero_shot_fitness.metrics import bootstrap_spearman_ci, residue_group_breakdown, spearman, top_k_enrichment
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


def test_bootstrap_spearman_ci_is_reproducible() -> None:
    records = [
        VariantRecord(Mutation("A1V", "A", 1, "V"), 0.9, False, 0.9),
        VariantRecord(Mutation("C2S", "C", 2, "S"), 0.8, False, 0.8),
        VariantRecord(Mutation("D3E", "D", 3, "E"), 0.1, False, 0.7),
        VariantRecord(Mutation("F4Y", "F", 4, "Y"), 0.2, False, 0.6),
    ]

    first = bootstrap_spearman_ci(records, iterations=25, seed=7)
    second = bootstrap_spearman_ci(records, iterations=25, seed=7)

    assert first == second
    assert first["iterations"] == 25
    assert first["ci_low"] is not None
    assert first["ci_high"] is not None


def test_residue_group_breakdown_reports_in_group_and_outside_group() -> None:
    records = [
        VariantRecord(Mutation("A1V", "A", 1, "V"), 0.1, False, 0.2, frozenset({"pocket"})),
        VariantRecord(Mutation("A2V", "A", 2, "V"), 0.2, False, 0.4, frozenset({"pocket"})),
        VariantRecord(Mutation("A3V", "A", 3, "V"), 0.3, False, 0.1, frozenset()),
        VariantRecord(Mutation("A4V", "A", 4, "V"), 0.4, False, 0.3, frozenset()),
    ]

    breakdown = residue_group_breakdown(records)

    assert breakdown["pocket"]["n"] == 2
    assert breakdown["pocket"]["outside_n"] == 2
    assert breakdown["pocket"]["spearman"] == pytest.approx(1.0)
