"""Static analysis checks for multi-timer coordination application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-timer coordination code structure and required elements."""
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

    # Check 2: Uses atomic_t for shared counters (AI failure: using plain int or volatile int)
    has_atomic_t = "atomic_t" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_type_used",
            passed=has_atomic_t,
            expected="atomic_t used for shared counters",
            actual="present" if has_atomic_t else "missing - may use non-atomic type",
            check_type="constraint",
        )
    )

    # Check 3: Uses atomic_inc for incrementing (AI failure: using ++ on shared state)
    has_atomic_inc = "atomic_inc" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_inc_used",
            passed=has_atomic_inc,
            expected="atomic_inc() used in timer callbacks",
            actual="present" if has_atomic_inc else "missing - may use non-atomic increment",
            check_type="constraint",
        )
    )

    # Check 4: Uses atomic_get for reading (AI failure: direct read of atomic_t)
    has_atomic_get = "atomic_get" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_get_used",
            passed=has_atomic_get,
            expected="atomic_get() used to read atomic counters",
            actual="present" if has_atomic_get else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Defines at least 3 timers (100ms, 250ms, 1000ms rates)
    timer_define_count = generated_code.count("K_TIMER_DEFINE")
    has_three_timers = timer_define_count >= 3
    details.append(
        CheckDetail(
            check_name="three_timers_defined",
            passed=has_three_timers,
            expected="3 K_TIMER_DEFINE calls for three timers",
            actual=f"{timer_define_count} K_TIMER_DEFINE found",
            check_type="exact_match",
        )
    )

    # Check 6: Uses K_MSEC for timer periods
    has_msec = "K_MSEC" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_msec_for_periods",
            passed=has_msec,
            expected="K_MSEC() used for timer periods",
            actual="present" if has_msec else "missing",
            check_type="exact_match",
        )
    )

    return details
