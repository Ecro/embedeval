"""Tests for EmbedEval scorer."""

from math import comb

from embedeval.models import (
    EvalResult,
    LayerResult,
    TokenUsage,
)
from embedeval.scorer import (
    _calculate_pass_at_k,
    _count_quality_passes,
    score,
    wilson_ci,
)


def _make_result(
    case_id: str = "case-001",
    model: str = "gpt-4",
    attempt: int = 1,
    passed: bool = True,
    failed_at_layer: int | None = None,
) -> EvalResult:
    """Create a minimal EvalResult for testing."""
    layers = []
    for i in range(5):
        layer_passed = passed if failed_at_layer is None else (i < failed_at_layer)
        layers.append(
            LayerResult(
                layer=i,
                name=f"layer_{i}",
                passed=layer_passed,
                details=[],
                error=None if layer_passed else "failed",
                duration_seconds=0.1,
            )
        )

    return EvalResult(
        case_id=case_id,
        model=model,
        attempt=attempt,
        generated_code="int main() {}",
        layers=layers,
        failed_at_layer=failed_at_layer,
        passed=passed,
        duration_seconds=0.5,
        token_usage=TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150),
        cost_usd=0.001,
    )


class TestScoreBasic:
    """Tests for basic scoring behavior."""

    def test_empty_results(self) -> None:
        report = score([])
        assert report.overall.total_cases == 0
        assert report.overall.total_models == 0
        assert report.models == []
        assert report.categories == []

    def test_single_passing_result(self) -> None:
        results = [_make_result(passed=True)]
        report = score(results)
        assert len(report.models) == 1
        assert report.models[0].pass_at_1 == 1.0
        assert report.models[0].passed_cases == 1

    def test_single_failing_result(self) -> None:
        results = [_make_result(passed=False, failed_at_layer=0)]
        report = score(results)
        assert report.models[0].pass_at_1 == 0.0
        assert report.models[0].passed_cases == 0

    def test_report_version(self) -> None:
        report = score([_make_result()])
        assert report.version == "0.1.0"

    def test_report_date_format(self) -> None:
        report = score([_make_result()])
        assert len(report.date) == 10
        assert report.date[4] == "-"


class TestPassAt1:
    """Tests for pass@1 calculation."""

    def test_all_pass(self) -> None:
        results = [
            _make_result(case_id="case-001", passed=True),
            _make_result(case_id="case-002", passed=True),
        ]
        report = score(results)
        assert report.models[0].pass_at_1 == 1.0

    def test_half_pass(self) -> None:
        results = [
            _make_result(case_id="case-001", passed=True),
            _make_result(case_id="case-002", passed=False, failed_at_layer=0),
        ]
        report = score(results)
        assert report.models[0].pass_at_1 == 0.5

    def test_none_pass(self) -> None:
        results = [
            _make_result(case_id="case-001", passed=False, failed_at_layer=0),
            _make_result(case_id="case-002", passed=False, failed_at_layer=1),
        ]
        report = score(results)
        assert report.models[0].pass_at_1 == 0.0


class TestPassAt5:
    """Tests for pass@5 calculation."""

    def test_one_of_five_passes(self) -> None:
        results = [
            _make_result(
                case_id="case-001", attempt=1, passed=False, failed_at_layer=0
            ),
            _make_result(
                case_id="case-001", attempt=2, passed=False, failed_at_layer=0
            ),
            _make_result(
                case_id="case-001", attempt=3, passed=False, failed_at_layer=0
            ),
            _make_result(
                case_id="case-001", attempt=4, passed=False, failed_at_layer=0
            ),
            _make_result(case_id="case-001", attempt=5, passed=True),
        ]
        report = score(results)
        assert report.models[0].pass_at_5 == 1.0

    def test_none_of_five_passes(self) -> None:
        results = [
            _make_result(case_id="case-001", attempt=i, passed=False, failed_at_layer=0)
            for i in range(1, 6)
        ]
        report = score(results)
        assert report.models[0].pass_at_5 == 0.0


class TestMultiModel:
    """Tests for multi-model comparison."""

    def test_two_models_compared(self) -> None:
        results = [
            _make_result(case_id="case-001", model="gpt-4", passed=True),
            _make_result(
                case_id="case-001", model="claude-3", passed=False, failed_at_layer=0
            ),
        ]
        report = score(results)
        assert len(report.models) == 2
        assert report.overall.total_models == 2
        assert report.overall.best_model == "gpt-4"
        assert report.overall.best_pass_at_1 == 1.0


