from __future__ import annotations

from collections import defaultdict
import csv
import json
from math import dist
from pathlib import Path


Coordinate = tuple[float, float, float]
PositionCovariates = dict[int, dict[str, float]]


def sample_sd(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    value_mean = sum(values) / len(values)
    return (sum((value - value_mean) ** 2 for value in values) / (len(values) - 1)) ** 0.5


def load_scored_variant_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def covariates_from_scored_rows(rows: list[dict[str, str]]) -> PositionCovariates:
    grouped: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[int(row["position"])].append(row)

    all_positions = sorted(grouped)
    min_position = min(all_positions) if all_positions else 0
    max_position = max(all_positions) if all_positions else 0
    position_span = max(1, max_position - min_position)
    covariates: PositionCovariates = {}
    for position, position_rows in grouped.items():
        fitness_values = [float(row["fitness"]) for row in position_rows]
        model_score_values = [float(row["model_score"]) for row in position_rows]
        covariates[position] = {
            "mutation_count": float(len(position_rows)),
            "fitness_mean": sum(fitness_values) / len(fitness_values),
            "fitness_sd": sample_sd(fitness_values),
            "fitness_range": max(fitness_values) - min(fitness_values),
            "model_score_mean": sum(model_score_values) / len(model_score_values),
            "model_score_sd": sample_sd(model_score_values),
            "relative_position": (position - min_position) / position_span,
        }
    return covariates


def parse_pdb_representative_atoms(pdb_text: str) -> dict[int, Coordinate]:
    residue_atoms: dict[int, dict[str, Coordinate]] = defaultdict(dict)
    residue_names: dict[int, str] = {}
    for line in pdb_text.splitlines():
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        atom_name = line[12:16].strip()
        residue_name = line[17:20].strip()
        try:
            residue_number = int(line[22:26])
            coordinate = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
        except ValueError:
            continue
        residue_atoms[residue_number][atom_name] = coordinate
        residue_names[residue_number] = residue_name

    representatives: dict[int, Coordinate] = {}
    for residue_number, atoms in residue_atoms.items():
        preferred_atom = "CA" if residue_names.get(residue_number) == "GLY" else "CB"
        if preferred_atom in atoms:
            representatives[residue_number] = atoms[preferred_atom]
        elif "CA" in atoms:
            representatives[residue_number] = atoms["CA"]
    return representatives


def contact_count_covariates(
    representatives: dict[int, Coordinate],
    cutoff_angstrom: float = 10.0,
) -> PositionCovariates:
    covariates: PositionCovariates = {}
    for position, coordinate in representatives.items():
        contact_count = sum(
            1
            for other_position, other_coordinate in representatives.items()
            if other_position != position and dist(coordinate, other_coordinate) <= cutoff_angstrom
        )
        covariates[position] = {f"structure_contact_count_{cutoff_angstrom:g}a": float(contact_count)}
    return covariates


def merge_covariates(*covariate_maps: PositionCovariates) -> PositionCovariates:
    merged: PositionCovariates = {}
    for covariate_map in covariate_maps:
        for position, covariates in covariate_map.items():
            merged.setdefault(position, {}).update(covariates)
    return merged


def write_position_covariates(
    path: Path,
    covariates: PositionCovariates,
    metadata: dict[str, object],
) -> None:
    payload = {
        **metadata,
        "notes": {
            "mutation_count": "Number of scored single mutants observed at a residue position.",
            "fitness_sd": "Experimental DMS fitness spread at a residue position; post-hoc control, not a prospective feature.",
            "model_score_sd": "ESM score spread at a residue position; model-sensitivity control, not independent biology.",
            "structure_contact_count_10a": "C-beta/C-alpha contact count within 10 A; burial/exposure proxy, not full SASA.",
        },
        "covariates": {
            str(position): covariates[position]
            for position in sorted(covariates)
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
