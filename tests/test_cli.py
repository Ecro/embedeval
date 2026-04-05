"""Tests for EmbedEval CLI."""

import re

from typer.testing import CliRunner

from embedeval import __version__
from embedeval.cli import app

runner = CliRunner()


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text (e.g. color codes added by rich/typer in CI)."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_version() -> None:
    assert __version__ == "0.1.0"


class TestMainCommand:
    """Tests for the main CLI entry point."""

    def test_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "EmbedEval" in result.output

    def test_no_args_shows_version(self) -> None:
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "v0.1.0" in result.output


class TestRunCommand:
    """Tests for the run subcommand."""

    def test_run_help(self) -> None:
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "--model" in output
        assert "--cases" in output
        assert "--category" in output
        assert "--difficulty" in output
        assert "--output-dir" in output
        assert "--verbose" in output


class TestValidateCommand:
    """Tests for the validate subcommand."""

    def test_validate_help(self) -> None:
        result = runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "--cases" in output
        assert "--category" in output


class TestReportCommand:
    """Tests for the report subcommand."""

    def test_report_help(self) -> None:
        result = runner.invoke(app, ["report", "--help"])
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "--results" in output
        assert "--output" in output


class TestListCommand:
    """Tests for the list subcommand."""

    def test_list_help(self) -> None:
        result = runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        output = strip_ansi(result.output)
        assert "--cases" in output
        assert "--category" in output
        assert "--difficulty" in output
