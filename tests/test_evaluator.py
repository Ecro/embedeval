"""Tests for EmbedEval evaluator."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from embedeval.evaluator import (
    _get_build_mode,
    _is_l1_skipped,
    _is_l2_skipped,
    _load_negatives,
    _prepare_build_dir,
    _run_mutant_checks,
    evaluate,
)
from embedeval.models import TokenUsage


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

    @patch("embedeval.evaluator._get_build_mode", return_value="local")
    @patch("embedeval.evaluator.subprocess")
    def test_compile_timeout(
        self,
        mock_subprocess: object,
        _mock_mode: object,
        empty_case_dir: Path,
    ) -> None:
        import subprocess as sp

        # Add CMakeLists.txt so the compile gate doesn't skip
        (empty_case_dir / "CMakeLists.txt").write_text(
            "cmake_minimum_required(VERSION 3.20)"
        )

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

    @patch("embedeval.evaluator._build_env_available", return_value=True)
    def test_compile_skip_no_cmakelists(
        self, _mock_build: object, empty_case_dir: Path
    ) -> None:
        """Non-compilable cases (no CMakeLists.txt) skip L1."""
        result = evaluate(
            case_dir=empty_case_dir,
            generated_code="test",
        )
        assert result.layers[1].passed is True
        assert "not a compilable case" in result.layers[1].details[0].actual


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


class TestGetBuildMode:
    """Tests for build mode detection."""

    def test_docker_mode(self) -> None:
        with patch.dict("os.environ", {"EMBEDEVAL_ENABLE_BUILD": "docker"}):
            assert _get_build_mode() == "docker"

    def test_local_mode_1(self) -> None:
        with patch.dict("os.environ", {"EMBEDEVAL_ENABLE_BUILD": "1"}):
            assert _get_build_mode() == "local"

    def test_local_mode_explicit(self) -> None:
        with patch.dict("os.environ", {"EMBEDEVAL_ENABLE_BUILD": "local"}):
            assert _get_build_mode() == "local"

    def test_skip_when_unset(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            assert _get_build_mode() == "skip"

    def test_skip_when_empty(self) -> None:
        with patch.dict("os.environ", {"EMBEDEVAL_ENABLE_BUILD": ""}):
            assert _get_build_mode() == "skip"

    def test_docker_case_insensitive(self) -> None:
        with patch.dict("os.environ", {"EMBEDEVAL_ENABLE_BUILD": "DOCKER"}):
            assert _get_build_mode() == "docker"


class TestPrepareBuildDir:
    """Tests for tmpdir-isolated build directory preparation."""

    def test_creates_src_main_c(self, tmp_path: Path) -> None:
        case_dir = tmp_path / "test-case"
        case_dir.mkdir()
        (case_dir / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.20)")
        (case_dir / "prj.conf").write_text("CONFIG_GPIO=y")

        build_dir = _prepare_build_dir(case_dir, "int main() { return 0; }")
        try:
            assert (build_dir / "src" / "main.c").is_file()
            assert (
                build_dir / "src" / "main.c"
            ).read_text() == "int main() { return 0; }"
            assert (build_dir / "CMakeLists.txt").is_file()
            assert (build_dir / "prj.conf").is_file()
        finally:
            import shutil

            shutil.rmtree(build_dir)

    def test_does_not_mutate_case_dir(self, tmp_path: Path) -> None:
        case_dir = tmp_path / "test-case"
        case_dir.mkdir()
        src_dir = case_dir / "src"
        src_dir.mkdir()
        original_code = "// original code"
        (src_dir / "main.c").write_text(original_code)
        (case_dir / "CMakeLists.txt").write_text("cmake")

        build_dir = _prepare_build_dir(case_dir, "// generated code")
        try:
            assert (src_dir / "main.c").read_text() == original_code
            assert (build_dir / "src" / "main.c").read_text() == "// generated code"
        finally:
            import shutil

            shutil.rmtree(build_dir)

    def test_copies_overlay_files(self, tmp_path: Path) -> None:
        case_dir = tmp_path / "test-case"
        case_dir.mkdir()
        (case_dir / "app.overlay").write_text("/ { };")
        (case_dir / "CMakeLists.txt").write_text("cmake")

        build_dir = _prepare_build_dir(case_dir, "code")
        try:
            assert (build_dir / "app.overlay").is_file()
        finally:
            import shutil

            shutil.rmtree(build_dir)

    def test_handles_missing_cmake(self, tmp_path: Path) -> None:
        case_dir = tmp_path / "test-case"
        case_dir.mkdir()

        build_dir = _prepare_build_dir(case_dir, "code")
        try:
            assert (build_dir / "src" / "main.c").is_file()
            assert not (build_dir / "CMakeLists.txt").exists()
        finally:
            import shutil

            shutil.rmtree(build_dir)


class TestDockerCompileMode:
    """Tests for Docker-based compilation."""

    @patch("embedeval.evaluator._get_build_mode", return_value="docker")
    @patch("embedeval.evaluator.subprocess")
    def test_docker_compile_success(
        self, mock_subprocess: MagicMock, _mock_mode: object, tmp_path: Path
    ) -> None:
        import subprocess as sp

        mock_subprocess.TimeoutExpired = sp.TimeoutExpired
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_result.stdout = ""
        mock_subprocess.run.return_value = mock_result

        case_dir = tmp_path / "case-001"
        case_dir.mkdir()
        (case_dir / "CMakeLists.txt").write_text("cmake")
        (case_dir / "prj.conf").write_text("CONFIG_GPIO=y")

        result = evaluate(case_dir=case_dir, generated_code="int main() {}")
        assert result.layers[1].passed is True
        assert result.layers[1].details[0].check_name == "west_build_docker"

    @patch("embedeval.evaluator._get_build_mode", return_value="docker")
    @patch("embedeval.evaluator.subprocess")
    def test_docker_compile_failure(
        self, mock_subprocess: MagicMock, _mock_mode: object, tmp_path: Path
    ) -> None:
        import subprocess as sp

        mock_subprocess.TimeoutExpired = sp.TimeoutExpired
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "error: undefined reference to 'foo'"
        mock_result.stdout = ""
        mock_subprocess.run.return_value = mock_result

        case_dir = tmp_path / "case-001"
        case_dir.mkdir()
        (case_dir / "CMakeLists.txt").write_text("cmake")

        result = evaluate(case_dir=case_dir, generated_code="int main() {}")
        assert result.layers[1].passed is False
        assert result.failed_at_layer == 1
        assert "undefined reference" in result.layers[1].error

    @patch("embedeval.evaluator._get_build_mode", return_value="docker")
    @patch("embedeval.evaluator.subprocess")
    def test_docker_compile_timeout(
        self, mock_subprocess: MagicMock, _mock_mode: object, tmp_path: Path
    ) -> None:
        import subprocess as sp

        mock_subprocess.TimeoutExpired = sp.TimeoutExpired
        mock_subprocess.run.side_effect = sp.TimeoutExpired(
            cmd="docker run", timeout=300.0
        )

        case_dir = tmp_path / "case-001"
        case_dir.mkdir()
        (case_dir / "CMakeLists.txt").write_text("cmake")

        result = evaluate(
            case_dir=case_dir, generated_code="int main() {}", timeout=300.0
        )
        assert result.layers[1].passed is False
        assert "timed out" in result.layers[1].error


def _make_case_with_negatives(tmp_path: Path, negatives_code: str) -> Path:
    """Create a case directory with static + behavior checks and negatives."""
    case_dir = tmp_path / "case-neg"
    checks_dir = case_dir / "checks"
    checks_dir.mkdir(parents=True)

    # Static check: requires "#include" to be present
    (checks_dir / "static.py").write_text(
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

    # Behavior check: requires "main" to be present
    (checks_dir / "behavior.py").write_text(
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

    (checks_dir / "negatives.py").write_text(negatives_code, encoding="utf-8")
    return case_dir


class TestMutantChecks:
    """Tests for Layer 4: Mutation meta-verification."""

    def test_no_negatives_file_auto_passes(self, tmp_path: Path) -> None:
        case_dir = tmp_path / "case-empty"
        case_dir.mkdir()
        result = _run_mutant_checks(case_dir, "any code")
        assert result.passed is True
        assert result.details == []

    def test_load_negatives_returns_list(self, tmp_path: Path) -> None:
        case_dir = tmp_path / "case-neg"
        checks_dir = case_dir / "checks"
        checks_dir.mkdir(parents=True)
        neg_code = (
            "NEGATIVES = [{'name': 'test',"
            " 'mutation': lambda c: c, 'must_fail': ['x']}]"
        )
        (checks_dir / "negatives.py").write_text(
            neg_code,
            encoding="utf-8",
        )
        result = _load_negatives(case_dir)
        assert result is not None
        assert len(result) == 1

    def test_load_negatives_missing_file(self, tmp_path: Path) -> None:
        case_dir = tmp_path / "case-empty"
        case_dir.mkdir()
        assert _load_negatives(case_dir) is None

    def test_mutation_caught_by_checks(self, tmp_path: Path) -> None:
        """Mutation removes #include -> has_include check catches it."""
        negatives_code = """\
NEGATIVES = [
    {
        "name": "remove_include",
        "mutation": lambda code: code.replace("#include", "// removed"),
        "must_fail": ["has_include"],
    },
]
"""
        case_dir = _make_case_with_negatives(tmp_path, negatives_code)
        code = "#include <zephyr/kernel.h>\nvoid main(void) {}"
        result = _run_mutant_checks(case_dir, code)
        assert result.passed is True
        assert len(result.details) == 1
        assert result.details[0].check_name == "mutation_remove_include"
        assert result.details[0].passed is True
        assert result.details[0].actual == "caught"

    def test_mutation_missed_by_checks(self, tmp_path: Path) -> None:
        """Mutation changes something, but targeted check still passes."""
        negatives_code = """\
NEGATIVES = [
    {
        "name": "sneaky_change",
        "mutation": lambda code: code.replace("void", "int"),
        "must_fail": ["has_include"],
    },
]
"""
        case_dir = _make_case_with_negatives(tmp_path, negatives_code)
        code = "#include <zephyr/kernel.h>\nvoid main(void) {}"
        result = _run_mutant_checks(case_dir, code)
        assert result.passed is False
        assert result.details[0].passed is False
        assert "missed" in result.details[0].actual

    def test_mutation_unchanged_code_skipped(self, tmp_path: Path) -> None:
        """Mutation that doesn't change code is skipped (not failed)."""
        negatives_code = """\
NEGATIVES = [
    {
        "name": "noop_mutation",
        "mutation": lambda code: code.replace("NONEXISTENT", "X"),
        "must_fail": ["has_include"],
    },
]
"""
        case_dir = _make_case_with_negatives(tmp_path, negatives_code)
        code = "#include <zephyr/kernel.h>\nvoid main(void) {}"
        result = _run_mutant_checks(case_dir, code)
        assert result.passed is True
        assert "skipped" in result.details[0].actual

    def test_should_fail_mutations_ignored(self, tmp_path: Path) -> None:
        """Only must_fail mutations are processed, should_fail is skipped."""
        negatives_code = """\
NEGATIVES = [
    {
        "name": "subtle_only",
        "mutation": lambda code: code.replace("#include", "// gone"),
        "should_fail": ["has_include"],
    },
]
"""
        case_dir = _make_case_with_negatives(tmp_path, negatives_code)
        code = "#include <zephyr/kernel.h>\nvoid main(void) {}"
        result = _run_mutant_checks(case_dir, code)
        assert result.passed is True
        assert result.details == []

    def test_mutation_error_skipped_gracefully(self, tmp_path: Path) -> None:
        """If mutation function raises, the mutation is skipped."""
        negatives_code = """\
def _bad_mutation(code):
    raise ValueError("broken mutation")

NEGATIVES = [
    {
        "name": "broken",
        "mutation": _bad_mutation,
        "must_fail": ["has_include"],
    },
]
"""
        case_dir = _make_case_with_negatives(tmp_path, negatives_code)
        result = _run_mutant_checks(case_dir, "any code")
        assert result.passed is True
        assert "skipped" in result.details[0].actual

    @patch("embedeval.evaluator._build_env_available", return_value=False)
    def test_l4_failure_does_not_affect_case_pass(
        self, _mock: object, tmp_path: Path
    ) -> None:
        """L4 failure is meta-verification only — case should still pass."""
        negatives_code = """\
NEGATIVES = [
    {
        "name": "sneaky_change",
        "mutation": lambda code: code.replace("void", "int"),
        "must_fail": ["has_include"],
    },
]
"""
        case_dir = _make_case_with_negatives(tmp_path, negatives_code)
        code = "#include <zephyr/kernel.h>\nvoid main(void) {}"
        result = evaluate(case_dir=case_dir, generated_code=code)
        # L0, L1(skip), L2(skip), L3 all pass
        assert result.layers[0].passed is True
        assert result.layers[3].passed is True
        # L4 fails (mutation not caught)
        assert result.layers[4].passed is False
        # But overall case still passes
        assert result.passed is True
        assert result.failed_at_layer is None
        # L4 failure must not reduce total_score
        assert result.total_score == 1.0


