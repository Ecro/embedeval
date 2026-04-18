#!/usr/bin/env python3
"""Reconcile plans/negatives-progress.json with live cases/ directory.

Runs at the start of every /negatives command invocation. Additive:
- New TCs on disk → added as 'pending' (or 'done' if negatives.py already exists)
- TC gained negatives.py while status was pending/in-progress → auto-promoted to 'done'
- TC lost negatives.py while status was 'done' → demoted to 'pending' + note
- TC removed from disk → marked 'orphaned' (file entry kept)

Existing status, notes, timestamps are preserved when no state change applies.

Safe to re-run. Idempotent on a stable cases/ directory.

Usage:
    uv run python scripts/sync_negatives_progress.py
    uv run python scripts/sync_negatives_progress.py --quiet
    uv run python scripts/sync_negatives_progress.py --json-only  # skip human output
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

# Priority by category — weakest Haiku categories first (from PLAN).
# New categories not listed default to priority 6 (last).
_PRIORITY: dict[str, int] = {
    "dma": 1,
    "isr-concurrency": 2,
    "threading": 3,
    "memory-opt": 4,
    # priority 5 reserved for "subtle/second-pass" follow-ups
    # all others default to 6 via _category_priority()
}


def _category_of(case_id: str) -> str:
    """Infer category from case_id by stripping trailing -NNN suffix."""
    parts = case_id.rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0]
    return case_id


def _category_priority(category: str) -> int:
    return _PRIORITY.get(category, 6)


@dataclass
class SyncStats:
    added_new: list[str] = field(default_factory=list)
    auto_promoted: list[str] = field(default_factory=list)
    regressed: list[str] = field(default_factory=list)
    orphaned: list[str] = field(default_factory=list)
    unchanged: int = 0


def _load_progress(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "version": 1,
            "generated": str(date.today()),
            "cases": [],
        }
    try:
        data: dict[str, Any] = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: progress file corrupt: {path}: {exc}")
    return data


def _scan_cases(cases_root: Path) -> dict[str, dict[str, bool]]:
    """Return {case_id: {'has_static': bool, 'has_negatives': bool}}."""
    out: dict[str, dict[str, bool]] = {}
    for case_dir in sorted(cases_root.iterdir()):
        if not case_dir.is_dir():
            continue
        checks = case_dir / "checks"
        if not checks.is_dir():
            continue
        out[case_dir.name] = {
            "has_static": (checks / "static.py").is_file(),
            "has_negatives": (checks / "negatives.py").is_file(),
        }
    return out


def reconcile(
    cases_root: Path,
    progress_path: Path,
) -> tuple[dict[str, Any], SyncStats]:
    data = _load_progress(progress_path)
    disk = _scan_cases(cases_root)
    stats = SyncStats()

    # Index existing entries by case_id for fast lookup
    existing: dict[str, dict[str, Any]] = {
        entry["case_id"]: entry for entry in data.get("cases", [])
    }

    merged: list[dict[str, Any]] = []

    # Pass 1: cases present on disk
    for case_id, flags in disk.items():
        if not flags["has_static"]:
            # Case dir exists but no static.py → not in scope for negatives oracle.
            # Skip silently — don't clutter progress file.
            continue

        category = _category_of(case_id)
        priority = _category_priority(category)

        if case_id in existing:
            entry = existing[case_id]
            # Preserve priority only if still matches heuristic; otherwise update
            # (supports future re-prioritization by editing _PRIORITY dict).
            entry["priority"] = priority
            entry["category"] = category

            # State transitions
            old_status = entry.get("status", "pending")
            if flags["has_negatives"] and old_status in ("pending", "in-progress"):
                entry["status"] = "done"
                entry["completed_at"] = entry.get("completed_at") or str(date.today())
                note = entry.get("notes") or ""
                entry["notes"] = (
                    note + " | auto-promoted: negatives.py authored outside command"
                ).strip(" |")
                stats.auto_promoted.append(case_id)
            elif not flags["has_negatives"] and old_status == "done":
                entry["status"] = "pending"
                entry["completed_at"] = None
                note = entry.get("notes") or ""
                entry["notes"] = (
                    note + " | regression: negatives.py removed"
                ).strip(" |")
                stats.regressed.append(case_id)
            elif entry.get("status") == "orphaned":
                # Case came back — demote orphaned to pending (or done if neg exists)
                entry["status"] = "done" if flags["has_negatives"] else "pending"
                note = entry.get("notes") or ""
                entry["notes"] = (note + " | orphan resolved").strip(" |")
                stats.added_new.append(case_id)  # treat as re-discovered
            else:
                stats.unchanged += 1

            merged.append(entry)
        else:
            # New TC — not previously tracked
            status = "done" if flags["has_negatives"] else "pending"
            merged.append(
                {
                    "case_id": case_id,
                    "category": category,
                    "priority": priority,
                    "status": status,
                    "started_at": None,
                    "completed_at": (
                        str(date.today()) if flags["has_negatives"] else None
                    ),
                    "notes": (
                        "pre-existing negatives.py discovered on first sync"
                        if flags["has_negatives"]
                        else None
                    ),
                }
            )
            stats.added_new.append(case_id)

    # Pass 2: entries in progress file but not on disk → orphaned
    for case_id, entry in existing.items():
        if case_id in disk:
            continue
        if entry.get("status") != "orphaned":
            entry["status"] = "orphaned"
            note = entry.get("notes") or ""
            entry["notes"] = (note + " | case dir missing on disk").strip(" |")
            stats.orphaned.append(case_id)
        merged.append(entry)

    # Stable sort: priority asc, then case_id asc
    merged.sort(key=lambda e: (e.get("priority", 99), e["case_id"]))
    data["cases"] = merged
    data["generated"] = str(date.today())
    data["version"] = data.get("version", 1)
    return data, stats


def _print_summary(data: dict[str, Any], stats: SyncStats) -> None:
    cases = data.get("cases", [])
    by_status: dict[str, int] = {}
    for c in cases:
        by_status[c["status"]] = by_status.get(c["status"], 0) + 1

    print("📊 Progress sync — cases/ vs progress file")
    if stats.added_new:
        shown = ", ".join(stats.added_new[:5])
        extra = len(stats.added_new) - 5
        more = f" (+{extra} more)" if extra > 0 else ""
        print(f"  + {len(stats.added_new)} new TCs added: {shown}{more}")
    if stats.auto_promoted:
        shown = ", ".join(stats.auto_promoted[:5])
        print(f"  ✓ {len(stats.auto_promoted)} auto-promoted to done: {shown}")
    if stats.regressed:
        shown = ", ".join(stats.regressed[:5])
        print(f"  ⚠ {len(stats.regressed)} regressions: {shown}")
    if stats.orphaned:
        shown = ", ".join(stats.orphaned[:5])
        print(f"  ⚠ {len(stats.orphaned)} orphaned: {shown}")
    if not (
        stats.added_new or stats.auto_promoted or stats.regressed or stats.orphaned
    ):
        print(f"  (no changes; {stats.unchanged} entries reconciled)")

    total = len(cases)
    parts = [f"{k}={v}" for k, v in sorted(by_status.items())]
    print(f"\nTotals: {total} cases — {' / '.join(parts)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="cases", help="cases root directory")
    parser.add_argument(
        "--progress",
        default="plans/negatives-progress.json",
        help="progress JSON path",
    )
    parser.add_argument("--quiet", action="store_true", help="suppress human summary")
    parser.add_argument(
        "--json-only", action="store_true", help="print JSON summary to stdout"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="do not write file; print what would change",
    )
    args = parser.parse_args()

    cases_root = Path(args.cases).resolve()
    if not cases_root.is_dir():
        print(f"ERROR: cases dir not found: {cases_root}", file=sys.stderr)
        return 2

    progress_path = Path(args.progress).resolve()
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    data, stats = reconcile(cases_root, progress_path)

    if not args.dry_run:
        progress_path.write_text(json.dumps(data, indent=2) + "\n")

    if args.json_only:
        print(
            json.dumps(
                {
                    "added_new": stats.added_new,
                    "auto_promoted": stats.auto_promoted,
                    "regressed": stats.regressed,
                    "orphaned": stats.orphaned,
                    "unchanged": stats.unchanged,
                    "totals": {
                        s: sum(1 for c in data["cases"] if c["status"] == s)
                        for s in {c["status"] for c in data["cases"]}
                    },
                },
                indent=2,
            )
        )
    elif not args.quiet:
        _print_summary(data, stats)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
