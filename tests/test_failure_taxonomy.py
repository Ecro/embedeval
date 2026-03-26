"""Tests for failure taxonomy module."""

from embedeval.failure_taxonomy import (
    FailurePattern,
    classify_all,
    classify_failure,
    _match_check_to_pattern,
)
from embedeval.models import (
    CheckDetail,
    EvalResult,
    LayerResult,
    TokenUsage,
)


def _make_result(
    case_id: str = "case-001",
    passed: bool = True,
    failed_checks: list[str] | None = None,
) -> EvalResult:
    details = []
    if failed_checks:
        for name in failed_checks:
            details.append(
                CheckDetail(
                    check_name=name, passed=False,
                    expected="pass", actual="fail", check_type="test",
                )
            )

    layers = [
        LayerResult(
            layer=3, name="static_heuristic",
            passed=passed, details=details, duration_seconds=0.0,
        )
    ]
    # Pad other layers
    for i in [0, 1, 2, 4]:
        layers.insert(i, LayerResult(
            layer=i, name=f"layer_{i}", passed=True, details=[], duration_seconds=0.0,
        ))

    return EvalResult(
        case_id=case_id,
        model="test",
        attempt=1,
        generated_code="",
        layers=layers,
        passed=passed,
        failed_at_layer=3 if not passed else None,
        duration_seconds=0.1,
        token_usage=TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0),
        cost_usd=0.0,
    )


class TestClassifyFailure:

    def test_passed_result_returns_none(self) -> None:
        result = _make_result(passed=True)
        assert classify_failure(result) is None

    def test_error_handling_classified_as_happy_path(self) -> None:
        result = _make_result(passed=False, failed_checks=["error_handling"])
        fc = classify_failure(result)
        assert fc is not None
        assert fc.pattern == FailurePattern.HAPPY_PATH_BIAS

    def test_cross_platform_classified(self) -> None:
        result = _make_result(passed=False, failed_checks=["no_cross_platform_apis"])
        fc = classify_failure(result)
        assert fc is not None
        assert fc.pattern == FailurePattern.CROSS_PLATFORM_CONFUSION

    def test_multiple_checks_votes_majority(self) -> None:
        result = _make_result(
            passed=False,
            failed_checks=["error_handling", "init_error_handling", "no_cross_platform_apis"],
        )
        fc = classify_failure(result)
        assert fc is not None
        # 2 happy_path vs 1 cross_platform → happy_path wins
        assert fc.pattern == FailurePattern.HAPPY_PATH_BIAS
        assert fc.confidence > 0.5

    def test_unknown_check_classified_as_unknown(self) -> None:
        result = _make_result(passed=False, failed_checks=["xyz_random_check"])
        fc = classify_failure(result)
        assert fc is not None
        assert fc.pattern == FailurePattern.UNKNOWN

    def test_no_failed_checks_returns_unknown(self) -> None:
        result = _make_result(passed=False, failed_checks=[])
        fc = classify_failure(result)
        assert fc is not None
        assert fc.pattern == FailurePattern.UNKNOWN
        assert fc.confidence == 0.0


class TestMatchCheckToPattern:

    def test_exact_match(self) -> None:
        assert _match_check_to_pattern("error_handling") == FailurePattern.HAPPY_PATH_BIAS

    def test_keyword_heuristic_error(self) -> None:
        assert _match_check_to_pattern("missing_error_check") == FailurePattern.HAPPY_PATH_BIAS

    def test_keyword_heuristic_volatile(self) -> None:
        assert _match_check_to_pattern("volatile_missing") == FailurePattern.SEMANTIC_MISMATCH

    def test_keyword_heuristic_isr(self) -> None:
        assert _match_check_to_pattern("isr_blocking_call") == FailurePattern.MISSING_SAFETY_PATTERN

    def test_no_match_returns_unknown(self) -> None:
        assert _match_check_to_pattern("completely_unrelated") == FailurePattern.UNKNOWN


class TestClassifyAll:

    def test_mixed_results(self) -> None:
        results = [
            _make_result("c1", passed=True),
            _make_result("c2", passed=False, failed_checks=["error_handling"]),
            _make_result("c3", passed=False, failed_checks=["no_cross_platform_apis"]),
        ]
        report = classify_all(results)
        assert report.total_failures == 2
        assert "happy_path_bias" in report.pattern_distribution
        assert "cross_platform" in report.pattern_distribution

    def test_all_pass_no_failures(self) -> None:
        results = [_make_result("c1", passed=True)]
        report = classify_all(results)
        assert report.total_failures == 0
        assert report.top_patterns == []

    def test_top_patterns_sorted(self) -> None:
        results = [
            _make_result("c1", passed=False, failed_checks=["error_handling"]),
            _make_result("c2", passed=False, failed_checks=["init_error_handling"]),
            _make_result("c3", passed=False, failed_checks=["no_cross_platform_apis"]),
        ]
        report = classify_all(results)
        # happy_path_bias=2, cross_platform=1
        assert report.top_patterns[0][0] == "happy_path_bias"
        assert report.top_patterns[0][1] == 2
