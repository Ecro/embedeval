"""Tests for scripts/sync_negatives_progress.py reconciliation logic.

Validates the core merge rules:
- new TCs are added
- pre-existing negatives.py is auto-promoted
- removed negatives.py is flagged as regression
- removed case dirs are marked orphaned
- existing state is preserved when no transition applies
"""

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "sync_negatives_progress",
    REPO_ROOT / "scripts" / "sync_negatives_progress.py",
)
assert _SPEC is not None and _SPEC.loader is not None
sync_mod = importlib.util.module_from_spec(_SPEC)
sys.modules["sync_negatives_progress"] = sync_mod
_SPEC.loader.exec_module(sync_mod)


def _make_case(root: Path, case_id: str, *, with_negatives: bool) -> None:
    checks = root / case_id / "checks"
    checks.mkdir(parents=True)
    (checks / "static.py").write_text("")
    if with_negatives:
        (checks / "negatives.py").write_text("NEGATIVES = []\n")


def test_new_tc_added_as_pending(tmp_path: Path) -> None:
    cases = tmp_path / "cases"
    cases.mkdir()
    _make_case(cases, "dma-099", with_negatives=False)
    progress = tmp_path / "progress.json"

    data, stats = sync_mod.reconcile(cases, progress)

    assert "dma-099" in stats.added_new
    entry = next(c for c in data["cases"] if c["case_id"] == "dma-099")
    assert entry["status"] == "pending"
    assert entry["category"] == "dma"
    assert entry["priority"] == 1  # dma is priority 1


def test_new_tc_with_existing_negatives_becomes_done(tmp_path: Path) -> None:
    cases = tmp_path / "cases"
    cases.mkdir()
    _make_case(cases, "dma-100", with_negatives=True)
    progress = tmp_path / "progress.json"

    data, stats = sync_mod.reconcile(cases, progress)

    assert "dma-100" in stats.added_new
    entry = next(c for c in data["cases"] if c["case_id"] == "dma-100")
    assert entry["status"] == "done"
    assert entry["completed_at"] is not None


def test_pending_tc_auto_promoted_when_negatives_added(tmp_path: Path) -> None:
    cases = tmp_path / "cases"
    cases.mkdir()
    _make_case(cases, "dma-101", with_negatives=True)
    progress = tmp_path / "progress.json"
    # Seed progress file showing pending status
    progress.write_text(
        json.dumps(
            {
                "version": 1,
                "generated": "2026-04-19",
                "cases": [
                    {
                        "case_id": "dma-101",
                        "category": "dma",
                        "priority": 1,
                        "status": "pending",
                        "started_at": None,
                        "completed_at": None,
                        "notes": None,
                    }
                ],
            }
        )
    )

    data, stats = sync_mod.reconcile(cases, progress)

    assert "dma-101" in stats.auto_promoted
    entry = next(c for c in data["cases"] if c["case_id"] == "dma-101")
    assert entry["status"] == "done"
    assert "auto-promoted" in entry["notes"]


def test_regression_when_negatives_removed(tmp_path: Path) -> None:
    cases = tmp_path / "cases"
    cases.mkdir()
    _make_case(cases, "dma-102", with_negatives=False)
    progress = tmp_path / "progress.json"
    progress.write_text(
        json.dumps(
            {
                "version": 1,
                "generated": "2026-04-01",
                "cases": [
                    {
                        "case_id": "dma-102",
                        "category": "dma",
                        "priority": 1,
                        "status": "done",
                        "started_at": None,
                        "completed_at": "2026-04-01",
                        "notes": None,
                    }
                ],
            }
        )
    )

    data, stats = sync_mod.reconcile(cases, progress)

    assert "dma-102" in stats.regressed
    entry = next(c for c in data["cases"] if c["case_id"] == "dma-102")
    assert entry["status"] == "pending"
    assert entry["completed_at"] is None
    assert "regression" in entry["notes"]


