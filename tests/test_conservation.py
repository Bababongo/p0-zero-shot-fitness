import pytest

from p0_zero_shot_fitness.conservation import (
    conservation_log_odds_score,
    derive_conservation_profile,
    normalize_a2m_sequence,
)
from p0_zero_shot_fitness.models import Mutation


def test_normalize_a2m_sequence_removes_insert_columns() -> None:
    assert normalize_a2m_sequence("ACd.E-F") == "ACE-F"


def test_derive_conservation_profile_reports_position_covariates() -> None:
    alignment = "\n".join(
        [
            ">query",
            "ACD",
            ">homolog_1",
            "ACD",
            ">homolog_2",
            "AVD",
        ]
    )

    profile = derive_conservation_profile(alignment, "ACD", pseudocount=0.1)

    assert profile["alignment_records"] == 3
    assert profile["covariates"]["1"]["msa_wild_type_frequency"] > 0.5
    assert profile["covariates"]["2"]["msa_normalized_entropy"] > profile["covariates"]["1"]["msa_normalized_entropy"]
    assert profile["aa_frequencies"]["2"]["C"] > profile["aa_frequencies"]["2"]["A"]


def test_conservation_log_odds_score_uses_mutant_frequency() -> None:
    alignment = "\n".join(
        [
            ">query",
            "ACD",
            ">homolog_1",
            "AVD",
            ">homolog_2",
            "AVD",
        ]
    )
    profile = derive_conservation_profile(alignment, "ACD", pseudocount=0.1)

    score = conservation_log_odds_score(Mutation("C2V", "C", 2, "V"), profile)

    assert score > 0
    assert score == pytest.approx(-conservation_log_odds_score(Mutation("V2C", "V", 2, "C"), profile))
