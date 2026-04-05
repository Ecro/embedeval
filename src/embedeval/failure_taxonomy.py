"""Automated failure classification based on check results.

Maps failed check names to failure pattern categories for systematic
analysis of why LLMs fail at embedded firmware tasks.
"""

import logging
from collections import Counter
from enum import Enum

from pydantic import BaseModel, Field

from embedeval.models import EvalResult

logger = logging.getLogger(__name__)


class FailurePattern(str, Enum):
    """Taxonomy of LLM failure patterns in embedded code generation."""

    HAPPY_PATH_BIAS = "happy_path_bias"
    SEMANTIC_MISMATCH = "semantic_mismatch"
    RESOURCE_IMBALANCE = "resource_imbalance"
    ORDER_VIOLATION = "order_violation"
    MAGIC_NUMBER = "magic_number"
    MISSING_OPERATION_LOOP = "missing_op_loop"
    API_HALLUCINATION = "api_hallucination"
    CROSS_PLATFORM_CONFUSION = "cross_platform"
    MISSING_SAFETY_PATTERN = "missing_safety"
    UNKNOWN = "unknown"


class FailureClassification(BaseModel):
    """Classification result for a single failed case."""

    case_id: str
    failed_layer: int
    pattern: FailurePattern
    failed_checks: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


class TaxonomyReport(BaseModel):
    """Failure taxonomy analysis report."""

    total_failures: int
    pattern_distribution: dict[str, int]
    classifications: list[FailureClassification]
    top_patterns: list[tuple[str, int]]


# Check name → failure pattern mapping
CHECK_PATTERN_MAP: dict[str, FailurePattern] = {
    # Happy path bias (error handling missing)
    "error_handling": FailurePattern.HAPPY_PATH_BIAS,
    "init_error_handling": FailurePattern.HAPPY_PATH_BIAS,
    "init_error_path_cleanup": FailurePattern.HAPPY_PATH_BIAS,
    "init_cleanup_no_comments": FailurePattern.HAPPY_PATH_BIAS,
    "error_path_returns": FailurePattern.HAPPY_PATH_BIAS,
    "dma_error_handling": FailurePattern.HAPPY_PATH_BIAS,
    "cleanup_on_error": FailurePattern.HAPPY_PATH_BIAS,
    # Semantic mismatch (compiles but wrong HW semantics)
    "cyclic_enabled": FailurePattern.SEMANTIC_MISMATCH,
    "reload_in_callback": FailurePattern.SEMANTIC_MISMATCH,
    "cache_aligned": FailurePattern.SEMANTIC_MISMATCH,
    "volatile_shared": FailurePattern.SEMANTIC_MISMATCH,
    "device_ready_check": FailurePattern.SEMANTIC_MISMATCH,
    "spinlock_used_in_both_contexts": FailurePattern.SEMANTIC_MISMATCH,
    # Resource imbalance (alloc without free)
    "register_unregister_balanced": FailurePattern.RESOURCE_IMBALANCE,
    "spinlock_balanced": FailurePattern.RESOURCE_IMBALANCE,
    "dma_stop_called": FailurePattern.RESOURCE_IMBALANCE,
    # Order violation
    "callback_before_sleep": FailurePattern.ORDER_VIOLATION,
    "key_passed_to_unlock": FailurePattern.ORDER_VIOLATION,
    # Cross-platform confusion
    "no_cross_platform_apis": FailurePattern.CROSS_PLATFORM_CONFUSION,
    "no_zephyr_apis_in_linux_driver": FailurePattern.CROSS_PLATFORM_CONFUSION,
    "no_freertos_apis": FailurePattern.CROSS_PLATFORM_CONFUSION,
    # API hallucination
    "no_hallucinated_apis": FailurePattern.API_HALLUCINATION,
    "no_deprecated_gpio_request": FailurePattern.API_HALLUCINATION,
    # Safety patterns missing
    "no_forbidden_apis_in_isr": FailurePattern.MISSING_SAFETY_PATTERN,
    "no_mutex_in_isr": FailurePattern.MISSING_SAFETY_PATTERN,
    "this_module_owner": FailurePattern.MISSING_SAFETY_PATTERN,
}


def classify_failure(result: EvalResult) -> FailureClassification | None:
    """Auto-classify a single failed result based on which checks failed.

    Returns None if the result passed (no failure to classify).
    """
    if result.passed:
        return None

    failed_layer = result.failed_at_layer if result.failed_at_layer is not None else -1
    failed_checks: list[str] = []

    for layer in result.layers:
        for detail in layer.details:
            if not detail.passed:
                failed_checks.append(detail.check_name)

    if not failed_checks:
        return FailureClassification(
            case_id=result.case_id,
            failed_layer=failed_layer,
            pattern=FailurePattern.UNKNOWN,
            failed_checks=[],
            confidence=0.0,
        )

    # Find the most common pattern among failed checks
    pattern_votes: Counter[FailurePattern] = Counter()
    for check_name in failed_checks:
        pattern = _match_check_to_pattern(check_name)
        pattern_votes[pattern] += 1

    if not pattern_votes:
        best_pattern = FailurePattern.UNKNOWN
        confidence = 0.0
    else:
        best_pattern = pattern_votes.most_common(1)[0][0]
        total_votes = sum(pattern_votes.values())
        confidence = pattern_votes[best_pattern] / total_votes

    return FailureClassification(
        case_id=result.case_id,
        failed_layer=failed_layer,
        pattern=best_pattern,
        failed_checks=failed_checks,
        confidence=confidence,
    )


def classify_all(results: list[EvalResult]) -> TaxonomyReport:
    """Classify all failures in a result set.

    Args:
        results: List of EvalResult (passed and failed).

    Returns:
        TaxonomyReport with pattern distribution and per-case classifications.
    """
    classifications: list[FailureClassification] = []
    for r in results:
        fc = classify_failure(r)
        if fc is not None:
            classifications.append(fc)

    distribution: Counter[str] = Counter()
    for c in classifications:
        distribution[c.pattern.value] += 1

    top = distribution.most_common()

    return TaxonomyReport(
        total_failures=len(classifications),
        pattern_distribution=dict(distribution),
        classifications=classifications,
        top_patterns=top,
    )


def _match_check_to_pattern(check_name: str) -> FailurePattern:
    """Match a check name to a failure pattern.

    First checks exact match in CHECK_PATTERN_MAP, then tries
    keyword-based heuristic matching.
    """
    if check_name in CHECK_PATTERN_MAP:
        return CHECK_PATTERN_MAP[check_name]

    # Keyword heuristic
    name_lower = check_name.lower()
    if any(kw in name_lower for kw in ("error", "cleanup", "rollback")):
        return FailurePattern.HAPPY_PATH_BIAS
    if any(kw in name_lower for kw in ("cross_platform", "hallucin", "wrong_api")):
        return FailurePattern.CROSS_PLATFORM_CONFUSION
    if any(kw in name_lower for kw in ("balanced", "free", "unregister", "stop")):
        return FailurePattern.RESOURCE_IMBALANCE
    if any(kw in name_lower for kw in ("order", "before", "after", "sequence")):
        return FailurePattern.ORDER_VIOLATION
    if any(kw in name_lower for kw in ("volatile", "barrier", "align", "cache")):
        return FailurePattern.SEMANTIC_MISMATCH
    if any(kw in name_lower for kw in ("isr", "forbidden", "mutex", "safety")):
        return FailurePattern.MISSING_SAFETY_PATTERN

    return FailurePattern.UNKNOWN
