from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p0_zero_shot_fitness.io import read_fasta_sequence, write_json


THREE_TO_ONE = {
    "ALA": "A",
    "ARG": "R",
    "ASN": "N",
    "ASP": "D",
    "CYS": "C",
    "GLN": "Q",
    "GLU": "E",
    "GLY": "G",
    "HIS": "H",
    "ILE": "I",
    "LEU": "L",
    "LYS": "K",
    "MET": "M",
    "PHE": "F",
    "PRO": "P",
    "SER": "S",
    "THR": "T",
    "TRP": "W",
    "TYR": "Y",
    "VAL": "V",
    "MSE": "M",
}


def pdb_chain_sequence(path: Path, chain: str) -> tuple[str, list[dict[str, object]]]:
    residues = []
    seen = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.startswith("ATOM  "):
            continue
        atom_chain = line[21].strip() or " "
        if atom_chain != chain:
            continue
        residue_name = line[17:20].strip()
        residue_number = line[22:26].strip()
        insertion_code = line[26].strip()
        key = (atom_chain, residue_number, insertion_code)
        if key in seen:
            continue
        seen.add(key)
        residues.append(
            {
                "residue_name": residue_name,
                "residue_number": residue_number,
                "insertion_code": insertion_code,
                "one_letter": THREE_TO_ONE.get(residue_name, "X"),
            }
        )
    return "".join(str(residue["one_letter"]) for residue in residues), residues


def first_mismatch(left: str, right: str) -> dict[str, object] | None:
    for index, (left_char, right_char) in enumerate(zip(left, right), start=1):
        if left_char != right_char:
            return {
                "position": index,
                "wild_type_residue": left_char,
                "structure_residue": right_char,
            }
    if len(left) != len(right):
        return {
            "position": min(len(left), len(right)) + 1,
            "wild_type_residue": left[min(len(left), len(right)) :]
            or None,
            "structure_residue": right[min(len(left), len(right)) :]
            or None,
        }
    return None


def audit_target(root: Path, target: dict[str, object]) -> dict[str, object]:
    fasta_path = root / str(target["wild_type_fasta"])
    structure_path = root / str(target["structure_path"])
    wild_type_sequence = read_fasta_sequence(fasta_path.read_text(encoding="utf-8"))
    structure_sequence, residues = pdb_chain_sequence(structure_path, str(target["chain"]))
    exact_sequence_match = wild_type_sequence == structure_sequence
    return {
        "dataset_id": target["dataset_id"],
        "protein_id": target["protein_id"],
        "chain": target["chain"],
        "manifest_status": target.get("structure_status"),
        "wild_type_length": len(wild_type_sequence),
        "structure_length": len(structure_sequence),
        "exact_sequence_match": exact_sequence_match,
        "first_mismatch": None
        if exact_sequence_match
        else first_mismatch(wild_type_sequence, structure_sequence),
        "first_structure_residue": residues[0] if residues else None,
        "last_structure_residue": residues[-1] if residues else None,
        "ready_for_target_numbered_profile": exact_sequence_match
        and target.get("structure_status") == "target_aligned_ready",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit P0 ProteinMPNN target structure readiness.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/proteingym/proteinmpnn_targets.json"),
    )
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    root = Path.cwd()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    targets = [audit_target(root, target) for target in manifest["targets"]]
    payload = {
        "manifest": str(args.manifest),
        "ready_targets": sum(target["ready_for_target_numbered_profile"] for target in targets),
        "total_targets": len(targets),
        "targets": targets,
    }
    if args.output_json:
        write_json(args.output_json, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
