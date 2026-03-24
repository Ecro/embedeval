"""Behavioral checks for ISR-to-thread via k_poll."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    check_no_isr_forbidden,
    find_isr_bodies,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate k_poll behavioral correctness."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: k_poll_signal_reset called after receiving signal
    # LLM failure: not resetting signal, causing spurious re-triggers
    has_reset = "k_poll_signal_reset" in generated_code
    details.append(
        CheckDetail(
            check_name="signal_reset_after_receive",
            passed=has_reset,
            expected="k_poll_signal_reset() called after signal received",
            actual="present" if has_reset else "missing (spurious retrigger risk)",
            check_type="constraint",
        )
    )

    # Check 2: Event state reset to K_POLL_STATE_NOT_READY
    # LLM failure: not resetting event state, k_poll returns immediately next time
    has_state_reset = "K_POLL_STATE_NOT_READY" in generated_code
    details.append(
        CheckDetail(
            check_name="event_state_reset",
            passed=has_state_reset,
            expected="Event state reset to K_POLL_STATE_NOT_READY after each poll",
            actual="present" if has_state_reset else "missing (k_poll may loop immediately)",
            check_type="constraint",
        )
    )

    # Check 3: k_poll NOT called in ISR context — using find_isr_bodies for accuracy
    isr_bodies = find_isr_bodies(stripped)
    isr_calls_poll = any("k_poll(" in body for body in isr_bodies)
    details.append(
        CheckDetail(
            check_name="k_poll_not_in_isr",
            passed=not isr_calls_poll,
            expected="k_poll() NOT called inside ISR (it blocks)",
            actual="ISR calls k_poll (BUG)" if isr_calls_poll else "clean",
            check_type="constraint",
        )
    )

    # Check 4: K_POLL_STATE_SIGNALED checked after k_poll returns
    has_state_check = "K_POLL_STATE_SIGNALED" in generated_code
    details.append(
        CheckDetail(
            check_name="signaled_state_checked",
            passed=has_state_check,
            expected="K_POLL_STATE_SIGNALED checked after k_poll wakes",
            actual="present" if has_state_check else "missing (no state validation)",
            check_type="constraint",
        )
    )

    # Check 5: No busy-wait loop without k_poll
    has_kpoll = "k_poll(" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_poll_not_busy_wait",
            passed=has_kpoll,
            expected="k_poll() used for blocking wait (not busy-polling)",
            actual="k_poll present" if has_kpoll else "no k_poll (busy-wait?)",
            check_type="exact_match",
        )
    )

    # Check 6: No forbidden blocking APIs inside ISR bodies
    # LLM failure: calling k_poll or k_sleep from within the ISR signaling function
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
