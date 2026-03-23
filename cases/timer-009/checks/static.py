"""Static analysis checks for semaphore timeout pattern application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate semaphore timeout code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/kernel.h
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

    # Check 2: Uses k_sem_take (not a polling pattern)
    has_sem_take = "k_sem_take" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_sem_take",
            passed=has_sem_take,
            expected="k_sem_take() used for event wait",
            actual="present" if has_sem_take else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Timeout is non-zero (not K_NO_WAIT)
    import re
    # k_sem_take must be called with a non-zero timeout (not K_NO_WAIT or K_MSEC(0))
    sem_take_zero = bool(re.search(r"k_sem_take\s*\([^,]+,\s*K_NO_WAIT\s*\)", generated_code))
    sem_take_zero_ms = bool(re.search(r"k_sem_take\s*\([^,]+,\s*K_MSEC\s*\(\s*0\s*\)\s*\)", generated_code))
    timeout_nonzero = not (sem_take_zero or sem_take_zero_ms)
    details.append(
        CheckDetail(
            check_name="sem_take_timeout_nonzero",
            passed=timeout_nonzero,
            expected="k_sem_take timeout > 0 (not K_NO_WAIT or K_MSEC(0))",
            actual="non-zero timeout" if timeout_nonzero else "zero/no-wait timeout found",
            check_type="constraint",
        )
    )

    # Check 4: k_timer or k_sem_give present (event source)
    has_event_source = "k_sem_give" in generated_code or "k_timer" in generated_code
    details.append(
        CheckDetail(
            check_name="event_source_defined",
            passed=has_event_source,
            expected="k_sem_give or k_timer present as event source",
            actual="present" if has_event_source else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Error/timeout path handled
    has_error_path = "-EAGAIN" in generated_code or "!= 0" in generated_code or "< 0" in generated_code
    details.append(
        CheckDetail(
            check_name="timeout_error_path_handled",
            passed=has_error_path,
            expected="Timeout/error path handled (-EAGAIN or return code check)",
            actual="present" if has_error_path else "missing",
            check_type="constraint",
        )
    )

    # Check 6: No busy-wait polling of semaphore
    has_busy_poll = bool(re.search(r"while\s*\([^)]*k_sem_count_get", generated_code))
    details.append(
        CheckDetail(
            check_name="no_busy_wait_semaphore_poll",
            passed=not has_busy_poll,
            expected="No busy-wait polling of semaphore count",
            actual="busy-wait found" if has_busy_poll else "clean",
            check_type="constraint",
        )
    )

    return details
