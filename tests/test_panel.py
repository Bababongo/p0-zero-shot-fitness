from pathlib import Path

import pytest

from p0_zero_shot_fitness.panel import cost_category, cost_units, validate_panel_registry


ROOT = Path(__file__).resolve().parents[1]


def test_cost_units_estimate_masked_marginal_work() -> None:
    units = cost_units(single_mutants=5004, sequence_length=266)

    assert units == 1_331_064
    assert cost_category(units) == "medium"
    assert cost_category(999_999) == "small"
    assert cost_category(2_500_000) == "large"
    assert cost_category(5_000_000) == "very_large"


def test_validate_panel_registry_against_local_proteingym_metadata() -> None:
    payload = validate_panel_registry(
        panel_csv=ROOT / "data" / "panels" / "p0_enzyme_panel_candidates.csv",
        proteingym_metadata_csv=ROOT / "data" / "proteingym" / "DMS_substitutions.csv",
        data_dir=ROOT / "data" / "proteingym",
    )

    assert payload["n_candidates"] == 18
    assert payload["n_metadata_matches"] == 18
    assert payload["status_counts"]["ready_for_p0_pipeline"] == 1
    assert payload["status_counts"]["metadata_ready_needs_local_data_and_annotations"] == 17

    recommendations = [candidate["dms_id"] for candidate in payload["recommended_first_three"]]
    assert recommendations == [
        "A4GRB6_PSEAI_Chen_2020",
        "R1AB_SARS2_Flynn_2022",
        "AMIE_PSEAE_Wrenbeck_2017",
    ]

    seed_case = next(
        candidate
        for candidate in payload["candidate_summaries"]
        if candidate["dms_id"] == "BLAT_ECOLX_Firnberg_2014"
    )
    assert seed_case["status"] == "ready_for_p0_pipeline"
    assert all(seed_case["local_status"].values())


def test_validate_panel_registry_rejects_missing_required_columns(tmp_path) -> None:
    broken_panel = tmp_path / "broken_panel.csv"
    broken_panel.write_text("dms_id\nBLAT_ECOLX_Firnberg_2014\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Panel registry is missing required columns"):
        validate_panel_registry(
            panel_csv=broken_panel,
            proteingym_metadata_csv=ROOT / "data" / "proteingym" / "DMS_substitutions.csv",
            data_dir=ROOT / "data" / "proteingym",
        )
