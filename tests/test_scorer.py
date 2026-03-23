"""Tests for EmbedEval scorer."""

from embedeval.models import (
    EvalResult,
    LayerResult,
    TokenUsage,
)
from embedeval.scorer import score


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
        token_usage=TokenUsage(
            input_tokens=100, output_tokens=50, total_tokens=150
        ),
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
            _make_result(case_id="case-001", attempt=1, passed=False, failed_at_layer=0),
            _make_result(case_id="case-001", attempt=2, passed=False, failed_at_layer=0),
            _make_result(case_id="case-001", attempt=3, passed=False, failed_at_layer=0),
            _make_result(case_id="case-001", attempt=4, passed=False, failed_at_layer=0),
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
            _make_result(case_id="case-001", model="claude-3", passed=False, failed_at_layer=0),
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
