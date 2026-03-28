"""Tests for Safety Guide generator."""

from pathlib import Path

from embedeval.models import (
    CaseCategory,
    CaseTier,
    EvalResult,
    LayerResult,
    ReasoningType,
    TokenUsage,
)
from embedeval.safety_guide import (
    _calculate_category_pass_rates,
    _task_success_rate,
    generate_safety_guide,
)


def _make_result(
    case_id: str = "case-001",
    model: str = "sonnet",
    passed: bool = True,
    tier: CaseTier = CaseTier.CORE,
    reasoning_types: list[ReasoningType] | None = None,
    failed_checks: list[str] | None = None,
    category: CaseCategory | None = None,
) -> EvalResult:
    from embedeval.models import CheckDetail

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
        LayerResult(layer=i, name=f"layer_{i}", passed=passed if i != 3 else (not failed_checks),
                    details=details if i == 3 else [], duration_seconds=0.0)
        for i in range(5)
    ]

    return EvalResult(
        case_id=case_id,
        category=category,
        model=model,
        attempt=1,
        generated_code="",
        layers=layers,
        passed=passed and not failed_checks,
        failed_at_layer=3 if failed_checks else None,
        duration_seconds=0.1,
        token_usage=TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0),
        cost_usd=0.0,
        tier=tier,
        reasoning_types=reasoning_types or [],
    )


class TestGenerateSafetyGuide:

    def test_generates_file(self, tmp_path: Path) -> None:
        results = [_make_result()]
        output = tmp_path / "SAFETY-GUIDE.md"
        generate_safety_guide(results, output)
        assert output.is_file()
        content = output.read_text()
        assert "Safety Guide" in content

    def test_contains_capability_boundary(self, tmp_path: Path) -> None:
        results = [_make_result()]
        output = tmp_path / "guide.md"
        generate_safety_guide(results, output)
        content = output.read_text()
        assert "Capability Boundary" in content
        assert "What LLMs Do Well" in content
        assert "What LLMs Cannot Do" in content

    def test_contains_task_checklists(self, tmp_path: Path) -> None:
        results = [_make_result()]
        output = tmp_path / "guide.md"
        generate_safety_guide(results, output)
        content = output.read_text()
        assert "ISR / Interrupt Handlers" in content
        assert "Error Recovery Paths" in content
        assert "volatile" in content

    def test_contains_reasoning_risk_table(self, tmp_path: Path) -> None:
        results = [
            _make_result("c1", passed=True, reasoning_types=[ReasoningType.API_RECALL]),
            _make_result("c2", passed=False, reasoning_types=[ReasoningType.SYSTEM_REASONING],
                        failed_checks=["error_handling"]),
        ]
        output = tmp_path / "guide.md"
        generate_safety_guide(results, output)
        content = output.read_text()
        assert "Reasoning Level" in content
        assert "L1 API Recall" in content

    def test_contains_failure_statistics(self, tmp_path: Path) -> None:
        results = [
            _make_result("c1", passed=True),
            _make_result("c2", passed=False, failed_checks=["error_handling"]),
            _make_result("c3", passed=False, failed_checks=["no_cross_platform_apis"]),
        ]
        output = tmp_path / "guide.md"
        generate_safety_guide(results, output)
        content = output.read_text()
        assert "Failure Pattern" in content
        assert "happy_path_bias" in content

    def test_contains_engineer_guidelines(self, tmp_path: Path) -> None:
        results = [_make_result()]
        output = tmp_path / "guide.md"
        generate_safety_guide(results, output)
        content = output.read_text()
        assert "Engineer Guidelines" in content
        assert "Recommended Workflow" in content
        assert "What LLMs Will Never Replace" in content

    def test_model_auto_detected(self, tmp_path: Path) -> None:
        results = [_make_result(model="claude-sonnet")]
        output = tmp_path / "guide.md"
        generate_safety_guide(results, output)
        content = output.read_text()
        assert "claude-sonnet" in content

    def test_no_failures_handled(self, tmp_path: Path) -> None:
        results = [_make_result("c1", passed=True), _make_result("c2", passed=True)]
        output = tmp_path / "guide.md"
        generate_safety_guide(results, output)
        content = output.read_text()
        assert "No failures detected" in content

    def test_empty_results(self, tmp_path: Path) -> None:
        output = tmp_path / "guide.md"
        generate_safety_guide([], output, model="test")
        assert output.is_file()

    def test_dynamic_success_rate_from_results(self, tmp_path: Path) -> None:
        """Success rate in checklists must come from benchmark data, not hardcoded."""
        results = [
            _make_result("isr-concurrency-001", passed=True, category=CaseCategory.ISR_CONCURRENCY),
            _make_result("isr-concurrency-002", passed=True, category=CaseCategory.ISR_CONCURRENCY),
            _make_result("isr-concurrency-003", passed=False, category=CaseCategory.ISR_CONCURRENCY,
                        failed_checks=["no_mutex_in_isr"]),
            _make_result("dma-001", passed=True, category=CaseCategory.DMA),
            _make_result("dma-002", passed=False, category=CaseCategory.DMA,
                        failed_checks=["cache_aligned"]),
        ]
        output = tmp_path / "guide.md"
        generate_safety_guide(results, output)
        content = output.read_text()
        # ISR: 2/3 = 67%
        assert "67%" in content
        # DMA: 1/2 = 50%
        assert "50%" in content

    def test_no_data_shows_na(self, tmp_path: Path) -> None:
        """Tasks with no matching results show N/A."""
        results = [
            _make_result("gpio-basic-001", passed=True, category=CaseCategory.GPIO_BASIC),
        ]
        output = tmp_path / "guide.md"
        generate_safety_guide(results, output)
        content = output.read_text()
        # ISR has no results → N/A
        assert "N/A" in content


class TestCategoryPassRates:

    def test_rates_from_category_field(self) -> None:
        results = [
            _make_result("isr-concurrency-001", passed=True, category=CaseCategory.ISR_CONCURRENCY),
            _make_result("isr-concurrency-002", passed=False, category=CaseCategory.ISR_CONCURRENCY,
                        failed_checks=["x"]),
        ]
        rates = _calculate_category_pass_rates(results)
        assert rates["isr-concurrency"] == 0.5

    def test_rates_fallback_to_case_id(self) -> None:
        results = [
            _make_result("dma-001", passed=True),
            _make_result("dma-002", passed=True),
            _make_result("dma-003", passed=False, failed_checks=["x"]),
        ]
        rates = _calculate_category_pass_rates(results)
        assert abs(rates["dma"] - 2 / 3) < 0.01

    def test_empty_results(self) -> None:
        assert _calculate_category_pass_rates([]) == {}

    def test_multi_category_task_averages(self) -> None:
        cat_rates = {"gpio-basic": 0.9, "spi-i2c": 0.8}
        rate = _task_success_rate(["gpio-basic", "spi-i2c"], cat_rates)
        assert rate == "85%"

    def test_missing_category_ignored(self) -> None:
        cat_rates = {"gpio-basic": 0.9}
        rate = _task_success_rate(["gpio-basic", "spi-i2c"], cat_rates)
        assert rate == "90%"

    def test_no_matching_categories(self) -> None:
        rate = _task_success_rate(["watchdog"], {})
        assert "N/A" in rate
