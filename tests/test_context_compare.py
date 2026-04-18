"""Tests for context_compare module."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from embedeval.context_compare import (
    CaseEffect,
    CategoryComparison,
    PerCaseComparison,
    classify_effect,
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
    attempts: int = 1,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_usd: float = 0.0,
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
                attempts=attempts,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost_usd,
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


def test_compare_warns_when_only_mock_available(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """F6 regression: mock model is context-independent, so any compare
    that resolves to mock will report ~0 lift/gap and look like a real
    null result. Surface the meaningless comparison explicitly."""
    bare = _build_tracker(None, {"mock": {"isr-001": False}})
    expert = _build_tracker("exp", {"mock": {"isr-001": True}})
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)

    with caplog.at_level("WARNING"):
        compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)
    assert "mock" in caplog.text.lower()
    assert "meaningless" in caplog.text.lower()


# ---------------------------------------------------------------------------
# Per-case effect classification
# ---------------------------------------------------------------------------


class TestClassifyEffect:
    def test_bare_fail_packed_pass_is_helpful(self) -> None:
        assert classify_effect(False, True) == CaseEffect.HELPFUL

    def test_bare_pass_packed_fail_is_harmful(self) -> None:
        assert classify_effect(True, False) == CaseEffect.HARMFUL

    def test_both_fail_is_no_effect_fail(self) -> None:
        assert classify_effect(False, False) == CaseEffect.NO_EFFECT_FAIL

    def test_both_pass_is_no_effect_pass(self) -> None:
        assert classify_effect(True, True) == CaseEffect.NO_EFFECT_PASS


def test_case_effect_serializes_as_string_value() -> None:
    """CaseEffect(str, Enum): JSON value must be 'helpful' string, not
    0 or '<CaseEffect.HELPFUL: 'helpful'>'. model_dump_json relies on
    the str mixin."""
    import json

    pc = PerCaseComparison(
        case_id="x-001",
        category="x",
        bare_to_expert_effect=CaseEffect.HELPFUL,
    )
    payload = json.loads(pc.model_dump_json())
    assert payload["bare_to_expert_effect"] == "helpful"


def test_compare_runs_includes_per_case(tmp_path: Path) -> None:
    """compare_runs should populate per_case for every case present
    in at least one tracker."""
    bare = _build_tracker(
        None,
        {"mock": {"isr-001": False, "isr-002": True, "dma-001": False}},
    )
    expert = _build_tracker(
        "exp",
        {"mock": {"isr-001": True, "isr-002": False, "dma-001": False}},
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    report = compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)

    assert len(report.per_case) == 3
    by_id = {pc.case_id: pc for pc in report.per_case}
    assert by_id["isr-001"].bare_to_expert_effect == CaseEffect.HELPFUL
    assert by_id["isr-002"].bare_to_expert_effect == CaseEffect.HARMFUL
    assert by_id["dma-001"].bare_to_expert_effect == CaseEffect.NO_EFFECT_FAIL
    # team not provided → bare_to_team_effect stays None
    for pc in report.per_case:
        assert pc.bare_to_team_effect is None


def test_effect_counts_per_category(tmp_path: Path) -> None:
    """CategoryComparison.effect_counts aggregates bare→expert effects
    within the category, excluding cases missing on either side."""
    bare = _build_tracker(
        None,
        {
            "mock": {
                "isr-001": False,  # will be helpful
                "isr-002": True,  # will be harmful
                "isr-003": False,  # no-effect-fail
                "isr-004": True,  # no-effect-pass
            }
        },
    )
    expert = _build_tracker(
        "exp",
        {
            "mock": {
                "isr-001": True,
                "isr-002": False,
                "isr-003": False,
                "isr-004": True,
            }
        },
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    report = compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)

    isr = next(c for c in report.per_category if c.category == "isr")
    assert isr.effect_counts == {
        "helpful": 1,
        "harmful": 1,
        "no-effect-fail": 1,
        "no-effect-pass": 1,
    }
    # OVERALL mirrors per-category when only one category exists
    assert report.overall.effect_counts == isr.effect_counts


def test_per_case_handles_missing_in_one_dir(tmp_path: Path) -> None:
    """Mixed case sets: case only in bare → effect is None, and it's
    excluded from effect_counts sums (sum < n_cases is expected)."""
    bare = _build_tracker(
        None,
        {"mock": {"isr-001": False, "isr-002": False}},
    )
    expert = _build_tracker("exp", {"mock": {"isr-001": True}})
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    report = compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)

    by_id = {pc.case_id: pc for pc in report.per_case}
    assert by_id["isr-001"].bare_to_expert_effect == CaseEffect.HELPFUL
    # isr-002 has no expert data → effect is None
    assert by_id["isr-002"].expert_passed is None
    assert by_id["isr-002"].bare_to_expert_effect is None
    # effect_counts sums to 1 (isr-001 only), not n_cases=2
    isr = next(c for c in report.per_category if c.category == "isr")
    assert sum(isr.effect_counts.values()) == 1
    assert isr.effect_counts["helpful"] == 1


def test_team_effect_opt_in_default_none(tmp_path: Path) -> None:
    """D1: bare_to_team_effect stays None unless include_team_effect=True."""
    bare = _build_tracker(None, {"mock": {"x-001": False}})
    team = _build_tracker("team", {"mock": {"x-001": True}})
    expert = _build_tracker("exp", {"mock": {"x-001": True}})
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    team_dir = _seed_dir(tmp_path, "team", team)
    expert_dir = _seed_dir(tmp_path, "expert", expert)

    # Default (opt-out)
    report = compare_runs(
        bare_dir=bare_dir, team_dir=team_dir, expert_dir=expert_dir
    )
    assert report.per_case[0].bare_to_team_effect is None

    # Opt-in
    report2 = compare_runs(
        bare_dir=bare_dir,
        team_dir=team_dir,
        expert_dir=expert_dir,
        include_team_effect=True,
    )
    assert report2.per_case[0].bare_to_team_effect == CaseEffect.HELPFUL


def test_table_renders_effect_column(tmp_path: Path) -> None:
    """Table must show 'H/Hm/F/P' column header and counts in rows."""
    bare = _build_tracker(
        None,
        {"mock": {"isr-001": False, "isr-002": True}},
    )
    expert = _build_tracker(
        "exp", {"mock": {"isr-001": True, "isr-002": False}}
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    text = format_comparison_table(
        compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)
    )
    assert "H/Hm/F/P" in text  # header abbreviation
    assert "1H/1Hm/0F/0P" in text  # one helpful + one harmful case
    # Footer explanation present
    assert "helpful" in text.lower() and "harmful" in text.lower()


def test_max_attempts_surfaced_in_run_summary(tmp_path: Path) -> None:
    """D3: n>1 attempts appear in RunSummary.max_attempts and the table
    footer warns that effect is last-attempt only."""
    bare = _build_tracker(
        None, {"mock": {"x-001": False}}, attempts=3
    )
    expert = _build_tracker("exp", {"mock": {"x-001": True}}, attempts=3)
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    report = compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)

    assert all(r.max_attempts == 3 for r in report.runs)
    text = format_comparison_table(report)
    assert "attempts_max=3" in text
    assert "last-attempt" in text


def test_json_export_includes_per_case_and_effect_counts(
    tmp_path: Path,
) -> None:
    """JSON output must carry the new per_case list and per-category
    effect_counts. Backward compat: existing lift/gap keys still there."""
    import json

    bare = _build_tracker(None, {"mock": {"x-001": False, "x-002": True}})
    expert = _build_tracker(
        "exp", {"mock": {"x-001": True, "x-002": False}}
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    report = compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)

    payload = json.loads(report.model_dump_json())
    assert "per_case" in payload
    assert len(payload["per_case"]) == 2
    cat = payload["per_category"][0]
    assert "effect_counts" in cat
    assert cat["effect_counts"]["helpful"] == 1
    assert cat["effect_counts"]["harmful"] == 1
    # Backward compat
    assert "lift" in cat and "gap" in cat
    # Top-level per_case has effect string values
    assert {
        pc["bare_to_expert_effect"] for pc in payload["per_case"]
    } == {"helpful", "harmful"}


def test_compare_runs_without_team_still_has_attempts(tmp_path: Path) -> None:
    """Sanity: attempts flow from tracker → RunSummary even in a
    bare/expert-only compare (no team tracker)."""
    bare = _build_tracker(None, {"mock": {"x-001": False}}, attempts=2)
    expert = _build_tracker("exp", {"mock": {"x-001": True}})
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    report = compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)

    labels_to_attempts = {r.label: r.max_attempts for r in report.runs}
    assert labels_to_attempts == {"bare": 2, "expert": 1}


def test_compare_runs_include_team_effect_requires_team_dir(
    tmp_path: Path,
) -> None:
    """W2 regression: Python API must reject include_team_effect=True
    without team_dir (CLI already does; mirror at the library layer so
    notebook/CI callers don't silently get misleading None effects)."""
    bare = _build_tracker(None, {"mock": {"x-001": False}})
    expert = _build_tracker("exp", {"mock": {"x-001": True}})
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    with pytest.raises(ValueError, match="team_dir"):
        compare_runs(
            bare_dir=bare_dir,
            expert_dir=expert_dir,
            include_team_effect=True,
        )


def test_run_summary_sums_tokens_and_cost(tmp_path: Path) -> None:
    """RunSummary.input_tokens / output_tokens / cost_usd must equal
    the sum of CaseResult aggregates for the model in that tracker."""
    bare = _build_tracker(
        None,
        {"mock": {"x-001": False, "x-002": True}},
        input_tokens=100,
        output_tokens=200,
        cost_usd=0.001,
    )
    expert = _build_tracker(
        "exp",
        {"mock": {"x-001": True, "x-002": True}},
        input_tokens=1_000,
        output_tokens=300,
        cost_usd=0.005,
    )
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    report = compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)

    labels = {r.label: r for r in report.runs}
    # Two cases × per-case aggregate
    assert labels["bare"].input_tokens == 200
    assert labels["bare"].output_tokens == 400
    assert labels["bare"].cost_usd == pytest.approx(0.002)
    assert labels["expert"].input_tokens == 2_000
    assert labels["expert"].cost_usd == pytest.approx(0.010)


