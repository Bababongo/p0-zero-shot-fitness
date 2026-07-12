from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p0_zero_shot_fitness.proteingym import materialize_proteingym_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize one ProteinGym substitution dataset locally.")
    parser.add_argument("--dms-id", default="A4GRB6_PSEAI_Chen_2020")
    parser.add_argument("--metadata-csv", type=Path, default=ROOT / "data" / "proteingym" / "DMS_substitutions.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "proteingym")
    parser.add_argument("--archive-path", type=Path, default=None, help="Optional ProteinGym substitutions zip path.")
    args = parser.parse_args()

    payload = materialize_proteingym_dataset(
        dms_id=args.dms_id,
        metadata_csv=args.metadata_csv,
        output_dir=args.output_dir,
        archive_path=args.archive_path,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