class TestL1SkipFlag:
    """Tests for _is_l1_skipped() metadata parsing."""

    def test_l1_skip_with_inline_comment(self, tmp_path: Path):
        meta = tmp_path / "metadata.yaml"
        meta.write_text("l1_skip: true  # reference fails L1: DT node missing\n")
        assert _is_l1_skipped(tmp_path) is True

    def test_l1_skip_without_comment(self, tmp_path: Path):
        meta = tmp_path / "metadata.yaml"
        meta.write_text("l1_skip: true\n")
        assert _is_l1_skipped(tmp_path) is True

    def test_l1_skip_false_value(self, tmp_path: Path):
        meta = tmp_path / "metadata.yaml"
        meta.write_text("l1_skip: false\n")
        assert _is_l1_skipped(tmp_path) is False

    def test_l1_skip_not_present(self, tmp_path: Path):
        meta = tmp_path / "metadata.yaml"
        meta.write_text("category: gpio-basic\nbuild_board: native_sim\n")
        assert _is_l1_skipped(tmp_path) is False

    def test_l1_skip_no_metadata_file(self, tmp_path: Path):
        assert _is_l1_skipped(tmp_path) is False

    def test_l1_skip_yes_value(self, tmp_path: Path):
        meta = tmp_path / "metadata.yaml"
        meta.write_text("l1_skip: yes\n")
        assert _is_l1_skipped(tmp_path) is True


class TestL2SkipFlag:
    """Tests for _is_l2_skipped() metadata parsing."""

    def test_l2_skip_with_inline_comment(self, tmp_path: Path):
        meta = tmp_path / "metadata.yaml"
        meta.write_text("l2_skip: true  # BLE: no BT controller on native_sim\n")
        assert _is_l2_skipped(tmp_path) is True

    def test_l2_skip_without_comment(self, tmp_path: Path):
        meta = tmp_path / "metadata.yaml"
        meta.write_text("l2_skip: true\n")
        assert _is_l2_skipped(tmp_path) is True

    def test_l2_skip_not_present(self, tmp_path: Path):
        meta = tmp_path / "metadata.yaml"
        meta.write_text("category: dma\n")
        assert _is_l2_skipped(tmp_path) is False