def test_table_shows_token_footer_when_nonzero(tmp_path: Path) -> None:
    """Token footer should appear only when at least one run has
    non-zero token or cost usage (suppresses noise for mock-only
    smoke tests where every run is zero)."""
    bare_zero = _build_tracker(None, {"mock": {"x-001": False}})
    expert_zero = _build_tracker("exp", {"mock": {"x-001": True}})
    zb = _seed_dir(tmp_path, "bare0", bare_zero)
    ze = _seed_dir(tmp_path, "expert0", expert_zero)
    text_zero = format_comparison_table(
        compare_runs(bare_dir=zb, expert_dir=ze)
    )
    assert "Total tokens used" not in text_zero

    bare = _build_tracker(
        None, {"mock": {"x-001": False}}, input_tokens=100
    )
    expert = _build_tracker(
        "exp",
        {"mock": {"x-001": True}},
        input_tokens=200,
        output_tokens=50,
        cost_usd=0.01,
    )
    bare_dir = _seed_dir(tmp_path, "bare1", bare)
    expert_dir = _seed_dir(tmp_path, "expert1", expert)
    text = format_comparison_table(
        compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)
    )
    assert "Total tokens used" in text
    # Cost is right-aligned in a 7-char field, so "0.01" appears padded;
    # assert on the value itself, not the full "$0.01" prefix-adjacent.
    assert "0.01" in text
    # bare had 100 input, expert had 200 → +100% input vs bare delta shown
    assert "+100% input vs bare" in text


