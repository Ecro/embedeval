"""Tests for scripts/rescore_run.py — replaying an archived run's stored
generations through the current evaluator without new LLM calls."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml


def _load_module() -> Any:
    """Load the re-score script as a module (scripts/ isn't on sys.path)."""
    script = Path(__file__).resolve().parent.parent / "scripts" / "rescore_run.py"
    spec = importlib.util.spec_from_file_location("rescore_run", script)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rescore_run"] = mod
    spec.loader.exec_module(mod)
    return mod


rescore = _load_module()

MODEL = "claude-code://claude-opus-5"


def _write_case(cases_root: Path, case_id: str, *, require: str = "#include") -> Path:
    """Create a zephyr-bucket case whose static check looks for `require`."""
    case_dir = cases_root / "zephyr" / case_id
    (case_dir / "checks").mkdir(parents=True)
    (case_dir / "metadata.yaml").write_text(
        yaml.safe_dump(
            {
                "id": case_id,
                "category": "kconfig",
                "difficulty": "easy",
                "title": f"Case {case_id}",
                "description": "Re-score test case",
                "tags": ["zephyr"],
                "platform": "native_sim",
                "sdk": "zephyr",
                "sdk_version": "4.1.0",
                "estimated_tokens": 100,
            }
        ),
        encoding="utf-8",
    )
    (case_dir / "checks" / "static.py").write_text(
        f'''
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    found = {require!r} in generated_code
    return [
        CheckDetail(
            check_name="requires_token",
            passed=found,
            expected={require!r},
            actual="found" if found else "missing",
            check_type="static",
        )
    ]
''',
        encoding="utf-8",
    )
    return case_dir


def _write_archive(
    run_dir: Path,
    records: list[dict],
    *,
    with_details: bool = True,
) -> Path:
    if with_details:
        details = run_dir / "details"
        details.mkdir(parents=True)
        for record in records:
            (details / f"{record['case_id']}.json").write_text(
                json.dumps(record), encoding="utf-8"
            )
    else:
        run_dir.mkdir(parents=True)
    return run_dir


def _record(case_id: str, code: str, model: str = MODEL) -> dict:
    return {
        "case_id": case_id,
        "category": "kconfig",
        "sdk": "zephyr",
        "model": model,
        "attempt": 1,
        "generated_code": code,
        "layers": [],
        "failed_at_layer": 0,
        "passed": False,
        "total_score": 0.0,
        "duration_seconds": 1.0,
        "token_usage": {
            "input_tokens": 22000,
            "output_tokens": 500,
            "total_tokens": 22500,
        },
        "cost_usd": 0.12,
    }


class TestLoadArchivedDetails:
    """Tests for archive loading and its failure modes."""

    def test_loads_all_case_records(self, tmp_path: Path) -> None:
        run_dir = _write_archive(
            tmp_path / "run",
            [_record("case-a", "#include <x.h>"), _record("case-b", "int main(){}")],
        )
        records = rescore.load_archived_details(run_dir)
        assert [r["case_id"] for r in records] == ["case-a", "case-b"]

    def test_missing_details_dir_raises(self, tmp_path: Path) -> None:
        run_dir = _write_archive(tmp_path / "run", [], with_details=False)
        with pytest.raises(rescore.RescoreError, match="no details/ directory"):
            rescore.load_archived_details(run_dir)

    def test_empty_details_dir_raises(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "run"
        (run_dir / "details").mkdir(parents=True)
        with pytest.raises(rescore.RescoreError, match="no case JSONs"):
            rescore.load_archived_details(run_dir)


class TestArchivedModel:
    """Tests for single-model enforcement."""

    def test_single_model(self) -> None:
        records = [_record("case-a", "x"), _record("case-b", "y")]
        assert rescore.archived_model(records) == MODEL

    def test_mixed_models_raise(self) -> None:
        records = [
            _record("case-a", "x"),
            _record("case-b", "y", model="claude-code://sonnet"),
        ]
        with pytest.raises(rescore.RescoreError, match="mixes models"):
            rescore.archived_model(records)


class TestRescoreRecords:
    """Tests for re-evaluating stored code against the current checks."""

    def test_current_checks_decide_the_verdict(self, tmp_path: Path) -> None:
        cases_root = tmp_path / "cases"
        _write_case(cases_root, "case-a", require="#include")
        # Archive says FAIL, but the stored code satisfies today's check —
        # that flip is exactly what re-scoring exists to capture.
        records = [_record("case-a", "#include <zephyr/kernel.h>")]

        results, case_dir_map, skipped = rescore.rescore_records(
            records, cases_root, progress=False
        )
        assert len(results) == 1
        assert results[0].passed is True
        assert results[0].case_id == "case-a"
        assert case_dir_map["case-a"].name == "case-a"
        assert skipped == []

    def test_failing_code_still_fails(self, tmp_path: Path) -> None:
        cases_root = tmp_path / "cases"
        _write_case(cases_root, "case-a", require="#include")
        records = [_record("case-a", "int main(void) { return 0; }")]

        results, _, _ = rescore.rescore_records(records, cases_root, progress=False)
        assert results[0].passed is False
        assert results[0].failed_at_layer == 0

    def test_preserves_generation_cost_and_tokens(self, tmp_path: Path) -> None:
        cases_root = tmp_path / "cases"
        _write_case(cases_root, "case-a")
        records = [_record("case-a", "#include <x.h>")]

        results, _, _ = rescore.rescore_records(records, cases_root, progress=False)
        # Re-scoring makes no LLM call, so the original run's spend is what
        # the artifact must keep reporting.
        assert results[0].cost_usd == 0.12
        assert results[0].token_usage.total_tokens == 22500

    def test_stub_without_code_raises(self, tmp_path: Path) -> None:
        cases_root = tmp_path / "cases"
        _write_case(cases_root, "case-a")
        # A tracker-merged stub: the archive has a file, but no submission.
        # Scoring it would read as FAIL@L0 rather than as a broken input set.
        records = [_record("case-a", "")]

        with pytest.raises(rescore.RescoreError, match="no stored generated_code"):
            rescore.rescore_records(records, cases_root, progress=False)

    def test_unknown_case_is_skipped(self, tmp_path: Path) -> None:
        cases_root = tmp_path / "cases"
        _write_case(cases_root, "case-a")
        records = [_record("case-a", "#include <x.h>"), _record("deleted-999", "x")]

        results, case_dir_map, skipped = rescore.rescore_records(
            records, cases_root, progress=False
        )
        assert [r.case_id for r in results] == ["case-a"]
        assert skipped == ["deleted-999"]
        assert "deleted-999" not in case_dir_map

    def test_metadata_fields_attached(self, tmp_path: Path) -> None:
        cases_root = tmp_path / "cases"
        _write_case(cases_root, "case-a")
        records = [_record("case-a", "#include <x.h>")]

        results, _, _ = rescore.rescore_records(records, cases_root, progress=False)
        assert results[0].sdk is not None
        assert results[0].category.value == "kconfig"


class TestRunIdRecovery:
    """Tests for recovering the archive's run id from its directory name."""

    def test_run_id_suffix(self) -> None:
        run_dir = Path("results/runs/2026-09-08_claude-code___claude-opus-5_n1")
        assert rescore._run_id_of(run_dir, MODEL) == "n1"

    def test_no_run_id(self) -> None:
        run_dir = Path("results/runs/2026-09-08_claude-code___claude-opus-5")
        assert rescore._run_id_of(run_dir, MODEL) is None


class TestPublishIntegration:
    """End-to-end: re-scored results land in the standard artifact set."""

    def test_writes_leaderboard_and_archive(self, tmp_path: Path) -> None:
        cases_root = tmp_path / "cases"
        _write_case(cases_root, "case-a")
        records = [_record("case-a", "#include <x.h>")]
        results, case_dir_map, _ = rescore.rescore_records(
            records, cases_root, progress=False
        )

        from embedeval.cli import publish_run_results

        output_dir = tmp_path / "results"
        json_path, leaderboard_path, run_dir, _guide = publish_run_results(
            results=results,
            model=MODEL,
            cases_dir=cases_root,
            output_dir=output_dir,
            case_dir_map=case_dir_map,
            run_id="n1_rescored",
        )
        assert json_path.is_file()
        assert leaderboard_path.is_file()
        assert (run_dir / "details" / "case-a.json").is_file()
        assert (run_dir / "per_check_metrics.json").is_file()
        assert (output_dir / "test_tracker.json").is_file()
        assert run_dir.name.endswith("_n1_rescored")
