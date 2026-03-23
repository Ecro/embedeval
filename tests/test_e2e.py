"""End-to-end tests for EmbedEval benchmark with pilot cases."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from embedeval.cli import app
from embedeval.models import BenchmarkReport
from embedeval.reporter import generate_json, generate_leaderboard
from embedeval.runner import run_benchmark
from embedeval.scorer import score

cli_runner = CliRunner()

CASES_DIR = Path(__file__).parent.parent / "cases"
PILOT_CASE_IDS = [
    "device-tree-001",
    "gpio-basic-001",
    "isr-concurrency-001",
    "kconfig-001",
    "timer-001",
    "watchdog-001",
]


@pytest.fixture()
def results_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for benchmark output."""
    out = tmp_path / "results"
    out.mkdir()
    return out


@patch("embedeval.evaluator._docker_available", return_value=False)
class TestE2EMockBenchmark:
    """End-to-end tests running mock benchmark against pilot cases."""

    def test_run_benchmark_returns_results_for_all_cases(
        self, _mock_docker: object
    ) -> None:
        """Benchmark with mock model returns one result per case."""
        results = run_benchmark(cases_dir=CASES_DIR, model="mock")
        assert len(results) == len(PILOT_CASE_IDS)

    def test_result_case_ids_match_pilot_cases(self, _mock_docker: object) -> None:
        """Each result case_id matches one of the pilot case directory names."""
        results = run_benchmark(cases_dir=CASES_DIR, model="mock")
        result_ids = {r.case_id for r in results}
        assert result_ids == set(PILOT_CASE_IDS)

    def test_scoring_produces_valid_report(self, _mock_docker: object) -> None:
        """Scoring produces a valid BenchmarkReport with expected structure."""
        results = run_benchmark(cases_dir=CASES_DIR, model="mock")
        report = score(results)

        assert isinstance(report, BenchmarkReport)
        assert report.version == "0.1.0"
        assert len(report.models) >= 1
        assert report.models[0].model == "mock"
        assert report.models[0].total_cases == len(PILOT_CASE_IDS)
        assert report.overall.total_cases == len(PILOT_CASE_IDS)
        assert report.overall.total_models == 1
        assert 0.0 <= report.overall.best_pass_at_1 <= 1.0

    def test_reporter_generates_valid_json(
        self, _mock_docker: object, results_dir: Path
    ) -> None:
        """Reporter generates valid JSON from benchmark results."""
        results = run_benchmark(cases_dir=CASES_DIR, model="mock")
        report = score(results)

        json_path = results_dir / "mock-results.json"
        generate_json(report, json_path)

        assert json_path.is_file()
        data = json.loads(json_path.read_text(encoding="utf-8"))
        assert "version" in data
        assert "models" in data
        assert "categories" in data
        assert "overall" in data

        # Verify round-trip: parse back into BenchmarkReport
        parsed_report = BenchmarkReport(**data)
        assert parsed_report.version == report.version
        assert len(parsed_report.models) == len(report.models)

    def test_reporter_generates_valid_markdown(
        self, _mock_docker: object, results_dir: Path
    ) -> None:
        """Reporter generates valid Markdown leaderboard."""
        results = run_benchmark(cases_dir=CASES_DIR, model="mock")
        report = score(results)

        md_path = results_dir / "LEADERBOARD.md"
        generate_leaderboard([report], md_path)

        assert md_path.is_file()
        content = md_path.read_text(encoding="utf-8")
        assert "# EmbedEval Leaderboard" in content
        assert "mock" in content
        assert "Model Comparison" in content
        assert "Category Results" in content


@patch("embedeval.evaluator._docker_available", return_value=False)
class TestPilotCaseValidation:
    """Validate that reference solutions pass all checks."""

    @pytest.mark.parametrize("case_id", PILOT_CASE_IDS)
    def test_reference_solution_passes_static_checks(
        self, _mock_docker: object, case_id: str
    ) -> None:
        """Each pilot case reference solution passes Layer 0 static checks."""
        from embedeval.evaluator import evaluate

        case_dir = CASES_DIR / case_id
        ref_file = case_dir / "reference" / "main.c"
        ref_code = ref_file.read_text(encoding="utf-8")

        result = evaluate(case_dir=case_dir, generated_code=ref_code, model="reference")
        layer_0 = result.layers[0]
        failed_checks = [d for d in layer_0.details if not d.passed]
        assert layer_0.passed, (
            f"Static checks failed for {case_id}: "
            f"{[(d.check_name, d.actual) for d in failed_checks]}"
        )

    @pytest.mark.parametrize("case_id", PILOT_CASE_IDS)
    def test_reference_solution_passes_behavioral_checks(
        self, _mock_docker: object, case_id: str
    ) -> None:
        """Each pilot case reference solution passes Layer 3 behavioral checks."""
        from embedeval.evaluator import evaluate

        case_dir = CASES_DIR / case_id
        ref_file = case_dir / "reference" / "main.c"
        ref_code = ref_file.read_text(encoding="utf-8")

        result = evaluate(case_dir=case_dir, generated_code=ref_code, model="reference")
        layer_3 = result.layers[3]
        failed_checks = [d for d in layer_3.details if not d.passed]
        assert layer_3.passed, (
            f"Behavioral checks failed for {case_id}: "
            f"{[(d.check_name, d.actual) for d in failed_checks]}"
        )

    @pytest.mark.parametrize("case_id", PILOT_CASE_IDS)
    def test_reference_solution_passes_all_layers(
        self, _mock_docker: object, case_id: str
    ) -> None:
        """Each pilot case reference solution passes the full evaluation."""
        from embedeval.evaluator import evaluate

        case_dir = CASES_DIR / case_id
        ref_file = case_dir / "reference" / "main.c"
        ref_code = ref_file.read_text(encoding="utf-8")

        result = evaluate(case_dir=case_dir, generated_code=ref_code, model="reference")
        assert result.passed, (
            f"Full evaluation failed for {case_id} at layer {result.failed_at_layer}"
        )


@patch("embedeval.evaluator._docker_available", return_value=False)
class TestCLIIntegration:
    """CLI integration tests using typer.testing.CliRunner."""

    def test_list_outputs_3_cases(self, _mock_docker: object) -> None:
        """'embedeval list --cases cases/' outputs 3 cases."""
        result = cli_runner.invoke(app, ["list", "--cases", str(CASES_DIR)])
        assert result.exit_code == 0
        assert f"Found {len(PILOT_CASE_IDS)} cases" in result.output
        for case_id in PILOT_CASE_IDS:
            assert case_id in result.output

    def test_validate_passes_all_cases(self, _mock_docker: object) -> None:
        """'embedeval validate --cases cases/' passes for all pilot cases."""
        result = cli_runner.invoke(app, ["validate", "--cases", str(CASES_DIR)])
        assert result.exit_code == 0
        assert f"{len(PILOT_CASE_IDS)} passed" in result.output
        assert "0 failed" in result.output