class TestLayerPassRates:
    """Tests for layer pass rate calculation."""

    def test_layer_rates_all_pass(self) -> None:
        results = [_make_result(passed=True)]
        report = score(results)
        for rate in report.models[0].layer_pass_rates.values():
            assert rate == 1.0

    def test_layer_rates_partial_fail(self) -> None:
        results = [_make_result(passed=False, failed_at_layer=2)]
        report = score(results)
        rates = report.models[0].layer_pass_rates
        assert rates["layer_0"] == 1.0
        assert rates["layer_1"] == 1.0
        assert rates["layer_2"] == 0.0


class TestCategoryScores:
    """Tests for per-category scoring."""

    def test_category_scores_calculated(self) -> None:
        results = [
            _make_result(case_id="kconfig-001", passed=True),
            _make_result(case_id="kconfig-002", passed=False, failed_at_layer=0),
        ]
        report = score(results)
        assert len(report.categories) == 1
        assert report.categories[0].total_cases == 2
        assert report.categories[0].passed_cases == 1
        assert report.categories[0].pass_at_1 == 0.5


class TestUnbiasedPassAtK:
    """Tests for unbiased pass@k estimator: 1 - C(n-c,k)/C(n,k)."""

    def test_exact_formula_n10_c3_k5(self) -> None:
        """Verify against hand-calculated value: n=10, c=3, k=5."""
        # 1 - C(7,5)/C(10,5) = 1 - 21/252 = 1 - 0.08333... = 0.91667
        results = []
        for i in range(1, 11):
            results.append(
                _make_result(
                    case_id="case-001",
                    attempt=i,
                    passed=(i <= 3),  # first 3 pass
                )
            )
        pass_at_5 = _calculate_pass_at_k(results, 5)
        expected = 1.0 - comb(7, 5) / comb(10, 5)
        assert abs(pass_at_5 - expected) < 1e-10

    def test_exact_formula_n10_c1_k1(self) -> None:
        """pass@1 with n=10, c=1: should be c/n = 0.1."""
        results = [
            _make_result(
                case_id="case-001",
                attempt=i,
                passed=(i == 5),
                failed_at_layer=0 if i != 5 else None,
            )
            for i in range(1, 11)
        ]
        pass_at_1 = _calculate_pass_at_k(results, 1)
        expected = 1.0 - comb(9, 1) / comb(10, 1)  # 1 - 9/10 = 0.1
        assert abs(pass_at_1 - expected) < 1e-10

    def test_all_correct_returns_one(self) -> None:
        """n=5, c=5, k=3: should return 1.0."""
        results = [
            _make_result(case_id="case-001", attempt=i, passed=True)
            for i in range(1, 6)
        ]
        assert _calculate_pass_at_k(results, 3) == 1.0

    def test_none_correct_returns_zero(self) -> None:
        """n=5, c=0, k=3: should return 0.0."""
        results = [
            _make_result(case_id="case-001", attempt=i, passed=False, failed_at_layer=0)
            for i in range(1, 6)
        ]
        assert _calculate_pass_at_k(results, 3) == 0.0

    def test_k_greater_than_n_fallback(self) -> None:
        """n=3, k=5: falls back to empirical (any correct → 1.0)."""
        results = [
            _make_result(
                case_id="case-001", attempt=1, passed=False, failed_at_layer=0
            ),
            _make_result(case_id="case-001", attempt=2, passed=True),
            _make_result(
                case_id="case-001", attempt=3, passed=False, failed_at_layer=0
            ),
        ]
        assert _calculate_pass_at_k(results, 5) == 1.0

    def test_k_greater_than_n_none_correct(self) -> None:
        """n=3, k=5, c=0: should return 0.0."""
        results = [
            _make_result(case_id="case-001", attempt=i, passed=False, failed_at_layer=0)
            for i in range(1, 4)
        ]
        assert _calculate_pass_at_k(results, 5) == 0.0

    def test_multi_case_averaging(self) -> None:
        """Two cases: one always passes, one always fails → 0.5."""
        results = [
            _make_result(case_id="case-001", attempt=1, passed=True),
            _make_result(
                case_id="case-002", attempt=1, passed=False, failed_at_layer=0
            ),
        ]
        assert _calculate_pass_at_k(results, 1) == 0.5

    def test_empty_results(self) -> None:
        assert _calculate_pass_at_k([], 1) == 0.0


