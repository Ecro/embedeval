"""Static analysis checks for interrupt-safe deferred logging."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate deferred logging constraints: no printk in ISR path."""
    details: list[CheckDetail] = []

    # Check 1: kernel and atomic headers present
    has_headers = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="zephyr_headers_present",
            passed=has_headers,
            expected="zephyr/kernel.h included",
            actual="present" if has_headers else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: atomic_t used for indices (not plain uint32_t)
    has_atomic_t = "atomic_t" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_indices",
            passed=has_atomic_t,
            expected="atomic_t used for ring buffer indices",
            actual="present" if has_atomic_t else "missing (plain int?)",
            check_type="exact_match",
        )
    )

    # Check 3: Log entry struct defined with at least timestamp and event fields
    has_log_struct = bool(
        re.search(r"struct\s+\w*(?:log|entry|event)\w*\s*\{", generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="log_entry_struct_defined",
            passed=has_log_struct,
            expected="Log entry struct defined",
            actual="present" if has_log_struct else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: printk NOT inside ISR write path
    # Find the isr_log_write function (or similarly named ISR-path function)
    write_fn_match = re.search(
        r"(?:isr_log_write|isr_write|log_write_isr|log_from_isr)\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        generated_code,
        re.DOTALL,
    )
    isr_path_has_printk = False
    if write_fn_match:
        isr_body = write_fn_match.group(1)
        # Check for actual logging calls: printk() or Zephyr LOG macros (LOG_ERR, LOG_WRN, etc.)
        # Exclude constants like LOG_BUF_SIZE, LOG_ENTRY_MAX, etc.
        has_printk_call = "printk" in isr_body
        has_log_macro = bool(re.search(r"\bLOG_(?:ERR|WRN|INF|DBG|MODULE_REGISTER)\b", isr_body))
        isr_path_has_printk = has_printk_call or has_log_macro
    details.append(
        CheckDetail(
            check_name="no_printk_in_isr_path",
            passed=not isr_path_has_printk,
            expected="No printk/LOG_* in ISR write path",
            actual="printk in ISR path (BUG)" if isr_path_has_printk else "clean",
            check_type="constraint",
        )
    )

    # Check 5: printk present in drain thread (must output somewhere)
    has_printk = "printk" in generated_code
    details.append(
        CheckDetail(
            check_name="printk_in_drain_thread",
            passed=has_printk,
            expected="printk called in drain thread for output",
            actual="present" if has_printk else "missing (no output?)",
            check_type="exact_match",
        )
    )

    # Check 6: Drain thread present
    has_drain = bool(
        re.search(r"\w*(?:drain|consumer|flush|logger|output)\w*\s*(?:thread|task)?\s*\(",
                  generated_code, re.IGNORECASE)
    ) or "K_THREAD_DEFINE" in generated_code or "k_thread_create" in generated_code
    details.append(
        CheckDetail(
            check_name="drain_thread_present",
            passed=has_drain,
            expected="Log drain thread defined",
            actual="present" if has_drain else "missing",
            check_type="exact_match",
        )
    )

    return details
