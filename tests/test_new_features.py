"""Tests for v3 features: after_date filter, feedback loop, agent mode."""

from pathlib import Path

from embedeval.models import CaseCategory, CaseMetadata, DifficultyTier
from embedeval.runner import Filters, filter_cases


# ============================================================
# Feature 2: after_date filter
# ============================================================

class TestAfterDateFilter:
    """Tests for --after-date temporal filtering."""

    def _make_case(self, case_id: str, created_date: str | None = None):
        meta = CaseMetadata(
            id=case_id,
            category=CaseCategory.GPIO_BASIC,
            difficulty=DifficultyTier.EASY,
            title="test",
            description="test",
            tags=[],
            platform="native_sim",
            estimated_tokens=100,
            sdk_version="4.1.0",
            created_date=created_date,
        )
        return (Path(f"/fake/cases/{case_id}"), meta)

    def test_after_date_includes_newer_cases(self):
        """Cases created after the filter date are included."""
        cases = [
            self._make_case("new-001", "2026-03-25"),
            self._make_case("old-001", "2026-01-01"),
        ]
        filters = Filters(after_date="2026-03-01")
        result = filter_cases(cases, filters)
        assert len(result) == 1
        assert result[0][1].id == "new-001"

    def test_after_date_excludes_older_cases(self):
        """Cases created on or before the filter date are excluded."""
        cases = [self._make_case("old-001", "2026-01-15")]
        filters = Filters(after_date="2026-01-15")  # equal = excluded
        result = filter_cases(cases, filters)
        assert len(result) == 0

    def test_after_date_none_created_includes_case(self):
        """Cases without created_date are always included (legacy-safe)."""
        cases = [self._make_case("legacy-001", None)]
        filters = Filters(after_date="2026-03-01")
        result = filter_cases(cases, filters)
        assert len(result) == 1

    def test_after_date_invalid_format_skips_filter(self):
        """Invalid date format doesn't crash — filter is skipped."""
        cases = [self._make_case("case-001", "2026-03-25")]
        filters = Filters(after_date="not-a-date")
        result = filter_cases(cases, filters)
        # Should include the case since filter is skipped on invalid format
        assert len(result) == 1

    def test_after_date_none_includes_all(self):
        """No after_date filter includes all cases."""
        cases = [
            self._make_case("a-001", "2020-01-01"),
            self._make_case("b-001", "2030-01-01"),
        ]
        filters = Filters(after_date=None)
        result = filter_cases(cases, filters)
        assert len(result) == 2


# ============================================================
# Feature 3: Feedback loop (unit test for error detail formatting)
# ============================================================

class TestFeedbackErrorFormatting:
    """Tests for compiler feedback error message construction."""

    def test_l0_failure_includes_check_details(self):
        """L0 static check failures should produce actionable error info."""
        from embedeval.models import CheckDetail, LayerResult

        layer = LayerResult(
            layer=0,
            name="static_analysis",
            passed=False,
            details=[
                CheckDetail(
                    check_name="volatile_present",
                    passed=False,
                    expected="volatile keyword on shared variable",
                    actual="missing",
                    check_type="exact_match",
                ),
                CheckDetail(
                    check_name="header_included",
                    passed=True,
                    expected="zephyr/kernel.h",
                    actual="present",
                    check_type="exact_match",
                ),
            ],
            error=None,
            duration_seconds=0.0,
        )

        # Simulate what runner.py feedback loop does
        error_msg = layer.error or ""
        failed_details = "\n".join(
            f"- {d.check_name}: expected={d.expected}, actual={d.actual}"
            for d in layer.details if not d.passed
        )
        error_info = "\n".join(filter(None, [error_msg, failed_details])) or "Check failed"

        assert "volatile_present" in error_info
        assert "missing" in error_info
        assert "header_included" not in error_info  # passed check not included
        assert error_info != "Check failed"  # should NOT be the generic fallback

    def test_l1_failure_uses_error_field(self):
        """L1 compile failures should use the stderr error field."""
        from embedeval.models import CheckDetail, LayerResult

        layer = LayerResult(
            layer=1,
            name="compile_gate",
            passed=False,
            details=[
                CheckDetail(
                    check_name="west_build",
                    passed=False,
                    expected="exit code 0",
                    actual="exit code 1",
                    check_type="compile",
                ),
            ],
            error="main.c:10: error: 'k_sleep' undeclared",
            duration_seconds=1.5,
        )

        error_msg = layer.error or ""
        failed_details = "\n".join(
            f"- {d.check_name}: expected={d.expected}, actual={d.actual}"
            for d in layer.details if not d.passed
        )
        error_info = "\n".join(filter(None, [error_msg, failed_details])) or "Check failed"

        assert "k_sleep" in error_info
        assert "undeclared" in error_info

    def test_empty_details_falls_back_to_check_failed(self):
        """When both error and details are empty, fallback to 'Check failed'."""
        from embedeval.models import LayerResult

        layer = LayerResult(
            layer=0, name="static_analysis", passed=False,
            details=[], error=None, duration_seconds=0.0,
        )

        error_msg = layer.error or ""
        failed_details = "\n".join(
            f"- {d.check_name}: expected={d.expected}, actual={d.actual}"
            for d in layer.details if not d.passed
        )
        error_info = "\n".join(filter(None, [error_msg, failed_details])) or "Check failed"

        assert error_info == "Check failed"


# ============================================================
# Feature 5: Agent mode
# ============================================================

class TestAgentResult:
    """Tests for AgentResult dataclass."""

    def test_agent_result_creation(self):
        from embedeval.agent import AgentResult

        result = AgentResult(
            case_id="test-001",
            passed=True,
            turns_used=2,
            max_turns=5,
        )
        assert result.passed is True
        assert result.turns_used == 2
        assert result.max_turns == 5
        assert result.history == []

    def test_agent_result_failed(self):
        from embedeval.agent import AgentResult

        result = AgentResult(
            case_id="test-001",
            passed=False,
            turns_used=5,
            max_turns=5,
        )
        assert result.passed is False
        assert result.turns_used == result.max_turns
