from __future__ import annotations

from pathlib import Path

from p0_zero_shot_fitness.models import VariantRecord


def write_scatter_svg(path: Path, records: list[VariantRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 760
    height = 520
    margin = 70
    plot_width = width - 2 * margin
    plot_height = height - 2 * margin
    x_values = [record.model_score for record in records]
    y_values = [record.fitness for record in records]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)

    def scale_x(value: float) -> float:
        if x_max == x_min:
            return margin + plot_width / 2
        return margin + ((value - x_min) / (x_max - x_min)) * plot_width

    def scale_y(value: float) -> float:
        if y_max == y_min:
            return margin + plot_height / 2
        return height - margin - ((value - y_min) / (y_max - y_min)) * plot_height

    points = []
    for record in records:
        color = "#d64f45" if record.is_catalytic else "#3478bf"
        radius = 7 if record.is_catalytic else 5
        points.append(
            f'<circle cx="{scale_x(record.model_score):.2f}" cy="{scale_y(record.fitness):.2f}" '
            f'r="{radius}" fill="{color}" fill-opacity="0.82">'
            f"<title>{record.mutation.raw}: fitness={record.fitness:.2f}, score={record.model_score:.2f}</title>"
            "</circle>"
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{width / 2}" y="32" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700">Zero-Shot Score vs Experimental Fitness</text>
  <line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#222" stroke-width="1.5"/>
  <line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" stroke="#222" stroke-width="1.5"/>
  <text x="{width / 2}" y="{height - 22}" text-anchor="middle" font-family="Arial" font-size="15">Placeholder model score</text>
  <text x="22" y="{height / 2}" transform="rotate(-90 22 {height / 2})" text-anchor="middle" font-family="Arial" font-size="15">Experimental fitness</text>
  <text x="{margin}" y="{height - margin + 24}" text-anchor="middle" font-family="Arial" font-size="12">{x_min:.2f}</text>
  <text x="{width - margin}" y="{height - margin + 24}" text-anchor="middle" font-family="Arial" font-size="12">{x_max:.2f}</text>
  <text x="{margin - 12}" y="{height - margin + 4}" text-anchor="end" font-family="Arial" font-size="12">{y_min:.2f}</text>
  <text x="{margin - 12}" y="{margin + 4}" text-anchor="end" font-family="Arial" font-size="12">{y_max:.2f}</text>
  {"".join(points)}
  <circle cx="{width - 205}" cy="72" r="7" fill="#d64f45" fill-opacity="0.82"/>
  <text x="{width - 188}" y="77" font-family="Arial" font-size="13">Catalytic mutation</text>
  <circle cx="{width - 205}" cy="96" r="5" fill="#3478bf" fill-opacity="0.82"/>
  <text x="{width - 188}" y="101" font-family="Arial" font-size="13">Non-catalytic mutation</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")
