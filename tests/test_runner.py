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
    category: str = "kconfig",
    difficulty: str = "easy",
    tags: list[str] | None = None,
    visibility: str | None = None,
) -> Path:
    """Helper to create a case directory with metadata."""
    case_dir = parent / case_id
    case_dir.mkdir(parents=True)
    metadata: dict = {
        "id": case_id,
        "category": category,
        "difficulty": difficulty,
        "title": f"Test case {case_id}",
        "description": f"Description for {case_id}",
        "tags": tags or ["test"],
        "platform": "native_sim",
        "estimated_tokens": 500,
        "sdk_version": "3.6.0",
    }
    if visibility is not None:
        metadata["visibility"] = visibility
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
        _create_case(tmp_path, "case-001", category="kconfig")
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


class TestPrivateHeldOutSet:
    """Tests for private/public visibility filtering."""

    def test_filter_excludes_private_by_default(self, tmp_path: Path) -> None:
        _create_case(tmp_path, "case-001", visibility="public")
        _create_case(tmp_path, "case-002", visibility="private")
        all_cases = discover_cases(tmp_path)

        from embedeval.models import Visibility

        filtered = filter_cases(all_cases, Filters(visibility=Visibility.PUBLIC))
        assert len(filtered) == 1
        assert filtered[0][1].id == "case-001"

    def test_filter_includes_private_when_requested(self, tmp_path: Path) -> None:
        _create_case(tmp_path, "case-001", visibility="public")
        _create_case(tmp_path, "case-002", visibility="private")
        all_cases = discover_cases(tmp_path)

        filtered = filter_cases(all_cases, Filters())  # no visibility filter
        assert len(filtered) == 2

    def test_no_visibility_defaults_to_public(self, tmp_path: Path) -> None:
        """Cases without visibility field should be included in public filter."""
        _create_case(tmp_path, "case-001")  # no visibility = defaults to public
        _create_case(tmp_path, "case-002", visibility="private")
        all_cases = discover_cases(tmp_path)

        from embedeval.models import Visibility

        filtered = filter_cases(all_cases, Filters(visibility=Visibility.PUBLIC))
        assert len(filtered) == 1
        assert filtered[0][1].id == "case-001"

    @patch("embedeval.runner.evaluate")
    @patch("embedeval.runner.call_model")
    def test_run_benchmark_excludes_private_by_default(
        self, mock_call_model: object, mock_evaluate: object, tmp_path: Path
    ) -> None:
        from unittest.mock import MagicMock

        from embedeval.models import EvalResult, TokenUsage

        _create_case(tmp_path, "kconfig-001")  # public (default)
        _create_case(tmp_path, "kconfig-002", visibility="private")

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

        results = run_benchmark(cases_dir=tmp_path, model="mock")
        assert len(results) == 1  # only public case

    @patch("embedeval.runner.evaluate")
    @patch("embedeval.runner.call_model")
    def test_run_benchmark_includes_private_when_flag_set(
        self, mock_call_model: object, mock_evaluate: object, tmp_path: Path
    ) -> None:
        from unittest.mock import MagicMock

        from embedeval.models import EvalResult, TokenUsage

        _create_case(tmp_path, "kconfig-001")  # public (default)
        _create_case(tmp_path, "kconfig-002", visibility="private")

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
            cases_dir=tmp_path, model="mock", include_private=True
        )
        assert len(results) == 2  # both cases


class TestMetadataNewFields:
    """Tests for build_board, l1_skip, l2_skip metadata fields."""

    def test_build_board_loaded(self, tmp_path: Path) -> None:
        case_dir = tmp_path / "adc-001"
        case_dir.mkdir()
        metadata = {
            "id": "adc-001",
            "category": "adc",
            "difficulty": "medium",
            "title": "ADC test",
            "description": "ADC test case",
            "tags": ["zephyr", "adc"],
            "platform": "native_sim",
            "estimated_tokens": 400,
            "sdk_version": "4.1.0",
            "build_board": "nrf52840dk/nrf52840",
        }
        (case_dir / "metadata.yaml").write_text(
            yaml.dump(metadata), encoding="utf-8"
        )
        (case_dir / "prompt.md").write_text("test", encoding="utf-8")
        meta = load_case_metadata(case_dir)
        assert meta is not None
        assert meta.build_board == "nrf52840dk/nrf52840"

    def test_l1_skip_loaded(self, tmp_path: Path) -> None:
        case_dir = tmp_path / "adc-002"
        case_dir.mkdir()
        metadata = {
            "id": "adc-002",
            "category": "adc",
            "difficulty": "hard",
            "title": "ADC skip test",
            "description": "L1 skip test case",
            "tags": ["zephyr"],
            "platform": "native_sim",
            "estimated_tokens": 400,
            "sdk_version": "4.1.0",
            "l1_skip": True,
        }
        (case_dir / "metadata.yaml").write_text(
            yaml.dump(metadata), encoding="utf-8"
        )
        (case_dir / "prompt.md").write_text("test", encoding="utf-8")
        meta = load_case_metadata(case_dir)
        assert meta is not None
        assert meta.l1_skip is True
        assert meta.l2_skip is False

    def test_l2_skip_loaded(self, tmp_path: Path) -> None:
        case_dir = tmp_path / "ble-001"
        case_dir.mkdir()
        metadata = {
            "id": "ble-001",
            "category": "ble",
            "difficulty": "hard",
            "title": "BLE skip test",
            "description": "L2 skip test case",
            "tags": ["zephyr", "ble"],
            "platform": "native_sim",
            "estimated_tokens": 600,
            "sdk_version": "4.1.0",
            "l2_skip": True,
        }
        (case_dir / "metadata.yaml").write_text(
            yaml.dump(metadata), encoding="utf-8"
        )
        (case_dir / "prompt.md").write_text("test", encoding="utf-8")
        meta = load_case_metadata(case_dir)
        assert meta is not None
        assert meta.l2_skip is True
        assert meta.l1_skip is False

    def test_defaults_when_fields_absent(self, tmp_path: Path) -> None:
        case_dir = _create_case(tmp_path, "kconfig-001")
        meta = load_case_metadata(case_dir)
        assert meta is not None
        assert meta.build_board is None
        assert meta.l1_skip is False
        assert meta.l2_skip is False
