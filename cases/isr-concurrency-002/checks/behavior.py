"""Behavioral checks for ISR-to-thread k_msgq communication."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate k_msgq behavioral properties."""
    details: list[CheckDetail] = []

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
    # This is correct for thread context
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

    return details
