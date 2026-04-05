"""Tests for TC restructure: tier classification, reasoning types, and scoring."""

import re
from pathlib import Path

import yaml
from typer.testing import CliRunner


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text (e.g. color codes added by rich/typer in CI)."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)

from embedeval.cli import app
from embedeval.models import (
    CaseTier,
    CheckDetail,
    EvalResult,
    LayerResult,
    ReasoningType,
    TokenUsage,
)
from embedeval.scorer import score

cli_runner = CliRunner()

CASES_DIR = Path(__file__).parent.parent / "cases"


def _make_result(
    case_id: str = "case-001",
    model: str = "test",
    passed: bool = True,
    tier: CaseTier = CaseTier.CORE,
    reasoning_types: list[ReasoningType] | None = None,
) -> EvalResult:
    layers = [
        LayerResult(layer=i, name=f"layer_{i}", passed=passed,
                    details=[], duration_seconds=0.0)
        for i in range(5)
    ]
    return EvalResult(
        case_id=case_id, model=model, attempt=1, generated_code="",
        layers=layers, passed=passed, duration_seconds=0.1,
        token_usage=TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0),
        cost_usd=0.0, tier=tier,
        reasoning_types=reasoning_types or [],
    )


class TestTierClassification:
    """Tests for tier metadata on real cases."""

    def test_all_cases_have_tier(self) -> None:
        """Every case has a tier field in metadata.yaml."""
        for case_dir in sorted(CASES_DIR.iterdir()):
            meta_file = case_dir / "metadata.yaml"
            if not case_dir.is_dir() or not meta_file.is_file():
                continue
            content = meta_file.read_text()
            assert "tier:" in content, f"{case_dir.name} missing tier field"

    def test_sanity_cases_are_easy(self) -> None:
        """Sanity tier cases should be easy difficulty."""
        for case_dir in sorted(CASES_DIR.iterdir()):
            meta_file = case_dir / "metadata.yaml"
            if not case_dir.is_dir() or not meta_file.is_file():
                continue
            data = yaml.safe_load(meta_file.read_text())
            if data.get("tier") == "sanity":
                assert data["difficulty"] == "easy", (
                    f"{data['id']}: sanity tier but difficulty={data['difficulty']}"
                )

    def test_challenge_cases_are_hard(self) -> None:
        """Challenge tier cases should be hard difficulty."""
        for case_dir in sorted(CASES_DIR.iterdir()):
            meta_file = case_dir / "metadata.yaml"
            if not case_dir.is_dir() or not meta_file.is_file():
                continue
            data = yaml.safe_load(meta_file.read_text())
            if data.get("tier") == "challenge":
                assert data["difficulty"] == "hard", (
                    f"{data['id']}: challenge tier but difficulty={data['difficulty']}"
                )

    def test_tier_distribution(self) -> None:
        """Verify expected tier distribution."""
        from collections import Counter
        counts: Counter[str] = Counter()
        for case_dir in sorted(CASES_DIR.iterdir()):
            meta_file = case_dir / "metadata.yaml"
            if not case_dir.is_dir() or not meta_file.is_file():
                continue
            data = yaml.safe_load(meta_file.read_text())
            counts[data.get("tier", "core")] += 1

        assert counts["sanity"] >= 2, "Should have at least 2 sanity cases"
        assert counts["core"] >= 50, "Should have at least 50 core cases"
        assert counts["challenge"] >= 50, "Should have at least 50 challenge cases"


class TestReasoningTypes:
    """Tests for reasoning type metadata on real cases."""

    def test_all_cases_have_reasoning_types(self) -> None:
        """Every case with behavior.py should have reasoning_types."""
        for case_dir in sorted(CASES_DIR.iterdir()):
            meta_file = case_dir / "metadata.yaml"
            behavior_file = case_dir / "checks" / "behavior.py"
            if not case_dir.is_dir() or not meta_file.is_file():
                continue
            if not behavior_file.is_file():
                continue
            content = meta_file.read_text()
            assert "reasoning_types:" in content, (
                f"{case_dir.name} has behavior.py but no reasoning_types"
            )

    def test_reasoning_types_are_valid(self) -> None:
        """All reasoning_types values are valid enum values."""
        valid = {"api_recall", "rule_application", "cross_domain", "system_reasoning"}
        for case_dir in sorted(CASES_DIR.iterdir()):
            meta_file = case_dir / "metadata.yaml"
            if not case_dir.is_dir() or not meta_file.is_file():
                continue
            data = yaml.safe_load(meta_file.read_text())
            for rt in data.get("reasoning_types", []):
                assert rt in valid, f"{data['id']}: invalid reasoning_type '{rt}'"


class TestTierScoring:
    """Tests for tier-based scoring in scorer.py."""

    def test_tier_scores_calculated(self) -> None:
        results = [
            _make_result("s1", passed=True, tier=CaseTier.SANITY),
            _make_result("c1", passed=True, tier=CaseTier.CORE),
            _make_result("c2", passed=False, tier=CaseTier.CORE),
            _make_result("h1", passed=False, tier=CaseTier.CHALLENGE),
        ]
        report = score(results)
        assert len(report.tier_scores) == 3

        sanity = next(t for t in report.tier_scores if t.tier == "sanity")
        core = next(t for t in report.tier_scores if t.tier == "core")
        challenge = next(t for t in report.tier_scores if t.tier == "challenge")

        assert sanity.pass_at_1 == 1.0
        assert core.pass_at_1 == 0.5
        assert challenge.pass_at_1 == 0.0

    def test_reasoning_scores_calculated(self) -> None:
        results = [
            _make_result("c1", passed=True,
                        reasoning_types=[ReasoningType.API_RECALL]),
            _make_result("c2", passed=True,
                        reasoning_types=[ReasoningType.API_RECALL, ReasoningType.CROSS_DOMAIN]),
            _make_result("c3", passed=False,
                        reasoning_types=[ReasoningType.CROSS_DOMAIN]),
        ]
        report = score(results)

        api = next(r for r in report.reasoning_scores if r.reasoning_type == "api_recall")
        cross = next(r for r in report.reasoning_scores if r.reasoning_type == "cross_domain")

        assert api.pass_at_1 == 1.0  # c1, c2 both pass
        assert api.total_cases == 2
        assert cross.pass_at_1 == 0.5  # c2 passes, c3 fails
        assert cross.total_cases == 2

    def test_no_tier_defaults_to_core(self) -> None:
        results = [_make_result("c1", passed=True, tier=None)]
        report = score(results)
        if report.tier_scores:
            core = next((t for t in report.tier_scores if t.tier == "core"), None)
            assert core is not None

    def test_empty_reasoning_types_no_crash(self) -> None:
        results = [_make_result("c1", passed=True, reasoning_types=[])]
        report = score(results)
        assert report.reasoning_scores == []


class TestCLITierFilter:
    """Tests for --tier CLI option."""

    def test_run_help_shows_tier(self) -> None:
        result = cli_runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "--tier" in strip_ansi(result.output)

    def test_guide_help(self) -> None:
        result = cli_runner.invoke(app, ["guide", "--help"])
        assert result.exit_code == 0
        assert "--results" in strip_ansi(result.output)
