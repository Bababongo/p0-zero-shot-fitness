import pytest

from p0_zero_shot_fitness.position_covariates import (
    approximate_sasa_covariates,
    contact_count_covariates,
    covariates_from_scored_rows,
    parse_pdb_atoms,
    parse_pdb_representative_atoms,
)


def test_covariates_from_scored_rows_reports_position_level_spread() -> None:
    rows = [
        {"position": "1", "fitness": "0.1", "model_score": "-1.0"},
        {"position": "1", "fitness": "0.3", "model_score": "-0.5"},
        {"position": "2", "fitness": "0.9", "model_score": "0.2"},
    ]

    covariates = covariates_from_scored_rows(rows)

    assert covariates[1]["mutation_count"] == 2.0
    assert covariates[1]["fitness_mean"] == pytest.approx(0.2)
    assert covariates[1]["fitness_sd"] > 0
    assert covariates[2]["mutation_count"] == 1.0


def test_parse_pdb_representative_atoms_and_contact_counts() -> None:
    pdb_text = "\n".join(
        [
            "ATOM      1  CA  GLY A   1       0.000   0.000   0.000  1.00 10.00           C",
            "ATOM      2  CA  ALA A   2       3.000   0.000   0.000  1.00 10.00           C",
            "ATOM      3  CB  ALA A   2       4.000   0.000   0.000  1.00 10.00           C",
            "ATOM      4  CA  SER A   3      20.000   0.000   0.000  1.00 10.00           C",
            "ATOM      5  CB  SER A   3      21.000   0.000   0.000  1.00 10.00           C",
        ]
    )

    representatives = parse_pdb_representative_atoms(pdb_text)
    contacts = contact_count_covariates(representatives, cutoff_angstrom=10.0)

    assert representatives[1] == (0.0, 0.0, 0.0)
    assert representatives[2] == (4.0, 0.0, 0.0)
    assert contacts[1]["structure_contact_count_10a"] == 1.0
    assert contacts[2]["structure_contact_count_10a"] == 1.0
    assert contacts[3]["structure_contact_count_10a"] == 0.0


def test_approximate_sasa_covariates_report_relative_accessibility() -> None:
    pdb_text = "\n".join(
        [
            "ATOM      1  CA  GLY A   1       0.000   0.000   0.000  1.00 10.00           C",
            "ATOM      2  CA  ALA A   2       2.000   0.000   0.000  1.00 10.00           C",
            "ATOM      3  CB  ALA A   2       3.000   0.000   0.000  1.00 10.00           C",
            "ATOM      4  CA  SER A   3      20.000   0.000   0.000  1.00 10.00           C",
        ]
    )

    residue_atoms = parse_pdb_atoms(pdb_text)
    covariates = approximate_sasa_covariates(residue_atoms, n_sphere_points=24)

    assert covariates[1]["structure_sasa_approx"] > 0
    assert 0 <= covariates[1]["structure_relative_sasa_approx"] <= 1
    assert 0 <= covariates[1]["structure_burial_approx"] <= 1
    assert max(row["structure_relative_sasa_approx"] for row in covariates.values()) == pytest.approx(1.0)
