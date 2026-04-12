"""Tests for generate_run_archive — especially the --run-id suffix that
keeps multiple same-day runs of the same model from stomping each other."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from embedeval.models import (
    BenchmarkReport,
    CaseCategory,
    EvalResult,
    LayerResult,
    ModelScore,
    OverallScore,
    TokenUsage,
)
from embedeval.reporter import _sanitize_run_id, generate_run_archive

MODEL = "claude-code://sonnet"


def _result(case_id: str, passed: bool = True) -> EvalResult:
    return EvalResult(
        case_id=case_id,
        category=CaseCategory.KCONFIG,
        model=MODEL,
        attempt=1,
        generated_code="int main(void) { return 0; }",
        layers=[
            LayerResult(
                layer=0,
                name="static_analysis",
                passed=passed,
                details=[],
                duration_seconds=0.1,
            )
        ],
        failed_at_layer=None if passed else 0,
        passed=passed,
        total_score=1.0 if passed else 0.0,
        duration_seconds=0.5,
        token_usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
        cost_usd=0.0,
    )


def _report(passed: int = 1, total: int = 1) -> BenchmarkReport:
    return BenchmarkReport(
        version="0.1.0",
        date=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
        models=[
            ModelScore(
                model=MODEL,
                pass_at_1=passed / total if total else 0.0,
                pass_at_5=passed / total if total else 0.0,
                total_cases=total,
                passed_cases=passed,
                layer_pass_rates={"static_analysis": 1.0},
                pass_at_1_ci=(0.0, 1.0),
            )
        ],
        categories=[],
        overall=OverallScore(
            total_cases=total,
            total_models=1,
            best_model=MODEL,
            best_pass_at_1=passed / total if total else 0.0,
        ),
    )


def test_archive_without_run_id_uses_date_model_dir(tmp_path: Path):
    results = [_result("kconfig-001")]
    run_dir = generate_run_archive(results, _report(), tmp_path, MODEL)

    assert run_dir.parent == tmp_path / "runs"
    name = run_dir.name
    # Contains date and sanitized model slug, no trailing suffix
    assert "claude-code" in name
    assert "sonnet" in name
    assert ":" not in name and "/" not in name
    assert (run_dir / "summary.json").is_file()
    assert (run_dir / "details" / "kconfig-001.json").is_file()


def test_archive_with_run_id_appends_suffix(tmp_path: Path):
    results = [_result("kconfig-001")]
    run_dir = generate_run_archive(
        results, _report(), tmp_path, MODEL, run_id="n1"
    )

    assert run_dir.name.endswith("_n1")
    summary = json.loads((run_dir / "summary.json").read_text())
    assert summary["run_id"] == "n1"


def test_archive_run_id_prevents_stomp(tmp_path: Path):
    """Two runs on the same day with different run_ids coexist."""
    r1 = generate_run_archive(
        [_result("kconfig-001", passed=True)],
        _report(1, 1),
        tmp_path,
        MODEL,
        run_id="n1",
    )
    r2 = generate_run_archive(
        [_result("kconfig-001", passed=False)],
        _report(0, 1),
        tmp_path,
        MODEL,
        run_id="n2",
    )

    assert r1 != r2
    assert r1.is_dir() and r2.is_dir()
    s1 = json.loads((r1 / "summary.json").read_text())
    s2 = json.loads((r2 / "summary.json").read_text())
    assert s1["passed"] == 1 and s2["passed"] == 0


def test_archive_without_run_id_same_day_overwrites(tmp_path: Path):
    """Sanity check: without run_id, two same-day runs share one dir."""
    r1 = generate_run_archive([_result("kconfig-001")], _report(1, 1), tmp_path, MODEL)
    r2 = generate_run_archive([_result("kconfig-001")], _report(1, 1), tmp_path, MODEL)
    assert r1 == r2


def test_sanitize_run_id_replaces_unsafe_chars():
    assert _sanitize_run_id("n1") == "n1"
    assert _sanitize_run_id("run 3") == "run-3"
    assert _sanitize_run_id("weird/id:with@stuff") == "weird-id-with-stuff"
    assert _sanitize_run_id("  leading  ") == "leading"
    assert _sanitize_run_id("---") == ""
    assert _sanitize_run_id("ok_2026.04.11") == "ok_2026.04.11"


def test_archive_sanitizes_unsafe_run_id(tmp_path: Path):
    run_dir = generate_run_archive(
        [_result("kconfig-001")],
        _report(),
        tmp_path,
        MODEL,
        run_id="run 3",
    )
    assert run_dir.name.endswith("_run-3")
    assert "/" not in run_dir.name
    assert " " not in run_dir.name


def test_archive_empty_run_id_behaves_like_none(tmp_path: Path):
    r_empty = generate_run_archive(
        [_result("kconfig-001")], _report(), tmp_path, MODEL, run_id=""
    )
    r_none = generate_run_archive(
        [_result("kconfig-001")], _report(), tmp_path, MODEL, run_id=None
    )
    assert r_empty == r_none
    # No "run_id" key should be written when id is empty
    summary = json.loads((r_empty / "summary.json").read_text())
    assert "run_id" not in summary


def test_archive_all_dashes_run_id_is_dropped(tmp_path: Path):
    """A run_id that sanitizes to empty string must not leave a dangling
    trailing underscore on the directory name."""
    run_dir = generate_run_archive(
        [_result("kconfig-001")], _report(), tmp_path, MODEL, run_id="---"
    )
    assert not run_dir.name.endswith("_")
