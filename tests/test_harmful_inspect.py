"""Tests for harmful_inspect — layer-based sub-classification."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from embedeval.harmful_inspect import (
    HarmfulClassification,
    classify_harmful,
    format_harmful_table,
    inspect_harmful,
)
from embedeval.test_tracker import (
    CaseResult,
    TrackerData,
    save_tracker,
)


def _build_tracker(
    results: dict[str, dict[str, tuple[bool, int | None, list[str]]]],
) -> TrackerData:
    """Create tracker. results = {model: {case_id: (passed, layer, checks)}}."""
    now = datetime.now(tz=timezone.utc).isoformat()
    tracker = TrackerData()
    for model, case_map in results.items():
        tracker.results[model] = {
            cid: CaseResult(
                case_id=cid,
                model=model,
                passed=passed,
                failed_at_layer=layer,
                failed_checks=checks,
                case_git_hash="x",
                tested_at=now,
            )
            for cid, (passed, layer, checks) in case_map.items()
        }
    return tracker


def _seed_dir(tmp_path: Path, name: str, tracker: TrackerData) -> Path:
    d = tmp_path / name
    d.mkdir()
    save_tracker(tracker, d)
    return d


class TestClassifyHarmful:
    def test_l0_static_is_likely_brittleness(self) -> None:
        cls, reason, hint = classify_harmful(0, ["check_dma_api"])
        assert cls == HarmfulClassification.LIKELY_BRITTLENESS
        assert "static" in reason.lower()
        assert "static.py" in hint

    def test_l1_compile_is_likely_real(self) -> None:
        cls, _, hint = classify_harmful(1, ["compile_zephyr"])
        assert cls == HarmfulClassification.LIKELY_REAL
        assert "pack" in hint.lower()

    def test_l2_runtime_is_likely_real(self) -> None:
        cls, _, _ = classify_harmful(2, ["runtime_qemu"])
        assert cls == HarmfulClassification.LIKELY_REAL

    def test_l3_behavioral_is_uncertain(self) -> None:
        cls, reason, _ = classify_harmful(3, ["check_log_pattern"])
        assert cls == HarmfulClassification.UNCERTAIN
        assert "output" in reason.lower()

    def test_l4_mutation_is_likely_real(self) -> None:
        cls, _, _ = classify_harmful(4, ["mutation_verify"])
        assert cls == HarmfulClassification.LIKELY_REAL

    def test_none_layer_is_uncertain(self) -> None:
        cls, _, _ = classify_harmful(None, [])
        assert cls == HarmfulClassification.UNCERTAIN

    def test_unknown_layer_is_uncertain(self) -> None:
        cls, reason, _ = classify_harmful(99, [])
        assert cls == HarmfulClassification.UNCERTAIN
        assert "99" in reason


def test_inspect_harmful_picks_only_bare_pass_expert_fail(
    tmp_path: Path,
) -> None:
    """Only cases where bare passed AND expert failed count as harmful.
    helpful / no-effect-* must be excluded."""
    bare = _build_tracker(
        {
            "haiku": {
                "isr-001": (True, None, []),  # harmful with expert
                "isr-002": (False, None, []),  # helpful with expert
                "isr-003": (True, None, []),  # no-effect-pass
                "isr-004": (False, None, []),  # no-effect-fail
            }
        }
    )
    expert = _build_tracker(
        {
            "haiku": {
                "isr-001": (False, 0, ["check_volatile"]),  # harmful L0
                "isr-002": (True, None, []),  # helpful
                "isr-003": (True, None, []),  # no-effect-pass
                "isr-004": (False, 0, ["x"]),  # no-effect-fail (not harmful)
            }
        }
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)

    cases = inspect_harmful(bare_dir=bare_dir, expert_dir=expert_dir)
    assert [hc.case_id for hc in cases] == ["isr-001"]
    assert cases[0].classification == HarmfulClassification.LIKELY_BRITTLENESS


def test_inspect_harmful_classifies_mixed_layer_failures(
    tmp_path: Path,
) -> None:
    """Four harmful cases across L0/L1/L2/L3 get correct classifications."""
    bare = _build_tracker(
        {
            "haiku": {
                "c-001": (True, None, []),
                "c-002": (True, None, []),
                "c-003": (True, None, []),
                "c-004": (True, None, []),
            }
        }
    )
    expert = _build_tracker(
        {
            "haiku": {
                "c-001": (False, 0, ["static_x"]),
                "c-002": (False, 1, ["compile_err"]),
                "c-003": (False, 2, ["runtime_err"]),
                "c-004": (False, 3, ["log_pattern"]),
            }
        }
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    cases = inspect_harmful(bare_dir=bare_dir, expert_dir=expert_dir)

    by_id = {hc.case_id: hc.classification for hc in cases}
    assert by_id["c-001"] == HarmfulClassification.LIKELY_BRITTLENESS
    assert by_id["c-002"] == HarmfulClassification.LIKELY_REAL
    assert by_id["c-003"] == HarmfulClassification.LIKELY_REAL
    assert by_id["c-004"] == HarmfulClassification.UNCERTAIN


def test_inspect_harmful_excludes_cases_missing_from_one_side(
    tmp_path: Path,
) -> None:
    """Mixed case sets: a case present only in bare has no expert data
    to compare against, so it can't be harmful by definition."""
    bare = _build_tracker(
        {"haiku": {"c-001": (True, None, []), "c-002": (True, None, [])}}
    )
    expert = _build_tracker({"haiku": {"c-001": (False, 0, ["x"])}})
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    cases = inspect_harmful(bare_dir=bare_dir, expert_dir=expert_dir)
    assert [hc.case_id for hc in cases] == ["c-001"]


