"""Static analysis checks for simple uptime counter application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate uptime counter code structure and required elements."""
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

    # Check 2: Uses k_uptime_get (not a custom counter)
    has_uptime_get = "k_uptime_get" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_uptime_get",
            passed=has_uptime_get,
            expected="k_uptime_get() used for uptime reading",
            actual="present" if has_uptime_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Uses k_sleep in loop (not a busy-wait)
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_sleep",
            passed=has_sleep,
            expected="k_sleep() used between uptime reads",
            actual="present" if has_sleep else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Uses int64_t for uptime (correct return type of k_uptime_get)
    has_int64 = "int64_t" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_int64_for_uptime",
            passed=has_int64,
            expected="int64_t used for uptime variable (return type of k_uptime_get)",
            actual="present" if has_int64 else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Infinite loop present (uptime should repeat)
    has_loop = "while (1)" in generated_code or "while(1)" in generated_code or "for (;;)" in generated_code
    details.append(
        CheckDetail(
            check_name="infinite_loop_present",
            passed=has_loop,
            expected="Infinite loop used for periodic uptime printing",
            actual="present" if has_loop else "missing",
            check_type="constraint",
        )
    )

    return details
