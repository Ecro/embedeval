"""EmbedEval scoring and aggregation."""

import logging
from collections import defaultdict
from datetime import datetime, timezone
from math import comb

from embedeval.models import (
    BenchmarkReport,
    CaseCategory,
    CategoryScore,
    EvalResult,
    ModelScore,
    OverallScore,
    ReasoningScore,
    TierScore,
)

logger = logging.getLogger(__name__)


def wilson_ci(
    pass_rate: float, n: int, z: float = 1.96
) -> tuple[float, float]:
    """Wilson score 95% confidence interval for a pass rate.

    Args:
        pass_rate: Observed pass rate (0.0 to 1.0).
        n: Number of cases.
        z: Z-score for confidence level (1.96 = 95%).

    Returns:
        (lower, upper) bounds of the confidence interval.
    """
    if n == 0:
        return (0.0, 0.0)
    denom = 1 + z**2 / n
    center = (pass_rate + z**2 / (2 * n)) / denom
    spread = (
        z * ((pass_rate * (1 - pass_rate) / n + z**2 / (4 * n**2)) ** 0.5) / denom
    )
    return (max(0.0, center - spread), min(1.0, center + spread))


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
    tier_scores = _calculate_tier_scores(results)
    reasoning_scores = _calculate_reasoning_scores(results)
    overall = _calculate_overall(model_scores)

    return BenchmarkReport(
        version="0.1.0",
        date=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
        models=model_scores,
        categories=category_scores,
        tier_scores=tier_scores,
        reasoning_scores=reasoning_scores,
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

        n_cases = len(case_ids)
        ci = wilson_ci(pass_at_1, n_cases)

        # n_samples = max attempts per case
        samples_per_case = max(
            (len([r for r in model_results if r.case_id == cid]) for cid in case_ids),
            default=1,
        )

        scores.append(
            ModelScore(
                model=model,
                pass_at_1=pass_at_1,
                pass_at_3=pass_at_3,
                pass_at_5=pass_at_5,
                avg_score=pass_at_1,
                total_cases=n_cases,
                passed_cases=passed_cases,
                layer_pass_rates=layer_pass_rates,
                pass_at_1_ci=ci,
                n_samples=samples_per_case,
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
    """Calculate pass@k using the unbiased estimator from Chen et al. (2021).

    pass@k = E[1 - C(n-c, k) / C(n, k)]

    where n = total samples per case, c = correct samples per case.
    When n < k, falls back to empirical estimate (any correct → 1.0).
    """
    by_case: dict[str, list[EvalResult]] = defaultdict(list)
    for r in results:
        by_case[r.case_id].append(r)

    if not by_case:
        return 0.0

    scores: list[float] = []
    for case_results in by_case.values():
        n = len(case_results)
        c = sum(1 for r in case_results if r.passed)
        if n < k:
            scores.append(1.0 if c > 0 else 0.0)
        elif n - c < k:
            scores.append(1.0)
        else:
            scores.append(1.0 - comb(n - c, k) / comb(n, k))

    return sum(scores) / len(scores)



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


def _calculate_tier_scores(results: list[EvalResult]) -> list[TierScore]:
    """Calculate pass rate breakdown by evaluation tier."""
    by_tier: dict[str, dict[str, list[EvalResult]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for r in results:
        tier_name = r.tier.value if r.tier else "core"
        by_tier[tier_name][r.case_id].append(r)

    scores: list[TierScore] = []
    for tier_name in ["sanity", "core", "challenge"]:
        if tier_name not in by_tier:
            continue
        cases = by_tier[tier_name]
        total = len(cases)
        passed = sum(
            1 for case_results in cases.values() if any(r.passed for r in case_results)
        )
        scores.append(
            TierScore(
                tier=tier_name,
                pass_at_1=passed / total if total > 0 else 0.0,
                total_cases=total,
                passed_cases=passed,
            )
        )
    return scores


def _calculate_reasoning_scores(results: list[EvalResult]) -> list[ReasoningScore]:
    """Calculate pass rate breakdown by reasoning type.

    A case counts toward a reasoning type if it has that type in its
    reasoning_types list. Cases can appear in multiple reasoning types.
    """
    by_type: dict[str, dict[str, list[EvalResult]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for r in results:
        if not r.reasoning_types:
            continue
        for rt in r.reasoning_types:
            rt_name = rt.value if hasattr(rt, "value") else str(rt)
            by_type[rt_name][r.case_id].append(r)

    scores: list[ReasoningScore] = []
    for rt_name in ["api_recall", "rule_application", "cross_domain", "system_reasoning"]:
        if rt_name not in by_type:
            continue
        cases = by_type[rt_name]
        total = len(cases)
        passed = sum(
            1 for case_results in cases.values() if any(r.passed for r in case_results)
        )
        scores.append(
            ReasoningScore(
                reasoning_type=rt_name,
                pass_at_1=passed / total if total > 0 else 0.0,
                total_cases=total,
                passed_cases=passed,
            )
        )
    return scores


def _resolve_category(key: str) -> CaseCategory:
    """Resolve a category key to a CaseCategory enum value."""
    for cat in CaseCategory:
        if cat.value == key or cat.name.lower() == key.lower():
            return cat
    return CaseCategory.KCONFIG
