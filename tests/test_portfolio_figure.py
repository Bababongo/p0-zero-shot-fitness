from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from scripts.build_portfolio_figure import build_svg, load_rows


def test_portfolio_figure_uses_four_enzyme_panel() -> None:
    rows = load_rows(Path("results/proteingym_four_enzyme_esm2_t12_35M_comparison.json"))

    assert [row.short_name for row in rows] == ["TEM-1", "VIM-2", "AMIE", "Beta-glucosidase"]
    assert sum(row.variants for row in rows) == 19013
    assert sum(row.null_read == "higher_than_position_matched_null" for row in rows) == 1


def test_portfolio_figure_svg_is_valid_xml() -> None:
    rows = load_rows(Path("results/proteingym_four_enzyme_esm2_t12_35M_comparison.json"))
    svg = build_svg(rows)

    root = ElementTree.fromstring(svg)

    assert root.tag.endswith("svg")
    assert "P0: Mechanism-sliced protein fitness" in svg
    assert "Beta-glucosidase" in svg
