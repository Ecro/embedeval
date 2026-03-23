"""Tests for EmbedEval runner."""

from pathlib import Path
from unittest.mock import patch

import yaml

from embedeval.models import CaseCategory, DifficultyTier, EvalPlatform
from embedeval.runner import (
    Filters,
    discover_cases,
    filter_cases,
    load_case_metadata,
    run_benchmark,
)


def _create_case(
    parent: Path,
    case_id: str,
    category: str = "zephyr-kconfig",
    difficulty: str = "easy",
    tags: list[str] | None = None,
) -> Path:
    """Helper to create a case directory with metadata."""
    case_dir = parent / case_id
    case_dir.mkdir(parents=True)
    metadata = {
        "id": case_id,
        "category": category,
        "difficulty": difficulty,
        "title": f"Test case {case_id}",
        "description": f"Description for {case_id}",
        "tags": tags or ["test"],
        "platform": "native_sim",
        "estimated_tokens": 500,
        "zephyr_version": "3.6.0",
    }
    (case_dir / "metadata.yaml").write_text(yaml.dump(metadata), encoding="utf-8")
    (case_dir / "prompt.md").write_text(
        f"Generate code for {case_id}", encoding="utf-8"
    )
    return case_dir


class TestLoadCaseMetadata:
    """Tests for metadata loading."""

    def test_valid_metadata(self, tmp_path: Path) -> None:
        case_dir = _create_case(tmp_path, "case-001")
        meta = load_case_metadata(case_dir)
        assert meta is not None
        assert meta.id == "case-001"
        assert meta.category == CaseCategory.KCONFIG
        assert meta.difficulty == DifficultyTier.EASY

    def test_missing_metadata_file(self, tmp_path: Path) -> None:
        case_dir = tmp_path / "empty-case"
        case_dir.mkdir()
        meta = load_case_metadata(case_dir)
        assert meta is None

    def test_invalid_metadata_format(self, tmp_path: Path) -> None:
        case_dir = tmp_path / "bad-case"
        case_dir.mkdir()
        (case_dir / "metadata.yaml").write_text("just a string", encoding="utf-8")
        meta = load_case_metadata(case_dir)
        assert meta is None


class TestDiscoverCases:
    """Tests for case discovery."""

    def test_discover_multiple_cases(self, tmp_path: Path) -> None:
        _create_case(tmp_path, "case-001")
        _create_case(tmp_path, "case-002")
        cases = discover_cases(tmp_path)
        assert len(cases) == 2

    def test_discover_skips_invalid(self, tmp_path: Path) -> None:
        _create_case(tmp_path, "case-001")
        invalid = tmp_path / "invalid-case"
        invalid.mkdir()
        cases = discover_cases(tmp_path)
        assert len(cases) == 1

    def test_discover_empty_dir(self, tmp_path: Path) -> None:
        cases = discover_cases(tmp_path)
        assert len(cases) == 0

    def test_discover_nonexistent_dir(self, tmp_path: Path) -> None:
        cases = discover_cases(tmp_path / "nonexistent")
        assert len(cases) == 0


class TestFilterCases:
    """Tests for case filtering."""

    def test_filter_by_category(self, tmp_path: Path) -> None:
        _create_case(tmp_path, "case-001", category="zephyr-kconfig")
        _create_case(tmp_path, "case-002", category="ble")
        all_cases = discover_cases(tmp_path)

        filtered = filter_cases(
            all_cases,
            Filters(categories=[CaseCategory.KCONFIG]),
        )
        assert len(filtered) == 1
        assert filtered[0][1].id == "case-001"

    def test_filter_by_difficulty(self, tmp_path: Path) -> None:
        _create_case(tmp_path, "case-001", difficulty="easy")
        _create_case(tmp_path, "case-002", difficulty="hard")
        all_cases = discover_cases(tmp_path)

        filtered = filter_cases(
            all_cases,
            Filters(difficulties=[DifficultyTier.HARD]),
        )
        assert len(filtered) == 1
        assert filtered[0][1].id == "case-002"

    def test_filter_by_tags(self, tmp_path: Path) -> None:
        _create_case(tmp_path, "case-001", tags=["gpio", "driver"])
        _create_case(tmp_path, "case-002", tags=["network"])
        all_cases = discover_cases(tmp_path)

        filtered = filter_cases(
            all_cases,
            Filters(tags=["gpio"]),
        )
        assert len(filtered) == 1
        assert filtered[0][1].id == "case-001"

    def test_empty_filters_pass_all(self, tmp_path: Path) -> None:
        _create_case(tmp_path, "case-001")
        _create_case(tmp_path, "case-002")
        all_cases = discover_cases(tmp_path)

        filtered = filter_cases(all_cases, Filters())
        assert len(filtered) == 2


class TestRunBenchmark:
    """Tests for end-to-end benchmark execution."""

    @patch("embedeval.runner.evaluate")
    @patch("embedeval.runner.call_model")
    def test_mock_end_to_end(
        self,
        mock_call_model: object,
        mock_evaluate: object,
        tmp_path: Path,
    ) -> None:
        from unittest.mock import MagicMock

        from embedeval.models import EvalResult, TokenUsage

        _create_case(tmp_path, "case-001")

        mock_response = MagicMock()
        mock_response.generated_code = "int main() {}"
        mock_response.token_usage = TokenUsage(
            input_tokens=10, output_tokens=5, total_tokens=15
        )
        mock_response.cost_usd = 0.0
        mock_call_model.return_value = mock_response  # type: ignore[union-attr]

        mock_result = MagicMock(spec=EvalResult)
        mock_result.passed = True
        mock_result.failed_at_layer = None
        mock_evaluate.return_value = mock_result  # type: ignore[union-attr]

        results = run_benchmark(
            cases_dir=tmp_path,
            model="mock",
        )
        assert len(results) == 1
        mock_call_model.assert_called_once()  # type: ignore[union-attr]
        mock_evaluate.assert_called_once()  # type: ignore[union-attr]

    def test_no_cases_returns_empty(self, tmp_path: Path) -> None:
        results = run_benchmark(
            cases_dir=tmp_path,
            model="mock",
        )
        assert results == []

    @patch("embedeval.runner.evaluate")
    @patch("embedeval.runner.call_model")
    def test_multiple_attempts(
        self,
        mock_call_model: object,
        mock_evaluate: object,
        tmp_path: Path,
    ) -> None:
        from unittest.mock import MagicMock

        from embedeval.models import EvalResult, TokenUsage

        _create_case(tmp_path, "case-001")

        mock_response = MagicMock()
        mock_response.generated_code = "int main() {}"
        mock_response.token_usage = TokenUsage(
            input_tokens=10, output_tokens=5, total_tokens=15
        )
        mock_response.cost_usd = 0.0
        mock_call_model.return_value = mock_response  # type: ignore[union-attr]

        mock_result = MagicMock(spec=EvalResult)
        mock_result.passed = True
        mock_result.failed_at_layer = None
        mock_evaluate.return_value = mock_result  # type: ignore[union-attr]

        results = run_benchmark(
            cases_dir=tmp_path,
            model="mock",
            attempts=3,
        )
        assert len(results) == 3
