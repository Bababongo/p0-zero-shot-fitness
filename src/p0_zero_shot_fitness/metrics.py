from __future__ import annotations

from collections import defaultdict
import random

from p0_zero_shot_fitness.models import VariantRecord


def rank_values(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(indexed):
        end = index + 1
        while end < len(indexed) and indexed[end][1] == indexed[index][1]:
            end += 1
        average_rank = (index + 1 + end) / 2
        for original_index, _ in indexed[index:end]:
            ranks[original_index] = average_rank
        index = end
    return ranks


def pearson(x_values: list[float], y_values: list[float]) -> float | None:
    if len(x_values) != len(y_values) or len(x_values) < 2:
        return None
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    x_denom = sum((x - x_mean) ** 2 for x in x_values) ** 0.5
    y_denom = sum((y - y_mean) ** 2 for y in y_values) ** 0.5
    if x_denom == 0 or y_denom == 0:
        return None
    return numerator / (x_denom * y_denom)


def spearman(x_values: list[float], y_values: list[float]) -> float | None:
    if len(x_values) < 2:
        return None
    return pearson(rank_values(x_values), rank_values(y_values))


def spearman_for_records(records: list[VariantRecord]) -> float | None:
    return spearman(
        [record.model_score for record in records],
        [record.fitness for record in records],
    )


def top_k_enrichment(records: list[VariantRecord], k: int = 5, fitness_threshold: float = 0.7) -> float | None:
    if not records or k <= 0:
        return None
    top_records = sorted(records, key=lambda record: record.model_score, reverse=True)[:k]
    background_rate = sum(record.fitness >= fitness_threshold for record in records) / len(records)
    top_rate = sum(record.fitness >= fitness_threshold for record in top_records) / len(top_records)
    if background_rate == 0:
        return None
    return top_rate / background_rate


def mutation_class_breakdown(records: list[VariantRecord]) -> dict[str, dict[str, float | int | None]]:
    grouped: dict[str, list[VariantRecord]] = defaultdict(list)
    for record in records:
        grouped[record.mutation.mutation_class].append(record)

    breakdown: dict[str, dict[str, float | int | None]] = {}
    for mutation_class, class_records in sorted(grouped.items()):
        breakdown[mutation_class] = {
            "n": len(class_records),
            "mean_fitness": sum(record.fitness for record in class_records) / len(class_records),
            "mean_model_score": sum(record.model_score for record in class_records) / len(class_records),
            "spearman": spearman_for_records(class_records),
        }
    return breakdown


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    sorted_values = sorted(values)
    position = (len(sorted_values) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def bootstrap_spearman_ci(
    records: list[VariantRecord],
    iterations: int = 1000,
    seed: int = 13,
    confidence: float = 0.95,
) -> dict[str, float | int | None]:
    if len(records) < 3 or iterations <= 0:
        return {
            "n": len(records),
            "iterations": iterations,
            "estimate": spearman_for_records(records),
            "ci_low": None,
            "ci_high": None,
        }

    rng = random.Random(seed)
    estimates: list[float] = []
    for _ in range(iterations):
        sample = [records[rng.randrange(len(records))] for _ in records]
        estimate = spearman_for_records(sample)
        if estimate is not None:
            estimates.append(estimate)

    alpha = 1 - confidence
    return {
        "n": len(records),
        "iterations": iterations,
        "estimate": spearman_for_records(records),
        "ci_low": percentile(estimates, alpha / 2),
        "ci_high": percentile(estimates, 1 - alpha / 2),
    }


def bootstrap_group_cis(
    records: list[VariantRecord],
    iterations: int = 1000,
    seed: int = 13,
) -> dict[str, dict[str, float | int | None]]:
    catalytic = [record for record in records if record.is_catalytic]
    non_catalytic = [record for record in records if not record.is_catalytic]
    return {
        "spearman_overall": bootstrap_spearman_ci(records, iterations=iterations, seed=seed),
        "spearman_catalytic": bootstrap_spearman_ci(catalytic, iterations=iterations, seed=seed + 1),
        "spearman_non_catalytic": bootstrap_spearman_ci(non_catalytic, iterations=iterations, seed=seed + 2),
    }


def bootstrap_residue_group_cis(
    records: list[VariantRecord],
    iterations: int = 1000,
    seed: int = 101,
) -> dict[str, dict[str, dict[str, float | int | None]]]:
    group_names = sorted({group_name for record in records for group_name in record.residue_groups})
    intervals: dict[str, dict[str, dict[str, float | int | None]]] = {}
    for offset, group_name in enumerate(group_names):
        in_group = [record for record in records if group_name in record.residue_groups]
        outside_group = [record for record in records if group_name not in record.residue_groups]
        intervals[group_name] = {
            "in_group": bootstrap_spearman_ci(
                in_group,
                iterations=iterations,
                seed=seed + offset * 2,
            ),
            "outside_group": bootstrap_spearman_ci(
                outside_group,
                iterations=iterations,
                seed=seed + offset * 2 + 1,
            ),
        }
    return intervals


def records_at_positions(records: list[VariantRecord], positions: set[int]) -> list[VariantRecord]:
    return [record for record in records if record.mutation.position in positions]


def position_matched_null_control(
    records: list[VariantRecord],
    target_positions: set[int],
    iterations: int = 1000,
    seed: int = 2026,
) -> dict[str, float | int | str | None]:
    """Compare a residue slice to random residue-position slices of the same size."""
    target_records = records_at_positions(records, target_positions)
    observed = spearman_for_records(target_records)
    all_positions = sorted({record.mutation.position for record in records})
    candidate_positions = [position for position in all_positions if position not in target_positions]

    if not target_positions or len(target_records) < 2 or iterations <= 0:
        return {
            "n_positions": len(target_positions),
            "n_variants": len(target_records),
            "iterations": iterations,
            "observed_spearman": observed,
            "null_mean": None,
            "null_ci_low": None,
            "null_ci_high": None,
            "percentile_rank": None,
            "two_sided_empirical_p": None,
            "direction": None,
        }

    sample_size = len(target_positions)
    if len(candidate_positions) < sample_size:
        candidate_positions = all_positions

    rng = random.Random(seed)
    estimates: list[float] = []
    for _ in range(iterations):
        sampled_positions = set(rng.sample(candidate_positions, sample_size))
        estimate = spearman_for_records(records_at_positions(records, sampled_positions))
        if estimate is not None:
            estimates.append(estimate)

    if observed is None or not estimates:
        return {
            "n_positions": len(target_positions),
            "n_variants": len(target_records),
            "iterations": iterations,
            "observed_spearman": observed,
            "null_mean": None,
            "null_ci_low": None,
            "null_ci_high": None,
            "percentile_rank": None,
            "two_sided_empirical_p": None,
            "direction": None,
        }

    null_ci_low = percentile(estimates, 0.025)
    null_ci_high = percentile(estimates, 0.975)
    less_equal = sum(estimate <= observed for estimate in estimates) / len(estimates)
    greater_equal = sum(estimate >= observed for estimate in estimates) / len(estimates)
    two_sided_p = min(1.0, 2 * min(less_equal, greater_equal))
    if null_ci_high is not None and observed > null_ci_high:
        direction = "higher_than_position_matched_null"
    elif null_ci_low is not None and observed < null_ci_low:
        direction = "lower_than_position_matched_null"
    else:
        direction = "inside_position_matched_null_interval"

    return {
        "n_positions": len(target_positions),
        "n_variants": len(target_records),
        "iterations": iterations,
        "observed_spearman": observed,
        "null_mean": sum(estimates) / len(estimates),
        "null_ci_low": null_ci_low,
        "null_ci_high": null_ci_high,
        "percentile_rank": less_equal,
        "two_sided_empirical_p": two_sided_p,
        "direction": direction,
    }


def matched_position_null_controls(
    records: list[VariantRecord],
    iterations: int = 1000,
    seed: int = 2026,
) -> dict[str, object]:
    catalytic_positions = {record.mutation.position for record in records if record.is_catalytic}
    group_names = sorted({group_name for record in records for group_name in record.residue_groups})
    residue_groups = {}
    for offset, group_name in enumerate(group_names):
        group_positions = {
            record.mutation.position
            for record in records
            if group_name in record.residue_groups
        }
        residue_groups[group_name] = position_matched_null_control(
            records,
            group_positions,
            iterations=iterations,
            seed=seed + offset + 1,
        )
    return {
        "catalytic": position_matched_null_control(
            records,
            catalytic_positions,
            iterations=iterations,
            seed=seed,
        ),
        "residue_groups": residue_groups,
    }


def residue_group_breakdown(records: list[VariantRecord]) -> dict[str, dict[str, float | int | None]]:
    group_names = sorted({group_name for record in records for group_name in record.residue_groups})
    breakdown: dict[str, dict[str, float | int | None]] = {}
    for group_name in group_names:
        in_group = [record for record in records if group_name in record.residue_groups]
        outside_group = [record for record in records if group_name not in record.residue_groups]
        breakdown[group_name] = {
            "n": len(in_group),
            "spearman": spearman_for_records(in_group),
            "mean_fitness": sum(record.fitness for record in in_group) / len(in_group) if in_group else None,
            "mean_model_score": sum(record.model_score for record in in_group) / len(in_group) if in_group else None,
            "outside_n": len(outside_group),
            "outside_spearman": spearman_for_records(outside_group),
        }
    return breakdown


def summarize_records(
    records: list[VariantRecord],
    bootstrap_iterations: int = 0,
    bootstrap_seed: int = 13,
    null_iterations: int = 0,
    null_seed: int = 2026,
) -> dict[str, object]:
    catalytic = [record for record in records if record.is_catalytic]
    non_catalytic = [record for record in records if not record.is_catalytic]
    summary: dict[str, object] = {
        "n_variants": len(records),
        "n_catalytic": len(catalytic),
        "n_non_catalytic": len(non_catalytic),
        "spearman_overall": spearman_for_records(records),
        "spearman_catalytic": spearman_for_records(catalytic),
        "spearman_non_catalytic": spearman_for_records(non_catalytic),
        "top_5_enrichment_fitness_ge_0_7": top_k_enrichment(records, k=5, fitness_threshold=0.7),
        "mutation_class_breakdown": mutation_class_breakdown(records),
        "residue_group_breakdown": residue_group_breakdown(records),
    }
    if bootstrap_iterations > 0:
        summary["bootstrap_ci"] = bootstrap_group_cis(
            records,
            iterations=bootstrap_iterations,
            seed=bootstrap_seed,
        )
        summary["residue_group_bootstrap_ci"] = bootstrap_residue_group_cis(
            records,
            iterations=bootstrap_iterations,
            seed=bootstrap_seed + 1000,
        )
    if null_iterations > 0:
        summary["matched_position_null"] = matched_position_null_controls(
            records,
            iterations=null_iterations,
            seed=null_seed,
        )
    return summary
