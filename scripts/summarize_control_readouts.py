from __future__ import annotations

import argparse
import json
from pathlib import Path


CONTROL_NAMES = [
    "mutation_count",
    "fitness_variance",
    "fitness_distribution",
    "model_score_sensitivity",
    "structure_contact_density",
    "structure_solvent_accessibility",
    "msa_conservation",
    "conservation_plus_sasa",
    "combined_available",
]


def slim_control(control: dict | None) -> dict | None:
    if not control:
        return None
    return {
        "observed_spearman": control.get("observed_spearman"),
        "direction": control.get("direction"),
        "two_sided_empirical_p": control.get("two_sided_empirical_p"),
        "null_ci_low": control.get("null_ci_low"),
        "null_ci_high": control.get("null_ci_high"),
        "n_positions": control.get("n_positions"),
        "n_variants": control.get("n_variants"),
    }


def slim_covariate_controls(controls: dict | None) -> dict[str, dict | None]:
    controls = controls or {}
    return {
        control_name: slim_control(controls.get(control_name))
        for control_name in CONTROL_NAMES
        if control_name in controls
    }


def summarize_metrics(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    metrics = payload["metrics"]
    position_null = metrics.get("matched_position_null", {})
    covariate_null = metrics.get("matched_covariate_null", {})
    rows = {
        "catalytic": {
            "position_matched": slim_control(position_null.get("catalytic")),
            "covariate_matched": slim_covariate_controls(covariate_null.get("catalytic")),
        }
    }
    for group_name, group_position_control in position_null.get("residue_groups", {}).items():
        rows[group_name] = {
            "position_matched": slim_control(group_position_control),
            "covariate_matched": slim_covariate_controls(
                covariate_null.get("residue_groups", {}).get(group_name)
            ),
        }
    return {
        "dataset": payload.get("dataset", "fixture"),
        "scorer": payload["scorer"],
        "path": str(path),
        "spearman_overall": metrics.get("spearman_overall"),
        "spearman_catalytic": metrics.get("spearman_catalytic"),
        "spearman_non_catalytic": metrics.get("spearman_non_catalytic"),
        "control_readouts": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize P0 position and covariate control readouts.")
    parser.add_argument("metrics_json", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    summary = {
        "control_names": CONTROL_NAMES,
        "runs": [summarize_metrics(path) for path in args.metrics_json],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
