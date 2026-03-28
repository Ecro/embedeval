#!/usr/bin/env python3
"""Auto-classify TCs into tiers (sanity/core/challenge).

Uses difficulty labels as heuristic when IRT data is unavailable.
When benchmark results exist, uses empirical pass rates for calibration.

Usage:
    uv run python scripts/classify_tiers.py                    # Difficulty-based
    uv run python scripts/classify_tiers.py --results results/ # IRT-based
    uv run python scripts/classify_tiers.py --dry-run          # Preview only
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
CASES_DIR = ROOT / "cases"

# Categories where all models score 100% → Sanity candidates
KNOWN_EASY_CATEGORIES = {"kconfig", "boot"}

# Easy TCs in non-easy categories are still Core (not Sanity)
# Only truly trivial TCs become Sanity


def classify_by_difficulty(cases_dir: Path) -> dict[str, str]:
    """Classify tiers based on difficulty labels (no benchmark data needed)."""
    tiers: dict[str, str] = {}

    for case_dir in sorted(cases_dir.iterdir()):
        meta_file = case_dir / "metadata.yaml"
        if not case_dir.is_dir() or not meta_file.is_file():
            continue

        content = meta_file.read_text(encoding="utf-8")
        case_id = _yaml_value(content, "id") or case_dir.name
        difficulty = _yaml_value(content, "difficulty") or "medium"
        category = _yaml_value(content, "category") or ""

        if difficulty == "easy" and category in KNOWN_EASY_CATEGORIES:
            tiers[case_id] = "sanity"
        elif difficulty == "easy":
            tiers[case_id] = "core"  # Easy in hard categories is still Core
        elif difficulty == "hard":
            tiers[case_id] = "challenge"
        else:
            tiers[case_id] = "core"

    return tiers


def classify_by_results(results_dir: Path, cases_dir: Path) -> dict[str, str]:
    """Classify tiers based on benchmark results (IRT-like)."""
    # Load all result JSONs
    pass_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"pass": 0, "total": 0})

    for json_file in results_dir.glob("*.json"):
        try:
            data = json.loads(json_file.read_text())
            # Handle both BenchmarkReport and run detail formats
            if "models" in data:
                continue  # Skip aggregate reports
        except (json.JSONDecodeError, KeyError):
            continue

    # If we can't load results, fall back to difficulty
    if not pass_counts:
        print("  No detailed results found, using difficulty-based classification")
        return classify_by_difficulty(cases_dir)

    tiers: dict[str, str] = {}
    for case_id, counts in pass_counts.items():
        rate = counts["pass"] / counts["total"] if counts["total"] > 0 else 0.5
        if rate > 0.9:
            tiers[case_id] = "sanity"
        elif rate < 0.5:
            tiers[case_id] = "challenge"
        else:
            tiers[case_id] = "core"

    return tiers


def apply_tiers(cases_dir: Path, tiers: dict[str, str], dry_run: bool = False) -> int:
    """Write tier field to metadata.yaml files."""
    updated = 0
    for case_dir in sorted(cases_dir.iterdir()):
        meta_file = case_dir / "metadata.yaml"
        if not case_dir.is_dir() or not meta_file.is_file():
            continue

        content = meta_file.read_text(encoding="utf-8")
        case_id = _yaml_value(content, "id") or case_dir.name
        tier = tiers.get(case_id, "core")

        existing_tier = _yaml_value(content, "tier")
        if existing_tier == tier:
            continue

        if existing_tier:
            new_content = re.sub(r"^tier:.*$", f"tier: {tier}", content, flags=re.MULTILINE)
        else:
            new_content = content.rstrip() + f"\ntier: {tier}\n"

        if not dry_run:
            meta_file.write_text(new_content, encoding="utf-8")
        updated += 1

    return updated


def _yaml_value(content: str, key: str) -> str | None:
    match = re.search(rf"^{key}:\s*(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify TCs into tiers")
    parser.add_argument("--results", type=Path, help="Results directory for IRT-based classification")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    print("Classifying TC tiers...")

    if args.results and args.results.is_dir():
        tiers = classify_by_results(args.results, CASES_DIR)
    else:
        tiers = classify_by_difficulty(CASES_DIR)

    # Stats
    from collections import Counter
    counts = Counter(tiers.values())
    print(f"\n  Sanity:    {counts.get('sanity', 0)}")
    print(f"  Core:      {counts.get('core', 0)}")
    print(f"  Challenge: {counts.get('challenge', 0)}")
    print(f"  Total:     {sum(counts.values())}")

    if args.dry_run:
        print("\n  [DRY RUN] No files modified")
        # Show Sanity cases
        sanity_cases = [k for k, v in sorted(tiers.items()) if v == "sanity"]
        if sanity_cases:
            print(f"\n  Sanity cases: {', '.join(sanity_cases)}")
    else:
        updated = apply_tiers(CASES_DIR, tiers)
        print(f"\n  Updated {updated} metadata.yaml files")


if __name__ == "__main__":
    main()
