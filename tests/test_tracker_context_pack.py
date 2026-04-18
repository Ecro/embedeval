"""Tests for tracker context_pack_hash enforcement."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from embedeval.models import (
    CaseCategory,
    EvalResult,
    LayerResult,
    TokenUsage,
)
from embedeval.test_tracker import (
    ContextPackMismatchError,
    TrackerData,
    update_tracker,
)


def _make_result(case_id: str = "isr-concurrency-001") -> EvalResult:
    return EvalResult(
        case_id=case_id,
        category=CaseCategory.ISR_CONCURRENCY,
        model="mock",
        attempt=1,
        generated_code="",
        layers=[
            LayerResult(
                layer=0,
                name="static_analysis",
                passed=True,
                details=[],
                duration_seconds=0.0,
            )
        ],
        failed_at_layer=None,
        passed=True,
        total_score=1.0,
        duration_seconds=0.0,
        token_usage=TokenUsage(input_tokens=1, output_tokens=1, total_tokens=2),
        cost_usd=0.0,
    )


def test_first_run_records_hash(tmp_path: Path) -> None:
    tracker = TrackerData()
    updated = update_tracker(
        tracker,
        [_make_result()],
        cases_dir=tmp_path,
        model="mock",
        context_pack_hash="aaaaaaaaaaaaaaaa",
    )
    assert updated.context_pack_hash == "aaaaaaaaaaaaaaaa"


def test_same_hash_appends_ok(tmp_path: Path) -> None:
    tracker = TrackerData(context_pack_hash="aaaaaaaaaaaaaaaa")
    update_tracker(
        tracker,
        [_make_result()],
        cases_dir=tmp_path,
        model="mock",
        context_pack_hash="aaaaaaaaaaaaaaaa",
    )
    assert tracker.context_pack_hash == "aaaaaaaaaaaaaaaa"


def test_mismatch_raises(tmp_path: Path) -> None:
    tracker = TrackerData(context_pack_hash="aaaaaaaaaaaaaaaa")
    # Seed with a prior result so "results non-empty" branch fires.
    update_tracker(
        tracker,
        [_make_result()],
        cases_dir=tmp_path,
        model="mock",
        context_pack_hash="aaaaaaaaaaaaaaaa",
    )
    with pytest.raises(ContextPackMismatchError, match="mismatch"):
        update_tracker(
            tracker,
            [_make_result("isr-concurrency-002")],
            cases_dir=tmp_path,
            model="mock",
            context_pack_hash="bbbbbbbbbbbbbbbb",
        )


def test_no_pack_no_enforcement(tmp_path: Path) -> None:
    """Backward compat: tracker without pack hash accepts pack-less runs."""
    tracker = TrackerData()
    update_tracker(
        tracker,
        [_make_result()],
        cases_dir=tmp_path,
        model="mock",
        context_pack_hash=None,
    )
    assert tracker.context_pack_hash is None


def test_legacy_bare_tracker_rejects_pack_run(tmp_path: Path) -> None:
    """Bare tracker with results MUST refuse a new packed run. Otherwise the
    pre-existing bare results would be misattributed as 'expert' runs."""
    tracker = TrackerData()
    from embedeval.test_tracker import CaseResult

    tracker.results.setdefault("mock", {})
    tracker.results["mock"]["isr-concurrency-001"] = CaseResult(
        case_id="isr-concurrency-001",
        model="mock",
        passed=True,
        case_git_hash="legacy",
        tested_at=datetime.now(tz=timezone.utc).isoformat(),
    )
    with pytest.raises(ContextPackMismatchError, match="mismatch"):
        update_tracker(
            tracker,
            [_make_result("isr-concurrency-002")],
            cases_dir=tmp_path,
            model="mock",
            context_pack_hash="cccccccccccccccc",
        )


def test_packed_tracker_rejects_bare_run(tmp_path: Path) -> None:
    """Tracker with pack hash MUST refuse no-pack run. Same reasoning in
    reverse: silently downgrading to bare invalidates the comparison."""
    tracker = TrackerData(context_pack_hash="ddddddddddddddd0")
    update_tracker(
        tracker,
        [_make_result("isr-concurrency-001")],
        cases_dir=tmp_path,
        model="mock",
        context_pack_hash="ddddddddddddddd0",
    )
    with pytest.raises(ContextPackMismatchError, match="mismatch"):
        update_tracker(
            tracker,
            [_make_result("isr-concurrency-002")],
            cases_dir=tmp_path,
            model="mock",
            context_pack_hash=None,
        )


def test_empty_tracker_accepts_any_first_run(tmp_path: Path) -> None:
    """First run into an empty dir sets the hash whether bare or packed."""
    tracker = TrackerData()
    update_tracker(
        tracker,
        [_make_result()],
        cases_dir=tmp_path,
        model="mock",
        context_pack_hash="eeeeeeeeeeeeeeee",
    )
    assert tracker.context_pack_hash == "eeeeeeeeeeeeeeee"


def test_cleared_tracker_with_prior_hash_rejects_new_pack(tmp_path: Path) -> None:
    """F7 regression: a tracker that had hash A and got its results
    cleared (e.g. all cases deleted) must NOT silently accept hash B on
    the next run. The hash carries semantic identity even with no rows."""
    tracker = TrackerData(context_pack_hash="aaaaaaaaaaaaaaaa")
    # results dict is empty but the hash is set — escape hatch must NOT fire
    with pytest.raises(ContextPackMismatchError, match="mismatch"):
        update_tracker(
            tracker,
            [_make_result()],
            cases_dir=tmp_path,
            model="mock",
            context_pack_hash="bbbbbbbbbbbbbbbb",
        )
