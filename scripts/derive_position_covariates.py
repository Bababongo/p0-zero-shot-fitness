from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p0_zero_shot_fitness.position_covariates import (
    approximate_sasa_covariates,
    contact_count_covariates,
    covariates_from_scored_rows,
    load_scored_variant_rows,
    merge_covariates,
    parse_pdb_atoms,
    parse_pdb_representative_atoms,
    write_position_covariates,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive per-position P0 control covariates.")
    parser.add_argument("--scored-variants-csv", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--pdb", type=Path, default=None)
    parser.add_argument("--structure-contact-cutoff", type=float, default=10.0)
    parser.add_argument("--skip-sasa", action="store_true", help="Skip approximate SASA derivation from the PDB.")
    parser.add_argument("--sasa-probe-radius", type=float, default=1.4)
    parser.add_argument("--sasa-sphere-points", type=int, default=48)
    args = parser.parse_args()

    rows = load_scored_variant_rows(args.scored_variants_csv)
    scored_covariates = covariates_from_scored_rows(rows)
    covariate_maps = [scored_covariates]
    metadata: dict[str, object] = {
        "dataset": args.dataset_name,
        "source_scored_variants_csv": str(args.scored_variants_csv),
        "source_pdb": str(args.pdb) if args.pdb else None,
        "structure_contact_cutoff_angstrom": args.structure_contact_cutoff if args.pdb else None,
        "sasa_probe_radius_angstrom": args.sasa_probe_radius if args.pdb and not args.skip_sasa else None,
        "sasa_sphere_points": args.sasa_sphere_points if args.pdb and not args.skip_sasa else None,
    }
    if args.pdb:
        pdb_text = args.pdb.read_text(encoding="utf-8")
        representatives = parse_pdb_representative_atoms(pdb_text)
        covariate_maps.append(contact_count_covariates(representatives, args.structure_contact_cutoff))
        metadata["n_structure_positions"] = len(representatives)
        if not args.skip_sasa:
            residue_atoms = parse_pdb_atoms(pdb_text)
            covariate_maps.append(
                approximate_sasa_covariates(
                    residue_atoms,
                    probe_radius=args.sasa_probe_radius,
                    n_sphere_points=args.sasa_sphere_points,
                )
            )
            metadata["n_sasa_positions"] = len(residue_atoms)

    covariates = merge_covariates(*covariate_maps)
    metadata["n_covariate_positions"] = len(covariates)
    write_position_covariates(args.output_json, covariates, metadata)
    print(f"Wrote {args.output_json} with {len(covariates)} residue positions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
