"""EmbedEval report generation."""

import json
import logging
from pathlib import Path

from embedeval.models import BenchmarkReport

logger = logging.getLogger(__name__)


def generate_json(report: BenchmarkReport, output: Path) -> None:
    """Write a benchmark report as JSON.

    Args:
        report: The benchmark report to serialize.
        output: Path to the output JSON file.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    data = report.model_dump(mode="json")
    output.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info("JSON report written to %s", output)


def generate_leaderboard(
    reports: list[BenchmarkReport],
    output: Path,
) -> None:
    """Generate a Markdown leaderboard from benchmark reports.

    Args:
        reports: List of benchmark reports (one per run).
        output: Path to the output Markdown file.
    """
    output.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# EmbedEval Leaderboard",
        "",
    ]

    lines.extend(_model_comparison_table(reports))
    lines.append("")
    lines.extend(_category_heatmap(reports))

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Leaderboard written to %s", output)


def _model_comparison_table(reports: list[BenchmarkReport]) -> list[str]:
    """Generate model comparison table."""
    lines: list[str] = [
        "## Model Comparison",
        "",
        "| Model | pass@1 | pass@5 | Cases Passed | Total Cases |",
        "|-------|--------|--------|-------------|-------------|",
    ]

    for report in reports:
        for model_score in report.models:
            lines.append(
                f"| {model_score.model} "
                f"| {model_score.pass_at_1:.1%} "
                f"| {model_score.pass_at_5:.1%} "
                f"| {model_score.passed_cases} "
                f"| {model_score.total_cases} |"
            )

    return lines


def _category_heatmap(reports: list[BenchmarkReport]) -> list[str]:
    """Generate per-category pass/fail heatmap."""
    lines: list[str] = [
        "## Category Results",
        "",
        "| Category | pass@1 | Passed | Total | Status |",
        "|----------|--------|--------|-------|--------|",
    ]

    for report in reports:
        for cat_score in report.categories:
            status = _pass_fail_icon(cat_score.pass_at_1)
            lines.append(
                f"| {cat_score.category.value} "
                f"| {cat_score.pass_at_1:.1%} "
                f"| {cat_score.passed_cases} "
                f"| {cat_score.total_cases} "
                f"| {status} |"
            )

    return lines


def _pass_fail_icon(rate: float) -> str:
    """Return a pass/fail status icon based on the rate."""
    if rate >= 0.8:
        return "PASS"
    elif rate >= 0.5:
        return "PARTIAL"
    else:
        return "FAIL"
