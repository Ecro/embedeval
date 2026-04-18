"""Tests for src/embedeval/context_diagnose.py.

Uses synthetic TrackerData + known FAILURE-FACTORS.md mapping so the
assertions don't drift when cases/ is edited.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pytest

from embedeval.context_diagnose import (
    CoverageDiagnosis,
    diagnose_coverage,
    format_diagnosis,
)
from embedeval.failure_factors import load_check_category_map
from embedeval.test_tracker import CaseResult, TrackerData, save_tracker


def _mapped_count(letter: str) -> int:
    """Count of checks mapped to a category letter in the live doc.
    Computed per-test so assertions don't hard-code values that drift
    when FAILURE-FACTORS.md is edited."""
    mapping = load_check_category_map()
    return sum(1 for cat in mapping.values() if cat == letter)


def _tracker(
    model: str,
    cases: dict[str, tuple[bool, list[str]]],
    pack_hash: str | None = None,
) -> TrackerData:
    """Build a tracker. cases = {case_id: (passed, failed_checks)}."""
    now = datetime.now(tz=timezone.utc).isoformat()
    tr = TrackerData()
    tr.context_pack_hash = pack_hash
    tr.results[model] = {
        cid: CaseResult(
            case_id=cid,
            model=model,
            passed=passed,
            failed_at_layer=None if passed else 0,
            failed_checks=checks,
            case_git_hash="x",
            tested_at=now,
        )
        for cid, (passed, checks) in cases.items()
    }
    return tr


def _seed(tmp_path: Path, name: str, tracker: TrackerData) -> Path:
    d = tmp_path / name
    d.mkdir()
    save_tracker(tracker, d)
    return d


# ---------------------------------------------------------------------------
# Mapping-derived fixtures — use real D-category checks so the rollup
# actually validates the parser integration, not just a mock dict.
# ---------------------------------------------------------------------------

# D-category checks (all from FAILURE-FACTORS.md line 195)
D_CHECKS = [
    "volatile_error_flag",
    "memory_barrier_present",
    "no_forbidden_apis_in_isr",
    "shared_variable_declared",
    "cache_flush_present",
]
# E-category checks
E_CHECKS = [
    "init_error_path_cleanup",
    "return_values_checked",
    "rollback_on_error",
]


def test_diagnose_flags_category_above_threshold(tmp_path: Path) -> None:
    """Team fails every D check in every case; expert fails none.
    The gap must be large enough to trip the default threshold and
    carry the D-category factor IDs."""
    team = _tracker(
        "haiku",
        {
            "threading-001": (False, list(D_CHECKS)),
            "threading-002": (False, list(D_CHECKS)),
        },
        pack_hash="team_hash_aaaaaaaaaaaa",
    )
    expert = _tracker(
        "haiku",
        {
            "threading-001": (True, []),
            "threading-002": (True, []),
        },
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)

    diag = diagnose_coverage(team_dir=team_dir, expert_dir=expert_dir)
    d = next(c for c in diag.per_category if c.category == "D")

    # Denominator is derived from the mapping (D checks × n_cases), so
    # the rate is (failed_check occurrences) / (mapped_checks × n_cases).
    # Compute the expected rate from the live mapping to stay resilient
    # to FAILURE-FACTORS.md edits.
    n_cases = 2
    d_checks_in_map = _mapped_count("D")
    # D_CHECKS are all mapped to D (verified in test_failure_factors.py).
    expected_team_rate = (len(D_CHECKS) * n_cases) / (d_checks_in_map * n_cases)
    assert d.team_failure_rate == pytest.approx(expected_team_rate)
    assert d.expert_failure_rate == pytest.approx(0.0)
    assert d.gap == pytest.approx(expected_team_rate)
    # 5 out of 24 D checks fail per case = ~21% — above the default 10pp.
    assert d.needs_coverage is True
    # High-strength factor IDs must land in the output as the pointer
    # the user acts on. D1/D2/D4/D5 are all High in the live doc.
    assert {"D1", "D2", "D4", "D5"} <= set(d.high_strength_factors)
    assert set(d.team_failed_checks) == set(D_CHECKS)


def test_diagnose_does_not_flag_category_below_threshold(
    tmp_path: Path,
) -> None:
    """5pp gap < 10pp default threshold → needs_coverage=False."""
    # 10 cases, same D-check fails in 1 team case and 0 expert cases
    # → approx 10pp at a single-check denominator.
    cases_all_pass = {f"threading-{i:03d}": (True, []) for i in range(1, 11)}
    team_cases = dict(cases_all_pass)
    team_cases["threading-001"] = (False, ["volatile_error_flag"])

    team = _tracker("haiku", team_cases, pack_hash="team_hash_aaaaaaaaaaaa")
    expert = _tracker("haiku", cases_all_pass, pack_hash="expert_hash_bbbbbbbbbbbb")
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)

    # Threshold 50pp keeps this small gap below the line.
    diag = diagnose_coverage(
        team_dir=team_dir, expert_dir=expert_dir, gap_threshold_pp=50.0
    )
    d = next((c for c in diag.per_category if c.category == "D"), None)
    assert d is not None
    assert d.needs_coverage is False


def test_diagnose_negative_gap_is_not_flagged(tmp_path: Path) -> None:
    """Team better than expert → gap is negative, never flagged."""
    team = _tracker(
        "haiku",
        {"threading-001": (True, [])},
        pack_hash="team_hash_aaaaaaaaaaaa",
    )
    expert = _tracker(
        "haiku",
        {"threading-001": (False, ["volatile_error_flag"])},
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)

    diag = diagnose_coverage(team_dir=team_dir, expert_dir=expert_dir)
    d = next(c for c in diag.per_category if c.category == "D")
    assert d.gap < 0
    assert d.needs_coverage is False


def test_diagnose_returns_high_strength_factors_per_flagged_category(
    tmp_path: Path,
) -> None:
    """Flagged D gets D's High-strength factor IDs from the live doc."""
    team = _tracker(
        "haiku",
        {
            "threading-001": (False, ["volatile_error_flag"]),
        },
        pack_hash="team_hash_aaaaaaaaaaaa",
    )
    expert = _tracker(
        "haiku",
        {
            "threading-001": (True, []),
        },
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)

    diag = diagnose_coverage(team_dir=team_dir, expert_dir=expert_dir)
    d = next(c for c in diag.per_category if c.category == "D")
    # Every ID must be D-prefixed (no cross-category leakage)
    for fid in d.high_strength_factors:
        assert fid.startswith("D"), fid
    assert d.factor_names  # non-empty
    # Factor names are the human-readable labels, not check tokens
    for fid, name in d.factor_names.items():
        assert fid.startswith("D")
        assert name  # non-empty string


