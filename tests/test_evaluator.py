"""Tests for EmbedEval evaluator."""

from pathlib import Path
from unittest.mock import patch

import pytest

from embedeval.evaluator import evaluate
from embedeval.models import CheckDetail, TokenUsage


@pytest.fixture()
def empty_case_dir(tmp_path: Path) -> Path:
    """Create a minimal case directory with no checks."""
    case_dir = tmp_path / "case-001"
    case_dir.mkdir()
    return case_dir


@pytest.fixture()
def case_with_static_checks(tmp_path: Path) -> Path:
    """Create a case directory with passing static checks."""
    case_dir = tmp_path / "case-002"
    checks_dir = case_dir / "checks"
    checks_dir.mkdir(parents=True)
    static_py = checks_dir / "static.py"
    static_py.write_text(
        """\
from embedeval.models import CheckDetail

def run_checks(generated_code: str) -> list[CheckDetail]:
    has_include = "#include" in generated_code
    return [
        CheckDetail(
            check_name="has_include",
            passed=has_include,
            expected="#include present",
            actual="found" if has_include else "missing",
            check_type="static",
        )
    ]
""",
        encoding="utf-8",
    )
    return case_dir


@pytest.fixture()
def case_with_failing_static(tmp_path: Path) -> Path:
    """Create a case directory with failing static checks."""
    case_dir = tmp_path / "case-003"
    checks_dir = case_dir / "checks"
    checks_dir.mkdir(parents=True)
    static_py = checks_dir / "static.py"
    static_py.write_text(
        """\
from embedeval.models import CheckDetail

def run_checks(generated_code: str) -> list[CheckDetail]:
    return [
        CheckDetail(
            check_name="always_fail",
            passed=False,
            expected="pass",
            actual="fail",
            check_type="static",
        )
    ]
""",
        encoding="utf-8",
    )
    return case_dir


@pytest.fixture()
def case_with_behavior_checks(tmp_path: Path) -> Path:
    """Create a case directory with behavioral checks."""
    case_dir = tmp_path / "case-004"
    checks_dir = case_dir / "checks"
    checks_dir.mkdir(parents=True)
    behavior_py = checks_dir / "behavior.py"
    behavior_py.write_text(
        """\
from embedeval.models import CheckDetail

def run_checks(generated_code: str) -> list[CheckDetail]:
    has_main = "main" in generated_code
    return [
        CheckDetail(
            check_name="has_main",
            passed=has_main,
            expected="main function",
            actual="found" if has_main else "missing",
            check_type="behavioral",
        )
    ]
""",
        encoding="utf-8",
    )
    return case_dir


@patch("embedeval.evaluator._build_env_available", return_value=False)
class TestEvaluateBasic:
    """Tests for basic evaluation pipeline behavior."""

    def test_empty_case_all_layers_pass(
        self, _mock_docker: object, empty_case_dir: Path
    ) -> None:
        result = evaluate(
            case_dir=empty_case_dir,
            generated_code="#include <zephyr/kernel.h>",
            model="mock",
        )
        assert result.passed is True
        assert result.failed_at_layer is None
        assert len(result.layers) == 5

    def test_case_id_from_directory_name(
        self, _mock_docker: object, empty_case_dir: Path
    ) -> None:
        result = evaluate(
            case_dir=empty_case_dir,
            generated_code="test",
        )
        assert result.case_id == empty_case_dir.name

    def test_model_and_attempt_tracked(
        self, _mock_docker: object, empty_case_dir: Path
    ) -> None:
        result = evaluate(
            case_dir=empty_case_dir,
            generated_code="test",
            model="gpt-4",
            attempt=3,
        )
        assert result.model == "gpt-4"
        assert result.attempt == 3

    def test_duration_recorded(
        self, _mock_docker: object, empty_case_dir: Path
    ) -> None:
        result = evaluate(
            case_dir=empty_case_dir,
            generated_code="test",
        )
        assert result.duration_seconds >= 0.0

    def test_token_usage_default(
        self, _mock_docker: object, empty_case_dir: Path
    ) -> None:
        result = evaluate(
            case_dir=empty_case_dir,
            generated_code="test",
        )
        assert result.token_usage.total_tokens == 0

    def test_token_usage_provided(
        self, _mock_docker: object, empty_case_dir: Path
    ) -> None:
        usage = TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)
        result = evaluate(
            case_dir=empty_case_dir,
            generated_code="test",
            token_usage=usage,
        )
        assert result.token_usage.total_tokens == 150


