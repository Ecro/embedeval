"""EmbedEval scoring and aggregation."""

import logging
from collections import defaultdict
from datetime import datetime, timezone

from embedeval.models import (
    BenchmarkReport,
    CaseCategory,
    CategoryScore,
    EvalResult,
    ModelScore,
    OverallScore,
)

logger = logging.getLogger(__name__)


def score(results: list[EvalResult]) -> BenchmarkReport:
    """Calculate benchmark scores from evaluation results.

    Args:
        results: List of EvalResult from benchmark runs.

    Returns:
        BenchmarkReport with model scores, category scores, and overall summary.
    """
    if not results:
        return _empty_report()

    model_scores = _calculate_model_scores(results)
    category_scores = _calculate_category_scores(results)
    overall = _calculate_overall(model_scores)

    return BenchmarkReport(
        version="0.1.0",
        date=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
        models=model_scores,
        categories=category_scores,
        overall=overall,
    )


def _empty_report() -> BenchmarkReport:
    """Return an empty report for no results."""
    return BenchmarkReport(
        version="0.1.0",
        date=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
        models=[],
        categories=[],
        overall=OverallScore(
            total_cases=0,
            total_models=0,
            best_model="none",
            best_pass_at_1=0.0,
        ),
    )


def _calculate_model_scores(results: list[EvalResult]) -> list[ModelScore]:
    """Calculate per-model scoring aggregates."""
    by_model: dict[str, list[EvalResult]] = defaultdict(list)
    for r in results:
        by_model[r.model].append(r)

    scores: list[ModelScore] = []
    for model, model_results in sorted(by_model.items()):
        pass_at_1 = _calculate_pass_at_k(model_results, 1)
        pass_at_3 = _calculate_pass_at_k(model_results, 3)
        pass_at_5 = _calculate_pass_at_k(model_results, 5)
        case_ids = {r.case_id for r in model_results}
        passed_cases = sum(
            1
            for cid in case_ids
            if any(r.passed for r in model_results if r.case_id == cid)
        )
        layer_pass_rates = _calculate_layer_pass_rates(model_results)

        avg_score = (pass_at_1 + pass_at_3 + pass_at_5) / 3.0

        scores.append(
            ModelScore(
                model=model,
                pass_at_1=pass_at_1,
                pass_at_3=pass_at_3,
                pass_at_5=pass_at_5,
                avg_score=avg_score,
                total_cases=len(case_ids),
                passed_cases=passed_cases,
                layer_pass_rates=layer_pass_rates,
            )
        )

    return scores


def _calculate_category_scores(
    results: list[EvalResult],
) -> list[CategoryScore]:
    """Calculate per-category scoring aggregates.

    Uses result.category when available, falls back to case_id prefix parsing.
    """
    by_category: dict[CaseCategory, dict[str, list[EvalResult]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for r in results:
        cat = (
            r.category
            if r.category is not None
            else _resolve_category(r.case_id.split("-")[0])
        )
        by_category[cat][r.case_id].append(r)

    scores: list[CategoryScore] = []
    for cat in sorted(by_category, key=lambda c: c.value):
        cases = by_category[cat]
        total = len(cases)
        passed = sum(
            1 for case_results in cases.values() if any(r.passed for r in case_results)
        )

        scores.append(
            CategoryScore(
                category=cat,
                pass_at_1=passed / total if total > 0 else 0.0,
                total_cases=total,
                passed_cases=passed,
            )
        )

    return scores


def _calculate_overall(model_scores: list[ModelScore]) -> OverallScore:
    """Calculate overall benchmark summary."""
    if not model_scores:
        return OverallScore(
            total_cases=0,
            total_models=0,
            best_model="none",
            best_pass_at_1=0.0,
        )

    best = max(model_scores, key=lambda m: m.pass_at_1)
    total_cases = max(m.total_cases for m in model_scores)

    return OverallScore(
        total_cases=total_cases,
        total_models=len(model_scores),
        best_model=best.model,
        best_pass_at_1=best.pass_at_1,
    )


def _calculate_pass_at_k(results: list[EvalResult], k: int) -> float:
    """Calculate pass@k: fraction of cases where at least 1 of k attempts passes.

    For pass@1 (k=1), only the first attempt is considered.
    For pass@k (k>1), the first k attempts sorted by attempt number are used.
    """
    by_case: dict[str, list[EvalResult]] = defaultdict(list)
    for r in results:
        by_case[r.case_id].append(r)

    if not by_case:
        return 0.0

    passed = 0
    for case_results in by_case.values():
        # Only consider first k attempts ordered by attempt number
        first_k = sorted(case_results, key=lambda r: r.attempt)[:k]
        if any(r.passed for r in first_k):
            passed += 1

    return passed / len(by_case)



def _calculate_layer_pass_rates(
    results: list[EvalResult],
) -> dict[str, float]:
    """Calculate pass rate for each layer across all results."""
    layer_counts: dict[str, int] = defaultdict(int)
    layer_passes: dict[str, int] = defaultdict(int)

    for r in results:
        for layer in r.layers:
            if layer.error and "Skipped" in layer.error:
                continue
            layer_counts[layer.name] += 1
            if layer.passed:
                layer_passes[layer.name] += 1

    return {
        name: layer_passes[name] / count if count > 0 else 0.0
        for name, count in sorted(layer_counts.items())
    }


def _resolve_category(key: str) -> CaseCategory:
    """Resolve a category key to a CaseCategory enum value."""
    for cat in CaseCategory:
        if cat.value == key or cat.name.lower() == key.lower():
            return cat
    return CaseCategory.KCONFIG
