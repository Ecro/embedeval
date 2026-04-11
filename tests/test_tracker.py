"""Tests for test_tracker — especially the case_dir_map path resolution."""

from __future__ import annotations

from pathlib import Path

from embedeval.models import EvalResult, LayerResult, TokenUsage
from embedeval.test_tracker import (
    TrackerData,
    _case_content_hash,
    update_tracker,
)

EMPTY_CONTENT_HASH_PREFIX = "01ba4719"


def _make_result(case_id: str, passed: bool = True) -> EvalResult:
    return EvalResult(
        case_id=case_id,
        model="test-model",
        attempt=1,
        generated_code="int main(void) { return 0; }",
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
        token_usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
        cost_usd=0.0,
    )


def _make_case_dir(root: Path, case_id: str, content: str) -> Path:
    case_dir = root / case_id
    case_dir.mkdir(parents=True)
    (case_dir / "prompt.md").write_text(content)
    (case_dir / "case.yaml").write_text(f"id: {case_id}\n")
    return case_dir


def test_update_tracker_records_correct_hash_for_public_case(tmp_path: Path):
    cases_dir = tmp_path / "cases"
    cases_dir.mkdir()
    _make_case_dir(cases_dir, "pub-001", "public content")

    tracker = TrackerData()
    tracker = update_tracker(
        tracker, [_make_result("pub-001")], cases_dir, "test-model"
    )

    stored = tracker.results["test-model"]["pub-001"].case_git_hash
    assert stored != "unknown"
    assert not stored.startswith(EMPTY_CONTENT_HASH_PREFIX)


def test_update_tracker_records_unknown_without_map_for_private_case(
    tmp_path: Path,
):
    """Regression: without case_dir_map, private cases should NOT silently
    get the empty-content hash — they should be clearly marked 'unknown'."""
    cases_dir = tmp_path / "cases"
    cases_dir.mkdir()
    priv_dir = tmp_path / "private_cases"
    priv_dir.mkdir()
    _make_case_dir(priv_dir, "priv-001", "private content")

    tracker = TrackerData()
    tracker = update_tracker(
        tracker, [_make_result("priv-001")], cases_dir, "test-model"
    )

    stored = tracker.results["test-model"]["priv-001"].case_git_hash
    # Must not be the silent empty-content hash that caused the original bug
    assert not stored.startswith(EMPTY_CONTENT_HASH_PREFIX), (
        "Private case without map should not record empty-content hash — "
        "got the exact stale value that caused --retest-only churn"
    )
    assert stored == "unknown"


def test_update_tracker_uses_case_dir_map_for_private_case(tmp_path: Path):
    cases_dir = tmp_path / "cases"
    cases_dir.mkdir()
    priv_dir = tmp_path / "private_cases"
    priv_dir.mkdir()
    real_priv_dir = _make_case_dir(priv_dir, "priv-001", "private content")

    case_dir_map = {"priv-001": real_priv_dir}

    tracker = TrackerData()
    tracker = update_tracker(
        tracker,
        [_make_result("priv-001")],
        cases_dir,
        "test-model",
        case_dir_map=case_dir_map,
    )

    stored = tracker.results["test-model"]["priv-001"].case_git_hash
    assert stored != "unknown"
    assert not stored.startswith(EMPTY_CONTENT_HASH_PREFIX)
    # And matches what a direct hash of the real dir would produce
    assert stored == _case_content_hash(real_priv_dir)


def test_update_tracker_map_overrides_cases_dir_for_same_id(tmp_path: Path):
    """When a case_id exists in both cases_dir and the map, map wins."""
    cases_dir = tmp_path / "cases"
    cases_dir.mkdir()
    _make_case_dir(cases_dir, "shared-001", "content A")

    alt_root = tmp_path / "alt"
    alt_root.mkdir()
    alt_dir = _make_case_dir(alt_root, "shared-001", "content B — different")

    tracker = TrackerData()
    tracker = update_tracker(
        tracker,
        [_make_result("shared-001")],
        cases_dir,
        "test-model",
        case_dir_map={"shared-001": alt_dir},
    )
    stored = tracker.results["test-model"]["shared-001"].case_git_hash
    assert stored == _case_content_hash(alt_dir)
    assert stored != _case_content_hash(cases_dir / "shared-001")


def test_case_content_hash_is_path_representation_independent(tmp_path: Path):
    """Regression: hash must be identical for the same directory regardless
    of whether it was reached via a relative or absolute path. The earlier
    version invoked `git ls-tree` with cwd=parent.parent, which silently
    returned empty for relative paths outside that cwd's repo — producing
    different hashes and causing --retest-only to re-flag every private
    case on every run."""
    import os

    case_dir = _make_case_dir(tmp_path / "cases", "case-001", "content")

    abs_hash = _case_content_hash(case_dir.resolve())

    old_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        rel_hash = _case_content_hash(Path("cases/case-001"))
    finally:
        os.chdir(old_cwd)

    assert abs_hash == rel_hash
    assert abs_hash != "unknown"


def test_case_content_hash_changes_when_file_content_changes(tmp_path: Path):
    case_dir = _make_case_dir(tmp_path / "cases", "case-001", "version 1")
    h1 = _case_content_hash(case_dir)

    (case_dir / "prompt.md").write_text("version 2 — different")
    h2 = _case_content_hash(case_dir)

    assert h1 != h2


def test_case_content_hash_ignores_pycache(tmp_path: Path):
    """__pycache__ and dotfiles shouldn't affect the semantic hash."""
    case_dir = _make_case_dir(tmp_path / "cases", "case-001", "content")
    h_before = _case_content_hash(case_dir)

    pycache = case_dir / "__pycache__"
    pycache.mkdir()
    (pycache / "checks.cpython-312.pyc").write_bytes(b"\x00\x01\x02")
    (case_dir / ".DS_Store").write_bytes(b"junk")

    h_after = _case_content_hash(case_dir)
    assert h_before == h_after


def test_update_tracker_mixed_public_and_private(tmp_path: Path):
    """Both a public case and a private case in one update call get
    non-empty, distinct hashes."""
    cases_dir = tmp_path / "cases"
    cases_dir.mkdir()
    pub_dir = _make_case_dir(cases_dir, "pub-001", "public")

    priv_root = tmp_path / "private_cases"
    priv_root.mkdir()
    priv_dir = _make_case_dir(priv_root, "priv-001", "private")

    tracker = TrackerData()
    tracker = update_tracker(
        tracker,
        [_make_result("pub-001"), _make_result("priv-001")],
        cases_dir,
        "test-model",
        case_dir_map={"pub-001": pub_dir, "priv-001": priv_dir},
    )

    pub_hash = tracker.results["test-model"]["pub-001"].case_git_hash
    priv_hash = tracker.results["test-model"]["priv-001"].case_git_hash
    assert pub_hash != priv_hash
    for h in (pub_hash, priv_hash):
        assert h != "unknown"
        assert not h.startswith(EMPTY_CONTENT_HASH_PREFIX)
