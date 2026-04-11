"""Tests for the comprehensive-results merge helper that fixes the
--retest-only leaderboard/safeguide stomp."""

from __future__ import annotations

from embedeval.cli import _build_comprehensive_results
from embedeval.models import (
    CaseCategory,
    CaseMetadata,
    CaseTier,
    DifficultyTier,
    EvalPlatform,
    EvalResult,
    LayerResult,
    ReasoningType,
    TokenUsage,
    Visibility,
)
from embedeval.test_tracker import CaseResult, TrackerData

MODEL = "test-model"


def _meta(case_id: str, category: str = "kconfig") -> CaseMetadata:
    return CaseMetadata(
        id=case_id,
        category=CaseCategory(category),
        difficulty=DifficultyTier.MEDIUM,
        title=f"title-{case_id}",
        description="desc",
        tags=[],
        platform=EvalPlatform.NATIVE_SIM,
        estimated_tokens=100,
        sdk_version="4.1.0",
        visibility=Visibility.PUBLIC,
        tier=CaseTier.CORE,
        reasoning_types=[ReasoningType.API_RECALL],
    )


def _result(case_id: str, passed: bool, category: str = "kconfig") -> EvalResult:
    return EvalResult(
        case_id=case_id,
        category=CaseCategory(category),
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
        token_usage=TokenUsage(input_tokens=1, output_tokens=1, total_tokens=2),
        cost_usd=0.0,
        tier=CaseTier.CORE,
        reasoning_types=[ReasoningType.API_RECALL],
    )


def _tracker(**entries: bool) -> TrackerData:
    """entries: case_id=passed mapping for the test model."""
    t = TrackerData()
    t.results[MODEL] = {
        cid: CaseResult(
            case_id=cid,
            model=MODEL,
            passed=passed,
            failed_at_layer=None if passed else 2,
            failed_checks=[] if passed else ["runtime_fail"],
            case_git_hash="a" * 16,
            tested_at="2026-04-11T00:00:00+00:00",
        )
        for cid, passed in entries.items()
    }
    return t


def test_empty_tracker_returns_only_new_results():
    new = [_result("kconfig-001", True), _result("kconfig-002", False)]
    metas = {m.id: m for m in (_meta("kconfig-001"), _meta("kconfig-002"))}
    merged = _build_comprehensive_results(new, TrackerData(), MODEL, metas)
    assert len(merged) == 2
    assert {r.case_id for r in merged} == {"kconfig-001", "kconfig-002"}


def test_new_results_override_tracker_entries():
    """If a case appears in both new_results and tracker, the new one wins."""
    new = [_result("kconfig-001", True)]  # new says PASS
    tracker = _tracker(**{"kconfig-001": False})  # tracker says FAIL
    merged = _build_comprehensive_results(
        new, tracker, MODEL, {"kconfig-001": _meta("kconfig-001")}
    )
    assert len(merged) == 1
    assert merged[0].passed is True
    assert merged[0].case_id == "kconfig-001"


def test_unchanged_tracker_entries_are_carried_forward():
    """The key anti-stomp property: running 1 case shouldn't drop 2 others."""
    new = [_result("kconfig-001", False)]
    tracker = _tracker(**{
        "kconfig-001": True,   # will be overridden by new
        "kconfig-002": True,
        "kconfig-003": False,
    })
    metas = {
        m.id: m
        for m in (_meta(c) for c in ("kconfig-001", "kconfig-002", "kconfig-003"))
    }
    merged = _build_comprehensive_results(new, tracker, MODEL, metas)
    ids = {r.case_id for r in merged}
    assert ids == {"kconfig-001", "kconfig-002", "kconfig-003"}
    by_id = {r.case_id: r for r in merged}
    # new wins on overlap
    assert by_id["kconfig-001"].passed is False
    # carried entries preserved
    assert by_id["kconfig-002"].passed is True
    assert by_id["kconfig-003"].passed is False
    # synthesized entries carry metadata needed for aggregation
    assert by_id["kconfig-002"].category == CaseCategory.KCONFIG
    assert by_id["kconfig-002"].tier == CaseTier.CORE
    assert by_id["kconfig-002"].reasoning_types == [ReasoningType.API_RECALL]


