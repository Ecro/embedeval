#!/usr/bin/env python3
"""Auto-update METHODOLOGY.md and README.md with live benchmark statistics.

Run after any change to cases/, src/, or tests/:
    python scripts/sync_docs.py

Called automatically by /wrapup workflow.
"""

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
CASES_DIR = ROOT / "cases"
SRC_DIR = ROOT / "src" / "embedeval"
TESTS_DIR = ROOT / "tests"
METHODOLOGY = ROOT / "docs" / "METHODOLOGY.md"
README = ROOT / "README.md"


def count_cases() -> dict:
    """Gather all benchmark case statistics."""
    stats: dict = {
        "total": 0,
        "categories": Counter(),
        "platforms": Counter(),
        "difficulties": Counter(),
        "visibility": {"public": 0, "private": 0},
        "negatives": 0,
        "must_fail_mutations": 0,
        "category_difficulty": {},  # cat -> {easy: N, medium: N, hard: N}
    }

    for case_dir in sorted(CASES_DIR.iterdir()):
        meta_file = case_dir / "metadata.yaml"
        if not case_dir.is_dir() or not meta_file.is_file():
            continue

        stats["total"] += 1
        content = meta_file.read_text(encoding="utf-8")

        # Parse YAML fields (simple line-based, no dependency needed)
        cat = _yaml_value(content, "category")
        diff = _yaml_value(content, "difficulty")
        plat = _yaml_value(content, "platform")
        vis = _yaml_value(content, "visibility") or "public"

        if cat:
            stats["categories"][cat] += 1
        if diff:
            stats["difficulties"][diff] += 1
        if plat:
            stats["platforms"][plat] += 1

        stats["visibility"][vis] += 1

        # Category × difficulty matrix
        if cat and diff:
            if cat not in stats["category_difficulty"]:
                stats["category_difficulty"][cat] = Counter()
            stats["category_difficulty"][cat][diff] += 1

        # Negatives
        neg_file = case_dir / "checks" / "negatives.py"
        if neg_file.is_file():
            stats["negatives"] += 1
            neg_content = neg_file.read_text(encoding="utf-8")
            stats["must_fail_mutations"] += neg_content.count('"must_fail"')

    return stats


def count_tests() -> int:
    """Count tests using pytest --co for accurate parametrized expansion."""
    try:
        result = subprocess.run(
            ["uv", "run", "pytest", "tests/", "--co", "-q"],
            capture_output=True, text=True, timeout=30,
            cwd=str(ROOT),
        )
        # Last line: "945 tests collected in 1.80s"
        for line in result.stdout.strip().splitlines()[-3:]:
            match = re.search(r"(\d+) tests? collected", line)
            if match:
                return int(match.group(1))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    # Fallback: count def test_ functions
    count = 0
    for tf in TESTS_DIR.glob("test_*.py"):
        content = tf.read_text(encoding="utf-8")
        count += len(re.findall(r"^\s+def test_", content, re.MULTILINE))
    return count


def count_modules() -> int:
    """Count Python modules in src/embedeval/."""
    return len(list(SRC_DIR.glob("*.py"))) - 1  # exclude __init__.py if present


def count_insights() -> int:
    """Count insight entries in INSIGHTS.md."""
    insights_file = ROOT / "docs" / "INSIGHTS.md"
    if not insights_file.is_file():
        return 0
    content = insights_file.read_text(encoding="utf-8")
    return len(re.findall(r"^## #\d+\.", content, re.MULTILINE))


