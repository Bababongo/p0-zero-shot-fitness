from __future__ import annotations

from collections import defaultdict

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


def summarize_records(records: list[VariantRecord]) -> dict[str, object]:
    catalytic = [record for record in records if record.is_catalytic]
    non_catalytic = [record for record in records if not record.is_catalytic]
    return {
        "n_variants": len(records),
        "n_catalytic": len(catalytic),
        "n_non_catalytic": len(non_catalytic),
        "spearman_overall": spearman_for_records(records),
        "spearman_catalytic": spearman_for_records(catalytic),
        "spearman_non_catalytic": spearman_for_records(non_catalytic),
        "top_5_enrichment_fitness_ge_0_7": top_k_enrichment(records, k=5, fitness_threshold=0.7),
        "mutation_class_breakdown": mutation_class_breakdown(records),
    }
