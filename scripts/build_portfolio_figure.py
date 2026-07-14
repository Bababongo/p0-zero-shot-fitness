from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EnzymePanelRow:
    short_name: str
    enzyme_class: str
    variants: int
    overall: float
    exact_site: float
    active_neighborhood: float
    null_read: str
    null_p: float


DATASET_LABELS = {
    "ProteinGym BLAT_ECOLX_Firnberg_2014": ("TEM-1", "serine beta-lactamase"),
    "ProteinGym A4GRB6_PSEAI_Chen_2020": ("VIM-2", "metallo-beta-lactamase"),
    "ProteinGym AMIE_PSEAE_Wrenbeck_2017": ("AMIE", "aliphatic amidase"),
    "ProteinGym Q59976_STRSQ_Romero_2015": ("Beta-glucosidase", "GH1 glycoside hydrolase"),
}


def load_rows(comparison_json: Path) -> list[EnzymePanelRow]:
    payload = json.loads(comparison_json.read_text(encoding="utf-8"))
    rows: list[EnzymePanelRow] = []
    for run in payload["comparison"]:
        dataset = run["dataset"]
        short_name, enzyme_class = DATASET_LABELS[dataset]
        metrics = run["metrics"]
        active = metrics["residue_group_breakdown"]["active_site_neighborhood"]
        null = metrics["matched_position_null"]["residue_groups"]["active_site_neighborhood"]
        rows.append(
            EnzymePanelRow(
                short_name=short_name,
                enzyme_class=enzyme_class,
                variants=int(metrics["n_variants"]),
                overall=float(metrics["spearman_overall"]),
                exact_site=float(metrics["spearman_catalytic"]),
                active_neighborhood=float(active["spearman"]),
                null_read=str(null["direction"]),
                null_p=float(null["two_sided_empirical_p"]),
            )
        )
    return rows


def x_for(value: float, *, left: float, width: float, max_value: float = 0.75) -> float:
    return left + (value / max_value) * width


def fmt(value: float) -> str:
    return f"{value:.3f}"


def null_label(row: EnzymePanelRow) -> str:
    if row.null_read == "higher_than_position_matched_null":
        return f"clears matched null, p={row.null_p:.3f}"
    return f"inside matched null, p={row.null_p:.3f}"


