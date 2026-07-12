import json

from p0_zero_shot_fitness.cli import main


def test_cli_runs_fixture_benchmark(tmp_path) -> None:
    output_dir = tmp_path / "results"

    exit_code = main(["--output-dir", str(output_dir)])

    assert exit_code == 0
    payload = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert payload["metrics"]["n_variants"] == 20


def test_cli_can_add_matched_position_null_controls(tmp_path) -> None:
    output_dir = tmp_path / "results"

    exit_code = main(["--output-dir", str(output_dir), "--null-iterations", "5"])

    assert exit_code == 0
    payload = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert payload["metrics"]["matched_position_null"]["catalytic"]["iterations"] == 5
