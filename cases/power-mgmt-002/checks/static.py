"""Static analysis checks for simple system sleep."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sleep code structure and required elements."""
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

    # Check 2: k_sleep used (not busy-wait)
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="k_sleep_used",
            passed=has_sleep,
            expected="k_sleep() called for CPU yield",
            actual="present" if has_sleep else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: K_MSEC used with k_sleep
    has_kmsec = "K_MSEC" in generated_code
    details.append(
        CheckDetail(
            check_name="k_msec_time_macro",
            passed=has_kmsec,
            expected="K_MSEC() time macro used",
            actual="present" if has_kmsec else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: k_uptime_get called for timestamps
    has_uptime = "k_uptime_get" in generated_code
    details.append(
        CheckDetail(
            check_name="k_uptime_get_used",
            passed=has_uptime,
            expected="k_uptime_get() called for timestamps",
            actual="present" if has_uptime else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: No busy-wait loop (k_busy_wait is forbidden here)
    has_busy_wait = "k_busy_wait" in generated_code
    details.append(
        CheckDetail(
            check_name="no_busy_wait",
            passed=not has_busy_wait,
            expected="k_busy_wait() NOT used (must use k_sleep)",
            actual="busy-wait present" if has_busy_wait else "absent",
            check_type="exact_match",
        )
    )

    return details
