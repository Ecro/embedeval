"""Negative tests — verify that intentionally broken code is caught by checks.

For each case with a checks/negatives.py file, apply mutations to the reference
solution and verify that the specified checks correctly FAIL.
"""

import importlib.util
from pathlib import Path

import pytest

CASES_DIR = Path(__file__).parent.parent / "cases"


def _discover_negatives():
    """Find all cases with negatives.py and yield (case_id, negative_entry) tuples."""
    items = []
    for neg_file in sorted(CASES_DIR.glob("*/checks/negatives.py")):
        case_id = neg_file.parent.parent.name
        spec = importlib.util.spec_from_file_location("neg", neg_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        negatives = getattr(mod, "NEGATIVES", [])
        for neg in negatives:
            items.append((case_id, neg))
    return items


NEGATIVE_ITEMS = _discover_negatives()


@pytest.mark.parametrize(
    "case_id,negative",
    NEGATIVE_ITEMS,
    ids=[f"{cid}-{neg['name']}" for cid, neg in NEGATIVE_ITEMS],
)
def test_negative_detected(case_id: str, negative: dict) -> None:
    """Mutated code must fail the specified checks."""
    case_dir = CASES_DIR / case_id
    ref_code = (case_dir / "reference" / "main.c").read_text(encoding="utf-8")

    # Apply mutation
    bad_code = negative["mutation"](ref_code)
    assert bad_code != ref_code, f"Mutation '{negative['name']}' did not change the code"

    # Determine which check module to use
    must_fail_checks = negative["must_fail"]

    # Run both static and behavior checks, collect all results
    all_details = []
    for module_name in ("static", "behavior"):
        check_file = case_dir / "checks" / f"{module_name}.py"
        if not check_file.exists():
            continue
        spec = importlib.util.spec_from_file_location("checks", check_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        details = mod.run_checks(bad_code)
        all_details.extend(details)

    # Verify each must_fail check actually failed
    for check_name in must_fail_checks:
        matching = [d for d in all_details if d.check_name == check_name]
        assert matching, f"Check '{check_name}' not found in any module for {case_id}"
        assert all(not d.passed for d in matching), (
            f"Check '{check_name}' should FAIL on mutation '{negative['name']}' "
            f"but at least one PASSED. results={[(d.passed, d.actual) for d in matching]}"
        )
