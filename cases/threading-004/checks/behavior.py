"""Behavioral checks for priority inheritance mutex."""

import re
from collections import Counter

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate priority inheritance mutex behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: k_mutex used, not k_sem (only k_mutex has priority inheritance)
    # (LLM failure: using k_sem which has no priority inheritance, defeats the purpose)
    uses_mutex = "k_mutex_lock" in generated_code
    uses_sem_give = "k_sem_give" in generated_code
    uses_sem_take = "k_sem_take" in generated_code
    correct_primitive = uses_mutex and not (uses_sem_give or uses_sem_take)
    details.append(
        CheckDetail(
            check_name="mutex_not_semaphore",
            passed=correct_primitive,
            expected="k_mutex used (not k_sem) — only mutex has priority inheritance",
            actual="mutex" if uses_mutex else "semaphore or missing",
            check_type="constraint",
        )
    )

    # Check 2: Three distinct priority values used
    # (LLM failure: same priority for all threads, inheritance has no effect)
    priority_matches = re.findall(
        r"K_THREAD_DEFINE\s*\([^,]+,\s*\d+,\s*\w+,"
        r"[^,]*,[^,]*,[^,]*,\s*(\d+)",
        generated_code,
    )
    unique_priorities = set(priority_matches)
    has_three_distinct = len(unique_priorities) >= 3
    details.append(
        CheckDetail(
            check_name="three_distinct_priorities",
            passed=has_three_distinct,
            expected="Three distinct priorities for low, med, high threads",
            actual=f"priorities={sorted(unique_priorities)}",
            check_type="constraint",
        )
    )

    # Check 3: Low priority thread holds mutex (locks before sleeping)
    # (LLM failure: high priority thread is the one holding the mutex)
    has_lock = "k_mutex_lock" in generated_code
    has_sleep_after_lock = False
    if has_lock:
        lock_pos = generated_code.find("k_mutex_lock")
        after_lock = generated_code[lock_pos:lock_pos + 500]
        has_sleep_after_lock = "k_sleep" in after_lock
    details.append(
        CheckDetail(
            check_name="mutex_holder_sleeps_while_locked",
            passed=has_sleep_after_lock,
            expected="Thread holding mutex calls k_sleep (simulates work under lock)",
            actual="present" if has_sleep_after_lock else "missing",
            check_type="constraint",
        )
    )

    # Check 4: Higher-priority thread attempts to acquire same mutex
    # (LLM failure: each thread uses a different mutex, no contention)
    mutex_lock_count = generated_code.count("k_mutex_lock")
    has_contention = mutex_lock_count >= 2
    details.append(
        CheckDetail(
            check_name="mutex_contention_present",
            passed=has_contention,
            expected="k_mutex_lock called >= 2 times (contention between threads)",
            actual=f"lock_count={mutex_lock_count}",
            check_type="constraint",
        )
    )

    # Check 5: Mutex unlocked after each lock (no deadlock path)
    # (LLM failure: locking twice without unlock — deadlock)
    unlock_count = generated_code.count("k_mutex_unlock")
    lock_count = generated_code.count("k_mutex_lock")
    no_deadlock = unlock_count >= lock_count
    details.append(
        CheckDetail(
            check_name="no_deadlock_unlock_balanced",
            passed=no_deadlock,
            expected="k_mutex_unlock called at least as many times as k_mutex_lock",
            actual=f"lock={lock_count}, unlock={unlock_count}",
            check_type="constraint",
        )
    )

    # Check 6: Same mutex used by multiple threads (not separate mutexes)
    mutex_names = re.findall(r'k_mutex_lock\s*\(\s*&?\s*(\w+)', generated_code)
    mutex_counts = Counter(mutex_names)
    same_mutex = any(c >= 2 for c in mutex_counts.values()) if mutex_counts else False
    details.append(
        CheckDetail(
            check_name="same_mutex_shared",
            passed=same_mutex,
            expected="Same mutex used by multiple threads for priority inheritance",
            actual=f"mutex usage: {dict(mutex_counts)}" if mutex_counts else "no mutex locks found",
            check_type="constraint",
        )
    )

    return details
