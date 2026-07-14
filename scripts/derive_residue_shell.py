from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Atom:
    residue_number: int
    residue_name: str
    atom_name: str
    coord: tuple[float, float, float]


def parse_atom_line(line: str) -> Atom:
    return Atom(
        residue_number=int(line[22:26]),
        residue_name=line[17:20].strip(),
        atom_name=line[12:16].strip(),
        coord=(
            float(line[30:38]),
            float(line[38:46]),
            float(line[46:54]),
        ),
    )


def atom_element(line: str) -> str:
    return line[76:78].strip() or line[12:16].strip()[0]


def distance(left: tuple[float, float, float], right: tuple[float, float, float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def load_heavy_atoms(pdb_path: Path, chain: str) -> list[Atom]:
    atoms = []
    for line in pdb_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("ATOM  "):
            continue
        if line[21].strip() != chain:
            continue
        if atom_element(line) == "H":
            continue
        atoms.append(parse_atom_line(line))
    return atoms


def derive_residue_shell(
    atoms: list[Atom],
    site_positions: set[int],
    cutoff_angstrom: float,
) -> dict[int, dict[str, object]]:
    site_atoms = [atom for atom in atoms if atom.residue_number in site_positions]
    if not site_atoms:
        raise ValueError("No site atoms found in structure for the requested site positions.")

    contacts: dict[int, dict[str, object]] = {}
    for atom in atoms:
        closest_site_atom = min(site_atoms, key=lambda site_atom: distance(atom.coord, site_atom.coord))
        min_distance = distance(atom.coord, closest_site_atom.coord)
        if min_distance > cutoff_angstrom:
            continue

        entry = contacts.setdefault(
            atom.residue_number,
            {
                "target_position": atom.residue_number,
                "residue_name": atom.residue_name,
                "min_distance_angstrom": min_distance,
                "closest_site_position": closest_site_atom.residue_number,
                "closest_site_residue_name": closest_site_atom.residue_name,
            },
        )
        if min_distance < float(entry["min_distance_angstrom"]):
            entry["min_distance_angstrom"] = min_distance
            entry["closest_site_position"] = closest_site_atom.residue_number
            entry["closest_site_residue_name"] = closest_site_atom.residue_name
    return contacts


def load_site_positions(path: Path, site_key: str) -> set[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    positions = payload.get(site_key)
    if not positions:
        raise ValueError(f"{path} does not contain non-empty site key {site_key!r}")
    return {int(position) for position in positions}


def build_payload(
    pdb_path: Path,
    chain: str,
    site_json: Path,
    site_key: str,
    cutoff_angstrom: float,
    group_name: str,
) -> dict[str, object]:
    site_positions = load_site_positions(site_json, site_key)
    atoms = load_heavy_atoms(pdb_path, chain)
    contacts = derive_residue_shell(atoms, site_positions, cutoff_angstrom)
    return {
        "pdb": pdb_path.name,
        "chain": chain,
        "site_json": str(site_json),
        "site_key": site_key,
        "site_positions": sorted(site_positions),
        "group_name": group_name,
        "cutoff_angstrom": cutoff_angstrom,
        "target_positions": sorted(contacts),
        "contacts": [
            {
                **contact,
                "min_distance_angstrom": round(float(contact["min_distance_angstrom"]), 3),
            }
            for _, contact in sorted(contacts.items())
        ],
        "method": (
            "Residues are included if any heavy atom is within the cutoff distance "
            "of any heavy atom from the requested site residues."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive a structure shell around a residue site.")
    parser.add_argument("--pdb", type=Path, required=True)
    parser.add_argument("--chain", default="A")
    parser.add_argument("--site-json", type=Path, required=True)
    parser.add_argument("--site-key", default="catalytic_residues")
    parser.add_argument("--cutoff-angstrom", type=float, default=5.0)
    parser.add_argument("--group-name", default="structure_site_shell_5a")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = build_payload(
        pdb_path=args.pdb,
        chain=args.chain,
        site_json=args.site_json,
        site_key=args.site_key,
        cutoff_angstrom=args.cutoff_angstrom,
        group_name=args.group_name,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
