"""Behavioral checks for thread-safe singleton initialization."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate double-check locking pattern correctness."""
    details: list[CheckDetail] = []

    # Check 1: Double-check pattern — initialized checked BEFORE and AFTER lock
    # Count occurrences of the initialized flag being checked
    init_checks = len(re.findall(r"\binitialized\b", generated_code))
    has_double_check = init_checks >= 2
    details.append(
        CheckDetail(
            check_name="double_check_pattern",
            passed=has_double_check,
            expected="initialized flag checked at least twice (before lock and under lock)",
            actual=f"initialized referenced {init_checks} times",
            check_type="constraint",
        )
    )

    # Check 2: First check before lock (fast path)
    # Pattern: if (initialized) return ... before k_mutex_lock
    first_check_pos = generated_code.find("initialized")
    lock_pos = generated_code.find("k_mutex_lock")
    has_fast_path = first_check_pos != -1 and lock_pos != -1 and first_check_pos < lock_pos
    details.append(
        CheckDetail(
            check_name="fast_path_before_lock",
            passed=has_fast_path,
            expected="initialized checked BEFORE k_mutex_lock (fast path)",
            actual="fast path present" if has_fast_path else "no fast path before lock",
            check_type="constraint",
        )
    )

    # Check 3: Second check under lock (prevents double init)
    # Pattern: k_mutex_lock ... if (!initialized) ... initialized = true
    under_lock_pattern = re.search(
        r"k_mutex_lock.*?if\s*\(\s*!?\s*initialized\s*\)",
        generated_code,
        re.DOTALL,
    )
    has_second_check = under_lock_pattern is not None
    details.append(
        CheckDetail(
            check_name="second_check_under_lock",
            passed=has_second_check,
            expected="initialized re-checked under k_mutex_lock",
            actual="second check found" if has_second_check else "no second check under lock",
            check_type="constraint",
        )
    )

    # Check 4: initialized set to true during init
    has_set_true = bool(
        re.search(r"initialized\s*=\s*true", generated_code)
        or re.search(r"initialized\s*=\s*1\b", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="initialized_flag_set",
            passed=has_set_true,
            expected="initialized flag set to true after init",
            actual="present" if has_set_true else "missing (infinite re-init?)",
            check_type="constraint",
        )
    )

    # Check 5: get_resource (or equivalent) function returns pointer
    has_get_fn = bool(
        re.search(r"\*\s*get_\w+\s*\(|get_resource|get_singleton|get_instance", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="getter_function_present",
            passed=has_get_fn,
            expected="get_resource() or equivalent function returning pointer",
            actual="present" if has_get_fn else "missing",
            check_type="exact_match",
        )
    )

    return details
