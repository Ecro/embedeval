"""Tests for IRT difficulty calibration."""

from embedeval.difficulty import (
    IRTParams,
    _suggest_difficulty,
    calibrate_difficulty,
)
from embedeval.models import (
    DifficultyTier,
    EvalResult,
    LayerResult,
    TokenUsage,
)


def _make_result(
    case_id: str = "case-001",
    model: str = "model-a",
    passed: bool = True,
) -> EvalResult:
    layers = [
        LayerResult(
            layer=i, name=f"layer_{i}", passed=passed,
            details=[], duration_seconds=0.0,
        )
        for i in range(5)
    ]
    return EvalResult(
        case_id=case_id,
        model=model,
        attempt=1,
        generated_code="",
        layers=layers,
        passed=passed,
        duration_seconds=0.1,
        token_usage=TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0),
        cost_usd=0.0,
    )


class TestSuggestDifficulty:

    def test_high_pass_rate_is_easy(self) -> None:
        assert _suggest_difficulty(0.95) == DifficultyTier.EASY

    def test_medium_pass_rate(self) -> None:
        assert _suggest_difficulty(0.6) == DifficultyTier.MEDIUM

    def test_low_pass_rate_is_hard(self) -> None:
        assert _suggest_difficulty(0.2) == DifficultyTier.HARD

    def test_boundary_80_is_medium(self) -> None:
        assert _suggest_difficulty(0.8) == DifficultyTier.MEDIUM

    def test_boundary_40_is_medium(self) -> None:
        assert _suggest_difficulty(0.4) == DifficultyTier.MEDIUM

    def test_zero_is_hard(self) -> None:
        assert _suggest_difficulty(0.0) == DifficultyTier.HARD

    def test_one_is_easy(self) -> None:
        assert _suggest_difficulty(1.0) == DifficultyTier.EASY


class TestCalibrateDifficulty:

    def test_single_model_all_pass(self) -> None:
        results = [
            _make_result(case_id="c1", model="m1", passed=True),
            _make_result(case_id="c2", model="m1", passed=True),
        ]
        report = calibrate_difficulty(results)
        assert report.total_cases == 2
        assert all(item.empirical_pass_rate == 1.0 for item in report.items)
        assert len(report.floor_cases) == 2

    def test_two_models_different_results(self) -> None:
        results = [
            _make_result(case_id="c1", model="m1", passed=True),
            _make_result(case_id="c1", model="m2", passed=False),
        ]
        report = calibrate_difficulty(results)
        assert report.total_cases == 1
        item = report.items[0]
        assert item.empirical_pass_rate == 0.5
        assert item.difficulty_b == 0.5
        assert item.discrimination_a > 0.0

    def test_discrimination_zero_when_single_model(self) -> None:
        results = [_make_result(case_id="c1", model="m1", passed=True)]
        report = calibrate_difficulty(results)
        assert report.items[0].discrimination_a == 0.0

    def test_floor_and_ceiling_cases(self) -> None:
        results = [
            _make_result(case_id="easy", model="m1", passed=True),
            _make_result(case_id="easy", model="m2", passed=True),
            _make_result(case_id="hard", model="m1", passed=False),
            _make_result(case_id="hard", model="m2", passed=False),
        ]
        report = calibrate_difficulty(results)
        assert "easy" in report.floor_cases
        assert "hard" in report.ceiling_cases

    def test_mislabel_detection(self) -> None:
        # All pass → empirical=easy, but assigned=medium (default) → mislabeled
        results = [
            _make_result(case_id="c1", model="m1", passed=True),
            _make_result(case_id="c1", model="m2", passed=True),
        ]
        report = calibrate_difficulty(results)
        item = report.items[0]
        assert item.suggested_difficulty == DifficultyTier.EASY
        assert item.assigned_difficulty == DifficultyTier.MEDIUM  # default
        assert item.is_mislabeled is True
        assert report.mislabel_count == 1

    def test_empty_results(self) -> None:
        report = calibrate_difficulty([])
        assert report.total_cases == 0
        assert report.mislabel_rate == 0.0

    def test_models_used_tracked(self) -> None:
        results = [
            _make_result(case_id="c1", model="sonnet"),
            _make_result(case_id="c1", model="haiku"),
        ]
        report = calibrate_difficulty(results)
        assert "haiku" in report.models_used
        assert "sonnet" in report.models_used

    def test_multiple_attempts_averaged(self) -> None:
        results = [
            _make_result(case_id="c1", model="m1", passed=True),
            _make_result(case_id="c1", model="m1", passed=False),
        ]
        report = calibrate_difficulty(results)
        assert report.items[0].empirical_pass_rate == 0.5