def test_orphan_when_case_removed_from_disk(tmp_path: Path) -> None:
    cases = tmp_path / "cases"
    cases.mkdir()
    # Intentionally don't create dma-103 on disk
    progress = tmp_path / "progress.json"
    progress.write_text(
        json.dumps(
            {
                "version": 1,
                "generated": "2026-04-01",
                "cases": [
                    {
                        "case_id": "dma-103",
                        "category": "dma",
                        "priority": 1,
                        "status": "pending",
                        "started_at": None,
                        "completed_at": None,
                        "notes": None,
                    }
                ],
            }
        )
    )

    data, stats = sync_mod.reconcile(cases, progress)

    assert "dma-103" in stats.orphaned
    entry = next(c for c in data["cases"] if c["case_id"] == "dma-103")
    assert entry["status"] == "orphaned"
    assert "case dir missing" in entry["notes"]


def test_unchanged_state_preserved(tmp_path: Path) -> None:
    cases = tmp_path / "cases"
    cases.mkdir()
    _make_case(cases, "dma-104", with_negatives=True)
    progress = tmp_path / "progress.json"
    progress.write_text(
        json.dumps(
            {
                "version": 1,
                "generated": "2026-04-01",
                "cases": [
                    {
                        "case_id": "dma-104",
                        "category": "dma",
                        "priority": 1,
                        "status": "done",
                        "started_at": "2026-04-10",
                        "completed_at": "2026-04-10",
                        "notes": "hand-audited by Ecro",
                    }
                ],
            }
        )
    )

    data, stats = sync_mod.reconcile(cases, progress)

    entry = next(c for c in data["cases"] if c["case_id"] == "dma-104")
    assert entry["status"] == "done"
    assert entry["started_at"] == "2026-04-10"
    assert entry["completed_at"] == "2026-04-10"
    assert entry["notes"] == "hand-audited by Ecro"
    assert stats.unchanged == 1


def test_idempotent_second_run(tmp_path: Path) -> None:
    cases = tmp_path / "cases"
    cases.mkdir()
    _make_case(cases, "dma-105", with_negatives=False)
    _make_case(cases, "threading-099", with_negatives=True)
    progress = tmp_path / "progress.json"

    data1, _stats1 = sync_mod.reconcile(cases, progress)
    progress.write_text(json.dumps(data1))

    data2, stats2 = sync_mod.reconcile(cases, progress)

    assert stats2.added_new == []
    assert stats2.auto_promoted == []
    assert stats2.regressed == []
    assert stats2.orphaned == []


def test_case_without_static_py_excluded(tmp_path: Path) -> None:
    """Non-code cases (no static.py) are not tracked — nothing to mutate."""
    cases = tmp_path / "cases"
    cases.mkdir()
    (cases / "bogus-001" / "checks").mkdir(parents=True)
    # No static.py written
    progress = tmp_path / "progress.json"

    data, _stats = sync_mod.reconcile(cases, progress)

    ids = {c["case_id"] for c in data["cases"]}
    assert "bogus-001" not in ids


def test_priority_assigned_by_category(tmp_path: Path) -> None:
    cases = tmp_path / "cases"
    cases.mkdir()
    _make_case(cases, "dma-200", with_negatives=False)
    _make_case(cases, "isr-concurrency-200", with_negatives=False)
    _make_case(cases, "yocto-200", with_negatives=False)
    progress = tmp_path / "progress.json"

    data, _stats = sync_mod.reconcile(cases, progress)

    by_id = {c["case_id"]: c for c in data["cases"]}
    assert by_id["dma-200"]["priority"] == 1
    assert by_id["isr-concurrency-200"]["priority"] == 2
    assert by_id["yocto-200"]["priority"] == 6  # default for unlisted categories


def test_orphan_resolved_when_case_returns(tmp_path: Path) -> None:
    cases = tmp_path / "cases"
    cases.mkdir()
    _make_case(cases, "dma-300", with_negatives=False)
    progress = tmp_path / "progress.json"
    # Seed orphaned state
    progress.write_text(
        json.dumps(
            {
                "version": 1,
                "generated": "2026-04-01",
                "cases": [
                    {
                        "case_id": "dma-300",
                        "category": "dma",
                        "priority": 1,
                        "status": "orphaned",
                        "started_at": None,
                        "completed_at": None,
                        "notes": "case dir missing on disk",
                    }
                ],
            }
        )
    )

    data, _stats = sync_mod.reconcile(cases, progress)

    entry = next(c for c in data["cases"] if c["case_id"] == "dma-300")
    assert entry["status"] == "pending"  # resolved
    assert "orphan resolved" in entry["notes"]
