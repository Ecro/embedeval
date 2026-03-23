"""Behavioral checks for simple system sleep."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sleep behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: k_uptime_get called twice (before and after sleep)
    # (LLM failure: calling k_uptime_get only once, or not at all)
    uptime_call_count = generated_code.count("k_uptime_get")
    has_two_uptime_calls = uptime_call_count >= 2
    details.append(
        CheckDetail(
            check_name="two_uptime_calls",
            passed=has_two_uptime_calls,
            expected="k_uptime_get() called >= 2 times (before and after sleep)",
            actual=f"count={uptime_call_count}",
            check_type="constraint",
        )
    )

    # Check 2: k_sleep called with K_MSEC (correct time macro)
    # (LLM failure: using raw integer or K_SECONDS instead of K_MSEC)
    has_sleep_with_kmsec = (
        "k_sleep" in generated_code
        and "K_MSEC" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="k_sleep_with_k_msec",
            passed=has_sleep_with_kmsec,
            expected="k_sleep(K_MSEC(...)) used for sleep",
            actual="present" if has_sleep_with_kmsec else "missing or wrong macro",
            check_type="constraint",
        )
    )

    # Check 3: Elapsed time computed and printed
    # (LLM failure: printing only uptime, not the elapsed difference)
    has_elapsed = (
        "elapsed" in generated_code.lower()
        or "diff" in generated_code.lower()
        or (
            "-" in generated_code
            and "uptime" in generated_code.lower()
        )
    )
    details.append(
        CheckDetail(
            check_name="elapsed_time_computed",
            passed=has_elapsed,
            expected="Elapsed time computed (difference of two uptime reads) and printed",
            actual="present" if has_elapsed else "missing",
            check_type="constraint",
        )
    )

    # Check 4: No busy-wait (for loop counting or k_busy_wait)
    # (LLM failure: using a counting loop to simulate delay)
    has_for_loop_as_delay = bool(
        re.search(r"for\s*\([^;]*;\s*[^;]*<\s*\d+\s*;", generated_code)
    )
    has_busy_wait = "k_busy_wait" in generated_code
    no_busy_wait = not has_for_loop_as_delay and not has_busy_wait
    details.append(
        CheckDetail(
            check_name="no_busy_wait_loop",
            passed=no_busy_wait,
            expected="No counting-loop or k_busy_wait used as delay",
            actual="clean" if no_busy_wait else "busy-wait detected",
            check_type="constraint",
        )
    )

    # Check 5: Timestamps printed before and after sleep
    # (LLM failure: only printing one timestamp)
    printk_count = generated_code.count("printk")
    has_multiple_prints = printk_count >= 3
    details.append(
        CheckDetail(
            check_name="multiple_printk_calls",
            passed=has_multiple_prints,
            expected="At least 3 printk calls (before, after, elapsed)",
            actual=f"printk_count={printk_count}",
            check_type="constraint",
        )
    )

    return details
