"""Behavioral checks for ISR-to-thread k_msgq communication."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    check_no_isr_forbidden,
    find_isr_bodies,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate k_msgq behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: Message struct defined
    has_struct = bool(re.search(r'\bstruct\b[^{]*\{[^}]*uint', generated_code, re.DOTALL))
    details.append(
        CheckDetail(
            check_name="message_struct_defined",
            passed=has_struct,
            expected="Message struct with data field defined",
            actual="present" if has_struct else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: K_MSGQ_DEFINE used with at least 4 slots
    msgq_def = re.search(r'K_MSGQ_DEFINE\s*\([^,]+,[^,]+,\s*(\d+)', generated_code)
    adequate_slots = False
    if msgq_def:
        slots = int(msgq_def.group(1))
        adequate_slots = slots >= 4
    details.append(
        CheckDetail(
            check_name="msgq_adequate_depth",
            passed=adequate_slots,
            expected="K_MSGQ_DEFINE with >= 4 slots",
            actual=f"slots={msgq_def.group(1) if msgq_def else 'not found'}",
            check_type="constraint",
        )
    )

    # Check 3: k_msgq_put called (ISR produces data)
    has_put = "k_msgq_put" in generated_code
    details.append(
        CheckDetail(
            check_name="k_msgq_put_called",
            passed=has_put,
            expected="k_msgq_put() called in ISR",
            actual="present" if has_put else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: k_msgq_get called (thread consumes data)
    has_get = "k_msgq_get" in generated_code
    details.append(
        CheckDetail(
            check_name="k_msgq_get_called",
            passed=has_get,
            expected="k_msgq_get() called in consumer thread",
            actual="present" if has_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Consumer uses K_FOREVER in get (efficient blocking wait)
    get_forever = bool(re.search(
        r'k_msgq_get\s*\([^)]*K_FOREVER[^)]*\)', generated_code
    ))
    details.append(
        CheckDetail(
            check_name="consumer_uses_k_forever",
            passed=get_forever,
            expected="k_msgq_get uses K_FOREVER in consumer thread (efficient blocking)",
            actual="present" if get_forever else "missing (may busy-poll)",
            check_type="constraint",
        )
    )

    # Check 6: k_sleep present in main (allows thread to run)
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="k_sleep_in_main",
            passed=has_sleep,
            expected="k_sleep() in main to allow consumer thread to run",
            actual="present" if has_sleep else "missing (thread may never run)",
            check_type="constraint",
        )
    )

    # Check 7: k_msgq_put inside ISR uses K_NO_WAIT (never block in ISR)
    # LLM failure: calling k_msgq_put with K_FOREVER inside ISR will deadlock
    isr_bodies = find_isr_bodies(stripped)
    isr_msgq_put_blocks = False
    for body in isr_bodies:
        if "k_msgq_put" in body and "K_FOREVER" in body:
            isr_msgq_put_blocks = True
    details.append(
        CheckDetail(
            check_name="msgq_put_no_wait_in_isr",
            passed=not isr_msgq_put_blocks,
            expected="k_msgq_put inside ISR uses K_NO_WAIT (not K_FOREVER)",
            actual="correct" if not isr_msgq_put_blocks else "BUG: k_msgq_put with K_FOREVER in ISR deadlocks",
            check_type="constraint",
        )
    )

    # Check 8: No forbidden APIs inside ISR bodies
    isr_violations = check_no_isr_forbidden(generated_code)
    details.append(
        CheckDetail(
            check_name="no_forbidden_apis_in_isr",
            passed=len(isr_violations) == 0,
            expected="No printk/k_malloc/k_mutex_lock/k_sleep inside ISR bodies",
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
