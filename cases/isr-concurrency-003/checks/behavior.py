"""Behavioral checks for spinlock-protected shared state."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate spinlock behavioral properties."""
    details: list[CheckDetail] = []

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
    # k_spin_unlock must receive the key returned by k_spin_lock
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
    # Heuristic: k_spin_lock appears in a thread function alongside printk
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

    return details
