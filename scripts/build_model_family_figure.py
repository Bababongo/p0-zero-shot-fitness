from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from pathlib import Path


DATASET_LABELS = {
    "ProteinGym A4GRB6_PSEAI_Chen_2020": ("VIM-2", "metallo-beta-lactamase"),
    "ProteinGym AMIE_PSEAE_Wrenbeck_2017": ("AMIE", "aliphatic amidase"),
    "ProteinGym Q59976_STRSQ_Romero_2015": ("Beta-glucosidase", "GH1 glycoside hydrolase"),
}

SCORER_LABELS = {
    "ESM2MaskedMarginalScorer": "ESM-2",
    "MSAConservationLogOddsScorer": "MSA",
    "ProteinMPNNProfileScorer": "ProteinMPNN",
}

SCORER_COLORS = {
    "ESM-2": "#2c7fb8",
    "MSA": "#5a7d38",
    "ProteinMPNN": "#b55b32",
}


@dataclass(frozen=True)
class ModelFamilyRun:
    label: str
    overall: float
    exact_site: float
    background: float


@dataclass(frozen=True)
class DatasetComparison:
    short_name: str
    enzyme_class: str
    runs: list[ModelFamilyRun]


def load_comparison(path: Path) -> list[DatasetComparison]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    comparisons: list[DatasetComparison] = []
    for dataset in payload["comparison"]:
        short_name, enzyme_class = DATASET_LABELS[str(dataset["dataset"])]
        runs = []
        for run in dataset["runs"]:
            label = SCORER_LABELS[str(run["scorer"])]
            runs.append(
                ModelFamilyRun(
                    label=label,
                    overall=float(run["spearman_overall"]),
                    exact_site=float(run["spearman_catalytic"]),
                    background=float(run["spearman_non_catalytic"]),
                )
            )
        comparisons.append(DatasetComparison(short_name=short_name, enzyme_class=enzyme_class, runs=runs))
    return comparisons


def x_for(value: float, *, left: float, width: float, max_value: float = 0.70) -> float:
    return left + (value / max_value) * width


def fmt(value: float) -> str:
    return f"{value:.3f}"


def svg_text_lines(*, x: float, y: float, lines: list[str], size: int, fill: str, weight: str | None = None) -> list[str]:
    attrs = [
        f'x="{x}"',
        f'y="{y}"',
        'font-family="Inter, Helvetica, Arial, sans-serif"',
        f'font-size="{size}"',
        f'fill="{fill}"',
    ]
    if weight is not None:
        attrs.append(f'font-weight="{weight}"')
    text = [f"<text {' '.join(attrs)}>"]
    for idx, line in enumerate(lines):
        dy = 0 if idx == 0 else size + 5
        text.append(f'<tspan x="{x}" dy="{dy}">{html.escape(line)}</tspan>')
    text.append("</text>")
    return text


