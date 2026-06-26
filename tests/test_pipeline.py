import json

from p0_zero_shot_fitness.pipeline import run_fixture_benchmark, run_proteingym_blat_benchmark


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
    assert payload["metrics"]["n_catalytic"] == 81
    assert (tmp_path / "scored_variants.csv").exists()