def build_svg(rows: list[EnzymePanelRow]) -> str:
    width = 1400
    height = 760
    chart_left = 265
    chart_width = 735
    row_top = 220
    row_gap = 98
    bar_height = 20
    axis_y = 575

    palette = {
        "bg": "#f7f4ed",
        "ink": "#18201d",
        "muted": "#60716b",
        "grid": "#d8d0c2",
        "overall": "#27847a",
        "exact": "#c37a2c",
        "active": "#6257a8",
        "callout": "#e8efe9",
        "line": "#b8ad9b",
    }

    total_variants = sum(row.variants for row in rows)
    active_hits = sum(1 for row in rows if row.null_read == "higher_than_position_matched_null")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">P0 four-enzyme ESM-2 35M portfolio figure</title>",
        "<desc id=\"desc\">A chart comparing overall, exact catalytic-site, and active-site-neighborhood Spearman correlations across four enzyme DMS datasets.</desc>",
        f'<rect width="{width}" height="{height}" rx="28" fill="{palette["bg"]}"/>',
        f'<text x="56" y="62" font-family="Inter, Helvetica, Arial, sans-serif" font-size="30" font-weight="700" fill="{palette["ink"]}">P0: Mechanism-sliced protein fitness</text>',
        f'<text x="56" y="98" font-family="Inter, Helvetica, Arial, sans-serif" font-size="17" fill="{palette["muted"]}">ESM-2 35M improves global ranking, but mechanism-slice claims need matched controls.</text>',
        f'<text x="56" y="139" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" font-weight="700" letter-spacing="1.6" fill="{palette["muted"]}">FOUR ENZYMES • {total_variants:,} SINGLE MUTANTS • ACTIVE-SITE-NEIGHBORHOOD NULL HITS: {active_hits}/4</text>',
    ]

    # Axis and grid.
    for tick in [0.0, 0.25, 0.50, 0.75]:
        x = x_for(tick, left=chart_left, width=chart_width)
        parts.append(f'<line x1="{x:.1f}" y1="164" x2="{x:.1f}" y2="{axis_y}" stroke="{palette["grid"]}" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{axis_y + 30}" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" fill="{palette["muted"]}">{tick:.2f}</text>')
    parts.append(f'<text x="{chart_left + chart_width / 2:.1f}" y="{axis_y + 58}" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="14" fill="{palette["muted"]}">Spearman correlation against experimental DMS fitness</text>')

    # Legend.
    legend_x = 56
    legend_y = 157
    legend_items = [
        ("overall", "Overall"),
        ("exact", "Exact catalytic/metal site"),
        ("active", "Active-site neighborhood"),
    ]
    for idx, (key, label) in enumerate(legend_items):
        x = legend_x + idx * 210
        if key == "overall":
            parts.append(f'<rect x="{x}" y="{legend_y - 12}" width="28" height="12" rx="6" fill="{palette[key]}"/>')
        elif key == "exact":
            parts.append(f'<circle cx="{x + 13}" cy="{legend_y - 6}" r="7" fill="{palette[key]}"/>')
        else:
            parts.append(f'<rect x="{x + 6}" y="{legend_y - 13}" width="14" height="14" transform="rotate(45 {x + 13} {legend_y - 6})" fill="{palette[key]}"/>')
        parts.append(f'<text x="{x + 36}" y="{legend_y - 2}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" fill="{palette["muted"]}">{label}</text>')

    # Rows.
    for idx, row in enumerate(rows):
        y = row_top + idx * row_gap
        baseline_x = chart_left
        overall_x = x_for(row.overall, left=chart_left, width=chart_width)
        exact_x = x_for(row.exact_site, left=chart_left, width=chart_width)
        active_x = x_for(row.active_neighborhood, left=chart_left, width=chart_width)
        clears = row.null_read == "higher_than_position_matched_null"
        tag_fill = "#dce9df" if clears else "#ece5da"

        safe_name = html.escape(row.short_name)
        safe_class = html.escape(row.enzyme_class)
        safe_null = html.escape(null_label(row))

        parts.extend(
            [
                f'<text x="56" y="{y - 13}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="20" font-weight="700" fill="{palette["ink"]}">{safe_name}</text>',
                f'<text x="56" y="{y + 12}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" fill="{palette["muted"]}">{safe_class}</text>',
                f'<text x="56" y="{y + 34}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" fill="{palette["muted"]}">{row.variants:,} variants</text>',
                f'<line x1="{chart_left}" y1="{y + 11}" x2="{chart_left + chart_width}" y2="{y + 11}" stroke="{palette["line"]}" stroke-width="1.2"/>',
                f'<rect x="{baseline_x}" y="{y}" width="{overall_x - baseline_x:.1f}" height="{bar_height}" rx="10" fill="{palette["overall"]}"/>',
                f'<text x="{overall_x + 10:.1f}" y="{y + 15}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="13" font-weight="700" fill="{palette["ink"]}">{fmt(row.overall)}</text>',
                f'<circle cx="{exact_x:.1f}" cy="{y + 46}" r="8" fill="{palette["exact"]}"/>',
                f'<text x="{exact_x + 13:.1f}" y="{y + 51}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="12" fill="{palette["muted"]}">{fmt(row.exact_site)}</text>',
                f'<rect x="{active_x - 8:.1f}" y="{y + 38}" width="16" height="16" transform="rotate(45 {active_x:.1f} {y + 46})" fill="{palette["active"]}"/>',
                f'<text x="{active_x + 14:.1f}" y="{y + 51}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="12" fill="{palette["muted"]}">{fmt(row.active_neighborhood)}</text>',
                f'<rect x="1040" y="{y - 7}" width="292" height="34" rx="17" fill="{tag_fill}" stroke="{palette["line"]}" stroke-width="1"/>',
                f'<text x="1186" y="{y + 14}" text-anchor="middle" font-family="Inter, Helvetica, Arial, sans-serif" font-size="12" font-weight="700" fill="{palette["ink"]}">{safe_null}</text>',
            ]
        )

    # Method strip.
    strip_y = 690
    parts.extend(
        [
            f'<rect x="56" y="{strip_y - 34}" width="1276" height="54" rx="18" fill="{palette["callout"]}" stroke="{palette["line"]}" stroke-width="1"/>',
            f'<text x="82" y="{strip_y - 10}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="{palette["ink"]}">Interview takeaway</text>',
            f'<text x="230" y="{strip_y - 10}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="14" fill="{palette["ink"]}">Scale helps the aggregate task. The mechanistic claim only survives where the residue slice beats matched-position controls.</text>',
            f'<text x="82" y="{strip_y + 13}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="12" fill="{palette["muted"]}">Source: results/proteingym_four_enzyme_esm2_t12_35M_comparison.json</text>',
        ]
    )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the P0 portfolio SVG figure from comparison metrics.")
    parser.add_argument(
        "--comparison-json",
        type=Path,
        default=Path("results/proteingym_four_enzyme_esm2_t12_35M_comparison.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/assets/p0_four_enzyme_35m_portfolio_figure.svg"),
    )
    args = parser.parse_args()

    rows = load_rows(args.comparison_json)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_svg(rows), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
