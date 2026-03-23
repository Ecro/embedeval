"""Behavioral checks for system PM policy override."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PM policy lock lifecycle behavioral correctness."""
    details: list[CheckDetail] = []

    # Check 1: start and stop functions defined (or equivalent structure)
    has_start = bool(
        re.search(r"\b\w*(?:start|begin|acquire|enable)_\w*(?:network|active|activity)\w*\s*\(",
                  generated_code, re.IGNORECASE)
    )
    has_stop = bool(
        re.search(r"\b\w*(?:stop|end|release|disable)_\w*(?:network|active|activity)\w*\s*\(",
                  generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="start_stop_functions",
            passed=has_start and has_stop,
            expected="start_network_activity() and stop_network_activity() defined",
            actual=f"start={has_start} stop={has_stop}",
            check_type="exact_match",
        )
    )

    # Check 2: Lock not leaked — get and put counts must match
    get_count = generated_code.count("pm_policy_state_lock_get")
    put_count = generated_code.count("pm_policy_state_lock_put")
    details.append(
        CheckDetail(
            check_name="lock_not_leaked",
            passed=get_count == put_count and get_count >= 1,
            expected="lock_get() and lock_put() called equal number of times",
            actual=f"get={get_count} put={put_count}",
            check_type="constraint",
        )
    )

    # Check 3: pm_state_force NOT used (that forces transition, not prevention)
    has_state_force = "pm_state_force" in generated_code
    details.append(
        CheckDetail(
            check_name="no_pm_state_force",
            passed=not has_state_force,
            expected="pm_state_force() NOT used (use lock_get for prevention)",
            actual="pm_state_force found (wrong API)" if has_state_force else "clean",
            check_type="constraint",
        )
    )

    # Check 4: Work done between lock and unlock
    # Pattern: lock_get ... (some code) ... lock_put
    between_lock = re.search(
        r"pm_policy_state_lock_get.*?pm_policy_state_lock_put",
        generated_code,
        re.DOTALL,
    )
    has_work_between = between_lock is not None and (
        "k_sleep" in between_lock.group(0) or "printk" in between_lock.group(0)
    )
    details.append(
        CheckDetail(
            check_name="work_between_lock_and_unlock",
            passed=has_work_between,
            expected="Active work (k_sleep or printk) between lock_get and lock_put",
            actual="work found" if has_work_between else "no work between lock/unlock",
            check_type="constraint",
        )
    )

    # Check 5: Deep sleep prevention message printed
    has_message = bool(
        re.search(r"(deep sleep|network active|sleep prevent)", generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="status_message_printed",
            passed=has_message,
            expected="Status message printed indicating deep sleep state",
            actual="message found" if has_message else "no status message",
            check_type="constraint",
        )
    )

    return details
