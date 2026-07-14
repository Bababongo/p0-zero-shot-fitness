from __future__ import annotations

import argparse
import json
import math
import shlex
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


def parse_mmcif_atom_site_rows(text: str) -> list[dict[str, str]]:
    """Parse the single-line atom_site loop emitted by RCSB mmCIF files."""
    lines = text.splitlines()
    rows: list[dict[str, str]] = []
    line_index = 0
    while line_index < len(lines):
        if lines[line_index].strip() != "loop_":
            line_index += 1
            continue

        header_index = line_index + 1
        headers: list[str] = []
        while header_index < len(lines) and lines[header_index].strip().startswith("_"):
            headers.append(lines[header_index].strip())
            header_index += 1

        if not headers or not all(header.startswith("_atom_site.") for header in headers):
            line_index = header_index + 1
            continue

        field_names = [header.removeprefix("_atom_site.") for header in headers]
        data_index = header_index
        while data_index < len(lines):
            stripped = lines[data_index].strip()
            if not stripped or stripped == "#":
                break
            if stripped == "loop_" or stripped.startswith("_"):
                break
            values = shlex.split(stripped)
            if len(values) == len(field_names):
                rows.append(dict(zip(field_names, values)))
            data_index += 1
        return rows

    return rows


def is_missing(value: object) -> bool:
    return value in {None, "", ".", "?"}


def numeric_string_to_int(value: str) -> int | None:
    if is_missing(value):
        return None
    try:
        return int(value)
    except ValueError:
        return None


def row_coord(row: dict[str, str]) -> tuple[float, float, float]:
    return (
        float(row["Cartn_x"]),
        float(row["Cartn_y"]),
        float(row["Cartn_z"]),
    )


def is_hydrogen(row: dict[str, str]) -> bool:
    return row.get("type_symbol", "").upper() in {"H", "D"}


def derive_mmcif_ligand_contacts(
    mmcif_text: str,
    protein_chain: str,
    ligand_chain: str,
    ligand: str,
    cutoff_angstrom: float,
) -> dict[int, dict[str, object]]:
    protein_atoms = []
    ligand_atoms = []
    for row in parse_mmcif_atom_site_rows(mmcif_text):
        if is_hydrogen(row):
            continue
        auth_chain = row.get("auth_asym_id")
        auth_comp = row.get("auth_comp_id")
        label_comp = row.get("label_comp_id")
        target_position = numeric_string_to_int(row.get("label_seq_id", ""))
        atom = {
            "coord": row_coord(row),
            "atom": row.get("auth_atom_id") or row.get("label_atom_id"),
            "residue_name": auth_comp or label_comp,
            "pdb_position": numeric_string_to_int(row.get("auth_seq_id", "")),
            "target_position": target_position,
            "label_chain": row.get("label_asym_id"),
            "auth_chain": auth_chain,
        }

        if auth_chain == protein_chain and target_position is not None and auth_comp != ligand and label_comp != ligand:
            protein_atoms.append(atom)
        elif auth_chain == ligand_chain and (auth_comp == ligand or label_comp == ligand):
            ligand_atoms.append(atom)

    if not protein_atoms:
        raise ValueError(f"No protein atoms found for chain {protein_chain!r} in mmCIF atom_site rows.")
    if not ligand_atoms:
        raise ValueError(f"No ligand atoms found for ligand {ligand!r} on chain {ligand_chain!r}.")

    contacts: dict[int, dict[str, object]] = {}
    for atom in protein_atoms:
        min_distance = min(
            distance(atom["coord"], ligand_atom["coord"])
            for ligand_atom in ligand_atoms
        )
        if min_distance <= cutoff_angstrom:
            target_position = int(atom["target_position"])
            entry = contacts.setdefault(
                target_position,
                {
                    "target_position": target_position,
                    "pdb_position": atom["pdb_position"],
                    "residue_name": atom["residue_name"],
                    "label_chain": atom["label_chain"],
                    "auth_chain": atom["auth_chain"],
                    "min_distance_angstrom": min_distance,
                },
            )
            entry["min_distance_angstrom"] = min(
                float(entry["min_distance_angstrom"]),
                min_distance,
            )
    return contacts


