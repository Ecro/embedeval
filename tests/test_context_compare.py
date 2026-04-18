"""Tests for context_compare module."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from embedeval.context_compare import (
    CategoryComparison,
    compare_runs,
    format_comparison_table,
)
from embedeval.test_tracker import (
    CaseResult,
    TrackerData,
    save_tracker,
)


def _build_tracker(
    pack_hash: str | None,
    results: dict[str, dict[str, bool]],
) -> TrackerData:
    """Create a tracker. results = {model: {case_id: passed}}."""
    now = datetime.now(tz=timezone.utc).isoformat()
    tracker = TrackerData(context_pack_hash=pack_hash)
    for model, case_map in results.items():
        tracker.results[model] = {
            cid: CaseResult(
                case_id=cid,
                model=model,
                passed=passed,
                case_git_hash="x",
                tested_at=now,
            )
            for cid, passed in case_map.items()
        }
    return tracker


def _seed_dir(tmp_path: Path, name: str, tracker: TrackerData) -> Path:
    d = tmp_path / name
    d.mkdir()
    save_tracker(tracker, d)
    return d


def test_compare_basic_lift_and_gap(tmp_path: Path) -> None:
    """Bare 0/3, team 1/3, expert 3/3 → lift=33pp, gap=67pp."""
    bare = _build_tracker(
        None,
        {
            "mock": {
                "isr-concurrency-001": False,
                "isr-concurrency-002": False,
                "isr-concurrency-003": False,
            }
        },
    )
    team = _build_tracker(
        "team_pack_hash01",
        {
            "mock": {
                "isr-concurrency-001": True,
                "isr-concurrency-002": False,
                "isr-concurrency-003": False,
            }
        },
    )
    expert = _build_tracker(
        "expert_pack_hash",
        {
            "mock": {
                "isr-concurrency-001": True,
                "isr-concurrency-002": True,
                "isr-concurrency-003": True,
            }
        },
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    team_dir = _seed_dir(tmp_path, "team", team)
    expert_dir = _seed_dir(tmp_path, "expert", expert)

    report = compare_runs(
        bare_dir=bare_dir,
        expert_dir=expert_dir,
        team_dir=team_dir,
    )

    assert report.model == "mock"
    assert len(report.per_category) == 1
    cat = report.per_category[0]
    assert cat.category == "isr-concurrency"
    assert cat.bare_pass_rate == 0.0
    assert cat.team_pass_rate == pytest.approx(1 / 3)
    assert cat.expert_pass_rate == 1.0
    assert cat.lift == pytest.approx(1 / 3)
    assert cat.gap == pytest.approx(2 / 3)


def test_compare_without_team(tmp_path: Path) -> None:
    bare = _build_tracker(None, {"mock": {"dma-001": False, "dma-002": False}})
    expert = _build_tracker(
        "exp", {"mock": {"dma-001": True, "dma-002": False}}
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)

    report = compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)
    cat = report.per_category[0]
    assert cat.lift is None
    # Without team, gap anchors to bare
    assert cat.gap == pytest.approx(0.5)


def test_compare_overall_micro_average(tmp_path: Path) -> None:
    """OVERALL pass rate = passed_total / case_total (micro), not avg-of-avg."""
    bare = _build_tracker(
        None,
        {
            "mock": {
                "isr-concurrency-001": False,
                "isr-concurrency-002": False,
                "dma-001": True,
                "dma-002": True,
                "dma-003": True,
            }
        },
    )
    expert = _build_tracker(
        "exp",
        {
            "mock": {
                "isr-concurrency-001": True,
                "isr-concurrency-002": True,
                "dma-001": True,
                "dma-002": True,
                "dma-003": True,
            }
        },
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    report = compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)

    # bare: 3/5 = 60% (micro), not (0% + 100%)/2 = 50% (macro)
    assert report.overall.bare_pass_rate == pytest.approx(0.6)
    assert report.overall.expert_pass_rate == 1.0


def test_compare_unknown_model_errors(tmp_path: Path) -> None:
    bare = _build_tracker(None, {"mock": {"x-001": True}})
    expert = _build_tracker("exp", {"mock": {"x-001": True}})
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    with pytest.raises(ValueError, match="not found"):
        compare_runs(
            bare_dir=bare_dir, expert_dir=expert_dir, model="claude-sonnet"
        )


def test_compare_missing_bare_dir_errors(tmp_path: Path) -> None:
    expert = _build_tracker("exp", {"mock": {"x-001": True}})
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    bare_dir = tmp_path / "missing"
    bare_dir.mkdir()
    # Empty tracker → no results
    with pytest.raises(ValueError, match="No tracker"):
        compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)


def test_format_table_renders_lift_and_gap(tmp_path: Path) -> None:
    bare = _build_tracker(None, {"mock": {"isr-concurrency-001": False}})
    team = _build_tracker("team", {"mock": {"isr-concurrency-001": True}})
    expert = _build_tracker("exp", {"mock": {"isr-concurrency-001": True}})
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    team_dir = _seed_dir(tmp_path, "team", team)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    report = compare_runs(
        bare_dir=bare_dir, team_dir=team_dir, expert_dir=expert_dir
    )
    text = format_comparison_table(report)
    assert "isr-concurrency" in text
    assert "Lift" in text
    assert "Gap" in text
    assert "+100pp" in text  # lift = 1.0


def test_category_lift_property() -> None:
    c = CategoryComparison(
        category="x", n_cases=1, bare_pass_rate=0.2, team_pass_rate=0.5
    )
    assert c.lift == pytest.approx(0.3)
    assert c.gap is None  # no expert


def test_category_gap_falls_back_to_bare_when_no_team() -> None:
    c = CategoryComparison(
        category="x",
        n_cases=1,
        bare_pass_rate=0.4,
        team_pass_rate=None,
        expert_pass_rate=0.9,
    )
    assert c.gap == pytest.approx(0.5)


def test_json_export_includes_lift_and_gap(tmp_path: Path) -> None:
    """F1 regression: model_dump_json() must include @computed_field
    decorated lift/gap. Plain @property would silently drop them."""
    import json

    bare = _build_tracker(None, {"mock": {"x-001": False}})
    team = _build_tracker("team", {"mock": {"x-001": True}})
    expert = _build_tracker("exp", {"mock": {"x-001": True}})
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    team_dir = _seed_dir(tmp_path, "team", team)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    report = compare_runs(
        bare_dir=bare_dir, team_dir=team_dir, expert_dir=expert_dir
    )

    payload = json.loads(report.model_dump_json())
    cat = payload["per_category"][0]
    assert "lift" in cat, f"lift missing from JSON; keys={list(cat.keys())}"
    assert "gap" in cat, f"gap missing from JSON; keys={list(cat.keys())}"
    assert cat["lift"] == pytest.approx(1.0)
    assert cat["gap"] == pytest.approx(0.0)
    # Overall block too
    assert "lift" in payload["overall"]
    assert "gap" in payload["overall"]


def test_compare_warns_on_case_count_mismatch(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """F5 regression: warn when bare/expert cover different case sets."""
    bare = _build_tracker(
        None,
        {"mock": {"isr-001": True, "isr-002": True, "isr-003": False}},
    )
    expert = _build_tracker("exp", {"mock": {"isr-001": True}})
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)

    with caplog.at_level("WARNING"):
        compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)
    assert "Case count mismatch" in caplog.text
    assert "bare=3" in caplog.text and "expert=1" in caplog.text
