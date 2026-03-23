"""EmbedEval report generation."""

import json
import logging
from pathlib import Path

from embedeval.models import BenchmarkReport

logger = logging.getLogger(__name__)

LAYER_DISPLAY_NAMES: dict[str, str] = {
    "static_analysis": "L0 Static",
    "compile_gate": "L1 Build",
    "runtime_execution": "L2 Runtime",
    "behavioral_assertion": "L3 Behavior",
    "test_quality_proof": "L4 Mutation",
}

LAYER_ORDER: list[str] = [
    "static_analysis",
    "compile_gate",
    "runtime_execution",
    "behavioral_assertion",
    "test_quality_proof",
]


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
    lines.append("")
    lines.extend(_layer_heatmap(reports))
    lines.append("")
    lines.extend(_failure_distribution(reports))
    lines.append("")
    lines.extend(_category_breakdown(reports))

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


def _layer_heatmap(reports: list[BenchmarkReport]) -> list[str]:
    """Generate layer failure heatmap showing pass rate per layer per model."""
    lines: list[str] = [
        "## Layer Pass Rate Heatmap",
        "",
    ]

    header_parts = ["| Model"]
    separator_parts = ["|-------"]
    for layer_key in LAYER_ORDER:
        display = LAYER_DISPLAY_NAMES[layer_key]
        header_parts.append(f" {display}")
        separator_parts.append("----------")
    header_parts.append(" |")
    separator_parts.append("|")

    lines.append("|".join(header_parts))
    lines.append("|".join(separator_parts))

    for report in reports:
        for model_score in report.models:
            row_parts = [f"| {model_score.model}"]
            for layer_key in LAYER_ORDER:
                rate = model_score.layer_pass_rates.get(layer_key)
                if rate is not None:
                    row_parts.append(f" {rate:.0%}")
                else:
                    row_parts.append(" -")
            row_parts.append(" |")
            lines.append("|".join(row_parts))

    return lines


def _failure_distribution(reports: list[BenchmarkReport]) -> list[str]:
    """Generate failure distribution analysis across layers."""
    lines: list[str] = [
        "## Failure Distribution",
        "",
        "| Layer | Failures | % of Total |",
        "|-------|----------|-----------|",
    ]

    layer_failures: dict[str, float] = {}
    for layer_key in LAYER_ORDER:
        layer_failures[layer_key] = 0.0

    for report in reports:
        for model_score in report.models:
            for layer_key in LAYER_ORDER:
                rate = model_score.layer_pass_rates.get(layer_key)
                if rate is not None:
                    failure_rate = 1.0 - rate
                    layer_failures[layer_key] += failure_rate

    total_failures = sum(layer_failures.values())

    for layer_key in LAYER_ORDER:
        display = LAYER_DISPLAY_NAMES[layer_key]
        failures = layer_failures[layer_key]
        if total_failures > 0:
            pct = failures / total_failures
        else:
            pct = 0.0
        lines.append(f"| {display} | {failures:.1f} | {pct:.0%} |")

    return lines


def _category_breakdown(reports: list[BenchmarkReport]) -> list[str]:
    """Generate category breakdown table with pass rates and case counts."""
    lines: list[str] = [
        "## Category Breakdown",
        "",
        "| Category | Pass@1 | Cases |",
        "|----------|--------|-------|",
    ]

    for report in reports:
        for cat_score in report.categories:
            lines.append(
                f"| {cat_score.category.value} "
                f"| {cat_score.pass_at_1:.0%} "
                f"| {cat_score.total_cases} |"
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