def test_table_rows_all_have_same_width(tmp_path: Path) -> None:
    """W1 regression: data rows, header, and separator must share width
    so the effect column doesn't misalign when buckets hit 100+ cases.
    Builds a synthetic category with counts wider than 99 to exercise
    the worst-case render path (100H/100Hm/100F/100P = 20 chars)."""
    bare_cases: dict[str, bool] = {}
    expert_cases: dict[str, bool] = {}
    # 100 helpful + 100 harmful + 100 both-fail + 100 both-pass = 400
    for i in range(100):
        cid = f"isr-{i:04d}"
        bare_cases[cid] = False
        expert_cases[cid] = True  # helpful
    for i in range(100, 200):
        cid = f"isr-{i:04d}"
        bare_cases[cid] = True
        expert_cases[cid] = False  # harmful
    for i in range(200, 300):
        cid = f"isr-{i:04d}"
        bare_cases[cid] = False
        expert_cases[cid] = False  # no-effect-fail
    for i in range(300, 400):
        cid = f"isr-{i:04d}"
        bare_cases[cid] = True
        expert_cases[cid] = True  # no-effect-pass

    bare = _build_tracker(None, {"mock": bare_cases})
    expert = _build_tracker("exp", {"mock": expert_cases})
    bare_dir = _seed_dir(tmp_path, "bare", bare)
    expert_dir = _seed_dir(tmp_path, "expert", expert)
    report = compare_runs(bare_dir=bare_dir, expert_dir=expert_dir)
    text = format_comparison_table(report)

    # Extract the tabular region (lines between the two separator lines)
    lines = text.splitlines()
    seps = [i for i, ln in enumerate(lines) if ln.strip().startswith("--")]
    assert len(seps) >= 2, f"expected 2 separators, got {seps}"
    body = lines[seps[0]: seps[1] + 1]
    widths = {len(ln) for ln in body}
    assert len(widths) == 1, (
        f"column alignment broken: body line widths = {widths}\n"
        + "\n".join(body)
    )
    # Worst-case render is actually present so we know we exercised it
    assert "100H/100Hm/100F/100P" in text
