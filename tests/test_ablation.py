"""Tests for ablation study module."""

from embedeval.ablation import AblationReport, run_ablation
from embedeval.models import (
    CheckDetail,
    EvalResult,
    LayerResult,
    TokenUsage,
)


def _make_result(
    case_id: str = "case-001",
    model: str = "model-a",
    layer_results: list[bool] | None = None,
) -> EvalResult:
    """Create EvalResult with specified layer pass/fail pattern."""
    if layer_results is None:
        layer_results = [True] * 5

    layers = []
    failed_at = None
    for i, passed in enumerate(layer_results):
        if not passed and failed_at is None:
            failed_at = i
        layers.append(
            LayerResult(
                layer=i,
                name=f"layer_{i}",
                passed=passed,
                details=[
                    CheckDetail(
                        check_name=f"check_{i}",
                        passed=passed,
                        expected="pass",
                        actual="pass" if passed else "fail",
                        check_type="test",
                    )
                ],
                duration_seconds=0.0,
            )
        )

    return EvalResult(
        case_id=case_id,
        model=model,
        attempt=1,
        generated_code="",
        layers=layers,
        passed=all(layer_results),
        failed_at_layer=failed_at,
        duration_seconds=0.1,
        token_usage=TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0),
        cost_usd=0.0,
    )


class TestRunAblation:

    def test_all_pass_returns_100_percent(self) -> None:
        results = [_make_result("c1"), _make_result("c2")]
        report = run_ablation(results)
        for config in report.configs:
            assert config.pass_rate == 1.0

    def test_l3_failure_shows_contribution(self) -> None:
        results = [
            _make_result("c1", layer_results=[True, True, True, False, False]),
            _make_result("c2", layer_results=[True, True, True, True, True]),
        ]
        report = run_ablation(results)

        # L0 only: both pass (L0=True for both)
        l0_config = next(c for c in report.configs if c.name == "L0 only")
        assert l0_config.pass_rate == 1.0

        # L0 + L3: c1 fails at L3, c2 passes → 50%
        l0_l3_config = next(c for c in report.configs if c.name == "L0 + L3")
        assert l0_l3_config.pass_rate == 0.5

        # L3 contribution should be positive
        assert report.layer_contributions["L3 (heuristic)"] > 0

    def test_l1_failure_shows_contribution(self) -> None:
        results = [
            _make_result("c1", layer_results=[True, False, False, True, True]),
            _make_result("c2", layer_results=[True, True, True, True, True]),
        ]
        report = run_ablation(results)
        assert report.layer_contributions["L1 (compile)"] > 0

    def test_empty_results(self) -> None:
        report = run_ablation([])
        assert report.configs == []
        assert report.layer_contributions == {}

    def test_model_filter(self) -> None:
        results = [
            _make_result("c1", model="sonnet"),
            _make_result("c1", model="haiku", layer_results=[True, True, True, False, False]),
        ]
        report = run_ablation(results, model="haiku")
        assert report.model == "haiku"
        # Only haiku result used — c1 fails at L3
        l0_l3 = next(c for c in report.configs if c.name == "L0 + L3")
        assert l0_l3.pass_rate == 0.0

    def test_configs_have_correct_layer_lists(self) -> None:
        results = [_make_result("c1")]
        report = run_ablation(results)
        names = [c.name for c in report.configs]
        assert "L0 only" in names
        assert "L0 + L3" in names
        assert "L0 + L1" in names
        assert "Full (L0-L4)" in names
