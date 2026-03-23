"""Tests for EmbedEval CLI."""

from typer.testing import CliRunner

from embedeval import __version__
from embedeval.cli import app

runner = CliRunner()


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
        assert "--model" in result.output
        assert "--cases" in result.output
        assert "--category" in result.output
        assert "--difficulty" in result.output
        assert "--output-dir" in result.output
        assert "--verbose" in result.output


class TestValidateCommand:
    """Tests for the validate subcommand."""

    def test_validate_help(self) -> None:
        result = runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        assert "--cases" in result.output
        assert "--category" in result.output


class TestReportCommand:
    """Tests for the report subcommand."""

    def test_report_help(self) -> None:
        result = runner.invoke(app, ["report", "--help"])
        assert result.exit_code == 0
        assert "--results" in result.output
        assert "--output" in result.output


class TestListCommand:
    """Tests for the list subcommand."""

    def test_list_help(self) -> None:
        result = runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        assert "--cases" in result.output
        assert "--category" in result.output
        assert "--difficulty" in result.output
