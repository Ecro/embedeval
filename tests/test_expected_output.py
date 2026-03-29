"""Validate expected_output.txt keywords match reference printk calls."""

import re
from pathlib import Path

import pytest

CASES_DIR = Path(__file__).parent.parent / "cases"

PRINT_PATTERN = re.compile(
    r'(?:printk|printf|LOG_(?:INF|ERR|WRN|DBG))\s*\(\s*"([^"]*)"'
)


def _get_all_print_strings(code: str) -> str:
    """Extract all printk/LOG_* format strings concatenated."""
    return " ".join(PRINT_PATTERN.findall(code))


def _discover_cases_with_expected_output() -> list[tuple[str, Path]]:
    """Find all cases that have expected_output.txt."""
    items = []
    for eo in sorted(CASES_DIR.glob("*/checks/expected_output.txt")):
        case_id = eo.parent.parent.name
        items.append((case_id, eo))
    return items


CASES = _discover_cases_with_expected_output()


@pytest.mark.parametrize(
    "case_id,expected_file",
    CASES,
    ids=[c[0] for c in CASES],
)
def test_keywords_appear_in_reference(
    case_id: str, expected_file: Path
) -> None:
    """Each keyword in expected_output.txt must trace to a printk in reference."""
    ref_file = expected_file.parent.parent / "reference" / "main.c"
    if not ref_file.exists():
        pytest.skip(f"No reference/main.c for {case_id}")

    code = ref_file.read_text(encoding="utf-8")
    all_prints = _get_all_print_strings(code)

    keywords = [
        kw.strip()
        for kw in expected_file.read_text(encoding="utf-8").splitlines()
        if kw.strip()
    ]
    assert keywords, f"{case_id}: expected_output.txt is empty"

    for kw in keywords:
        # Keyword should appear as a substring of some printk format string
        # OR appear literally in the code (for LOG_* macros with module prefix)
        assert kw in all_prints or kw in code, (
            f"{case_id}: keyword '{kw}' not found in any printk/LOG_* call"
        )


@pytest.mark.parametrize(
    "case_id,expected_file",
    CASES,
    ids=[c[0] for c in CASES],
)
def test_expected_output_not_empty(
    case_id: str, expected_file: Path
) -> None:
    """Each expected_output.txt must have at least one non-empty line."""
    keywords = [
        kw.strip()
        for kw in expected_file.read_text(encoding="utf-8").splitlines()
        if kw.strip()
    ]
    assert len(keywords) >= 1, f"{case_id}: expected_output.txt has no keywords"
