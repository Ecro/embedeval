"""EmbedEval report generation."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import yaml

from embedeval.models import BenchmarkReport, EvalResult

logger = logging.getLogger(__name__)

LAYER_DISPLAY_NAMES: dict[str, str] = {
    "static_analysis": "L0 Static",
    "compile_gate": "L1 Build",
    "runtime_execution": "L2 Runtime",
    "static_heuristic": "L3 Heuristic",
    "test_quality_proof": "L4 Mutation",
}

LAYER_ORDER: list[str] = [
    "static_analysis",
    "compile_gate",
    "runtime_execution",
    "static_heuristic",
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
    lines.append("")
    lines.extend(_cross_benchmark_comparison(reports))

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Leaderboard written to %s", output)


def _model_comparison_table(reports: list[BenchmarkReport]) -> list[str]:
    """Generate model comparison table."""
    lines: list[str] = [
        "## Model Comparison",
        "",
        "| Model | pass@1 | pass@3 | pass@5 | avg_score | Cases Passed | Total Cases |",
        "|-------|--------|--------|--------|-----------|-------------|-------------|",
    ]

    for report in reports:
        for model_score in report.models:
            lines.append(
                f"| {model_score.model} "
                f"| {model_score.pass_at_1:.1%} "
                f"| {model_score.pass_at_3:.1%} "
                f"| {model_score.pass_at_5:.1%} "
                f"| {model_score.avg_score:.1%} "
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


def _load_external_benchmarks() -> dict[str, dict[str, float | str]]:
    """Load external benchmark scores from external_benchmarks.yaml.

    Searches: package data dir → CWD → repo root (relative to source).
    """
    candidates = [
        Path.cwd() / "external_benchmarks.yaml",
        Path(__file__).parent / "external_benchmarks.yaml",
        Path(__file__).parent.parent.parent / "external_benchmarks.yaml",
    ]
    for yaml_path in candidates:
        if yaml_path.exists():
            break
    else:
        return {}
    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        return data.get("models", {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


def _match_external(model_name: str, externals: dict) -> dict | None:
    """Find matching external benchmark entry.

    Uses longest-match to avoid ambiguity (e.g., "gpt-4o" vs "gpt-4o-mini").
    """
    model_lower = model_name.lower()
    best_match: tuple[int, dict] | None = None
    for key, scores in externals.items():
        key_lower = key.lower()
        if key_lower in model_lower:
            if best_match is None or len(key_lower) > best_match[0]:
                best_match = (len(key_lower), scores)
    return best_match[1] if best_match else None


def _cross_benchmark_comparison(reports: list[BenchmarkReport]) -> list[str]:
    """Generate cross-benchmark comparison table (EmbedEval vs HumanEval/SWE-bench)."""
    externals = _load_external_benchmarks()
    if not externals:
        return []

    lines: list[str] = [
        "## Cross-Benchmark Comparison",
        "",
        "| Model | HumanEval | SWE-bench | EmbedEval | Embed Gap |",
        "|-------|-----------|-----------|-----------|-----------|",
    ]

    has_data = False
    for report in reports:
        for model_score in report.models:
            ext = _match_external(model_score.model, externals)
            if ext is None:
                continue
            has_data = True
            humaneval = ext.get("humaneval", 0)
            swe_bench = ext.get("swe_bench", 0)
            embed_pct = model_score.pass_at_1 * 100
            gap = embed_pct - humaneval
            lines.append(
                f"| {model_score.model} "
                f"| {humaneval:.1f}% "
                f"| {swe_bench:.1f}% "
                f"| {embed_pct:.1f}% "
                f"| {gap:+.1f}%p |"
            )

    if not has_data:
        return []

    lines.extend([
        "",
        "*Embed Gap = EmbedEval pass@1 - HumanEval. "
        "Negative = harder than general coding.*",
    ])
    return lines


def generate_run_archive(
    results: list[EvalResult],
    report: BenchmarkReport,
    output_base: Path,
    model: str,
) -> Path:
    """Save detailed per-case results and summary to a timestamped run directory.

    Returns the run directory path.
    """
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    model_slug = model.replace("/", "_").replace(":", "_")
    run_dir = output_base / "runs" / f"{timestamp}_{model_slug}"
    details_dir = run_dir / "details"
    details_dir.mkdir(parents=True, exist_ok=True)

    # Save per-case detailed results
    for r in results:
        case_data = r.model_dump(mode="json")
        case_file = details_dir / f"{r.case_id}.json"
        case_file.write_text(
            json.dumps(case_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # Save summary
    summary_file = run_dir / "summary.json"
    summary = report.model_dump(mode="json")
    summary["run_timestamp"] = timestamp
    summary["model"] = model
    summary["total_results"] = len(results)
    summary["passed"] = sum(1 for r in results if r.passed)
    summary["failed"] = sum(1 for r in results if not r.passed)
    summary_file.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Append to history
    _append_history(output_base, summary)

    logger.info("Run archive saved to %s", run_dir)
    return run_dir


def generate_failure_report(
    results: list[EvalResult],
    output: Path,
    model: str,
) -> None:
    """Generate a Markdown failure analysis report."""
    lines: list[str] = []
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    pass_at_1 = passed / total if total > 0 else 0.0

    lines.append(f"# Benchmark Report: {model}")
    lines.append(f"\n**Date:** {timestamp}")
    lines.append(f"\n## Summary\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Model | {model} |")
    lines.append(f"| Total Cases | {total} |")
    lines.append(f"| Passed | {passed} |")
    lines.append(f"| Failed | {failed} |")
    lines.append(f"| pass@1 | {pass_at_1:.1%} |")

    # Failed cases detail
    failed_results = [r for r in results if not r.passed]
    if failed_results:
        lines.append(f"\n## Failed Cases ({len(failed_results)})\n")
        lines.append("| Case | Difficulty | Failed Layer | Failed Checks |")
        lines.append("|------|-----------|-------------|--------------|")

        for r in sorted(failed_results, key=lambda x: x.case_id):
            diff = r.category.value if r.category else "?"
            layer_name = "?"
            failed_checks: list[str] = []
            for layer in r.layers:
                fc = [d.check_name for d in layer.details if not d.passed]
                if fc:
                    layer_name = layer.name
                    failed_checks.extend(fc)
            checks_str = ", ".join(failed_checks) if failed_checks else "unknown"
            lines.append(
                f"| `{r.case_id}` | {diff} | {layer_name} | {checks_str} |"
            )

    # Failure pattern analysis
    pattern_counts: dict[str, list[str]] = {}
    for r in failed_results:
        for layer in r.layers:
            for d in layer.details:
                if not d.passed:
                    pattern_counts.setdefault(d.check_name, []).append(r.case_id)

    if pattern_counts:
        lines.append(f"\n## Failure Patterns\n")
        lines.append("| Check Name | Failures | Cases |")
        lines.append("|-----------|----------|-------|")
        for check, cases in sorted(
            pattern_counts.items(), key=lambda x: -len(x[1])
        ):
            case_list = ", ".join(cases[:5])
            if len(cases) > 5:
                case_list += f" (+{len(cases)-5} more)"
            lines.append(f"| `{check}` | {len(cases)} | {case_list} |")

    # By difficulty
    by_diff: dict[str, dict[str, int]] = {}
    for r in results:
        # Extract difficulty from case_id pattern
        diff = "unknown"
        for layer in r.layers:
            pass  # We need metadata for difficulty
        if r.case_id not in by_diff:
            by_diff.setdefault("all", {"total": 0, "passed": 0})
            by_diff["all"]["total"] += 1
            if r.passed:
                by_diff["all"]["passed"] += 1

    # TC improvement suggestions
    lines.append(f"\n## TC Improvement Suggestions\n")
    always_pass = [r.case_id for r in results if r.passed]
    if len(always_pass) == total:
        lines.append("All cases passed — consider adding harder test cases.\n")
    elif pass_at_1 > 0.9:
        lines.append(
            f"pass@1 is {pass_at_1:.0%} — most cases are too easy for this model.\n"
        )
        lines.append("Consider strengthening checks or adding hallucination traps.\n")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Failure report written to %s", output)


def _append_history(output_base: Path, run_summary: dict[str, object]) -> None:  # noqa: C901
    """Append a run summary to history.json."""
    history_file = output_base / "history.json"
    history: list[dict[str, object]] = []
    if history_file.is_file():
        try:
            history = json.loads(history_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError):
            history = []

    entry = {
        "timestamp": run_summary.get("run_timestamp", ""),
        "model": run_summary.get("model", ""),
        "total": run_summary.get("total_results", 0),
        "passed": run_summary.get("passed", 0),
        "failed": run_summary.get("failed", 0),
    }
    overall = run_summary.get("overall")
    if isinstance(overall, dict):
        entry["pass_at_1"] = overall.get("best_pass_at_1", 0.0)
    history.append(entry)

    history_file.write_text(
        json.dumps(history, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _pass_fail_icon(rate: float) -> str:
    """Return a pass/fail status icon based on the rate."""
    if rate >= 0.8:
        return "PASS"
    elif rate >= 0.5:
        return "PARTIAL"
    else:
        return "FAIL"
