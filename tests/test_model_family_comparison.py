from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def write_metrics(path: Path, dataset: str, scorer: str, spearman: float) -> None:
    path.write_text(
        json.dumps(
            {
                "dataset": dataset,
                "scorer": scorer,
                "metrics": {
                    "spearman_overall": spearman,
                    "spearman_catalytic": spearman / 2,
                    "spearman_non_catalytic": spearman,
                    "residue_group_breakdown": {
                        "structure_wl3_inhibitor_contact_5a": {
                            "n": 2,
                            "spearman": spearman + 0.1,
                            "outside_spearman": spearman,
                        }
                    },
                    "matched_position_null": {
                        "residue_groups": {
                            "structure_wl3_inhibitor_contact_5a": {
                                "direction": "inside_position_matched_null_interval",
                                "two_sided_empirical_p": 0.5,
                            }
                        }
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def test_compare_model_family_metrics_script(tmp_path: Path) -> None:
    dataset = "ProteinGym A4GRB6_PSEAI_Chen_2020"
    esm = tmp_path / "esm.json"
    msa = tmp_path / "msa.json"
    pmpnn = tmp_path / "pmpnn.json"
    output = tmp_path / "comparison.json"
    write_metrics(esm, dataset, "ESM2MaskedMarginalScorer", 0.5)
    write_metrics(msa, dataset, "MSAConservationLogOddsScorer", 0.4)
    write_metrics(pmpnn, dataset, "ProteinMPNNProfileScorer", 0.3)

    subprocess.run(
        [
            sys.executable,
            "scripts/compare_model_family_metrics.py",
            str(esm),
            str(msa),
            str(pmpnn),
            "--output",
            str(output),
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
    )

    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["comparison_type"] == "P0 model-family comparison"
    assert payload["comparison"][0]["dataset"] == dataset
    assert len(payload["comparison"][0]["runs"]) == 3
    first_run = payload["comparison"][0]["runs"][0]
    assert "structure_wl3_inhibitor_contact_5a" in first_run["groups"]
