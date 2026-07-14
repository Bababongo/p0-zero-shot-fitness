from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p0_zero_shot_fitness.conservation import derive_conservation_profile
from p0_zero_shot_fitness.io import read_fasta_sequence, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive per-position conservation covariates from an MSA.")
    parser.add_argument("--msa-a2m", type=Path, required=True)
    parser.add_argument("--wild-type-fasta", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--pseudocount", type=float, default=0.5)
    args = parser.parse_args()

    wild_type_sequence = read_fasta_sequence(args.wild_type_fasta.read_text(encoding="utf-8"))
    profile = derive_conservation_profile(
        args.msa_a2m.read_text(encoding="utf-8"),
        wild_type_sequence=wild_type_sequence,
        pseudocount=args.pseudocount,
    )
    profile["dataset"] = args.dataset_name
    profile["source_msa_a2m"] = str(args.msa_a2m)
    profile["source_wild_type_fasta"] = str(args.wild_type_fasta)
    write_json(args.output_json, profile)
    print(f"Wrote {args.output_json} with {len(profile['covariates'])} residue positions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
