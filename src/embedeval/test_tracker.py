"""Test result tracking with git-based change detection for selective retesting."""

import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from embedeval.models import EvalResult

logger = logging.getLogger(__name__)

TRACKER_FILENAME = "test_tracker.json"


class CaseResult(BaseModel):
    """Stored result for a single test case."""

    case_id: str
    model: str
    passed: bool
    failed_at_layer: int | None = None
    failed_checks: list[str] = Field(default_factory=list)
    case_git_hash: str  # git hash of the case directory at test time
    tested_at: str  # ISO timestamp
    pass_at_1: float = 0.0  # for multi-attempt


class TrackerData(BaseModel):
    """Persistent test result tracker."""

    version: int = 1
    results: dict[str, dict[str, CaseResult]] = Field(default_factory=dict)
    # results[model][case_id] = CaseResult


def _case_content_hash(case_dir: Path) -> str:
    """Get a content-based hash for a case directory.

    Uses git ls-tree for committed state + checks for uncommitted changes.
    More reliable than commit hash alone since it catches staged/unstaged edits.
    """
    try:
        # Get tree hash for committed content
        result = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "HEAD", "--", str(case_dir)],
            capture_output=True,
            text=True,
            cwd=case_dir.parent.parent,
        )
        committed_files = result.stdout.strip() if result.returncode == 0 else ""

        # Check for any uncommitted changes in this directory
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", str(case_dir)],
            capture_output=True,
            text=True,
            cwd=case_dir.parent.parent,
        )
        uncommitted = result.stdout.strip() if result.returncode == 0 else ""

        # Build composite hash from committed tree + uncommitted indicator
        import hashlib

        content = committed_files + "\n" + uncommitted
        # Hash actual file contents (not mtime — mtime resets on clone)
        for f in sorted(case_dir.rglob("*")):
            if f.is_file() and not f.name.startswith("."):
                try:
                    fhash = hashlib.sha256(f.read_bytes()).hexdigest()[:8]
                    content += f"\n{f.relative_to(case_dir)}:{fhash}"
                except Exception:
                    pass

        return hashlib.sha256(content.encode()).hexdigest()[:16]
    except Exception:
        return "unknown"


def load_tracker(results_dir: Path) -> TrackerData:
    """Load tracker data from disk."""
    tracker_file = results_dir / TRACKER_FILENAME
    if not tracker_file.is_file():
        return TrackerData()

    try:
        data = json.loads(tracker_file.read_text(encoding="utf-8"))
        return TrackerData(**data)
    except Exception as exc:
        logger.warning("Failed to load tracker: %s", exc)
        return TrackerData()