class TestWilsonCI:
    """Tests for Wilson score confidence interval."""

    def test_zero_cases(self) -> None:
        assert wilson_ci(0.5, 0) == (0.0, 0.0)

    def test_perfect_score_small_n(self) -> None:
        lo, hi = wilson_ci(1.0, 10)
        assert lo < 1.0
        assert hi == 1.0

    def test_zero_score_small_n(self) -> None:
        lo, hi = wilson_ci(0.0, 10)
        assert lo == 0.0
        assert hi > 0.0

    def test_interval_contains_point_estimate(self) -> None:
        lo, hi = wilson_ci(0.5, 100)
        assert lo < 0.5 < hi

    def test_larger_n_gives_tighter_interval(self) -> None:
        lo10, hi10 = wilson_ci(0.5, 10)
        lo100, hi100 = wilson_ci(0.5, 100)
        assert (hi100 - lo100) < (hi10 - lo10)

    def test_known_value(self) -> None:
        """n=220, p=0.89: interval should be roughly (0.84, 0.93)."""
        lo, hi = wilson_ci(0.89, 220)
        assert 0.83 < lo < 0.86
        assert 0.92 < hi < 0.94


class TestModelScoreCI:
    """Tests that model scores include CI and n_samples."""

    def test_ci_present(self) -> None:
        results = [
            _make_result(case_id="case-001", passed=True),
            _make_result(case_id="case-002", passed=False, failed_at_layer=0),
        ]
        report = score(results)
        ms = report.models[0]
        lo, hi = ms.pass_at_1_ci
        assert lo < ms.pass_at_1
        assert hi > ms.pass_at_1

    def test_n_samples_recorded(self) -> None:
        results = [
            _make_result(case_id="case-001", attempt=1, passed=True),
            _make_result(case_id="case-001", attempt=2, passed=True),
        ]
        report = score(results)
        assert report.models[0].n_samples == 2


class TestBenchmarkReportMetadata:
    """Tests for report metadata fields."""

    def test_default_metadata(self) -> None:
        report = score([_make_result()])
        assert report.temperature == 0.0
        assert report.n_samples_per_case == 1
        assert report.n_runs == 1


class TestQualityScoring:
    """Tests for _count_quality_passes() — L0+L3 only scoring."""

    def _make_layered_result(
        self,
        case_id: str,
        l0_pass: bool = True,
        l1_pass: bool = True,
        l2_pass: bool = True,
        l3_pass: bool = True,
        l3_skipped: bool = False,
    ) -> EvalResult:
        """Create a result with specific layer outcomes."""
        layers = []
        for i, (passed, name) in enumerate(
            [
                (l0_pass, "static_analysis"),
                (l1_pass, "compile_gate"),
                (l2_pass, "runtime_execution"),
                (l3_pass if not l3_skipped else False, "static_heuristic"),
                (True, "test_quality_proof"),
            ]
        ):
            error = None
            if not passed:
                error = "Skipped: layer 1 failed" if l3_skipped and i == 3 else "failed"
            layers.append(
                LayerResult(
                    layer=i,
                    name=name,
                    passed=passed,
                    details=[],
                    error=error,
                    duration_seconds=0.1,
                )
            )

        failed_at = None
        overall_pass = l0_pass and l1_pass and l2_pass and (l3_pass or l3_skipped)
        if not overall_pass:
            for i, p in enumerate([l0_pass, l1_pass, l2_pass, l3_pass]):
                if not p:
                    failed_at = i
                    break

        return EvalResult(
            case_id=case_id,
            model="test",
            attempt=1,
            generated_code="int main() {}",
            layers=layers,
            failed_at_layer=failed_at,
            passed=overall_pass,
            duration_seconds=0.5,
            token_usage=TokenUsage(
                input_tokens=100, output_tokens=50, total_tokens=150
            ),
            cost_usd=0.001,
        )

    def test_all_pass_counts_as_quality_pass(self):
        r = self._make_layered_result("c1")
        assert _count_quality_passes([r], {"c1"}) == 1

    def test_l1_fail_still_quality_pass(self):
        """L1 compile failure should not affect quality score (L0+L3 only)."""
        r = self._make_layered_result("c1", l1_pass=False, l3_skipped=True)
        assert _count_quality_passes([r], {"c1"}) == 1

    def test_l2_fail_still_quality_pass(self):
        """L2 runtime failure should not affect quality score."""
        r = self._make_layered_result("c1", l2_pass=False, l3_skipped=True)
        assert _count_quality_passes([r], {"c1"}) == 1

    def test_l0_fail_no_quality_pass(self):
        """L0 static failure means quality fail."""
        r = self._make_layered_result("c1", l0_pass=False)
        assert _count_quality_passes([r], {"c1"}) == 0

    def test_l3_fail_no_quality_pass(self):
        """L3 heuristic failure means quality fail."""
        r = self._make_layered_result("c1", l3_pass=False)
        assert _count_quality_passes([r], {"c1"}) == 0

    def test_quality_score_in_report(self):
        """Verify pass_at_1_quality is populated in the scored report."""
        results = [_make_result(passed=True)]
        report = score(results)
        assert report.models[0].pass_at_1_quality >= 0.0
