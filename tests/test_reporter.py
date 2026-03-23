"""Tests for EmbedEval reporter."""

import json
from pathlib import Path

from embedeval.models import (
    BenchmarkReport,
    CaseCategory,
    CategoryScore,
    ModelScore,
    OverallScore,
)
from embedeval.reporter import generate_json, generate_leaderboard


def _make_report() -> BenchmarkReport:
    """Create a sample benchmark report."""
    return BenchmarkReport(
        version="0.1.0",
        date="2026-03-23",
        models=[
            ModelScore(
                model="gpt-4",
                pass_at_1=0.8,
                pass_at_5=0.95,
                total_cases=10,
                passed_cases=8,
                layer_pass_rates={
                    "static_analysis": 1.0,
                    "compile_gate": 0.9,
                    "runtime_execution": 0.85,
                    "behavioral_assertion": 0.8,
                    "test_quality_proof": 0.8,
                },
            ),
            ModelScore(
                model="claude-3",
                pass_at_1=0.7,
                pass_at_5=0.9,
                total_cases=10,
                passed_cases=7,
                layer_pass_rates={
                    "static_analysis": 0.95,
                    "compile_gate": 0.85,
                    "runtime_execution": 0.8,
                    "behavioral_assertion": 0.7,
                    "test_quality_proof": 0.7,
                },
            ),
        ],
        categories=[
            CategoryScore(
                category=CaseCategory.KCONFIG,
                pass_at_1=0.9,
                total_cases=5,
                passed_cases=4,
            ),
            CategoryScore(
                category=CaseCategory.BLE,
                pass_at_1=0.4,
                total_cases=5,
                passed_cases=2,
            ),
        ],
        overall=OverallScore(
            total_cases=10,
            total_models=2,
            best_model="gpt-4",
            best_pass_at_1=0.8,
        ),
    )


class TestGenerateJson:
    """Tests for JSON report generation."""

    def test_creates_valid_json(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "results" / "report.json"
        generate_json(report, output)

        assert output.exists()
        data = json.loads(output.read_text(encoding="utf-8"))
        assert data["version"] == "0.1.0"

    def test_json_contains_models(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "report.json"
        generate_json(report, output)

        data = json.loads(output.read_text(encoding="utf-8"))
        assert len(data["models"]) == 2
        assert data["models"][0]["model"] == "gpt-4"

    def test_json_contains_categories(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "report.json"
        generate_json(report, output)

        data = json.loads(output.read_text(encoding="utf-8"))
        assert len(data["categories"]) == 2

    def test_json_contains_overall(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "report.json"
        generate_json(report, output)

        data = json.loads(output.read_text(encoding="utf-8"))
        assert data["overall"]["best_model"] == "gpt-4"

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "deep" / "nested" / "report.json"
        generate_json(report, output)
        assert output.exists()


class TestGenerateLeaderboard:
    """Tests for Markdown leaderboard generation."""

    def test_creates_markdown_file(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report], output)
        assert output.exists()

    def test_contains_header(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report], output)

        content = output.read_text(encoding="utf-8")
        assert "# EmbedEval Leaderboard" in content

    def test_contains_model_table(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report], output)

        content = output.read_text(encoding="utf-8")
        assert "## Model Comparison" in content
        assert "| Model |" in content
        assert "gpt-4" in content
        assert "claude-3" in content

    def test_contains_category_heatmap(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report], output)

        content = output.read_text(encoding="utf-8")
        assert "## Category Results" in content
        assert "zephyr-kconfig" in content
        assert "PASS" in content
        assert "FAIL" in content

    def test_pass_fail_icons(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report], output)

        content = output.read_text(encoding="utf-8")
        assert "PASS" in content
        assert "FAIL" in content

    def test_multiple_reports(self, tmp_path: Path) -> None:
        report1 = _make_report()
        report2 = _make_report()
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report1, report2], output)

        content = output.read_text(encoding="utf-8")
        assert content.count("gpt-4") == 2

    def test_empty_reports(self, tmp_path: Path) -> None:
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([], output)

        content = output.read_text(encoding="utf-8")
        assert "# EmbedEval Leaderboard" in content
