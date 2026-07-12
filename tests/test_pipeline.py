import json

from p0_zero_shot_fitness.pipeline import (
    run_fixture_benchmark,
    run_proteingym_blat_benchmark,
    run_proteingym_vim2_benchmark,
)


def test_fixture_pipeline_writes_expected_artifacts(tmp_path) -> None:
    payload = run_fixture_benchmark(tmp_path)

    assert payload["metrics"]["n_variants"] == 20
    assert payload["metrics"]["n_catalytic"] == 6
    assert payload["metrics"]["n_non_catalytic"] == 14
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "scored_variants.csv").exists()
    assert (tmp_path / "fitness_scatter.svg").exists()

    metrics_payload = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    assert metrics_payload["scorer"] == "PlaceholderConservationScorer"
    assert "spearman_overall" in metrics_payload["metrics"]


def test_proteingym_blat_pipeline_runs_real_dataset(tmp_path) -> None:
    payload = run_proteingym_blat_benchmark(tmp_path)

    assert payload["dataset"] == "ProteinGym BLAT_ECOLX_Firnberg_2014"
    assert payload["metrics"]["n_variants"] == 4783
    assert payload["metrics"]["n_catalytic"] == 57
    assert payload["metrics"]["residue_group_breakdown"]["active_site_neighborhood"]["n"] == 461
    assert payload["metrics"]["residue_group_breakdown"]["structure_ligand_contact_5a"]["n"] == 277
    assert payload["metrics"]["residue_group_breakdown"]["uniprot_active_site"]["n"] == 57
    assert (tmp_path / "scored_variants.csv").exists()


def test_proteingym_blat_pipeline_can_add_bootstrap_intervals(tmp_path) -> None:
    payload = run_proteingym_blat_benchmark(tmp_path, bootstrap_iterations=10)

    assert "bootstrap_ci" in payload["metrics"]
    assert payload["metrics"]["bootstrap_ci"]["spearman_overall"]["iterations"] == 10


def test_proteingym_blat_pipeline_can_add_matched_position_null_controls(tmp_path) -> None:
    payload = run_proteingym_blat_benchmark(tmp_path, null_iterations=10)

    null_controls = payload["metrics"]["matched_position_null"]
    assert null_controls["catalytic"]["iterations"] == 10
    assert null_controls["catalytic"]["n_positions"] == 4
    assert null_controls["residue_groups"]["uniprot_active_site"]["n_positions"] == 4


def test_proteingym_vim2_pipeline_runs_second_enzyme_dataset(tmp_path) -> None:
    payload = run_proteingym_vim2_benchmark(tmp_path)

    assert payload["dataset"] == "ProteinGym A4GRB6_PSEAI_Chen_2020"
    assert payload["metrics"]["n_variants"] == 5004
    assert payload["metrics"]["n_catalytic"] == 113
    assert payload["metrics"]["residue_group_breakdown"]["curated_metal_binding_site"]["n"] == 113
    assert payload["metrics"]["residue_group_breakdown"]["active_site_neighborhood"]["n"] == 448
    assert (tmp_path / "scored_variants.csv").exists()
