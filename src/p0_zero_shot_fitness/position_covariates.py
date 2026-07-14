from __future__ import annotations

from collections import defaultdict
import csv
from dataclasses import dataclass
import json
from functools import lru_cache
from math import cos, dist, pi, sin, sqrt
from pathlib import Path


Coordinate = tuple[float, float, float]
PositionCovariates = dict[int, dict[str, float]]

VDW_RADII = {
    "C": 1.70,
    "N": 1.55,
    "O": 1.52,
    "S": 1.80,
    "P": 1.80,
}


@dataclass(frozen=True)
class PdbAtom:
    residue_number: int
    atom_name: str
    element: str
    coordinate: Coordinate
    radius: float


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


def _infer_element(atom_name: str, pdb_element: str) -> str:
    element = pdb_element.strip().upper()
    if element:
        return element[0]
    stripped = atom_name.strip().upper()
    for character in stripped:
        if character.isalpha():
            return character
    return "C"


def parse_pdb_atoms(pdb_text: str) -> dict[int, list[PdbAtom]]:
    residue_atoms: dict[int, list[PdbAtom]] = defaultdict(list)
    for line in pdb_text.splitlines():
        if not line.startswith("ATOM  "):
            continue
        atom_name = line[12:16].strip()
        element = _infer_element(atom_name, line[76:78] if len(line) >= 78 else "")
        if element in {"H", "D"}:
            continue
        try:
            residue_number = int(line[22:26])
            coordinate = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
        except ValueError:
            continue
        residue_atoms[residue_number].append(
            PdbAtom(
                residue_number=residue_number,
                atom_name=atom_name,
                element=element,
                coordinate=coordinate,
                radius=VDW_RADII.get(element, 1.70),
            )
        )
    return residue_atoms


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


@lru_cache(maxsize=16)
def sphere_points(n_points: int) -> tuple[Coordinate, ...]:
    if n_points <= 0:
        raise ValueError("n_points must be positive")
    golden_angle = pi * (3.0 - sqrt(5.0))
    points: list[Coordinate] = []
    for index in range(n_points):
        z = 1.0 - (2.0 * (index + 0.5) / n_points)
        radius = sqrt(max(0.0, 1.0 - z * z))
        theta = golden_angle * index
        points.append((cos(theta) * radius, sin(theta) * radius, z))
    return tuple(points)


def approximate_sasa_covariates(
    residue_atoms: dict[int, list[PdbAtom]],
    probe_radius: float = 1.4,
    n_sphere_points: int = 48,
) -> PositionCovariates:
    """Approximate residue solvent-accessible surface area from heavy atoms.

    This is a lightweight Shrake-Rupley-style approximation. It is intended as
    a structural accessibility control for the benchmark, not as a replacement
    for a dedicated structural-biology package.
    """
    atoms = [atom for atoms_for_residue in residue_atoms.values() for atom in atoms_for_residue]
    if not atoms:
        return {}

    expanded_radii = [atom.radius + probe_radius for atom in atoms]
    neighbor_indices: list[list[int]] = []
    for atom_index, atom in enumerate(atoms):
        candidates: list[int] = []
        for other_index, other_atom in enumerate(atoms):
            if atom_index == other_index:
                continue
            if dist(atom.coordinate, other_atom.coordinate) <= expanded_radii[atom_index] + expanded_radii[other_index]:
                candidates.append(other_index)
        neighbor_indices.append(candidates)

    residue_sasa: dict[int, float] = defaultdict(float)
    unit_points = sphere_points(n_sphere_points)
    for atom_index, atom in enumerate(atoms):
        expanded_radius = expanded_radii[atom_index]
        accessible_points = 0
        for unit_x, unit_y, unit_z in unit_points:
            surface_point = (
                atom.coordinate[0] + unit_x * expanded_radius,
                atom.coordinate[1] + unit_y * expanded_radius,
                atom.coordinate[2] + unit_z * expanded_radius,
            )
            is_accessible = True
            for other_index in neighbor_indices[atom_index]:
                if dist(surface_point, atoms[other_index].coordinate) <= expanded_radii[other_index]:
                    is_accessible = False
                    break
            if is_accessible:
                accessible_points += 1
        atom_sasa = (accessible_points / n_sphere_points) * 4.0 * pi * expanded_radius**2
        residue_sasa[atom.residue_number] += atom_sasa

    max_sasa = max(residue_sasa.values()) if residue_sasa else 1.0
    return {
        position: {
            "structure_sasa_approx": float(sasa),
            "structure_relative_sasa_approx": float(sasa / max_sasa) if max_sasa else 0.0,
            "structure_burial_approx": float(1.0 - (sasa / max_sasa)) if max_sasa else 0.0,
        }
        for position, sasa in residue_sasa.items()
    }


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
            "structure_sasa_approx": "Approximate residue solvent-accessible surface area in A^2 from heavy atoms using a lightweight Shrake-Rupley-style calculation.",
            "structure_relative_sasa_approx": "Approximate residue SASA divided by the maximum residue SASA observed in the same structure.",
            "structure_burial_approx": "One minus structure_relative_sasa_approx; higher values are more buried by this structure proxy.",
        },
        "covariates": {
            str(position): covariates[position]
            for position in sorted(covariates)
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