def build_mmcif_payload(
    mmcif_path: Path,
    protein_chain: str,
    ligand_chain: str,
    ligand: str,
    cutoff_angstrom: float,
) -> dict[str, object]:
    contacts = derive_mmcif_ligand_contacts(
        mmcif_text=mmcif_path.read_text(encoding="utf-8"),
        protein_chain=protein_chain,
        ligand_chain=ligand_chain,
        ligand=ligand,
        cutoff_angstrom=cutoff_angstrom,
    )
    return {
        "structure": mmcif_path.name,
        "format": "mmCIF",
        "protein_chain": protein_chain,
        "ligand_chain": ligand_chain,
        "ligand": ligand,
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
            "Residues are included if any protein heavy atom with a numeric mmCIF "
            "label_seq_id is within the cutoff distance of any ligand heavy atom. "
            "label_seq_id is used as target-sequence numbering."
        ),
    }


def build_pdb_payload(
    pdb_path: Path,
    chain: str,
    ligand: str,
    cutoff_angstrom: float,
    pdb_to_target_offset: int,
) -> dict[str, object]:
    protein_atoms = []
    ligand_atoms = []
    for line in pdb_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith(("ATOM  ", "HETATM")):
            continue
        atom = parse_atom_line(line)
        if atom["chain"] != chain:
            continue
        if atom["element"] == "H":
            continue
        if atom["record"] == "ATOM":
            protein_atoms.append(atom)
        elif atom["record"] == "HETATM" and atom["residue_name"] == ligand:
            ligand_atoms.append(atom)

    if not protein_atoms:
        raise ValueError(f"No protein atoms found for chain {chain!r} in {pdb_path}.")
    if not ligand_atoms:
        raise ValueError(f"No ligand atoms found for ligand {ligand!r} on chain {chain!r}.")

    contacts: dict[int, dict[str, object]] = {}
    for atom in protein_atoms:
        min_distance = min(
            distance(atom["coord"], ligand_atom["coord"])
            for ligand_atom in ligand_atoms
        )
        if min_distance <= cutoff_angstrom:
            pdb_residue = int(atom["residue_number"])
            target_residue = pdb_residue + pdb_to_target_offset
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

    return {
        "structure": pdb_path.name,
        "format": "PDB",
        "chain": chain,
        "ligand": ligand,
        "cutoff_angstrom": cutoff_angstrom,
        "pdb_to_target_offset": pdb_to_target_offset,
        "target_positions": sorted(contacts),
        "contacts": [
            {
                **contact,
                "min_distance_angstrom": round(float(contact["min_distance_angstrom"]), 3),
            }
            for _, contact in sorted(contacts.items())
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive ligand-contact residues from a PDB or mmCIF file.")
    parser.add_argument("--pdb", type=Path, default=None)
    parser.add_argument("--mmcif", type=Path, default=None)
    parser.add_argument("--chain", dest="protein_chain", default="A")
    parser.add_argument("--protein-chain", dest="protein_chain")
    parser.add_argument("--ligand-chain", default=None)
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

    if bool(args.pdb) == bool(args.mmcif):
        parser.error("Provide exactly one of --pdb or --mmcif.")

    if args.mmcif:
        payload = build_mmcif_payload(
            mmcif_path=args.mmcif,
            protein_chain=args.protein_chain,
            ligand_chain=args.ligand_chain or args.protein_chain,
            ligand=args.ligand,
            cutoff_angstrom=args.cutoff_angstrom,
        )
    else:
        payload = build_pdb_payload(
            pdb_path=args.pdb,
            chain=args.protein_chain,
            ligand=args.ligand,
            cutoff_angstrom=args.cutoff_angstrom,
            pdb_to_target_offset=args.pdb_to_target_offset,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
