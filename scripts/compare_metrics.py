from __future__ import annotations

import argparse
import json
from pathlib import Path


KEY_METRICS = [
    "n_variants",
    "n_catalytic",
    "n_non_catalytic",
    "spearman_overall",
    "spearman_catalytic",
    "spearman_non_catalytic",
    "top_5_enrichment_fitness_ge_0_7",
]


def load_metrics(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": str(path),
        "dataset": payload.get("dataset", "fixture"),
        "scorer": payload["scorer"],
        "metrics": payload["metrics"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare P0 benchmark metric JSON files.")
    parser.add_argument("metrics_json", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    runs = [load_metrics(path) for path in args.metrics_json]
    comparison = {
        "comparison": [
            {
                "dataset": run["dataset"],
                "scorer": run["scorer"],
                "path": run["path"],
                "metrics": {metric: run["metrics"].get(metric) for metric in KEY_METRICS},
            }
            for run in runs
        ]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(comparison, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
