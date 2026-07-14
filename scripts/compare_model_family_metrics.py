from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_GROUPS = {
    "ProteinGym A4GRB6_PSEAI_Chen_2020": [
        "curated_metal_binding_site",
        "structure_metal_site_shell_5a",
        "structure_wl3_inhibitor_contact_5a",
        "active_site_neighborhood",
    ],
    "ProteinGym AMIE_PSEAE_Wrenbeck_2017": [
        "uniprot_active_site",
        "structure_catalytic_shell_5a",
        "active_site_neighborhood",
    ],
    "ProteinGym Q59976_STRSQ_Romero_2015": [
        "curated_catalytic_site",
        "structure_catalytic_shell_5a",
        "active_site_neighborhood",
    ],
}


def load_payload(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": str(path),
        "dataset": str(payload.get("dataset", "unknown")),
        "scorer": str(payload.get("scorer", "unknown")),
        "metrics": payload["metrics"],
    }


def group_read(metrics: dict[str, object], group_name: str) -> dict[str, object]:
    breakdown = metrics.get("residue_group_breakdown", {})
    if not isinstance(breakdown, dict):
        return {}
    group = breakdown.get(group_name, {})
    if not isinstance(group, dict):
        return {}

    result = {
        "n": group.get("n"),
        "spearman": group.get("spearman"),
        "outside_spearman": group.get("outside_spearman"),
    }
    matched_position = metrics.get("matched_position_null", {})
    if isinstance(matched_position, dict):
        residue_groups = matched_position.get("residue_groups", {})
        if isinstance(residue_groups, dict) and isinstance(residue_groups.get(group_name), dict):
            result["position_null_direction"] = residue_groups[group_name].get("direction")
            result["position_null_p"] = residue_groups[group_name].get("two_sided_empirical_p")

    matched_covariate = metrics.get("matched_covariate_null", {})
    if isinstance(matched_covariate, dict):
        residue_groups = matched_covariate.get("residue_groups", {})
        if isinstance(residue_groups, dict) and isinstance(residue_groups.get(group_name), dict):
            controls = residue_groups[group_name]
            if isinstance(controls, dict):
                strict = controls.get("conservation_plus_sasa") or controls.get("combined_available")
                if isinstance(strict, dict):
                    result["strict_null_direction"] = strict.get("direction")
                    result["strict_null_p"] = strict.get("two_sided_empirical_p")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare ESM-2, MSA conservation, and ProteinMPNN P0 model-family metrics."
    )
    parser.add_argument("metrics_json", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    runs = [load_payload(path) for path in args.metrics_json]
    datasets = sorted({run["dataset"] for run in runs})
    comparison = []
    for dataset in datasets:
        dataset_runs = [run for run in runs if run["dataset"] == dataset]
        group_names = DEFAULT_GROUPS.get(dataset, [])
        comparison.append(
            {
                "dataset": dataset,
                "runs": [
                    {
                        "scorer": run["scorer"],
                        "path": run["path"],
                        "spearman_overall": run["metrics"].get("spearman_overall"),
                        "spearman_catalytic": run["metrics"].get("spearman_catalytic"),
                        "spearman_non_catalytic": run["metrics"].get("spearman_non_catalytic"),
                        "groups": {
                            group_name: group_read(run["metrics"], group_name)
                            for group_name in group_names
                        },
                    }
                    for run in dataset_runs
                ],
            }
        )

    payload = {
        "comparison_type": "P0 model-family comparison",
        "model_families": [
            "ESM-2 masked marginal sequence model",
            "MSA conservation baseline",
            "ProteinMPNN fixed-backbone structure profile",
        ],
        "comparison": comparison,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
