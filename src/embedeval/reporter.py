"""EmbedEval report generation."""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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

    lines.extend(_scenario_summary(reports))
    lines.append("")
    lines.extend(_model_comparison_table(reports))
    lines.append("")
    lines.extend(_tier_breakdown(reports))
    lines.append("")
    lines.extend(_reasoning_breakdown(reports))
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


def _scenario_summary(reports: list[BenchmarkReport]) -> list[str]:
    """Generate scenario summary when multiple scenarios are present."""
    scenarios = {r.scenario for r in reports}
    if len(scenarios) <= 1 and "generation" in scenarios:
        return []

    lines: list[str] = [
        "## Scenario Comparison",
        "",
        "| Scenario | Model | pass@1 | Cases |",
        "|----------|-------|--------|-------|",
    ]
    for report in reports:
        for model_score in report.models:
            lines.append(
                f"| {report.scenario} "
                f"| {model_score.model} "
                f"| {model_score.pass_at_1:.1%} "
                f"| {model_score.total_cases} |"
            )
    return lines


def _model_comparison_table(reports: list[BenchmarkReport]) -> list[str]:
    """Generate model comparison table."""
    # Check if any model has comparable scores (different case sets)
    has_comparable = any(
        ms.pass_at_1_comparable is not None for r in reports for ms in r.models
    )

    # Case set warnings (deduplicated across reports)
    lines: list[str] = []
    seen_warnings: set[str] = set()
    for report in reports:
        w = report.overall.case_set_warning
        if w and w not in seen_warnings:
            seen_warnings.add(w)
            lines.extend(
                [
                    "> **Warning:** " + w,
                    "",
                ]
            )

    lines.extend(
        [
            "## Model Comparison",
            "",
        ]
    )

    if has_comparable:
        hdr = (
            "| Model | pass@1 (full) | pass@1 (comparable)"
            " | pass@1 (quality) | 95% CI"
            " | pass@5 | Passed | Total | Common |"
        )
        sep = (
            "|-------|---------------|--------------------"
            "-|------------------|--------"
            "|--------|--------|-------|--------|"
        )
        lines.extend([hdr, sep])
    else:
        lines.extend(
            [
                "| Model | pass@1 (full) | pass@1 (quality) | 95% CI"
                " | pass@5 | Passed | Quality | Total | Samples |",
                "|-------|---------------|------------------|--------|"
                "--------|--------|---------|-------|---------|",
            ]
        )

    for report in reports:
        for model_score in report.models:
            lo, hi = model_score.pass_at_1_ci
            ci_str = f"[{lo:.1%}, {hi:.1%}]"
            if has_comparable:
                comp_str = (
                    f"{model_score.pass_at_1_comparable:.1%}"
                    if model_score.pass_at_1_comparable is not None
                    else "-"
                )
                common_str = (
                    str(model_score.comparable_cases)
                    if model_score.comparable_cases is not None
                    else str(model_score.total_cases)
                )
                lines.append(
                    f"| {model_score.model} "
                    f"| {model_score.pass_at_1:.1%} "
                    f"| {comp_str} "
                    f"| {model_score.pass_at_1_quality:.1%} "
                    f"| {ci_str} "
                    f"| {model_score.pass_at_5:.1%} "
                    f"| {model_score.passed_cases} "
                    f"| {model_score.total_cases} "
                    f"| {common_str} |"
                )
            else:
                lines.append(
                    f"| {model_score.model} "
                    f"| {model_score.pass_at_1:.1%} "
                    f"| {model_score.pass_at_1_quality:.1%} "
                    f"| {ci_str} "
                    f"| {model_score.pass_at_5:.1%} "
                    f"| {model_score.passed_cases} "
                    f"| {model_score.passed_cases_quality} "
                    f"| {model_score.total_cases} "
                    f"| n={model_score.n_samples} |"
                )

    lines.append("")
    if has_comparable:
        lines.append(
            "*pass@1 (full) = all layers, all cases per model. "
            "pass@1 (comparable) = common cases only (fair cross-model comparison). "
            "pass@1 (quality) = L0+L3 only.*"
        )
    else:
        lines.append(
            "*pass@1 (full) = all layers must pass. "
            "pass@1 (quality) = L0+L3 only (code quality, ignoring build/runtime).*"
        )

    return lines


