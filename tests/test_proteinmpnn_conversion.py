from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from p0_zero_shot_fitness.models import Mutation
from p0_zero_shot_fitness.structure_profiles import structure_profile_log_odds_score


def test_convert_proteinmpnn_npz_to_profile(tmp_path: Path) -> None:
    fasta = tmp_path / "toy.fasta"
    fasta.write_text(">toy\nAC\n", encoding="utf-8")
    npz = tmp_path / "toy.npz"
    log_p = np.full((2, 2, 21), -10.0)
    log_p[:, 0, 0] = -0.1  # A at position 1
    log_p[:, 0, 17] = -1.1  # V at position 1
    log_p[:, 1, 1] = -0.2  # C at position 2
    log_p[:, 1, 17] = -2.2  # V at position 2
    np.savez(npz, log_p=log_p, S=np.array([[0, 1], [0, 1]]))
    output_json = tmp_path / "profile.json"

    subprocess.run(
        [
            sys.executable,
            "scripts/convert_proteinmpnn_npz_to_profile.py",
            "--proteinmpnn-npz",
            str(npz),
            "--wild-type-fasta",
            str(fasta),
            "--output-json",
            str(output_json),
            "--protein",
            "toy",
            "--structure",
            "toy.pdb",
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
    )

    profile = json.loads(output_json.read_text(encoding="utf-8"))

    assert profile["format"] == "p0_structure_log_probability_profile.v1"
    assert profile["batch_count"] == 2
    assert profile["sequence_from_npz_matches_fasta"] is True
    assert profile["positions"]["1"]["wild_type"] == "A"
    assert structure_profile_log_odds_score(Mutation("A1V", "A", 1, "V"), profile) == pytest.approx(-1.0)


def test_convert_proteinmpnn_npz_rejects_sequence_mismatch(tmp_path: Path) -> None:
    fasta = tmp_path / "toy.fasta"
    fasta.write_text(">toy\nAC\n", encoding="utf-8")
    npz = tmp_path / "toy.npz"
    log_p = np.full((1, 2, 21), -10.0)
    np.savez(npz, log_p=log_p, S=np.array([[0, 17]]))
    output_json = tmp_path / "profile.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/convert_proteinmpnn_npz_to_profile.py",
            "--proteinmpnn-npz",
            str(npz),
            "--wild-type-fasta",
            str(fasta),
            "--output-json",
            str(output_json),
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "does not match FASTA" in result.stderr
