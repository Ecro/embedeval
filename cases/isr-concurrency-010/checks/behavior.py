"""Behavioral checks for interrupt-safe deferred logging."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate deferred logging behavioral correctness."""
    details: list[CheckDetail] = []

    # Check 1: ISR handler function calls isr_log_write (or equivalent), not printk
    isr_fn_match = re.search(
        r"void\s+\w*(?:isr|irq|interrupt)\w*\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        generated_code,
        re.IGNORECASE | re.DOTALL,
    )
    isr_calls_printk = False
    if isr_fn_match:
        isr_body = isr_fn_match.group(1)
        # Only flag actual log macros, not constants like LOG_BUF_SIZE
        isr_calls_printk = "printk" in isr_body or bool(
            re.search(r"\bLOG_(ERR|WRN|INF|DBG)\b", isr_body)
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

    return details
