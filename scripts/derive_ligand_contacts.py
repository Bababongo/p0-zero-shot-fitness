from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def parse_atom_line(line: str) -> dict[str, object]:
    return {
        "record": line[:6].strip(),
        "atom": line[12:16].strip(),
        "altloc": line[16].strip(),
        "residue_name": line[17:20].strip(),
        "chain": line[21].strip(),
        "residue_number": int(line[22:26]),
        "coord": (
            float(line[30:38]),
            float(line[38:46]),
            float(line[46:54]),
        ),
        "element": line[76:78].strip() or line[12:16].strip()[0],
    }


def distance(left: tuple[float, float, float], right: tuple[float, float, float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive ligand-contact residues from a PDB file.")
    parser.add_argument("--pdb", type=Path, required=True)
    parser.add_argument("--chain", default="A")
    parser.add_argument("--ligand", required=True)
    parser.add_argument("--cutoff-angstrom", type=float, default=5.0)
    parser.add_argument(
        "--pdb-to-target-offset",
        type=int,
        default=-2,
        help="Offset added to PDB residue numbers to map into target sequence numbering.",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    protein_atoms = []
    ligand_atoms = []
    for line in args.pdb.read_text(encoding="utf-8").splitlines():
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        atom = parse_atom_line(line)
        if atom["chain"] != args.chain:
            continue
        if atom["element"] == "H":
            continue
        if atom["record"] == "ATOM":
            protein_atoms.append(atom)
        elif atom["record"] == "HETATM" and atom["residue_name"] == args.ligand:
            ligand_atoms.append(atom)

    contacts: dict[int, dict[str, object]] = {}
    for atom in protein_atoms:
        min_distance = min(
            distance(atom["coord"], ligand_atom["coord"])
            for ligand_atom in ligand_atoms
        )
        if min_distance <= args.cutoff_angstrom:
            pdb_residue = int(atom["residue_number"])
            target_residue = pdb_residue + args.pdb_to_target_offset
            entry = contacts.setdefault(
                target_residue,
                {
                    "target_position": target_residue,
                    "pdb_position": pdb_residue,
                    "residue_name": atom["residue_name"],
                    "min_distance_angstrom": min_distance,
                },
            )
            entry["min_distance_angstrom"] = min(
                float(entry["min_distance_angstrom"]),
                min_distance,
            )

    payload = {
        "pdb": args.pdb.name,
        "chain": args.chain,
        "ligand": args.ligand,
        "cutoff_angstrom": args.cutoff_angstrom,
        "pdb_to_target_offset": args.pdb_to_target_offset,
        "target_positions": sorted(contacts),
        "contacts": [
            {
                **contact,
                "min_distance_angstrom": round(float(contact["min_distance_angstrom"]), 3),
            }
            for _, contact in sorted(contacts.items())
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
