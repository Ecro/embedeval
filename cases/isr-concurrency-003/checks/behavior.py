"""Behavioral checks for spinlock-protected shared state."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    check_no_isr_forbidden,
    find_isr_bodies,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate spinlock behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: lock/unlock appear in pairs (balanced spinlock usage)
    lock_count = generated_code.count("k_spin_lock")
    unlock_count = generated_code.count("k_spin_unlock")
    details.append(
        CheckDetail(
            check_name="spinlock_balanced",
            passed=lock_count > 0 and lock_count == unlock_count,
            expected="Equal number of k_spin_lock and k_spin_unlock calls",
            actual=f"lock={lock_count}, unlock={unlock_count}",
            check_type="constraint",
        )
    )

    # Check 2: key passed to unlock (correct API usage)
    has_key_in_unlock = bool(re.search(
        r'k_spin_unlock\s*\([^,]+,\s*\w+\)', generated_code
    ))
    details.append(
        CheckDetail(
            check_name="key_passed_to_unlock",
            passed=has_key_in_unlock,
            expected="Key variable passed to k_spin_unlock()",
            actual="present" if has_key_in_unlock else "missing (IRQ state not restored)",
            check_type="constraint",
        )
    )

    # Check 3: Consumer/reader thread defined
    has_thread = (
        "K_THREAD_DEFINE" in generated_code
        or "k_thread_create" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="reader_thread_defined",
            passed=has_thread,
            expected="Reader thread defined with K_THREAD_DEFINE or k_thread_create",
            actual="present" if has_thread else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Shared variable modified in ISR (incremented/written)
    has_isr_write = bool(re.search(
        r'(isr_handler|ISR|irq_handler)[^}]*\+\+|'
        r'(isr_handler|ISR|irq_handler)[^}]*\+=',
        generated_code, re.IGNORECASE | re.DOTALL
    ))
    details.append(
        CheckDetail(
            check_name="isr_modifies_shared",
            passed=has_isr_write,
            expected="ISR handler modifies the shared variable",
            actual="present" if has_isr_write else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Thread reads shared variable under spinlock
    has_thread_read = bool(re.search(
        r'k_spin_lock[^}]*printk|printk[^}]*k_spin_lock',
        generated_code, re.DOTALL
    ))
    details.append(
        CheckDetail(
            check_name="thread_reads_under_lock",
            passed=has_thread_read,
            expected="Thread reads shared variable under spinlock before printing",
            actual="present" if has_thread_read else "not confirmed",
            check_type="constraint",
        )
    )

    # Check 6: k_sleep present (cooperative scheduling)
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="k_sleep_present",
            passed=has_sleep,
            expected="k_sleep() present to allow thread scheduling",
            actual="present" if has_sleep else "missing",
            check_type="constraint",
        )
    )

    # Check 7: No k_mutex used in ISR (mutex cannot be used in ISR context)
    # LLM failure: using k_mutex_lock in the ISR body instead of spinlock
    isr_bodies = find_isr_bodies(stripped)
    isr_uses_mutex = any("k_mutex" in body for body in isr_bodies)
    details.append(
        CheckDetail(
            check_name="no_mutex_in_isr",
            passed=not isr_uses_mutex,
            expected="No k_mutex operations inside ISR (spinlock required in ISR)",
            actual="correct" if not isr_uses_mutex else "BUG: k_mutex used in ISR — will deadlock",
            check_type="constraint",
        )
    )

    # Check 8: No forbidden blocking APIs inside ISR bodies
    isr_violations = check_no_isr_forbidden(generated_code)
    details.append(
        CheckDetail(
            check_name="no_forbidden_apis_in_isr",
            passed=len(isr_violations) == 0,
            expected="No printk/k_malloc/k_sleep inside ISR bodies",
            actual="clean" if not isr_violations else f"violations: {isr_violations}",
            check_type="constraint",
        )
    )

    # Check 9: No cross-platform API contamination
    cross_platform = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(
        CheckDetail(
            check_name="no_cross_platform_apis",
            passed=len(cross_platform) == 0,
            expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
            actual="clean" if not cross_platform else f"found: {[a for a, _ in cross_platform]}",
            check_type="constraint",
        )
    )

    return details
