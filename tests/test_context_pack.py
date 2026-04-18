"""Tests for Context Quality Mode (context pack injection + tracker hash)."""

from pathlib import Path

import pytest

from embedeval.context_pack import (
    EXPERT_KEYWORD,
    MAX_PACK_CHARS,
    ContextPackTooLargeError,
    bundled_expert_pack_path,
    hash_context_pack,
    resolve_context_pack,
)
from embedeval.llm_client import _build_full_prompt, call_model


class TestBuildFullPrompt:
    """Verifies that context_pack actually reaches the prompt the LLM sees.

    This is the core invariant of Context Quality Mode — if the pack
    doesn't make it into the prompt, every metric we compute is meaningless.
    """

    def test_context_pack_prepended(self) -> None:
        full = _build_full_prompt(
            prompt="Write a function",
            context_files=None,
            context_pack="ALWAYS USE VOLATILE",
        )
        # Pack must come BEFORE the user prompt so it frames the task
        pack_idx = full.index("ALWAYS USE VOLATILE")
        prompt_idx = full.index("Write a function")
        assert pack_idx < prompt_idx
        assert "## Team Context" in full

    def test_no_pack_no_team_context_header(self) -> None:
        """When no pack is provided, prompt MUST be unchanged from baseline."""
        full = _build_full_prompt(
            prompt="Write a function",
            context_files=None,
            context_pack=None,
        )
        assert full == "Write a function"
        assert "Team Context" not in full

    def test_empty_pack_treated_as_none(self) -> None:
        """Whitespace-only pack should not introduce a Team Context header."""
        full = _build_full_prompt(
            prompt="Write a function",
            context_files=None,
            context_pack="   \n\n  ",
        )
        assert "Team Context" not in full

    def test_pack_and_per_case_context_coexist(self, tmp_path: Path) -> None:
        """Pack (run-wide) and context_files (per-case) are independent channels."""
        ctx_file = tmp_path / "ref.h"
        ctx_file.write_text("#define PER_CASE_REF 1\n")
        full = _build_full_prompt(
            prompt="Use the reference",
            context_files=[str(ctx_file)],
            context_pack="TEAM_RULE_X",
        )
        # Both must be present, pack first
        assert "TEAM_RULE_X" in full
        assert "PER_CASE_REF" in full
        assert full.index("TEAM_RULE_X") < full.index("PER_CASE_REF")
        assert full.index("PER_CASE_REF") < full.index("Use the reference")


class TestMockSeesPrompt:
    """The mock model echoes the prompt prefix back. Use it as a smoke
    test that context_pack reaches the model layer end-to-end."""

    def test_mock_echoes_context_pack(self) -> None:
        response = call_model(
            model="mock",
            prompt="task body",
            context_pack="MARKER_TEAM_CONTEXT_42",
        )
        assert "MARKER_TEAM_CONTEXT_42" in response.generated_code

    def test_mock_without_pack_has_no_marker(self) -> None:
        response = call_model(model="mock", prompt="task body")
        assert "Team Context" not in response.generated_code


class TestHashContextPack:
    def test_same_content_same_hash(self) -> None:
        a = hash_context_pack("hello world")
        b = hash_context_pack("hello world")
        assert a == b
        assert len(a) == 16

    def test_different_content_different_hash(self) -> None:
        a = hash_context_pack("hello world")
        b = hash_context_pack("hello world!")
        assert a != b

    def test_whitespace_change_changes_hash(self) -> None:
        """Intentional: a whitespace edit IS a different pack to the LLM."""
        a = hash_context_pack("rule x")
        b = hash_context_pack("rule x ")
        assert a != b

    def test_oversized_pack_raises(self) -> None:
        with pytest.raises(ContextPackTooLargeError):
            hash_context_pack("x" * (MAX_PACK_CHARS + 1))


class TestResolveContextPack:
    def test_expert_keyword_resolves_to_bundled(self) -> None:
        path = resolve_context_pack(EXPERT_KEYWORD)
        # Bundled file must exist after Phase 3 ships it
        assert path == bundled_expert_pack_path()

    def test_existing_path_returns_path(self, tmp_path: Path) -> None:
        f = tmp_path / "team.md"
        f.write_text("rules\n")
        assert resolve_context_pack(str(f)) == f

    def test_missing_file_raises(self) -> None:
        with pytest.raises(FileNotFoundError, match="not found"):
            resolve_context_pack("/no/such/file.md")


class TestCliRejection:
    """F2/F3 regression: CLI must reject invalid context_pack inputs early
    rather than silently corrupting the tracker."""

    def test_bugfix_scenario_rejects_context_pack(self, tmp_path: Path) -> None:
        """F2: --context-pack with --scenario bugfix would silently strip
        the pack while still recording its hash. Must error."""
        from typer.testing import CliRunner

        from embedeval.cli import app

        pack = tmp_path / "pack.md"
        pack.write_text("rule x\n")

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "run",
                "--cases",
                "cases",
                "--model",
                "mock",
                "--scenario",
                "bugfix",
                "--context-pack",
                str(pack),
                "--output-dir",
                str(tmp_path / "out"),
            ],
        )
        assert result.exit_code == 1
        assert "not supported" in (result.stdout + (result.stderr or ""))

    def test_empty_context_pack_file_rejected(self, tmp_path: Path) -> None:
        """F3: empty pack file would hash to a stable non-null value but
        produce no prompt change. Must error before tracker is touched."""
        from typer.testing import CliRunner

        from embedeval.cli import app

        empty = tmp_path / "empty.md"
        empty.write_text("   \n\n  \n")  # whitespace only

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "run",
                "--cases",
                "cases",
                "--model",
                "mock",
                "--context-pack",
                str(empty),
                "--output-dir",
                str(tmp_path / "out"),
            ],
        )
        assert result.exit_code == 1
        assert "empty" in (result.stdout + (result.stderr or "")).lower()
