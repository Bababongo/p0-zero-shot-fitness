from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p0_zero_shot_fitness.io import write_json
from p0_zero_shot_fitness.panel import validate_panel_registry


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the P0 enzyme-panel registry against ProteinGym metadata.")
    parser.add_argument("--panel-csv", type=Path, default=ROOT / "data" / "panels" / "p0_enzyme_panel_candidates.csv")
    parser.add_argument("--proteingym-metadata-csv", type=Path, default=ROOT / "data" / "proteingym" / "DMS_substitutions.csv")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "proteingym")
    parser.add_argument("--output-json", type=Path, default=ROOT / "results" / "panel_registry_validation.json")
    args = parser.parse_args()

    payload = validate_panel_registry(
        panel_csv=args.panel_csv,
        proteingym_metadata_csv=args.proteingym_metadata_csv,
        data_dir=args.data_dir,
    )
    write_json(args.output_json, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
