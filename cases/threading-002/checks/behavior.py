"""Behavioral checks for mutex-protected shared counter."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate mutex counter behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Counter increment appears inside a mutex-locked region
    # Strategy: look for lock...increment...unlock pattern within any function body.
    # (LLM failure: incrementing counter outside the mutex)
    has_lock = "k_mutex_lock" in generated_code
    has_increment = "++" in generated_code or "+= 1" in generated_code
    # Find whether any occurrence of "++" falls between a lock and unlock pair
    increment_inside_lock = False
    if has_lock and has_increment:
        # Find all lock positions and the nearest following unlock
        for lock_m in re.finditer(r"k_mutex_lock", generated_code):
            unlock_m = re.search(r"k_mutex_unlock", generated_code[lock_m.end():])
            if unlock_m:
                region = generated_code[lock_m.start():lock_m.end() + unlock_m.end()]
                if "++" in region or "+= 1" in region:
                    increment_inside_lock = True
                    break
    details.append(
        CheckDetail(
            check_name="lock_before_increment",
            passed=increment_inside_lock,
            expected="Counter incremented between k_mutex_lock and k_mutex_unlock",
            actual="correct" if increment_inside_lock else "increment outside mutex region",
            check_type="constraint",
        )
    )

    # Check 2: k_mutex_unlock called after increment (unlock on success path)
    # (LLM failure: forgetting to call unlock)
    unlock_count = generated_code.count("k_mutex_unlock")
    lock_count = generated_code.count("k_mutex_lock")
    has_balanced_unlock = unlock_count >= lock_count and unlock_count > 0
    details.append(
        CheckDetail(
            check_name="mutex_unlock_present",
            passed=has_balanced_unlock,
            expected="k_mutex_unlock() called at least as many times as k_mutex_lock()",
            actual=f"lock={lock_count}, unlock={unlock_count}",
            check_type="constraint",
        )
    )

    # Check 3: Thread sleeps between increments (not a tight lock-holding loop)
    # (LLM failure: holding mutex across k_sleep, starvation)
    has_sleep = "k_sleep" in generated_code or "k_msleep" in generated_code
    details.append(
        CheckDetail(
            check_name="thread_yields_between_increments",
            passed=has_sleep,
            expected="k_sleep() called between increments to yield CPU",
            actual="present" if has_sleep else "missing",
            check_type="constraint",
        )
    )

    # Check 4: K_FOREVER used for mutex lock timeout (blocking)
    # (LLM failure: using K_NO_WAIT which may silently skip the lock)
    has_forever_lock = "K_FOREVER" in generated_code and "k_mutex_lock" in generated_code
    details.append(
        CheckDetail(
            check_name="mutex_lock_blocks_forever",
            passed=has_forever_lock,
            expected="k_mutex_lock uses K_FOREVER timeout",
            actual="present" if has_forever_lock else "K_NO_WAIT or timeout used",
            check_type="constraint",
        )
    )

    # Check 5: k_mutex used (not k_sem) as the synchronization primitive
    # (LLM failure: using k_sem instead of k_mutex — semantically wrong for mutual exclusion)
    uses_mutex = "k_mutex_lock" in generated_code
    uses_sem_without_mutex = (
        ("k_sem_take" in generated_code or "k_sem_give" in generated_code)
        and not uses_mutex
    )
    correct_primitive = uses_mutex and not uses_sem_without_mutex
    details.append(
        CheckDetail(
            check_name="correct_sync_primitive",
            passed=correct_primitive,
            expected="k_mutex used (not k_sem) for mutual exclusion",
            actual="mutex" if uses_mutex else "semaphore or missing",
            check_type="constraint",
        )
    )

    # Check 6: k_sleep is NOT between mutex lock and unlock (starvation bug)
    lock_pos = generated_code.find("k_mutex_lock")
    unlock_pos = generated_code.find("k_mutex_unlock")
    sleep_pos = generated_code.find("k_sleep")
    sleep_inside_mutex = (lock_pos != -1 and unlock_pos != -1 and sleep_pos != -1 and
                          lock_pos < sleep_pos < unlock_pos)
    details.append(
        CheckDetail(
            check_name="no_sleep_under_mutex",
            passed=not sleep_inside_mutex,
            expected="k_sleep() NOT called while holding mutex (prevents starvation)",
            actual="clean" if not sleep_inside_mutex else "k_sleep inside mutex lock — starvation risk",
            check_type="constraint",
        )
    )

    return details
