"""Static analysis checks for periodic kernel timer application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate timer code structure and required elements."""
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

    # Check 2: Uses K_TIMER_DEFINE or k_timer_init
    has_timer_def = (
        "K_TIMER_DEFINE" in generated_code or "k_timer_init" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="timer_defined",
            passed=has_timer_def,
            expected="K_TIMER_DEFINE or k_timer_init used",
            actual="present" if has_timer_def else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Uses k_timer_start
    has_timer_start = "k_timer_start" in generated_code
    details.append(
        CheckDetail(
            check_name="timer_started",
            passed=has_timer_start,
            expected="k_timer_start() called",
            actual="present" if has_timer_start else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Uses K_MSEC or K_SECONDS for duration
    has_duration = "K_MSEC" in generated_code or "K_SECONDS" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_duration_macro",
            passed=has_duration,
            expected="K_MSEC or K_SECONDS used for timer duration",
            actual="present" if has_duration else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Has a counter variable
    has_counter = "counter" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="counter_variable",
            passed=has_counter,
            expected="Counter variable defined",
            actual="present" if has_counter else "missing",
            check_type="exact_match",
        )
    )

    return details