def _tier_breakdown(reports: list[BenchmarkReport]) -> list[str]:
    """Generate tier-based pass rate breakdown."""
    has_tiers = any(r.tier_scores for r in reports)
    if not has_tiers:
        return []

    lines: list[str] = [
        "## Tier Breakdown",
        "",
        "| Tier | pass@1 | Passed | Total |",
        "|------|--------|--------|-------|",
    ]
    for report in reports:
        for ts in report.tier_scores:
            label = ts.tier.capitalize()
            if ts.tier == "sanity":
                label += " (not scored)"
            lines.append(
                f"| {label} | {ts.pass_at_1:.1%} "
                f"| {ts.passed_cases} | {ts.total_cases} |"
            )
    return lines


REASONING_LABELS: dict[str, str] = {
    "api_recall": "L1 API Recall",
    "rule_application": "L2 Rule Application",
    "cross_domain": "L3 Cross-Domain",
    "system_reasoning": "L4 System Reasoning",
}


def _reasoning_breakdown(reports: list[BenchmarkReport]) -> list[str]:
    """Generate reasoning type pass rate breakdown."""
    has_reasoning = any(r.reasoning_scores for r in reports)
    if not has_reasoning:
        return []

    lines: list[str] = [
        "## Reasoning Type Breakdown",
        "",
        "| Reasoning Type | pass@1 | Cases | LLM Reliability |",
        "|----------------|--------|-------|-----------------|",
    ]
    for report in reports:
        for rs in report.reasoning_scores:
            label = REASONING_LABELS.get(rs.reasoning_type, rs.reasoning_type)
            if rs.pass_at_1 >= 0.9:
                reliability = "Reliable"
            elif rs.pass_at_1 >= 0.7:
                reliability = "Review recommended"
            else:
                reliability = "Expert review required"
            lines.append(
                f"| {label} | {rs.pass_at_1:.1%} | {rs.total_cases} | {reliability} |"
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


def _match_external(
    model_name: str, externals: dict[str, Any]
) -> dict[str, Any] | None:
    """Find matching external benchmark entry.

    Uses longest-match to avoid ambiguity (e.g., "gpt-4o" vs "gpt-4o-mini").
    """
    model_lower = model_name.lower()
    best_match: tuple[int, dict[str, Any]] | None = None
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
        "| Model | HumanEval | SWE-bench | EmbedEval (full)"
        " | EmbedEval (quality) | Embed Gap |",
        "|-------|-----------|-----------|------------------"
        "|---------------------|-----------|",
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
            embed_full = model_score.pass_at_1 * 100
            embed_quality = model_score.pass_at_1_quality * 100
            gap = embed_full - humaneval
            lines.append(
                f"| {model_score.model} "
                f"| {humaneval:.1f}% "
                f"| {swe_bench:.1f}% "
                f"| {embed_full:.1f}% "
                f"| {embed_quality:.1f}% "
                f"| {gap:+.1f}%p |"
            )

    if not has_data:
        return []

    lines.extend(
        [
            "",
            "*Embed Gap = EmbedEval pass@1 - HumanEval. "
            "Negative = harder than general coding.*",
        ]
    )
    return lines


_RUN_ID_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_run_id(run_id: str) -> str:
    """Reduce a caller-supplied run id to filesystem-safe characters."""
    cleaned = _RUN_ID_SAFE.sub("-", run_id.strip()).strip("-.")
    return cleaned


def generate_run_archive(
    results: list[EvalResult],
    report: BenchmarkReport,
    output_base: Path,
    model: str,
    run_id: str | None = None,
) -> Path:
    """Save detailed per-case results and summary to a timestamped run directory.

    Args:
        run_id: Optional suffix (e.g. "n1", "n2") that distinguishes
            multiple runs of the same model on the same day. Without it,
            a second run on 2026-04-11 would overwrite the first under
            `runs/2026-04-11_<model>/`. When provided, the archive goes
            to `runs/<date>_<model>_<run_id>/`. The id is sanitized to
            `[A-Za-z0-9._-]` to keep it filesystem-safe.

    Returns the run directory path.
    """
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    model_slug = model.replace("/", "_").replace(":", "_")
    dir_name = f"{timestamp}_{model_slug}"
    safe_run_id: str | None = None
    if run_id:
        safe_run_id = _sanitize_run_id(run_id)
        if safe_run_id:
            dir_name = f"{dir_name}_{safe_run_id}"
    run_dir = output_base / "runs" / dir_name
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
    summary["scenario"] = report.scenario
    summary["total_results"] = len(results)
    summary["passed"] = sum(1 for r in results if r.passed)
    summary["failed"] = sum(1 for r in results if not r.passed)
    if safe_run_id:
        summary["run_id"] = safe_run_id
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
    lines.append("\n## Summary\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
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
            lines.append(f"| `{r.case_id}` | {diff} | {layer_name} | {checks_str} |")

    # Failure pattern analysis
    pattern_counts: dict[str, list[str]] = {}
    for r in failed_results:
        for layer in r.layers:
            for d in layer.details:
                if not d.passed:
                    pattern_counts.setdefault(d.check_name, []).append(r.case_id)

    if pattern_counts:
        lines.append("\n## Failure Patterns\n")
        lines.append("| Check Name | Failures | Cases |")
        lines.append("|-----------|----------|-------|")
        for check, cases in sorted(pattern_counts.items(), key=lambda x: -len(x[1])):
            case_list = ", ".join(cases[:5])
            if len(cases) > 5:
                case_list += f" (+{len(cases) - 5} more)"
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

    # Failure classification: separate prose/format failures from genuine code errors
    if failed_results:
        prose_cases = []
        genuine_cases = []
        for r in failed_results:
            code = r.generated_code
            is_prose = (
                not code
                or code.startswith(("I ", "Here", "Based", "This", "The ", "Let"))
                or (
                    len(code) > 50
                    and "#include" not in code
                    and "CONFIG_" not in code
                    and not code.strip().startswith(("&", "/", "/*"))
                )
            )
            if is_prose:
                prose_cases.append(r.case_id)
            else:
                genuine_cases.append(r.case_id)

        if prose_cases:
            lines.append("\n## Failure Classification\n")
            genuine_str = ", ".join(genuine_cases[:5])
            if len(genuine_cases) > 5:
                genuine_str += f" (+{len(genuine_cases) - 5} more)"
            prose_str = ", ".join(prose_cases)
            lines.append("| Type | Count | Cases |")
            lines.append("|------|-------|-------|")
            lines.append(
                f"| Genuine code error | {len(genuine_cases)} | {genuine_str} |"
            )
            lines.append(
                f"| LLM format failure (prose) | {len(prose_cases)} | {prose_str} |"
            )
            lines.append("")
            adjusted_total = len(results) - len(prose_cases)
            adjusted_passed = sum(1 for r in results if r.passed)
            if adjusted_total > 0:
                adj_rate = adjusted_passed / adjusted_total
                lines.append(
                    f"*Adjusted pass@1 (excluding format failures):"
                    f" {adj_rate:.1%}"
                    f" ({adjusted_passed}/{adjusted_total})*\n"
                )

    # TC improvement suggestions
    lines.append("\n## TC Improvement Suggestions\n")
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


def generate_safe_guide(
    output_base: Path,
) -> Path | None:
    """Generate SAFE_GUIDE.md from all available run data.

    Aggregates per-category pass rates across all models in results/runs/,
    then produces risk-tier guidance for embedded engineers.

    Returns the output path, or None if no data available.
    """
    runs_dir = output_base / "runs"
    if not runs_dir.is_dir():
        return None

    # Collect per-model, per-category results from summary.json files
    # model -> {cat -> {passed, total}}
    model_data: dict[str, dict[str, dict[str, Any]]] = {}

    for run_dir in sorted(runs_dir.iterdir()):
        summary_file = run_dir / "summary.json"
        if not summary_file.is_file():
            continue
        try:
            summary = json.loads(summary_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError):
            continue

        model = summary.get("model", "unknown")
        categories = summary.get("categories", [])
        if not categories:
            continue

        # Keep latest run per model (dirs are sorted by date)
        cat_map: dict[str, dict[str, Any]] = {}
        for cat in categories:
            cat_name = cat.get("category", "")
            if cat_name:
                cat_map[cat_name] = {
                    "passed": cat.get("passed_cases", 0),
                    "total": cat.get("total_cases", 0),
                    "pass_at_1": cat.get("pass_at_1", 0.0),
                }
        model_data[model] = cat_map

    if not model_data:
        return None

    # Collect all categories
    all_cats = sorted({cat for cats in model_data.values() for cat in cats})
    models = sorted(model_data.keys())

    # Classify categories into risk tiers based on worst-model performance
    risk_tiers: dict[str, list[tuple[str, dict[str, float]]]] = {
        "critical": [],  # <50% on any model — DO NOT trust
        "caution": [],  # 50-79% — always review
        "moderate": [],  # 80-89% — spot check
        "reliable": [],  # 90%+ on all models — generally safe
    }

    for cat in all_cats:
        rates: dict[str, float] = {}
        for model in models:
            cat_data = model_data[model].get(cat)
            if cat_data:
                rates[model] = cat_data["pass_at_1"]

        if not rates:
            continue

        worst = min(rates.values())
        if worst < 0.5:
            risk_tiers["critical"].append((cat, rates))
        elif worst < 0.8:
            risk_tiers["caution"].append((cat, rates))
        elif worst < 0.9:
            risk_tiers["moderate"].append((cat, rates))
        else:
            risk_tiers["reliable"].append((cat, rates))

    # Collect common failure patterns from detail JSONs
    failure_patterns: dict[str, int] = {}
    for run_dir in runs_dir.iterdir():
        details_dir = run_dir / "details"
        if not details_dir.is_dir():
            continue
        for detail_file in details_dir.glob("*.json"):
            try:
                data = json.loads(detail_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, TypeError):
                continue
            if data.get("passed", True):
                continue
            for layer in data.get("layers", []):
                for check in layer.get("details", []):
                    if not check.get("passed", True):
                        name = check.get("check_name", "")
                        if name:
                            failure_patterns[name] = failure_patterns.get(name, 0) + 1

    top_failures = sorted(failure_patterns.items(), key=lambda x: -x[1])[:20]

    # Build the guide
    lines: list[str] = []
    lines.append("# EmbedEval Safe Guide for Embedded Engineers")
    lines.append("")
    lines.append(
        "*Auto-generated from benchmark results. "
        "Use this to decide when LLM-generated code needs human review.*"
    )
    lines.append("")
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"**Last updated:** {timestamp}")
    lines.append("")

    # Model overview
    lines.append("## Models Tested")
    lines.append("")
    lines.append("| Model | pass@1 | Cases |")
    lines.append("|-------|--------|-------|")
    for model in models:
        cats = model_data[model]
        total = sum(c["total"] for c in cats.values())
        passed = sum(c["passed"] for c in cats.values())
        rate = passed / total if total > 0 else 0.0
        short_name = model.replace("claude-code://", "")
        lines.append(f"| {short_name} | {rate:.1%} | {total} |")
    lines.append("")

    # Risk tiers
    _tier_header = {
        "critical": (
            "CRITICAL — Do Not Trust",
            "LLM fails >50% of the time. "
            "Always write this code manually or review every line.",
        ),
        "caution": (
            "CAUTION — Always Review",
            "LLM fails 20-50%. Use as starting point only. Expert review mandatory.",
        ),
        "moderate": (
            "MODERATE — Spot Check",
            "LLM is mostly correct (80-89%). "
            "Review safety-critical patterns (volatile, ISR, error paths).",
        ),
        "reliable": (
            "RELIABLE — Generally Safe",
            "LLM passes 90%+. Standard code review is sufficient.",
        ),
    }

    for tier_key in ["critical", "caution", "moderate", "reliable"]:
        cats_in_tier = risk_tiers[tier_key]
        if not cats_in_tier:
            continue
        title, desc = _tier_header[tier_key]
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"*{desc}*")
        lines.append("")

        # Model columns
        header = "| Category |"
        sep = "|----------|"
        for model in models:
            short = model.replace("claude-code://", "")
            header += f" {short} |"
            sep += "------|"
        lines.append(header)
        lines.append(sep)

        for cat, rates in sorted(cats_in_tier, key=lambda x: min(x[1].values())):
            row = f"| {cat} |"
            for model in models:
                r = rates.get(model)
                if r is not None:
                    row += f" {r:.0%} |"
                else:
                    row += " - |"
            lines.append(row)
        lines.append("")

    # Common failure patterns
    if top_failures:
        lines.append("## Most Common Failure Patterns")
        lines.append("")
        lines.append(
            "*These checks fail most often across all models and runs. "
            "Pay special attention to these patterns in LLM-generated code.*"
        )
        lines.append("")
        lines.append("| Pattern | Failures | What to Check |")
        lines.append("|---------|----------|---------------|")
        for check_name, count in top_failures:
            hint = _failure_hint(check_name)
            lines.append(f"| `{check_name}` | {count} | {hint} |")
        lines.append("")

    # Practical recommendations
    lines.append("## Practical Recommendations")
    lines.append("")
    lines.append("### When using LLM for embedded code:")
    lines.append("")
    lines.append(
        "1. **Always review** volatile qualifiers, memory barriers, "
        "and ISR-safe patterns"
    )
    lines.append(
        "2. **Never trust** DMA configuration, memory domain setup, "
        "or lock ordering without verification"
    )
    lines.append(
        "3. **Verify** error handling paths — LLMs often generate happy-path-only code"
    )
    lines.append(
        "4. **Check** that Kconfig/prj.conf options match the APIs used in the code"
    )
    lines.append(
        "5. **Test** on actual hardware or QEMU — static checks alone "
        "miss runtime issues"
    )
    lines.append("")

    # Write
    output_path = output_base / "SAFE_GUIDE.md"
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Safe guide written to %s", output_path)
    return output_path


def _failure_hint(check_name: str) -> str:
    """Return a human-readable hint for a check failure pattern."""
    hints: dict[str, str] = {
        "volatile": "Variable shared with ISR/callback must be volatile",
        "memory_barrier": "Data + index update needs compiler_barrier() or __dmb()",
        "lock_order": "Consistent lock acquisition order prevents deadlock",
        "error_handling": "Check return values of all API calls",
        "printk_in_isr": "Never use printk/printf inside ISR handlers",
        "cache": "DMA buffers need cache flush/invalidate",
        "dma_config": "Use correct Zephyr DMA API (dma_config, not dma_configure)",
        "mem_slab": "Use K_MEM_SLAB_DEFINE for static memory pools",
        "sentinel": "Device tree match tables must end with empty {} entry",
        "cleanup": "Init error paths must free all previously acquired resources",
    }
    name_lower = check_name.lower()
    for key, hint in hints.items():
        if key in name_lower:
            return hint
    return "Review LLM output against hardware/RTOS requirements"


def _pass_fail_icon(rate: float) -> str:
    """Return a pass/fail status icon based on the rate."""
    if rate >= 0.8:
        return "PASS"
    elif rate >= 0.5:
        return "PARTIAL"
    else:
        return "FAIL"
