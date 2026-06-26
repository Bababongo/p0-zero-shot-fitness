import json

from p0_zero_shot_fitness.cli import main


def test_cli_runs_fixture_benchmark(tmp_path) -> None:
    output_dir = tmp_path / "results"

    exit_code = main(["--output-dir", str(output_dir)])

    assert exit_code == 0
    payload = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert payload["metrics"]["n_variants"] == 20
