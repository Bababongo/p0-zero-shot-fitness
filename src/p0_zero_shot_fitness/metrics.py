from __future__ import annotations

from collections import defaultdict
import math
import random

from p0_zero_shot_fitness.models import VariantRecord


PositionCovariates = dict[int, dict[str, float]]


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


def sample_sd(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    value_mean = sum(values) / len(values)
    return (sum((value - value_mean) ** 2 for value in values) / (len(values) - 1)) ** 0.5


def derived_position_covariates(records: list[VariantRecord]) -> PositionCovariates:
    """Build per-position controls available from any scored DMS table.

    These are not evolutionary conservation scores. They are local, audit-style
    covariates used to test whether residue-slice results are explained by
    mutation coverage, experimental variance, model-score sensitivity, or
    position along the sequence.
    """
    grouped: dict[int, list[VariantRecord]] = defaultdict(list)
    for record in records:
        grouped[record.mutation.position].append(record)

    all_positions = sorted(grouped)
    min_position = min(all_positions) if all_positions else 0
    max_position = max(all_positions) if all_positions else 0
    position_span = max(1, max_position - min_position)
    covariates: PositionCovariates = {}
    for position, position_records in grouped.items():
        fitness_values = [record.fitness for record in position_records]
        score_values = [record.model_score for record in position_records]
        covariates[position] = {
            "mutation_count": float(len(position_records)),
            "fitness_mean": sum(fitness_values) / len(fitness_values),
            "fitness_sd": sample_sd(fitness_values),
            "fitness_range": max(fitness_values) - min(fitness_values),
            "model_score_mean": sum(score_values) / len(score_values),
            "model_score_sd": sample_sd(score_values),
            "relative_position": (position - min_position) / position_span,
        }
    return covariates


def merge_position_covariates(*covariate_maps: PositionCovariates | None) -> PositionCovariates:
    merged: PositionCovariates = {}
    for covariate_map in covariate_maps:
        if not covariate_map:
            continue
        for position, covariates in covariate_map.items():
            merged.setdefault(position, {}).update(covariates)
    return merged


def available_covariate_sets(position_covariates: PositionCovariates) -> dict[str, list[str]]:
    available = {
        covariate_name
        for covariates in position_covariates.values()
        for covariate_name in covariates
    }
    requested_sets = {
        "mutation_count": ["mutation_count"],
        "fitness_variance": ["fitness_sd"],
        "fitness_distribution": ["fitness_mean", "fitness_sd", "fitness_range"],
        "model_score_sensitivity": ["model_score_mean", "model_score_sd"],
        "relative_position": ["relative_position"],
        "structure_contact_density": ["structure_contact_count_10a"],
        "structure_solvent_accessibility": ["structure_relative_sasa_approx"],
        "combined_available": [
            "mutation_count",
            "fitness_sd",
            "fitness_range",
            "model_score_mean",
            "model_score_sd",
            "relative_position",
            "structure_contact_count_10a",
            "structure_relative_sasa_approx",
        ],
    }
    return {
        name: [covariate for covariate in covariates if covariate in available]
        for name, covariates in requested_sets.items()
        if any(covariate in available for covariate in covariates)
    }


def _complete_positions(
    positions: list[int],
    position_covariates: PositionCovariates,
    covariate_names: list[str],
) -> list[int]:
    return [
        position
        for position in positions
        if all(covariate_name in position_covariates.get(position, {}) for covariate_name in covariate_names)
    ]


def _covariate_standardization(
    positions: list[int],
    position_covariates: PositionCovariates,
    covariate_names: list[str],
) -> dict[str, tuple[float, float]]:
    standardization = {}
    for covariate_name in covariate_names:
        values = [position_covariates[position][covariate_name] for position in positions]
        value_mean = sum(values) / len(values)
        value_sd = sample_sd(values)
        standardization[covariate_name] = (value_mean, value_sd if value_sd > 0 else 1.0)
    return standardization


def _covariate_distance(
    left_position: int,
    right_position: int,
    position_covariates: PositionCovariates,
    covariate_names: list[str],
    standardization: dict[str, tuple[float, float]],
) -> float:
    total = 0.0
    for covariate_name in covariate_names:
        mean_value, sd_value = standardization[covariate_name]
        left = (position_covariates[left_position][covariate_name] - mean_value) / sd_value
        right = (position_covariates[right_position][covariate_name] - mean_value) / sd_value
        total += (left - right) ** 2
    return math.sqrt(total)


def covariate_matched_null_control(
    records: list[VariantRecord],
    target_positions: set[int],
    position_covariates: PositionCovariates,
    covariate_names: list[str],
    iterations: int = 1000,
    seed: int = 707,
    nearest_pool_size: int = 25,
) -> dict[str, object]:
    target_records = records_at_positions(records, target_positions)
    all_positions = sorted({record.mutation.position for record in records})
    target_positions_with_covariates = _complete_positions(
        sorted(target_positions),
        position_covariates,
        covariate_names,
    )
    candidate_positions = _complete_positions(
        [position for position in all_positions if position not in target_positions],
        position_covariates,
        covariate_names,
    )
    observed = spearman_for_records(records_at_positions(records, set(target_positions_with_covariates)))

    empty_result = {
        "covariates": covariate_names,
        "n_positions": len(target_positions),
        "n_positions_with_covariates": len(target_positions_with_covariates),
        "n_variants": len(target_records),
        "iterations": iterations,
        "observed_spearman": observed,
        "null_mean": None,
        "null_ci_low": None,
        "null_ci_high": None,
        "percentile_rank": None,
        "two_sided_empirical_p": None,
        "direction": None,
        "nearest_pool_size": nearest_pool_size,
        "candidate_positions": len(candidate_positions),
    }
    if (
        not covariate_names
        or len(target_positions_with_covariates) == 0
        or len(candidate_positions) == 0
        or observed is None
        or iterations <= 0
    ):
        return empty_result

    standardization = _covariate_standardization(
        target_positions_with_covariates + candidate_positions,
        position_covariates,
        covariate_names,
    )
    nearest_candidates: dict[int, list[int]] = {}
    for target_position in target_positions_with_covariates:
        ranked_candidates = sorted(
            candidate_positions,
            key=lambda candidate_position: _covariate_distance(
                target_position,
                candidate_position,
                position_covariates,
                covariate_names,
                standardization,
            ),
        )
        nearest_candidates[target_position] = ranked_candidates[: max(1, nearest_pool_size)]

    rng = random.Random(seed)
    estimates: list[float] = []
    for _ in range(iterations):
        sampled_positions: set[int] = set()
        ordered_targets = list(target_positions_with_covariates)
        rng.shuffle(ordered_targets)
        for target_position in ordered_targets:
            pool = [position for position in nearest_candidates[target_position] if position not in sampled_positions]
            if not pool:
                pool = nearest_candidates[target_position]
            sampled_positions.add(rng.choice(pool))
        if len(sampled_positions) < len(target_positions_with_covariates):
            remaining = [position for position in candidate_positions if position not in sampled_positions]
            rng.shuffle(remaining)
            needed = len(target_positions_with_covariates) - len(sampled_positions)
            sampled_positions.update(remaining[:needed])
        estimate = spearman_for_records(records_at_positions(records, sampled_positions))
        if estimate is not None:
            estimates.append(estimate)

    if not estimates:
        return empty_result

    null_ci_low = percentile(estimates, 0.025)
    null_ci_high = percentile(estimates, 0.975)
    less_equal = sum(estimate <= observed for estimate in estimates) / len(estimates)
    greater_equal = sum(estimate >= observed for estimate in estimates) / len(estimates)
    two_sided_p = min(1.0, 2 * min(less_equal, greater_equal))
    if null_ci_high is not None and observed > null_ci_high:
        direction = "higher_than_covariate_matched_null"
    elif null_ci_low is not None and observed < null_ci_low:
        direction = "lower_than_covariate_matched_null"
    else:
        direction = "inside_covariate_matched_null_interval"

    return {
        "covariates": covariate_names,
        "n_positions": len(target_positions),
        "n_positions_with_covariates": len(target_positions_with_covariates),
        "n_variants": len(records_at_positions(records, set(target_positions_with_covariates))),
        "iterations": iterations,
        "observed_spearman": observed,
        "null_mean": sum(estimates) / len(estimates),
        "null_ci_low": null_ci_low,
        "null_ci_high": null_ci_high,
        "percentile_rank": less_equal,
        "two_sided_empirical_p": two_sided_p,
        "direction": direction,
        "nearest_pool_size": nearest_pool_size,
        "candidate_positions": len(candidate_positions),
    }


def matched_covariate_null_controls(
    records: list[VariantRecord],
    position_covariates: PositionCovariates,
    iterations: int = 1000,
    seed: int = 707,
    nearest_pool_size: int = 25,
) -> dict[str, object]:
    covariate_sets = available_covariate_sets(position_covariates)
    catalytic_positions = {record.mutation.position for record in records if record.is_catalytic}
    group_names = sorted({group_name for record in records for group_name in record.residue_groups})

    def controls_for_positions(target_positions: set[int], offset: int) -> dict[str, object]:
        return {
            control_name: covariate_matched_null_control(
                records,
                target_positions,
                position_covariates,
                covariate_names,
                iterations=iterations,
                seed=seed + offset * 100 + control_offset,
                nearest_pool_size=nearest_pool_size,
            )
            for control_offset, (control_name, covariate_names) in enumerate(covariate_sets.items())
        }

    residue_groups = {}
    for offset, group_name in enumerate(group_names, start=1):
        group_positions = {
            record.mutation.position
            for record in records
            if group_name in record.residue_groups
        }
        residue_groups[group_name] = controls_for_positions(group_positions, offset)
    return {
        "available_covariate_sets": covariate_sets,
        "catalytic": controls_for_positions(catalytic_positions, 0),
        "residue_groups": residue_groups,
    }


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
    position_covariates: PositionCovariates | None = None,
    covariate_null_iterations: int = 0,
    covariate_null_seed: int = 707,
    covariate_nearest_pool_size: int = 25,
) -> dict[str, object]:
    catalytic = [record for record in records if record.is_catalytic]
    non_catalytic = [record for record in records if not record.is_catalytic]
    derived_covariates = derived_position_covariates(records)
    merged_covariates = merge_position_covariates(derived_covariates, position_covariates)
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
    if covariate_null_iterations > 0:
        summary["matched_covariate_null"] = matched_covariate_null_controls(
            records,
            merged_covariates,
            iterations=covariate_null_iterations,
            seed=covariate_null_seed,
            nearest_pool_size=covariate_nearest_pool_size,
        )
    return summary