def test_inspect_harmful_model_resolution(tmp_path: Path) -> None:
    """With multiple shared non-mock models, require --model; with one,
    auto-pick; with only mock shared, fall back to mock."""
    # Ambiguous: two non-mock models shared
    bare = _build_tracker(
        {
            "haiku": {"c-001": (True, None, [])},
            "sonnet": {"c-001": (True, None, [])},
        }
    )
    expert = _build_tracker(
        {
            "haiku": {"c-001": (False, 1, ["x"])},
            "sonnet": {"c-001": (False, 1, ["x"])},
        }
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    with pytest.raises(ValueError, match="Multiple models"):
        inspect_harmful(bare_dir=bare_dir, expert_dir=expert_dir)

    # Explicit model resolves
    cases = inspect_harmful(
        bare_dir=bare_dir, expert_dir=expert_dir, model="haiku"
    )
    assert len(cases) == 1


def test_inspect_harmful_errors_when_no_shared_model(tmp_path: Path) -> None:
    bare = _build_tracker({"haiku": {"c-001": (True, None, [])}})
    expert = _build_tracker({"sonnet": {"c-001": (False, 1, ["x"])}})
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    with pytest.raises(ValueError, match="No model is present in both"):
        inspect_harmful(bare_dir=bare_dir, expert_dir=expert_dir)


def test_format_harmful_table_empty_case(tmp_path: Path) -> None:
    """No harmful cases → friendly message, not an empty table."""
    text = format_harmful_table([])
    assert "No harmful cases" in text


def test_format_harmful_table_shows_summary_and_rows(tmp_path: Path) -> None:
    bare = _build_tracker(
        {
            "haiku": {
                "c-001": (True, None, []),
                "c-002": (True, None, []),
            }
        }
    )
    expert = _build_tracker(
        {
            "haiku": {
                "c-001": (False, 0, ["static_pattern"]),
                "c-002": (False, 1, ["compile_zephyr"]),
            }
        }
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    cases = inspect_harmful(bare_dir=bare_dir, expert_dir=expert_dir)
    text = format_harmful_table(cases)

    assert "Harmful cases: 2 total" in text
    assert "likely-brittleness: 1" in text
    assert "likely-real:        1" in text
    assert "c-001" in text and "c-002" in text
    assert "L0" in text and "L1" in text


def test_inspect_harmful_json_serializable(tmp_path: Path) -> None:
    """HarmfulCase.model_dump must serialize the enum as its string
    value (not repr), matching the CaseEffect serialization pattern."""
    import json

    bare = _build_tracker({"haiku": {"c-001": (True, None, [])}})
    expert = _build_tracker(
        {"haiku": {"c-001": (False, 0, ["static_pattern"])}}
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    cases = inspect_harmful(bare_dir=bare_dir, expert_dir=expert_dir)
    payload = json.loads(
        json.dumps([hc.model_dump(mode="json") for hc in cases])
    )
    assert payload[0]["classification"] == "likely-brittleness"