def build_svg(comparisons: list[DatasetComparison]) -> str:
    width = 1500
    height = 860
    chart_left = 315
    chart_width = 805
    row_top = 220
    row_gap = 168
    bar_gap = 36
    bar_height = 20
    axis_y = 735

    palette = {
        "bg": "#f8f5ee",
        "ink": "#17201c",
        "muted": "#65746d",
        "grid": "#d8d1c5",
        "line": "#b9ad9c",
        "panel": "#eee9df",
        "callout": "#e7eee9",
        "exact": "#1f1f1f",
        "background": "#ffffff",
    }

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">P0 model-family comparison</title>',
        '<desc id="desc">A comparison of ESM-2, MSA conservation, and ProteinMPNN Spearman correlations across VIM-2, AMIE, and beta-glucosidase.</desc>',
        f'<rect width="{width}" height="{height}" rx="28" fill="{palette["bg"]}"/>',
        f'<text x="58" y="66" font-family="Inter, Helvetica, Arial, sans-serif" font-size="32" font-weight="700" fill="{palette["ink"]}">P0 model-family comparison</text>',
        f'<text x="58" y="103" font-family="Inter, Helvetica, Arial, sans-serif" font-size="17" fill="{palette["muted"]}">Same DMS assays, same mechanism labels, different biological inductive biases.</text>',
        f'<text x="58" y="145" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" font-weight="700" letter-spacing="1.5" fill="{palette["muted"]}">OVERALL BARS + EXACT CATALYTIC/METAL-SITE DOTS</text>',
    ]

    # Legend.
    legend_x = 58
    legend_y = 184
    for idx, (label, color) in enumerate(SCORER_COLORS.items()):
        x = legend_x + idx * 155
        parts.append(f'<rect x="{x}" y="{legend_y - 14}" width="32" height="14" rx="7" fill="{color}"/>')
        parts.append(f'<text x="{x + 42}" y="{legend_y - 3}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" fill="{palette["muted"]}">{html.escape(label)}</text>')
    parts.append(f'<circle cx="555" cy="{legend_y - 7}" r="7" fill="{palette["exact"]}"/>')
    parts.append(f'<text x="570" y="{legend_y - 3}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" fill="{palette["muted"]}">exact catalytic or metal-site Spearman</text>')

    # Axis and grid.
    for tick in [0.0, 0.25, 0.50, 0.70]:
        x = x_for(tick, left=chart_left, width=chart_width)
        parts.append(f'<line x1="{x:.1f}" y1="206" x2="{x:.1f}" y2="{axis_y}" stroke="{palette["grid"]}" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{axis_y + 30}" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" fill="{palette["muted"]}">{tick:.2f}</text>')
    parts.append(f'<text x="{chart_left + chart_width / 2:.1f}" y="{axis_y + 60}" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="14" fill="{palette["muted"]}">Spearman correlation against experimental DMS fitness</text>')

    # Dataset rows.
    for row_idx, comparison in enumerate(comparisons):
        y0 = row_top + row_idx * row_gap
        safe_name = html.escape(comparison.short_name)
        safe_class = html.escape(comparison.enzyme_class)
        parts.append(f'<text x="58" y="{y0 + 16}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="22" font-weight="700" fill="{palette["ink"]}">{safe_name}</text>')
        parts.append(f'<text x="58" y="{y0 + 42}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" fill="{palette["muted"]}">{safe_class}</text>')

        for run_idx, run in enumerate(comparison.runs):
            y = y0 + run_idx * bar_gap
            color = SCORER_COLORS[run.label]
            overall_x = x_for(run.overall, left=chart_left, width=chart_width)
            exact_x = x_for(run.exact_site, left=chart_left, width=chart_width)
            background_x = x_for(run.background, left=chart_left, width=chart_width)
            safe_label = html.escape(run.label)
            parts.extend(
                [
                    f'<text x="205" y="{y + 16}" text-anchor="end" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" font-weight="700" fill="{palette["muted"]}">{safe_label}</text>',
                    f'<line x1="{chart_left}" y1="{y + 10}" x2="{chart_left + chart_width}" y2="{y + 10}" stroke="{palette["line"]}" stroke-width="1" opacity="0.45"/>',
                    f'<rect x="{chart_left}" y="{y}" width="{overall_x - chart_left:.1f}" height="{bar_height}" rx="10" fill="{color}"/>',
                    f'<text x="{overall_x + 10:.1f}" y="{y + 15}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="12" font-weight="700" fill="{palette["ink"]}">{fmt(run.overall)}</text>',
                    f'<circle cx="{background_x:.1f}" cy="{y + 10}" r="7" fill="{palette["background"]}" stroke="{color}" stroke-width="2"/>',
                    f'<circle cx="{exact_x:.1f}" cy="{y + 10}" r="7" fill="{palette["exact"]}"/>',
                ]
            )

        # Callout per row.
        if comparison.short_name == "VIM-2":
            callout = ["ProteinMPNN wins overall,", "but drops at metal-site", "residues."]
        elif comparison.short_name == "AMIE":
            callout = ["MSA is strongest overall;", "ProteinMPNN does not", "rescue catalysis."]
        else:
            callout = ["High exact-site score,", "but n is tiny and the", "broader shell is weak."]
        parts.append(f'<rect x="1160" y="{y0 - 8}" width="282" height="82" rx="18" fill="{palette["panel"]}" stroke="{palette["line"]}" stroke-width="1"/>')
        parts.append(f'<text x="1183" y="{y0 + 18}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" font-weight="700" fill="{palette["ink"]}">Read</text>')
        parts.extend(svg_text_lines(x=1183, y=y0 + 41, lines=callout, size=12, fill=palette["muted"]))
    parts.extend(
        [
            f'<rect x="58" y="805" width="1384" height="42" rx="16" fill="{palette["callout"]}" stroke="{palette["line"]}" stroke-width="1"/>',
            f'<text x="84" y="831" font-family="Inter, Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="{palette["ink"]}">Takeaway</text>',
            f'<text x="170" y="831" font-family="Inter, Helvetica, Arial, sans-serif" font-size="14" fill="{palette["ink"]}">Global fitness ranking and mechanism-local behavior can diverge across model families.</text>',
        ]
    )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the P0 model-family comparison SVG figure.")
    parser.add_argument(
        "--comparison-json",
        type=Path,
        default=Path("results/proteingym_ready_enzyme_model_family_comparison.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/assets/p0_model_family_comparison.svg"),
    )
    args = parser.parse_args()

    comparisons = load_comparison(args.comparison_json)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_svg(comparisons), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