def update_methodology(stats: dict) -> bool:
    """Update the overview statistics table in METHODOLOGY.md."""
    if not METHODOLOGY.is_file():
        print("METHODOLOGY.md not found, skipping")
        return False

    content = METHODOLOGY.read_text(encoding="utf-8")
    original = content

    # Update overview statistics table
    n_tests = count_tests()
    n_cats = len(stats["categories"])
    n_plats = len(stats["platforms"])
    easy = stats["difficulties"].get("easy", 0)
    med = stats["difficulties"].get("medium", 0)
    hard = stats["difficulties"].get("hard", 0)
    priv = stats["visibility"]["private"]
    neg = stats["negatives"]
    mf = stats["must_fail_mutations"]

    new_table = (
        "| Metric | Value |\n"
        "|--------|-------|\n"
        f"| **Total cases** | {stats['total']} |\n"
        f"| **Categories** | {n_cats} |\n"
        f"| **Platforms** | {n_plats} ({', '.join(sorted(stats['platforms'].keys()))}) |\n"
        f"| **Difficulty** | {easy} easy, {med} medium, {hard} hard |\n"
        f"| **Private held-out** | {priv} cases ({priv * 100 // stats['total']}%) for contamination prevention |\n"
        f"| **Evaluation scenarios** | 2 (generation, bugfix) |\n"
        f"| **Negatives (mutation tests)** | {neg} cases, {mf} must_fail mutations |"
    )

    # Replace the statistics table (match from header to end of Negatives row)
    content = re.sub(
        r"\| Metric \| Value \|.*?\| \*\*Negatives \(mutation tests\)\*\* \|[^\n]*",
        new_table,
        content,
        flags=re.DOTALL,
    )

    # Update difficulty distribution table
    cat_diff_lines = []
    for cat in sorted(stats["category_difficulty"]):
        cd = stats["category_difficulty"][cat]
        total = sum(cd.values())
        cat_diff_lines.append(
            f"| {cat} | {cd.get('easy', 0)} | {cd.get('medium', 0)} | {cd.get('hard', 0)} | {total} |"
        )
    new_diff_table = "\n".join(cat_diff_lines)

    content = re.sub(
        r"(\| Category \| Easy \| Medium \| Hard \| Total \|\n\|.*?\|.*?\|.*?\|.*?\|.*?\|\n)((?:\|.*?\|.*?\|.*?\|.*?\|.*?\|\n?)+)",
        r"\1" + new_diff_table + "\n",
        content,
    )

    if content != original:
        METHODOLOGY.write_text(content, encoding="utf-8")
        print(f"  Updated METHODOLOGY.md")
        return True
    else:
        print(f"  METHODOLOGY.md already up to date")
        return False


def update_readme(stats: dict) -> bool:
    """Update test count and case count in README.md."""
    if not README.is_file():
        print("README.md not found, skipping")
        return False

    content = README.read_text(encoding="utf-8")
    original = content

    n_tests = count_tests()
    n_modules = count_modules()
    n_insights = count_insights()
    priv = stats["visibility"]["private"]
    pub = stats["total"] - priv

    # Update test count
    content = re.sub(
        r"├── tests/\s+# \d+ tests",
        f"├── tests/                   # {n_tests} tests",
        content,
    )

    # Update case count
    content = re.sub(
        r"├── cases/\s+# \d+ test cases \(\d+ public \+ \d+ private\)",
        f"├── cases/                   # {stats['total']} test cases ({pub} public + {priv} private)",
        content,
    )

    # Update module count
    content = re.sub(
        r"├── src/embedeval/\s+# Core library \(\d+ modules\)",
        f"├── src/embedeval/           # Core library ({n_modules} modules)",
        content,
    )

    # Update insights count
    content = re.sub(
        r"└── INSIGHTS\.md\s+# \d+ accumulated insights",
        f"└── INSIGHTS.md          # {n_insights} accumulated insights",
        content,
    )

    if content != original:
        README.write_text(content, encoding="utf-8")
        print(f"  Updated README.md")
        return True
    else:
        print(f"  README.md already up to date")
        return False


def _yaml_value(content: str, key: str) -> str | None:
    """Extract a simple YAML value (no nested structures)."""
    match = re.search(rf"^{key}:\s*(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return None


def main() -> None:
    print("Syncing documentation with live statistics...")

    stats = count_cases()
    n_tests = count_tests()

    print(f"\n  Cases: {stats['total']} ({stats['visibility']['public']} public, {stats['visibility']['private']} private)")
    print(f"  Categories: {len(stats['categories'])}")
    print(f"  Platforms: {len(stats['platforms'])}")
    print(f"  Difficulty: {stats['difficulties'].get('easy', 0)}e / {stats['difficulties'].get('medium', 0)}m / {stats['difficulties'].get('hard', 0)}h")
    print(f"  Negatives: {stats['negatives']} TCs, {stats['must_fail_mutations']} mutations")
    print(f"  Tests: {n_tests}")
    print(f"  Modules: {count_modules()}")
    print(f"  Insights: {count_insights()}")
    print()

    changed = False
    changed |= update_methodology(stats)
    changed |= update_readme(stats)

    if changed:
        print("\nDocumentation updated. Review changes with: git diff docs/ README.md")
    else:
        print("\nAll documentation is already up to date.")


if __name__ == "__main__":
    main()
