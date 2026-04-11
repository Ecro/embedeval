"""One-shot migration: recompute case_git_hash for private cases.

Historically, test_tracker.update_tracker() resolved every case_id
against cases_dir, which for private cases (living in
../embedeval-private/cases/) pointed to a non-existent path and wrote
the empty-content hash (01ba4719c80b6fe9...).

This script rehashes any tracker entry whose case_id resolves to a
real directory under the private cases root, restoring correct hashes
so that --retest-only stops re-flagging them as stale.

Usage:
    uv run python scripts/fix_private_case_hashes.py \\
        --results results \\
        --private ../embedeval-private/cases
"""

from __future__ import annotations

import argparse
from pathlib import Path

from embedeval.test_tracker import (
    _case_content_hash,
    load_tracker,
    save_tracker,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", default="results", type=Path)
    ap.add_argument("--private", default="../embedeval-private/cases", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    private_root: Path = args.private.resolve()
    if not private_root.is_dir():
        print(f"Private cases dir not found: {private_root}")
        return 1

    tracker = load_tracker(args.results)
    if not tracker.results:
        print("Empty tracker — nothing to do.")
        return 0

    fixed = 0
    unknown = 0
    skipped = 0
    for model, cases in tracker.results.items():
        for case_id, cr in cases.items():
            case_dir = private_root / case_id
            if not case_dir.is_dir():
                # Not a private case — leave untouched
                skipped += 1
                continue
            correct = _case_content_hash(case_dir)
            if correct == "unknown":
                unknown += 1
                continue
            if cr.case_git_hash != correct:
                print(f"  {model} {case_id}: {cr.case_git_hash[:8]} -> {correct[:8]}")
                if not args.dry_run:
                    cr.case_git_hash = correct
                fixed += 1

    print(f"Fixed: {fixed}  Unknown: {unknown}  Non-private (skipped): {skipped}")
    if args.dry_run:
        print("Dry-run — no changes saved.")
        return 0

    if fixed:
        save_tracker(tracker, args.results)
        print(f"Saved: {args.results}/test_tracker.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
