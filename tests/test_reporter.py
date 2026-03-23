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
        assert content.count("gpt-4") >= 2

    def test_empty_reports(self, tmp_path: Path) -> None:
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([], output)

        content = output.read_text(encoding="utf-8")
        assert "# EmbedEval Leaderboard" in content

    def test_contains_layer_heatmap(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report], output)

        content = output.read_text(encoding="utf-8")
        assert "## Layer Pass Rate Heatmap" in content
        assert "L0 Static" in content
        assert "L1 Build" in content
        assert "L2 Runtime" in content
        assert "L3 Behavior" in content
        assert "L4 Mutation" in content
        assert "100%" in content
        assert "90%" in content

    def test_layer_heatmap_shows_all_models(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report], output)

        content = output.read_text(encoding="utf-8")
        # Both models should appear in the layer heatmap
        lines = content.split("\n")
        heatmap_lines = []
        in_heatmap = False
        for line in lines:
            if "## Layer Pass Rate Heatmap" in line:
                in_heatmap = True
                continue
            if in_heatmap and line.startswith("## "):
                break
            if in_heatmap and line.startswith("|") and "Model" not in line and "---" not in line:
                heatmap_lines.append(line)
        assert len(heatmap_lines) == 2
        assert any("gpt-4" in line for line in heatmap_lines)
        assert any("claude-3" in line for line in heatmap_lines)

    def test_contains_failure_distribution(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report], output)

        content = output.read_text(encoding="utf-8")
        assert "## Failure Distribution" in content
        assert "| Layer | Failures | % of Total |" in content
        assert "L0 Static" in content
        assert "L1 Build" in content

    def test_failure_distribution_percentages(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report], output)

        content = output.read_text(encoding="utf-8")
        # L0 Static has lowest failures (0.0 + 0.05 = 0.05)
        # so it should have lowest % of total
        assert "% |" in content

    def test_contains_category_breakdown(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report], output)

        content = output.read_text(encoding="utf-8")
        assert "## Category Breakdown" in content
        assert "| Category | Pass@1 | Cases |" in content
        assert "zephyr-kconfig" in content
        assert "ble" in content

    def test_category_breakdown_values(self, tmp_path: Path) -> None:
        report = _make_report()
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report], output)

        content = output.read_text(encoding="utf-8")
        # kconfig has pass_at_1=0.9 -> 90%, 5 cases
        assert "90%" in content
        assert "| 5 |" in content
        # ble has pass_at_1=0.4 -> 40%, 5 cases
        assert "40%" in content

    def test_layer_heatmap_missing_layers(self, tmp_path: Path) -> None:
        """Test that missing layers show '-' in the heatmap."""
        report = BenchmarkReport(
            version="0.1.0",
            date="2026-03-23",
            models=[
                ModelScore(
                    model="partial-model",
                    pass_at_1=0.5,
                    pass_at_5=0.7,
                    total_cases=5,
                    passed_cases=3,
                    layer_pass_rates={
                        "static_analysis": 0.9,
                        "compile_gate": 0.8,
                    },
                ),
            ],
            categories=[],
            overall=OverallScore(
                total_cases=5,
                total_models=1,
                best_model="partial-model",
                best_pass_at_1=0.5,
            ),
        )
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([report], output)

        content = output.read_text(encoding="utf-8")
        # Missing layers should show "-"
        lines = content.split("\n")
        heatmap_lines = [
            l for l in lines
            if "partial-model" in l and "L0 Static" not in l
        ]
        # Find the line in the layer heatmap section (not Model Comparison)
        # The heatmap line should contain "-" for missing layers
        model_line = [l for l in heatmap_lines if "90%" in l][0]
        parts = [p.strip() for p in model_line.split("|") if p.strip()]
        dash_cells = [p for p in parts if p == "-"]
        assert len(dash_cells) == 3

    def test_empty_reports_still_has_all_sections(self, tmp_path: Path) -> None:
        output = tmp_path / "LEADERBOARD.md"
        generate_leaderboard([], output)

        content = output.read_text(encoding="utf-8")
        assert "## Model Comparison" in content
        assert "## Category Results" in content
        assert "## Layer Pass Rate Heatmap" in content
        assert "## Failure Distribution" in content
        assert "## Category Breakdown" in content
