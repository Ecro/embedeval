"""Tests for runner checkpoint + per-case error resilience."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from embedeval.models import (
    CaseCategory,
    CaseMetadata,
    CaseTier,
    DifficultyTier,
    EvalPlatform,
    EvalResult,
    LayerResult,
    TokenUsage,
    Visibility,
)
from embedeval.runner import (
    _append_checkpoint,
    _load_checkpoint,
    _make_error_result,
)


def _meta(case_id: str) -> CaseMetadata:
    return CaseMetadata(
        id=case_id,
        category=CaseCategory.KCONFIG,
        difficulty=DifficultyTier.MEDIUM,
        title="test",
        description="desc",
        tags=[],
        platform=EvalPlatform.NATIVE_SIM,
        estimated_tokens=100,
        sdk_version="4.1.0",
        visibility=Visibility.PUBLIC,
        tier=CaseTier.CORE,
    )


def _result(case_id: str, passed: bool = True) -> EvalResult:
    return EvalResult(
        case_id=case_id,
        category=CaseCategory.KCONFIG,
        model="test",
        attempt=1,
        generated_code="int main(void) {}",
        layers=[
            LayerResult(
                layer=0,
                name="static_analysis",
                passed=passed,
                details=[],
                duration_seconds=0.0,
            )
        ],
        failed_at_layer=None if passed else 0,
        passed=passed,
        total_score=1.0 if passed else 0.0,
        duration_seconds=0.1,
        token_usage=TokenUsage(input_tokens=1, output_tokens=1, total_tokens=2),
        cost_usd=0.0,
    )


# ---------- _make_error_result ----------


def test_make_error_result_captures_exception_type():
    meta = _meta("case-001")
    exc = UnicodeDecodeError("utf-8", b"", 0, 1, "test error")
    result = _make_error_result(meta, "model", 1, exc)
    assert not result.passed
    assert result.failed_at_layer == 0
    assert "UnicodeDecodeError" in result.layers[0].error
    assert result.tier == CaseTier.CORE


def test_make_error_result_truncates_long_messages():
    meta = _meta("case-001")
    exc = RuntimeError("x" * 1000)
    result = _make_error_result(meta, "model", 1, exc)
    assert len(result.layers[0].error) <= 500


# ---------- Checkpoint I/O ----------


def test_load_checkpoint_empty_file(tmp_path: Path):
    ckpt = tmp_path / "ckpt.jsonl"
    ckpt.write_text("")
    loaded = _load_checkpoint(ckpt)
    assert loaded == {}


def test_load_checkpoint_missing_file(tmp_path: Path):
    loaded = _load_checkpoint(tmp_path / "missing.jsonl")
    assert loaded == {}


def test_append_and_load_roundtrip(tmp_path: Path):
    ckpt = tmp_path / "ckpt.jsonl"
    r1 = _result("case-001", passed=True)
    r2 = _result("case-002", passed=False)

    _append_checkpoint(ckpt, r1)
    _append_checkpoint(ckpt, r2)

    loaded = _load_checkpoint(ckpt)
    assert set(loaded.keys()) == {"case-001", "case-002"}
    assert loaded["case-001"].passed is True
    assert loaded["case-002"].passed is False


def test_load_checkpoint_skips_corrupt_lines(tmp_path: Path):
    ckpt = tmp_path / "ckpt.jsonl"
    r1 = _result("case-001")
    _append_checkpoint(ckpt, r1)
    # Inject a corrupt line
    with ckpt.open("a") as f:
        f.write("NOT VALID JSON\n")
    _append_checkpoint(ckpt, _result("case-003"))

    loaded = _load_checkpoint(ckpt)
    assert set(loaded.keys()) == {"case-001", "case-003"}


def test_checkpoint_deduplicates_by_case_id(tmp_path: Path):
    """If the same case_id appears twice (e.g., re-appended after partial
    resume), the latest entry wins."""
    ckpt = tmp_path / "ckpt.jsonl"
    r_fail = _result("case-001", passed=False)
    r_pass = _result("case-001", passed=True)

    _append_checkpoint(ckpt, r_fail)
    _append_checkpoint(ckpt, r_pass)

    loaded = _load_checkpoint(ckpt)
    assert loaded["case-001"].passed is True


# ---------- Integration: broad except catch ----------


def test_run_single_case_unicode_error_caught(tmp_path: Path):
    """Simulate a UnicodeDecodeError in call_model — it should NOT kill
    the run. This is a smoke test for the except-Exception path."""
    from embedeval.runner import _run_single_case

    meta = _meta("case-001")
    case_dir = tmp_path / "case-001"
    case_dir.mkdir()
    (case_dir / "prompt.md").write_text("test")

    # _run_single_case calls call_model which we mock to raise
    with patch("embedeval.runner.call_model") as mock_call:
        mock_call.side_effect = UnicodeDecodeError(
            "utf-8", b"\xe2", 0, 1, "test"
        )
        try:
            _run_single_case(
                meta=meta,
                case_dir=case_dir,
                prompt="test",
                context_files=[],
                model="test-model",
                attempt=1,
                feedback_rounds=0,
            )
            raised = False
        except UnicodeDecodeError:
            raised = True

    # The exception SHOULD propagate from _run_single_case —
    # it's the CALLER (run_benchmark) that catches it broadly.
    assert raised, (
        "_run_single_case should not silently swallow errors — "
        "run_benchmark's broad except handles that"
    )
