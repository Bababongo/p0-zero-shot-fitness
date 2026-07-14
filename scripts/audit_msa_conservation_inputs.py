from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DEFAULT_DMS_IDS = [
    "BLAT_ECOLX_Firnberg_2014",
    "A4GRB6_PSEAI_Chen_2020",
    "AMIE_PSEAE_Wrenbeck_2017",
    "Q59976_STRSQ_Romero_2015",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit whether required ProteinGym MSA files exist locally.")
    parser.add_argument("--metadata-csv", type=Path, default=Path("data/proteingym/DMS_substitutions.csv"))
    parser.add_argument("--msa-dir", type=Path, default=Path("data/proteingym/msas"))
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--dms-id", action="append", default=[])
    args = parser.parse_args()

    requested_ids = set(args.dms_id or DEFAULT_DMS_IDS)
    rows = []
    with args.metadata_csv.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["DMS_id"] not in requested_ids:
                continue
            msa_path = args.msa_dir / row["MSA_filename"]
            rows.append(
                {
                    "DMS_id": row["DMS_id"],
                    "UniProt_ID": row["UniProt_ID"],
                    "MSA_filename": row["MSA_filename"],
                    "MSA_num_seqs": row["MSA_num_seqs"],
                    "MSA_N_eff": row["MSA_N_eff"],
                    "MSA_Neff_L_category": row["MSA_Neff_L_category"],
                    "expected_local_path": str(msa_path),
                    "exists_locally": msa_path.exists(),
                }
            )

    payload = {
        "status": "ready" if rows and all(row["exists_locally"] for row in rows) else "missing_msa_files",
        "metadata_csv": str(args.metadata_csv),
        "msa_dir": str(args.msa_dir),
        "required_files": rows,
        "next_step": (
            "Run scripts/derive_msa_conservation.py for each MSA, then "
            "scripts/score_msa_conservation_baseline.py against the matching scored_variants.csv."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output_json}: {payload['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
