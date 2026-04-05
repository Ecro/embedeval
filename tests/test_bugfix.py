"""Tests for the bug fix evaluation scenario."""

import importlib.util
import re
from pathlib import Path
from unittest.mock import MagicMock, patch


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text (e.g. color codes added by rich/typer in CI)."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)

from typer.testing import CliRunner

from embedeval.bugfix import (
    BugfixCase,
    discover_bugfix_cases,
    generate_bugfix_prompt,
    run_bugfix_benchmark,
)
from embedeval.cli import app
from embedeval.models import (
    CaseCategory,
    CaseMetadata,
    CheckDetail,
    DifficultyTier,
    EvalPlatform,
    EvalResult,
    LLMResponse,
    TokenUsage,
)

CASES_DIR = Path(__file__).parent.parent / "cases"

cli_runner = CliRunner()


class TestDiscoverBugfixCases:
    """Tests for discover_bugfix_cases()."""

    def test_discovers_cases_from_real_directory(self) -> None:
        """Discover bugfix cases from the real cases/ directory."""
        cases = discover_bugfix_cases(CASES_DIR, include_private=True)
        assert len(cases) > 0, "Should find at least one bugfix case"
        for bc in cases:
            assert isinstance(bc, BugfixCase)
            assert bc.case_id
            assert bc.mutation_name
            assert bc.buggy_code
            assert bc.description

    def test_only_must_fail_mutations(self) -> None:
        """Only mutations with 'must_fail' key are included."""
        cases = discover_bugfix_cases(CASES_DIR, include_private=True)
        for bc in cases:
            negatives_path = bc.case_dir / "checks" / "negatives.py"
            spec = importlib.util.spec_from_file_location("neg", negatives_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            neg = next(n for n in mod.NEGATIVES if n.get("name") == bc.mutation_name)
            assert "must_fail" in neg, f"{bc.bugfix_id} has no 'must_fail' key"

    def test_bugfix_id_format(self) -> None:
        """bugfix_id is case_id:mutation_name."""
        cases = discover_bugfix_cases(CASES_DIR, include_private=True)
        for bc in cases:
            assert ":" in bc.bugfix_id
            parts = bc.bugfix_id.split(":", 1)
            assert parts[0] == bc.case_id
            assert parts[1] == bc.mutation_name

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Empty cases directory returns no bugfix cases."""
        cases = discover_bugfix_cases(tmp_path)
        assert cases == []

    def test_no_negatives_file(self, tmp_path: Path) -> None:
        """Case without negatives.py is skipped."""
        case_dir = tmp_path / "test-case-001"
        case_dir.mkdir()
        (case_dir / "metadata.yaml").write_text(
            "id: test-case-001\n"
            "category: gpio-basic\n"
            "difficulty: easy\n"
            'title: "Test"\n'
            'description: "Test case"\n'
            "tags: [test]\n"
            "platform: native_sim\n"
            "estimated_tokens: 100\n"
            'sdk_version: "4.1.0"\n'
        )
        ref_dir = case_dir / "reference"
        ref_dir.mkdir()
        (ref_dir / "main.c").write_text("#include <stdio.h>\n")

        cases = discover_bugfix_cases(tmp_path, include_private=True)
        assert cases == []

    def test_buggy_code_differs_from_reference(self) -> None:
        """Buggy code must differ from the reference solution."""
        cases = discover_bugfix_cases(CASES_DIR, include_private=True)
        for bc in cases:
            ref_path = bc.case_dir / "reference" / "main.c"
            ref_code = ref_path.read_text(encoding="utf-8")
            assert bc.buggy_code != ref_code, (
                f"Buggy code for {bc.bugfix_id} is identical"
            )


class TestGenerateBugfixPrompt:
    """Tests for generate_bugfix_prompt()."""

    def test_prompt_contains_required_fields(self) -> None:
        """Prompt contains platform, category, code, description."""
        meta = CaseMetadata(
            id="gpio-basic-001",
            category=CaseCategory.GPIO_BASIC,
            difficulty=DifficultyTier.EASY,
            title="GPIO Button Interrupt",
            description="Test case",
            tags=["test"],
            platform=EvalPlatform.NATIVE_SIM,
            estimated_tokens=300,
            sdk_version="4.1.0",
        )
        bc = BugfixCase(
            case_id="gpio-basic-001",
            mutation_name="test_mutation",
            buggy_code="#include <broken.h>\nint main() {}",
            description="Missing device ready check",
            case_dir=Path("/tmp/fake"),
            metadata=meta,
        )
        prompt = generate_bugfix_prompt(bc)

        assert "native_sim" in prompt
        assert "gpio-basic" in prompt
        assert "GPIO Button Interrupt" in prompt
        assert "#include <broken.h>" in prompt
        assert "Missing device ready check" in prompt
        assert "Find and fix the bug" in prompt

    def test_prompt_format_structure(self) -> None:
        """Prompt follows the template structure."""
        meta = CaseMetadata(
            id="isr-001",
            category=CaseCategory.ISR_CONCURRENCY,
            difficulty=DifficultyTier.MEDIUM,
            title="ISR Spinlock",
            description="ISR test",
            tags=["isr"],
            platform=EvalPlatform.NATIVE_SIM,
            estimated_tokens=400,
            sdk_version="4.1.0",
        )
        bc = BugfixCase(
            case_id="isr-001",
            mutation_name="mutex_swap",
            buggy_code="void isr() {}",
            description="Wrong lock type",
            case_dir=Path("/tmp/fake"),
            metadata=meta,
        )
        prompt = generate_bugfix_prompt(bc)

        assert "## Buggy Code" in prompt
        assert "## Bug Hint" in prompt
        assert "## Task" in prompt
        assert "```c" in prompt


class TestMutationValidity:
    """Verify that mutations actually make code fail checks."""

    def test_buggy_code_fails_behavior_checks(self) -> None:
        """Buggy code from must_fail mutations fails checks."""
        cases = discover_bugfix_cases(CASES_DIR, include_private=True)
        assert len(cases) > 0

        for bc in cases:
            behavior_path = bc.case_dir / "checks" / "behavior.py"
            static_path = bc.case_dir / "checks" / "static.py"

            all_details: list[CheckDetail] = []
            for check_path in (static_path, behavior_path):
                if not check_path.is_file():
                    continue
                mod_key = f"{bc.case_id}.{check_path.stem}"
                spec = importlib.util.spec_from_file_location(mod_key, check_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                all_details.extend(mod.run_checks(bc.buggy_code))

            negatives_path = bc.case_dir / "checks" / "negatives.py"
            spec = importlib.util.spec_from_file_location("neg", negatives_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            neg = next(n for n in mod.NEGATIVES if n.get("name") == bc.mutation_name)

            for check_name in neg["must_fail"]:
                matching = [d for d in all_details if d.check_name == check_name]
                assert matching, f"Check '{check_name}' not found for {bc.bugfix_id}"
                assert all(not d.passed for d in matching), (
                    f"Check '{check_name}' should FAIL on {bc.bugfix_id} but passed"
                )

    def test_reference_code_passes_behavior_checks(self) -> None:
        """Reference code passes all behavior checks."""
        cases = discover_bugfix_cases(CASES_DIR, include_private=True)
        seen_case_dirs: set[Path] = set()

        for bc in cases:
            if bc.case_dir in seen_case_dirs:
                continue
            seen_case_dirs.add(bc.case_dir)

            ref_path = bc.case_dir / "reference" / "main.c"
            ref_code = ref_path.read_text(encoding="utf-8")
            behavior_path = bc.case_dir / "checks" / "behavior.py"
            if not behavior_path.is_file():
                continue

            spec = importlib.util.spec_from_file_location(
                f"{bc.case_id}.behavior", behavior_path
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            details = mod.run_checks(ref_code)

            for d in details:
                assert d.passed, (
                    f"Reference code for {bc.case_id} fails check '{d.check_name}'"
                )


class TestRunBugfixBenchmark:
    """Tests for run_bugfix_benchmark() with mock LLM."""

    @patch("embedeval.bugfix.call_model")
    def test_mock_pipeline_e2e(self, mock_call: MagicMock) -> None:
        """Full bugfix pipeline with mock LLM."""
        ref_path = CASES_DIR / "gpio-basic-001" / "reference" / "main.c"
        ref_code = ref_path.read_text(encoding="utf-8")
        mock_call.return_value = LLMResponse(
            model="mock",
            generated_code=ref_code,
            token_usage=TokenUsage(
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
            ),
            cost_usd=0.0,
            duration_seconds=0.1,
        )

        from embedeval.runner import Filters

        filters = Filters(categories=[CaseCategory.GPIO_BASIC])
        results = run_bugfix_benchmark(
            cases_dir=CASES_DIR,
            model="mock",
            filters=filters,
            include_private=True,
        )

        assert len(results) > 0
        for r in results:
            assert isinstance(r, EvalResult)
            assert ":" in r.case_id

    @patch("embedeval.bugfix.call_model")
    def test_no_cases_returns_empty(self, mock_call: MagicMock, tmp_path: Path) -> None:
        """Empty cases directory returns empty results."""
        results = run_bugfix_benchmark(
            cases_dir=tmp_path,
            model="mock",
            include_private=True,
        )
        assert results == []
        mock_call.assert_not_called()


class TestCLIScenario:
    """Tests for --scenario CLI option."""

    def test_run_help_shows_scenario(self) -> None:
        result = cli_runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "--scenario" in strip_ansi(result.output)

    def test_invalid_scenario_fails(self) -> None:
        result = cli_runner.invoke(app, ["run", "--scenario", "unknown"])
        assert result.exit_code == 1
        assert "Unknown scenario" in result.output