def test_diagnose_unmapped_check_logs_warning_not_crash(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """New checks added to case suites before FAILURE-FACTORS.md gets
    updated must not crash diagnosis — warn and continue."""
    team = _tracker(
        "haiku",
        {
            "threading-001": (
                False,
                ["nonexistent_brand_new_check_xyz", "volatile_error_flag"],
            ),
        },
        pack_hash="team_hash_aaaaaaaaaaaa",
    )
    expert = _tracker(
        "haiku",
        {"threading-001": (True, [])},
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)

    with caplog.at_level(logging.WARNING, logger="embedeval.context_diagnose"):
        diag = diagnose_coverage(team_dir=team_dir, expert_dir=expert_dir)

    assert "nonexistent_brand_new_check_xyz" in diag.unmapped_checks
    # The mapped check still rolled up into D
    d = next(c for c in diag.per_category if c.category == "D")
    assert "volatile_error_flag" in d.team_failed_checks
    # Warning was logged
    assert any("Unmapped checks" in rec.getMessage() for rec in caplog.records)


def test_diagnose_json_export_has_full_schema(tmp_path: Path) -> None:
    """Round-trip via model_dump_json — every declared field present."""
    team = _tracker(
        "haiku",
        {"threading-001": (False, ["volatile_error_flag"])},
        pack_hash="team_hash_aaaaaaaaaaaa",
    )
    expert = _tracker(
        "haiku",
        {"threading-001": (True, [])},
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)

    diag = diagnose_coverage(team_dir=team_dir, expert_dir=expert_dir)
    payload = json.loads(diag.model_dump_json())

    assert set(payload.keys()) >= {
        "model",
        "gap_threshold",
        "per_category",
        "unmapped_checks",
    }
    assert payload["model"] == "haiku"
    assert payload["gap_threshold"] == pytest.approx(0.10)
    for cd in payload["per_category"]:
        assert {
            "category",
            "category_title",
            "team_failed_checks",
            "expert_failed_checks",
            "team_failed_occurrences",
            "expert_failed_occurrences",
            "total_check_occurrences",
            "team_failure_rate",
            "expert_failure_rate",
            "gap",
            "needs_coverage",
            "high_strength_factors",
            "factor_names",
        } <= set(cd.keys())


def test_diagnose_sorts_by_gap_descending(tmp_path: Path) -> None:
    """Largest gap first so the worst offender is obvious."""
    # D and E both get failures in team; D gets more → higher gap.
    team = _tracker(
        "haiku",
        {
            "c-001": (
                False,
                ["volatile_error_flag", "memory_barrier_present"],
            ),
            "c-002": (False, ["init_error_path_cleanup"]),
        },
        pack_hash="team_hash_aaaaaaaaaaaa",
    )
    expert = _tracker(
        "haiku",
        {
            "c-001": (True, []),
            "c-002": (True, []),
        },
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)
    diag = diagnose_coverage(team_dir=team_dir, expert_dir=expert_dir)
    gaps = [c.gap for c in diag.per_category]
    assert gaps == sorted(gaps, reverse=True), gaps


def test_diagnose_threshold_boundary_is_exclusive(tmp_path: Path) -> None:
    """Bracket the boundary: gap is flagged when threshold < gap and
    NOT flagged when threshold >= gap. The strict-greater semantics
    make the equal case fall on the "not flagged" side."""
    team = _tracker(
        "haiku",
        {"threading-001": (False, ["volatile_error_flag"])},
        pack_hash="team_hash_aaaaaaaaaaaa",
    )
    expert = _tracker(
        "haiku",
        {"threading-001": (True, [])},
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)

    d_count = _mapped_count("D")
    gap_pp = (1 / d_count) * 100.0  # 1 failure out of d_count possible

    # Strictly BELOW gap → flagged.
    diag_below = diagnose_coverage(
        team_dir=team_dir,
        expert_dir=expert_dir,
        gap_threshold_pp=gap_pp - 0.1,
    )
    d = next(c for c in diag_below.per_category if c.category == "D")
    assert d.needs_coverage is True

    # Strictly ABOVE gap → not flagged.
    diag_above = diagnose_coverage(
        team_dir=team_dir,
        expert_dir=expert_dir,
        gap_threshold_pp=gap_pp + 0.1,
    )
    d = next(c for c in diag_above.per_category if c.category == "D")
    assert d.needs_coverage is False


def test_diagnose_empty_team_raises(tmp_path: Path) -> None:
    """Empty team tracker must raise cleanly with a useful message."""
    team_dir = _seed(tmp_path, "team", TrackerData())
    expert = _tracker(
        "haiku",
        {"threading-001": (True, [])},
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    expert_dir = _seed(tmp_path, "expert", expert)
    with pytest.raises(ValueError, match="team dir"):
        diagnose_coverage(team_dir=team_dir, expert_dir=expert_dir)


def test_diagnose_requires_shared_model(tmp_path: Path) -> None:
    """No overlap between trackers' models → clean error."""
    team = _tracker(
        "haiku",
        {"threading-001": (False, ["volatile_error_flag"])},
        pack_hash="team_hash_aaaaaaaaaaaa",
    )
    expert = _tracker(
        "sonnet",
        {"threading-001": (True, [])},
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)
    with pytest.raises(ValueError, match="No model is present in both"):
        diagnose_coverage(team_dir=team_dir, expert_dir=expert_dir)


def test_format_diagnosis_flagged_category_mentions_factor_ids(
    tmp_path: Path,
) -> None:
    """Human-readable table must surface High-strength factor IDs so
    the reader can act without opening FAILURE-FACTORS.md."""
    # Saturate D failures so the gap exceeds the default 10pp threshold
    # regardless of the exact D check count.
    team = _tracker(
        "haiku",
        {
            "threading-001": (False, list(D_CHECKS)),
            "threading-002": (False, list(D_CHECKS)),
        },
        pack_hash="team_hash_aaaaaaaaaaaa",
    )
    expert = _tracker(
        "haiku",
        {
            "threading-001": (True, []),
            "threading-002": (True, []),
        },
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)
    diag = diagnose_coverage(team_dir=team_dir, expert_dir=expert_dir)
    text = format_diagnosis(diag)
    assert "D. Memory Model & Concurrency" in text
    assert "D1" in text
    # "To improve coverage:" block only when at least one is flagged
    assert "To improve coverage" in text
    # GitHub anchor must use double-dash for `&` (see _github_anchor
    # rationale — GitHub does NOT collapse consecutive hyphens).
    assert "#d-memory-model--concurrency" in text


def test_format_diagnosis_reports_no_gaps_when_none(tmp_path: Path) -> None:
    """When team == expert on all checks, the user sees a celebratory
    terminator and the table still shows every category at 0%/0%/+0pp.

    The mapping-derived denominator means per_category is NEVER empty
    when FAILURE-FACTORS.md has any mapped checks — this test pins the
    success path so we don't regress back to the circular denominator
    where all-passing categories silently vanished.
    """
    team = _tracker(
        "haiku",
        {"threading-001": (True, [])},
        pack_hash="team_hash_aaaaaaaaaaaa",
    )
    expert = _tracker(
        "haiku",
        {"threading-001": (True, [])},
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)
    diag = diagnose_coverage(team_dir=team_dir, expert_dir=expert_dir)
    text = format_diagnosis(diag)
    # All 6 A-F categories must show up — the denominator is based on
    # the mapping, not on observed failures.
    assert len(diag.per_category) == 6
    for cd in diag.per_category:
        assert cd.team_failure_rate == 0.0
        assert cd.expert_failure_rate == 0.0
        assert cd.gap == 0.0
        assert cd.needs_coverage is False
    assert "No gaps found" in text
    assert "No categories with check data" not in text


def test_github_anchor_matches_gfm_rules() -> None:
    """_github_anchor must match GitHub Flavored Markdown's slugger:
    lowercase; drop chars not in [\\w\\s-]; spaces→`-`; consecutive
    hyphens are NOT collapsed (so `&` surrounded by spaces becomes
    `--`). This is what the CLI emits in its "See docs/..." links, so
    regressions break user-clicked URLs."""
    from embedeval.context_diagnose import _github_anchor

    # Canonical GFM cases taken from the live FAILURE-FACTORS.md
    # category headings.
    assert _github_anchor("A. Hardware Awareness Gap") == "a-hardware-awareness-gap"
    assert (
        _github_anchor("D. Memory Model & Concurrency") == "d-memory-model--concurrency"
    )
    assert (
        _github_anchor("E. Error Handling & Safety Patterns")
        == "e-error-handling--safety-patterns"
    )
    # Multiple drops plus double-space remnant:
    # "F. Toolchain, SDK & Platform Knowledge"
    #  →  "f toolchain sdk  platform knowledge" (`.`, `,`, `&` stripped)
    #  →  "f-toolchain-sdk--platform-knowledge"
    assert (
        _github_anchor("F. Toolchain, SDK & Platform Knowledge")
        == "f-toolchain-sdk--platform-knowledge"
    )


def test_diagnose_raises_value_error_not_assertion_on_stale_doc(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If FAILURE-FACTORS.md is mid-edit (mapping line references a
    category letter whose section header was deleted), diagnosis must
    surface a ValueError the CLI catch path can format — not a bare
    AssertionError printing a Python traceback."""
    import embedeval.context_diagnose as cd_mod

    # Simulate: parse_factors returned only A (no D section) but the
    # mapping still has a D-letter check.
    def fake_load_factors():  # type: ignore[no-untyped-def]
        from embedeval.failure_factors import Category, Factor

        return [
            Category(
                letter="A",
                title="Hardware Awareness Gap",
                factors=(
                    Factor(
                        factor_id="A1",
                        name="Fake",
                        strength="High",
                        evidence="Empirical",
                        description="x",
                    ),
                ),
            )
        ]

    def fake_load_check_category_map():  # type: ignore[no-untyped-def]
        return {"volatile_error_flag": "D"}

    monkeypatch.setattr(cd_mod, "load_factors", fake_load_factors)
    monkeypatch.setattr(cd_mod, "load_check_category_map", fake_load_check_category_map)

    team = _tracker(
        "haiku",
        {"threading-001": (False, ["volatile_error_flag"])},
        pack_hash="team_hash_aaaaaaaaaaaa",
    )
    expert = _tracker(
        "haiku",
        {"threading-001": (True, [])},
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)

    with pytest.raises(ValueError, match="unknown category"):
        diagnose_coverage(team_dir=team_dir, expert_dir=expert_dir)


def test_diagnose_denominator_uses_mapping_not_observed_failures(
    tmp_path: Path,
) -> None:
    """Regression: the denominator must come from the FAILURE-FACTORS
    mapping, not from observed failures. If it came from failures, a
    category with zero failures in both runs would have denominator 0
    and be dropped — making the tool blind to its success stories."""
    # Team and expert both pass everything. A category that the tracker
    # never "observed" (because no failures) must still appear with a
    # non-zero denominator.
    team = _tracker(
        "haiku",
        {"c-001": (True, [])},
        pack_hash="team_hash_aaaaaaaaaaaa",
    )
    expert = _tracker(
        "haiku",
        {"c-001": (True, [])},
        pack_hash="expert_hash_bbbbbbbbbbbb",
    )
    team_dir = _seed(tmp_path, "team", team)
    expert_dir = _seed(tmp_path, "expert", expert)
    diag = diagnose_coverage(team_dir=team_dir, expert_dir=expert_dir)
    # Every A-F category that has ANY mapped check must appear with a
    # non-zero denominator.
    mapping = load_check_category_map()
    expected_letters = set(mapping.values())
    got_letters = {c.category for c in diag.per_category}
    assert expected_letters <= got_letters
    for cd in diag.per_category:
        assert cd.total_check_occurrences > 0


def test_coverage_diagnosis_schema_is_pydantic_v2() -> None:
    """Guard: model_dump_json includes every field declared on the
    BaseModel (catches a future @property that drops to plain instead
    of @computed_field — a prior bug in this codebase)."""
    cd = CoverageDiagnosis(model="haiku", gap_threshold=0.10)
    payload = json.loads(cd.model_dump_json())
    # Declared fields — if any are renamed, update this list
    assert set(payload.keys()) == {
        "model",
        "gap_threshold",
        "per_category",
        "unmapped_checks",
    }
