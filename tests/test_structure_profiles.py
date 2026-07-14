from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from p0_zero_shot_fitness.models import Mutation
from p0_zero_shot_fitness.structure_profiles import structure_profile_log_odds_score


def test_structure_profile_log_odds_score_uses_mutant_minus_wild_type() -> None:
    profile = {
        "positions": {
            "2": {
                "wild_type": "C",
                "log_probabilities": {
                    "C": -0.2,
                    "V": -2.0,
                },
            }
        }
    }

    score = structure_profile_log_odds_score(Mutation("C2V", "C", 2, "V"), profile)

    assert score == pytest.approx(-1.8)


def test_structure_profile_accepts_probabilities() -> None:
    profile = {
        "positions": {
            "2": {
                "wild_type": "C",
                "probabilities": {
                    "C": 0.8,
                    "V": 0.2,
                },
            }
        }
    }

    score = structure_profile_log_odds_score(Mutation("C2V", "C", 2, "V"), profile)

    assert score == pytest.approx(-1.3862943611198906)


def test_structure_profile_rejects_wild_type_mismatch() -> None:
    profile = {
        "positions": {
            "2": {
                "wild_type": "A",
                "log_probabilities": {
                    "C": -0.2,
                    "V": -2.0,
                },
            }
        }
    }

    with pytest.raises(ValueError, match="wild type mismatch"):
        structure_profile_log_odds_score(Mutation("C2V", "C", 2, "V"), profile)


def test_score_structure_profile_baseline_script(tmp_path: Path) -> None:
    scored_variants = tmp_path / "scored_variants.csv"
    scored_variants.write_text(
        "\n".join(
            [
                "variant,wild_type,position,mutant,fitness,is_catalytic,residue_groups,mutation_class,model_score",
                "A1V,A,1,V,0.1,true,pocket,class_changing,0.0",
                "A1C,A,1,C,0.2,true,pocket,class_changing,0.0",
                "C2V,C,2,V,0.3,false,,class_changing,0.0",
                "C2A,C,2,A,0.4,false,,class_changing,0.0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    profile = tmp_path / "structure_profile.json"
    profile.write_text(
        json.dumps(
            {
                "scorer": "ProteinMPNNProfileScorer",
                "positions": {
                    "1": {
                        "wild_type": "A",
                        "log_probabilities": {
                            "A": -0.1,
                            "C": -2.0,
                            "V": -1.0,
                        },
                    },
                    "2": {
                        "wild_type": "C",
                        "log_probabilities": {
                            "A": -2.0,
                            "C": -0.1,
                            "V": -1.0,
                        },
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    output_dir = tmp_path / "out"

    subprocess.run(
        [
            sys.executable,
            "scripts/score_structure_profile_baseline.py",
            "--scored-variants-csv",
            str(scored_variants),
            "--structure-profile-json",
            str(profile),
            "--output-dir",
            str(output_dir),
            "--dataset-name",
            "fixture",
            "--null-iterations",
            "5",
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
    )

    metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))

    assert metrics["scorer"] == "ProteinMPNNProfileScorer"
    assert metrics["metrics"]["n_variants"] == 4
    assert (output_dir / "scored_variants.csv").exists()
    assert (output_dir / "fitness_scatter.svg").exists()
