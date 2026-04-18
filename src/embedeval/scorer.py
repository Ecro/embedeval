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
    PerCheckStat,
    ReasoningScore,
    TierScore,
)

logger = logging.getLogger(__name__)


def wilson_ci(pass_rate: float, n: int, z: float = 1.96) -> tuple[float, float]:
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
    spread = z * ((pass_rate * (1 - pass_rate) / n + z**2 / (4 * n**2)) ** 0.5) / denom
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

    # Find common cases across all models for comparable scoring
    all_model_case_ids = [
        {r.case_id for r in model_results} for model_results in by_model.values()
    ]
    common_case_ids: set[str] | None = None
    if len(all_model_case_ids) > 1:
        common_case_ids = set.intersection(*all_model_case_ids)

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

        # Quality score: L0+L3 only (ignoring L1 compile and L2 runtime)
        passed_quality = _count_quality_passes(model_results, case_ids)
        pass_at_1_quality = passed_quality / n_cases if n_cases > 0 else 0.0
        ci = wilson_ci(pass_at_1, n_cases)

        # n_samples = max attempts per case
        samples_per_case = max(
            (len([r for r in model_results if r.case_id == cid]) for cid in case_ids),
            default=1,
        )

        per_check_stats = _calculate_per_check_stats(model_results)

        # Comparable pass@1: score on common cases only
        pass_at_1_comparable: float | None = None
        comparable_cases: int | None = None
        if common_case_ids is not None and len(common_case_ids) > 0:
            # Check if all models tested the exact same set of cases
            all_same = all(ids == common_case_ids for ids in all_model_case_ids)
            if not all_same:
                common_results = [
                    r for r in model_results if r.case_id in common_case_ids
                ]
                if common_results:
                    pass_at_1_comparable = _calculate_pass_at_k(common_results, 1)
                    comparable_cases = len(common_case_ids)

        scores.append(
            ModelScore(
                model=model,
                pass_at_1=pass_at_1,
                pass_at_1_quality=pass_at_1_quality,
                pass_at_1_comparable=pass_at_1_comparable,
                pass_at_3=pass_at_3,
                pass_at_5=pass_at_5,
                avg_score=pass_at_1,
                total_cases=n_cases,
                passed_cases=passed_cases,
                passed_cases_quality=passed_quality,
                comparable_cases=comparable_cases,
                layer_pass_rates=layer_pass_rates,
                pass_at_1_ci=ci,
                n_samples=samples_per_case,
                per_check_stats=per_check_stats,
            )
        )

    return scores


def _calculate_per_check_stats(
    model_results: list[EvalResult],
) -> list[PerCheckStat]:
    """Aggregate per-check pass/fail across all evaluations for one model.

    Walks every CheckDetail in every LayerResult, grouping by
    (check_name, category). Emits a PerCheckStat per unique key.

    Downstream consumers (Hiloop transpile evidence injection, per-check
    dashboards) should read this field from summary.json — do not scrape
    report.md for this data.
    """
    # key = (check_name, category_str)
    totals: dict[tuple[str, str | None], int] = defaultdict(int)
    fails: dict[tuple[str, str | None], int] = defaultdict(int)
    failing_tcs: dict[tuple[str, str | None], set[str]] = defaultdict(set)

    for result in model_results:
        category = result.category.value if result.category else None
        for layer in result.layers:
            for detail in layer.details:
                # Skip L4 mutation synthetic checks — they measure benchmark
                # quality (did mutation get caught), not model behavior.
                if detail.check_type == "mutation":
                    continue
                key = (detail.check_name, category)
                totals[key] += 1
                if not detail.passed:
                    fails[key] += 1
                    failing_tcs[key].add(result.case_id)

    stats: list[PerCheckStat] = []
    for key, total in sorted(totals.items()):
        check_name, category = key
        fail_count = fails.get(key, 0)
        pass_rate = (total - fail_count) / total if total > 0 else 0.0
        stats.append(
            PerCheckStat(
                check_name=check_name,
                category=category,
                total_runs=total,
                fail_count=fail_count,
                pass_rate=pass_rate,
                failing_tc_ids=sorted(failing_tcs.get(key, set())),
            )
        )
    return stats


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

    # Detect case set mismatch using comparable_cases (already computed
    # correctly via set intersection in _calculate_model_scores)
    common_cases: int | None = None
    case_set_warning: str | None = None
    if len(model_scores) > 1:
        any_comparable = any(m.comparable_cases is not None for m in model_scores)
        if any_comparable:
            case_counts = {m.model: m.total_cases for m in model_scores}
            min_model = min(case_counts, key=case_counts.get)  # type: ignore[arg-type]
            max_model = max(case_counts, key=case_counts.get)  # type: ignore[arg-type]
            case_set_warning = (
                f"Models tested on different case sets: "
                f"{min_model}={case_counts[min_model]}, "
                f"{max_model}={case_counts[max_model]}. "
                f"Use comparable scores for fair comparison."
            )
            common_cases = model_scores[0].comparable_cases

    return OverallScore(
        total_cases=total_cases,
        total_models=len(model_scores),
        best_model=best.model,
        best_pass_at_1=best.pass_at_1,
        common_cases=common_cases,
        case_set_warning=case_set_warning,
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


def _count_quality_passes(
    results: list[EvalResult],
    case_ids: set[str],
) -> int:
    """Count cases that pass L0+L3 quality checks (ignoring L1 compile and L2 runtime).

    A case passes quality if:
    - L0 (static_analysis) passed (if present)
    - L3 (static_heuristic/behavior) passed (if present)
    - L1 and L2 results are ignored
    """
    passed = 0
    for cid in case_ids:
        case_results = [r for r in results if r.case_id == cid]
        # Check if any attempt passes quality
        any_pass = False
        for r in case_results:
            l0_ok = True
            l3_ok = True
            for layer in r.layers:
                if layer.layer == 0 and not layer.passed:
                    l0_ok = False
                if layer.layer == 3:
                    # Skip if L3 was skipped due to earlier failure
                    if layer.error and "Skipped" in layer.error:
                        continue
                    if not layer.passed:
                        l3_ok = False
            if l0_ok and l3_ok:
                any_pass = True
                break
        if any_pass:
            passed += 1
    return passed


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
    for rt_name in [
        "api_recall",
        "rule_application",
        "cross_domain",
        "system_reasoning",
    ]:
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