@patch("embedeval.evaluator._build_env_available", return_value=False)
class TestLayerSkipping:
    """Tests for layer fail -> skip subsequent behavior."""

    def test_static_fail_skips_subsequent_layers(
        self, _mock_docker: object, case_with_failing_static: Path
    ) -> None:
        result = evaluate(
            case_dir=case_with_failing_static,
            generated_code="no include here",
        )
        assert result.passed is False
        assert result.failed_at_layer == 0
        assert result.layers[0].passed is False
        for layer in result.layers[1:]:
            assert layer.passed is False
            assert layer.error is not None
            assert "Skipped" in layer.error


@patch("embedeval.evaluator._build_env_available", return_value=False)
class TestStaticChecks:
    """Tests for Layer 0: Static analysis."""

    def test_passing_static_checks(
        self, _mock_docker: object, case_with_static_checks: Path
    ) -> None:
        result = evaluate(
            case_dir=case_with_static_checks,
            generated_code="#include <zephyr/kernel.h>\nvoid main(void) {}",
        )
        assert result.layers[0].passed is True
        assert len(result.layers[0].details) == 1
        assert result.layers[0].details[0].check_name == "has_include"

    def test_failing_static_checks(
        self, _mock_docker: object, case_with_static_checks: Path
    ) -> None:
        result = evaluate(
            case_dir=case_with_static_checks,
            generated_code="void main(void) {}",
        )
        assert result.layers[0].passed is False


class TestDockerLayers:
    """Tests for Docker-dependent layers (1, 2)."""

    @patch("embedeval.evaluator._build_env_available", return_value=False)
    def test_no_docker_layers_pass(
        self, _mock_docker: object, empty_case_dir: Path
    ) -> None:
        result = evaluate(
            case_dir=empty_case_dir,
            generated_code="test",
        )
        assert result.layers[1].passed is True
        assert result.layers[2].passed is True

    @patch("embedeval.evaluator._build_env_available", return_value=True)
    @patch("embedeval.evaluator.subprocess")
    def test_compile_timeout(
        self,
        mock_subprocess: object,
        _mock_docker: object,
        empty_case_dir: Path,
    ) -> None:
        import subprocess as sp

        # Make subprocess.run raise TimeoutExpired
        mock_subprocess.run.side_effect = sp.TimeoutExpired(  # type: ignore[union-attr]
            cmd="west build", timeout=300.0
        )
        mock_subprocess.TimeoutExpired = sp.TimeoutExpired  # type: ignore[union-attr]

        result = evaluate(
            case_dir=empty_case_dir,
            generated_code="test",
            timeout=300.0,
        )
        assert result.layers[1].passed is False
        assert result.layers[1].error is not None
        assert "timed out" in result.layers[1].error


@patch("embedeval.evaluator._build_env_available", return_value=False)
class TestBehavioralChecks:
    """Tests for Layer 3: Behavioral assertions."""

    def test_passing_behavior_checks(
        self, _mock_docker: object, case_with_behavior_checks: Path
    ) -> None:
        result = evaluate(
            case_dir=case_with_behavior_checks,
            generated_code="void main(void) { }",
        )
        assert result.layers[3].passed is True
        assert len(result.layers[3].details) == 1

    def test_failing_behavior_checks(
        self, _mock_docker: object, case_with_behavior_checks: Path
    ) -> None:
        result = evaluate(
            case_dir=case_with_behavior_checks,
            generated_code="void entry(void) { }",
        )
        assert result.layers[3].passed is False
