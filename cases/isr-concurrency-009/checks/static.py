"""Static analysis checks for ISR-to-thread via k_poll."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate k_poll signal usage for ISR-to-thread signaling."""
    details: list[CheckDetail] = []

    # Check 1: kernel header
    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header_included",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: k_poll_signal declared
    has_signal = "k_poll_signal" in generated_code
    details.append(
        CheckDetail(
            check_name="k_poll_signal_declared",
            passed=has_signal,
            expected="k_poll_signal declared",
            actual="present" if has_signal else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: k_poll_signal_init called
    has_init = "k_poll_signal_init" in generated_code
    details.append(
        CheckDetail(
            check_name="signal_initialized",
            passed=has_init,
            expected="k_poll_signal_init() called before use",
            actual="present" if has_init else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: k_poll_signal_raise called (ISR side)
    has_raise = "k_poll_signal_raise" in generated_code
    details.append(
        CheckDetail(
            check_name="k_poll_signal_raise_in_isr",
            passed=has_raise,
            expected="k_poll_signal_raise() called (ISR-safe non-blocking)",
            actual="present" if has_raise else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: k_poll called (thread side)
    has_poll = "k_poll(" in generated_code
    details.append(
        CheckDetail(
            check_name="k_poll_in_thread",
            passed=has_poll,
            expected="k_poll() called in thread to wait for events",
            actual="present" if has_poll else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: K_POLL_EVENT_INITIALIZER or k_poll_event used
    has_event = "K_POLL_EVENT_INITIALIZER" in generated_code or "k_poll_event" in generated_code
    details.append(
        CheckDetail(
            check_name="poll_event_defined",
            passed=has_event,
            expected="k_poll_event array with K_POLL_EVENT_INITIALIZER",
            actual="present" if has_event else "missing",
            check_type="exact_match",
        )
    )

    return details