def save_tracker(tracker: TrackerData, results_dir: Path) -> None:
    """Save tracker data to disk."""
    results_dir.mkdir(parents=True, exist_ok=True)
    tracker_file = results_dir / TRACKER_FILENAME
    tracker_file.write_text(
        json.dumps(tracker.model_dump(mode="json"), indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    logger.info("Tracker saved to %s", tracker_file)


def update_tracker(
    tracker: TrackerData,
    results: list["EvalResult"],
    cases_dir: Path,
    model: str,
    case_dir_map: dict[str, Path] | None = None,
) -> TrackerData:
    """Update tracker with new benchmark results.

    Args:
        case_dir_map: Optional mapping of case_id -> case_dir Path, required
            when cases live in multiple roots (e.g., public + private). Without
            this, private cases resolve to non-existent paths under cases_dir
            and get recorded with the empty-content hash.
    """
    if model not in tracker.results:
        tracker.results[model] = {}

    now = datetime.now(tz=timezone.utc).isoformat()

    for r in results:
        if case_dir_map and r.case_id in case_dir_map:
            case_dir = case_dir_map[r.case_id]
        else:
            case_dir = cases_dir / r.case_id

        if not case_dir.is_dir():
            logger.warning(
                "update_tracker: case dir missing for %s (%s) — hash unknown",
                r.case_id,
                case_dir,
            )
            content_hash = "unknown"
        else:
            content_hash = _case_content_hash(case_dir)

        failed_checks: list[str] = []
        for layer in r.layers:
            for d in layer.details:
                if not d.passed:
                    failed_checks.append(d.check_name)

        tracker.results[model][r.case_id] = CaseResult(
            case_id=r.case_id,
            model=model,
            passed=r.passed,
            failed_at_layer=r.failed_at_layer,
            failed_checks=failed_checks,
            case_git_hash=content_hash,
            tested_at=now,
        )

    return tracker


def find_cases_needing_retest(
    tracker: TrackerData,
    model: str,
    cases_dir: Path,
    all_case_ids: list[str],
    case_dir_map: dict[str, Path] | None = None,
) -> list[str]:
    """Find cases that need retesting for a given model.

    A case needs retest if:
    1. It has never been tested with this model
    2. The case directory content changed since last test

    Args:
        case_dir_map: Optional mapping of case_id -> case_dir Path.
            When provided, used instead of cases_dir / case_id to
            support cases spread across multiple directories.
    """
    model_results = tracker.results.get(model, {})
    needs_retest: list[str] = []

    for case_id in all_case_ids:
        prev = model_results.get(case_id)
        if prev is None:
            # Never tested
            needs_retest.append(case_id)
            continue

        # Check if case content changed
        if case_dir_map and case_id in case_dir_map:
            case_dir = case_dir_map[case_id]
        else:
            case_dir = cases_dir / case_id
        if not case_dir.is_dir():
            continue  # Case deleted — skip
        current_hash = _case_content_hash(case_dir)
        if current_hash != prev.case_git_hash:
            logger.info(
                "Case %s changed: %s -> %s",
                case_id,
                prev.case_git_hash[:8],
                current_hash[:8],
            )
            needs_retest.append(case_id)

    return needs_retest


def mark_cases_changed(
    tracker: TrackerData,
    changed_case_ids: list[str],
    cases_dir: Path,
) -> int:
    """Mark specific cases as changed (needs retest) across all models.

    Called from /wrapup when cases/ files are modified.
    Updates the stored hash to a sentinel so --retest-only picks them up.

    Returns the number of case/model pairs invalidated.
    """
    count = 0
    for model, cases in tracker.results.items():
        for case_id in changed_case_ids:
            if case_id in cases:
                new_hash = _case_content_hash(cases_dir / case_id)
                old_hash = cases[case_id].case_git_hash
                if new_hash != old_hash:
                    cases[case_id].case_git_hash = "changed"
                    count += 1
                    logger.info(
                        "Marked %s as needs-retest for %s",
                        case_id,
                        model,
                    )
    return count


def detect_changed_cases_from_git(cases_dir: Path) -> list[str]:
    """Detect which cases changed in the most recent commit.

    Used by /wrapup to find cases/ changes after committing.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "--", str(cases_dir)],
            capture_output=True,
            text=True,
            cwd=cases_dir.parent,
        )
        if result.returncode != 0:
            return []

        changed_ids: set[str] = set()
        for line in result.stdout.strip().splitlines():
            # e.g., "cases/kconfig-001/checks/static.py"
            parts = Path(line).parts
            if len(parts) >= 2 and parts[0] == cases_dir.name:
                changed_ids.add(parts[1])
        return sorted(changed_ids)
    except Exception:
        return []


def generate_results_doc(
    tracker: TrackerData,
    output: Path,
    cases_dir: Path | None = None,
    case_dir_map: dict[str, Path] | None = None,
) -> None:
    """Generate a Markdown test results document from tracker data.

    If cases_dir is provided, checks content hashes to show
    which cases need retesting (TC changed since last test).

    case_dir_map: Optional per-case_id path override for cases living
        outside cases_dir (e.g., private cases). When provided, takes
        precedence over cases_dir / case_id.
    """
    lines: list[str] = [
        "# EmbedEval Test Results",
        "",
        f"*Last updated: "
        f"{datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
    ]

    if not tracker.results:
        lines.append("No test results recorded yet.")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    # Build change map: model -> set of case_ids needing retest
    needs_retest: dict[str, set[str]] = {}
    if cases_dir:
        for model, cases in tracker.results.items():
            stale = set()
            for case_id, cr in cases.items():
                if case_dir_map and case_id in case_dir_map:
                    case_path = case_dir_map[case_id]
                else:
                    case_path = cases_dir / case_id
                if not case_path.is_dir():
                    continue
                current = _case_content_hash(case_path)
                if current != cr.case_git_hash:
                    stale.add(case_id)
            needs_retest[model] = stale

    # Summary per model
    total_stale = sum(len(s) for s in needs_retest.values())
    lines.append("## Summary")
    lines.append("")

    if total_stale > 0:
        lines.append(
            f"> **{total_stale} case(s) need retesting** "
            f"— run `/test <model> --retest-only`"
        )
        lines.append("")

    hdr = "| Model | Cases | Passed | Failed | pass@1 |"
    sep = "|-------|-------|--------|--------|--------|"
    if cases_dir:
        hdr += " Retest |"
        sep += "--------|"
    lines.append(hdr)
    lines.append(sep)

    for model, cases in sorted(tracker.results.items()):
        total = len(cases)
        passed = sum(1 for c in cases.values() if c.passed)
        failed = total - passed
        rate = passed / total if total > 0 else 0.0
        row = f"| {model} | {total} | {passed} | {failed} | {rate:.1%} |"
        if cases_dir:
            n = len(needs_retest.get(model, set()))
            row += f" {n} |" if n > 0 else " - |"
        lines.append(row)

    lines.append("")

    # Per-model detail tables
    for model, cases in sorted(tracker.results.items()):
        model_stale = needs_retest.get(model, set())
        lines.append(f"## {model}")
        lines.append("")

        # Show retest-needed cases prominently
        if model_stale:
            lines.append(f"### Needs Retest ({len(model_stale)})")
            lines.append("")
            for cid in sorted(model_stale):
                prev = cases.get(cid)
                if prev:
                    status = "PASS" if prev.passed else "FAIL"
                    lines.append(
                        f"- **{cid}** (was {status}, tested {prev.tested_at[:10]})"
                    )
                else:
                    lines.append(f"- **{cid}** (never tested)")
            lines.append("")

        # Group by category
        by_category: dict[str, list[CaseResult]] = {}
        for cr in sorted(cases.values(), key=lambda x: x.case_id):
            parts = cr.case_id.rsplit("-", 1)
            cat = parts[0] if len(parts) == 2 and parts[1].isdigit() else cr.case_id
            by_category.setdefault(cat, []).append(cr)

        lines.append("| Category | Cases | Passed | pass@1 | Failed Checks |")
        lines.append("|----------|-------|--------|--------|---------------|")

        for cat, cat_cases in sorted(by_category.items()):
            total = len(cat_cases)
            passed = sum(1 for c in cat_cases if c.passed)
            rate = passed / total if total > 0 else 0.0
            all_failed = []
            for c in cat_cases:
                if not c.passed:
                    all_failed.extend(c.failed_checks[:3])
            failed_str = ", ".join(all_failed[:5]) if all_failed else "-"
            if len(all_failed) > 5:
                failed_str += f" (+{len(all_failed) - 5})"
            lines.append(f"| {cat} | {total} | {passed} | {rate:.0%} | {failed_str} |")

        lines.append("")

        # Failed cases detail
        failed_cases = [c for c in cases.values() if not c.passed]
        if failed_cases:
            lines.append(f"### Failed Cases ({len(failed_cases)})")
            lines.append("")
            hdr = "| Case | Layer | Failed Checks | Tested |"
            sep = "|------|-------|---------------|--------|"
            if model_stale:
                hdr += " Status |"
                sep += "--------|"
            lines.append(hdr)
            lines.append(sep)
            for c in sorted(failed_cases, key=lambda x: x.case_id):
                layer_str = (
                    f"L{c.failed_at_layer}" if c.failed_at_layer is not None else "?"
                )
                checks = ", ".join(c.failed_checks[:4])
                if len(c.failed_checks) > 4:
                    checks += f" (+{len(c.failed_checks) - 4})"
                tested = c.tested_at[:10] if c.tested_at else "?"
                row = f"| {c.case_id} | {layer_str} | {checks} | {tested} |"
                if model_stale:
                    if c.case_id in model_stale:
                        row += " RETEST |"
                    else:
                        row += " - |"
                lines.append(row)
            lines.append("")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Test results doc written to %s", output)