def test_orphan_tracker_entries_are_dropped():
    """An entry in the tracker without matching CaseMetadata (e.g., deleted
    TC) must not contaminate the aggregate."""
    new = [_result("kconfig-001", True)]
    tracker = _tracker(**{
        "kconfig-001": True,
        "zombie-999": False,  # no meta for this one
    })
    metas = {"kconfig-001": _meta("kconfig-001")}
    merged = _build_comprehensive_results(new, tracker, MODEL, metas)
    assert {r.case_id for r in merged} == {"kconfig-001"}


def test_synthesized_layer_fields_reflect_failed_layer():
    """For a tracker entry with failed_at_layer=2, layers 0-1 should be PASS
    and layers 2-4 should be FAIL (or at least not PASS)."""
    new: list[EvalResult] = []
    tracker = _tracker(**{"kconfig-002": False})
    merged = _build_comprehensive_results(
        new, tracker, MODEL, {"kconfig-002": _meta("kconfig-002")}
    )
    assert len(merged) == 1
    r = merged[0]
    # failed_at_layer=2 → L0, L1 pass; L2, L3, L4 fail
    passed_layers = [layer.passed for layer in r.layers]
    assert passed_layers == [True, True, False, False, False]
    assert r.failed_at_layer == 2


def test_synthesized_layers_carry_skipped_marker_for_quality_scoring():
    """A tracker entry that failed at L1 (build) should count as a quality
    PASS because L0 was OK and L3 was skipped, not failed. Without the
    'Skipped:' marker on synth layers, scorer._count_quality_passes would
    wrongly count L3 as a real fail and under-report quality."""
    from embedeval.scorer import score

    # Build tracker where the case failed at L1
    tracker = TrackerData()
    tracker.results[MODEL] = {
        "kconfig-002": CaseResult(
            case_id="kconfig-002",
            model=MODEL,
            passed=False,
            failed_at_layer=1,  # build gate
            failed_checks=["west_build_docker"],
            case_git_hash="b" * 16,
            tested_at="2026-04-11T00:00:00+00:00",
        ),
    }

    merged = _build_comprehensive_results(
        [], tracker, MODEL, {"kconfig-002": _meta("kconfig-002")}
    )
    assert len(merged) == 1
    r = merged[0]
    # Layers after failed_at_layer=1 should have the "Skipped:" error
    assert r.layers[0].error is None  # L0 passed
    assert r.layers[1].error is None  # L1 the failing layer
    assert r.layers[3].error is not None
    assert "Skipped" in r.layers[3].error

    # End-to-end: quality pass count should include this case
    report = score(merged)
    model_score = next(ms for ms in report.models if ms.model == MODEL)
    assert model_score.passed_cases == 0  # full pass@1: still 0
    assert model_score.passed_cases_quality == 1  # quality: counts


def test_score_aggregation_matches_comprehensive_not_new_only():
    """Integration: the scorer applied to the merged list must reflect
    the full model state, not just the retested slice."""
    from embedeval.scorer import score

    new = [_result("kconfig-001", True)]  # 1 pass
    tracker = _tracker(**{
        "kconfig-001": False,  # tracker stale — will be overridden
        "kconfig-002": True,
        "kconfig-003": True,
        "kconfig-004": False,
    })
    metas = {m.id: m for m in [_meta(f"kconfig-00{i}") for i in range(1, 5)]}
    merged = _build_comprehensive_results(new, tracker, MODEL, metas)
    report = score(merged)
    # 4 cases, 3 passed (001 new-pass, 002, 003)
    model_score = next(ms for ms in report.models if ms.model == MODEL)
    assert model_score.total_cases == 4
    assert model_score.passed_cases == 3
    assert model_score.pass_at_1 == 0.75
