"""Behavioral checks for ISR-to-thread via k_poll."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate k_poll behavioral correctness."""
    details: list[CheckDetail] = []

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

    # Check 3: k_poll NOT called in ISR context
    # Heuristic: check for k_poll inside ISR-named functions
    isr_pattern = re.search(
        r"void\s+\w*(?:isr|irq|interrupt|handler)\w*\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        generated_code,
        re.IGNORECASE | re.DOTALL,
    )
    isr_calls_poll = False
    if isr_pattern:
        isr_body = isr_pattern.group(1)
        isr_calls_poll = "k_poll(" in isr_body
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
    # Detect tight while(1) { } without k_poll inside
    # This is a heuristic — if k_poll present, assume it's in the loop
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

    return details
