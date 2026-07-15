from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from scripts.build_model_family_figure import build_svg, load_comparison


def test_model_family_figure_builds_valid_svg() -> None:
    comparisons = load_comparison(Path("results/proteingym_ready_enzyme_model_family_comparison.json"))

    svg = build_svg(comparisons)

    ET.fromstring(svg)
    assert "P0 model-family comparison" in svg
    assert "ProteinMPNN wins overall" in svg
    assert "VIM-2" in svg
