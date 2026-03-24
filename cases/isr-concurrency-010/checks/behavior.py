"""Behavioral checks for interrupt-safe deferred logging."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    check_no_isr_forbidden,
    find_isr_bodies,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate deferred logging behavioral correctness."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: ISR handler function calls isr_log_write (or equivalent), not printk
    # Use find_isr_bodies for accuracy instead of fragile regex
    isr_bodies = find_isr_bodies(stripped)
    # Also check named ISR functions not caught by heuristic patterns
    isr_fn_match = re.search(
        r"void\s+\w*(?:isr|irq|interrupt)\w*\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        generated_code,
        re.IGNORECASE | re.DOTALL,
    )
    isr_bodies_raw = list(isr_bodies)
    if isr_fn_match:
        isr_bodies_raw.append(isr_fn_match.group(1))

    isr_calls_printk = any(
        "printk" in body or bool(re.search(r"\bLOG_(ERR|WRN|INF|DBG)\b", body))
        for body in isr_bodies_raw
    )
    details.append(
        CheckDetail(
            check_name="isr_defers_logging",
            passed=not isr_calls_printk,
            expected="ISR handler does NOT call printk/LOG_* directly",
            actual="ISR calls printk (BUG)" if isr_calls_printk else "deferred correctly",
            check_type="constraint",
        )
    )

    # Check 2: Drain thread reads entries and calls printk
    drain_fn_match = re.search(
        r"void\s+\w*(?:drain|flush|log_thread|consumer|logger)\w*\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        generated_code,
        re.IGNORECASE | re.DOTALL,
    )
    drain_has_printk = False
    if drain_fn_match:
        drain_body = drain_fn_match.group(1)
        drain_has_printk = "printk" in drain_body
    details.append(
        CheckDetail(
            check_name="drain_thread_calls_printk",
            passed=drain_has_printk,
            expected="Drain thread calls printk to output log entries",
            actual="printk in drain" if drain_has_printk else "no printk in drain",
            check_type="exact_match",
        )
    )

    # Check 3: Atomic operations used for index management
    has_atomic_ops = "atomic_get" in generated_code and "atomic_set" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_index_management",
            passed=has_atomic_ops,
            expected="atomic_get and atomic_set used for index management",
            actual="present" if has_atomic_ops else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Buffer size defined as a constant (not magic number inline)
    has_buf_size = bool(
        re.search(r"#define\s+\w*(?:BUF|LOG|RING|SIZE)\w*\s+\d+", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="buffer_size_defined",
            passed=has_buf_size,
            expected="Buffer size defined as named constant",
            actual="present" if has_buf_size else "missing (magic number?)",
            check_type="constraint",
        )
    )

    # Check 5: Drain thread sleeps between passes (not busy-polling)
    has_drain_sleep = bool(
        re.search(r"k_sleep\s*\(|k_msleep\s*\(|k_usleep\s*\(", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="drain_thread_not_busy_polling",
            passed=has_drain_sleep,
            expected="Drain thread sleeps between drain passes (not busy-polling)",
            actual="sleep found" if has_drain_sleep else "no sleep (busy-poll?)",
            check_type="constraint",
        )
    )

    # Check 6: No forbidden blocking APIs inside ISR bodies (using check_utils)
    # LLM failure: calling printk or k_malloc directly in ISR instead of buffering
    isr_violations = check_no_isr_forbidden(generated_code)
    # For deferred logging the ISR must not call printk — this is the core requirement
    details.append(
        CheckDetail(
            check_name="no_forbidden_apis_in_isr",
            passed=len(isr_violations) == 0,
            expected="No printk/k_malloc/k_sleep inside ISR bodies",
            actual="clean" if not isr_violations else f"violations: {isr_violations}",
            check_type="constraint",
        )
    )

    # Check 7: No cross-platform API contamination
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
