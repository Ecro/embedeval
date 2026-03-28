"""Behavioral checks for periodic kernel timer application."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate timer behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Expiry function increments counter
    has_increment = "++" in generated_code or "+= 1" in generated_code
    details.append(
        CheckDetail(
            check_name="expiry_increments_counter",
            passed=has_increment,
            expected="Counter incremented in expiry function",
            actual="present" if has_increment else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Counter is volatile (ISR-safe access)
    has_volatile = "volatile" in generated_code and "counter" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="counter_is_volatile",
            passed=has_volatile,
            expected="Counter declared volatile for ISR-safe access",
            actual="present" if has_volatile else "missing",
            check_type="constraint",
        )
    )

    # Check 3: Timer period uses 500ms (as specified)
    has_500ms = bool(re.search(r"K_MSEC\s*\(\s*500\s*\)", generated_code))
    details.append(
        CheckDetail(
            check_name="timer_period_500ms",
            passed=has_500ms,
            expected="Timer period set to K_MSEC(500)",
            actual="present" if has_500ms else "missing or wrong value",
            check_type="exact_match",
        )
    )

    # Check 4: Main loop with sleep (not busy-wait)
    has_sleep = "k_sleep" in generated_code
    has_loop = "while" in generated_code or "for" in generated_code
    details.append(
        CheckDetail(
            check_name="main_loop_with_sleep",
            passed=has_sleep and has_loop,
            expected="Main loop uses k_sleep (not busy-wait)",
            actual=f"sleep={has_sleep}, loop={has_loop}",
            check_type="constraint",
        )
    )

    # Check 5: Expiry function has correct signature (struct k_timer *)
    has_timer_param = bool(
        re.search(r"\w+\s*\(\s*struct\s+k_timer\s*\*", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="expiry_function_signature",
            passed=has_timer_param,
            expected="Expiry function takes struct k_timer * parameter",
            actual="correct signature" if has_timer_param else "wrong signature",
            check_type="exact_match",
        )
    )

    # Check: timer period explicitly configured with a value
    has_period = bool(re.search(r'K_MSEC\s*\(\s*\d+\s*\)|K_SECONDS\s*\(\s*\d+\s*\)', generated_code))
    details.append(
        CheckDetail(
            check_name="timer_period_configured",
            passed=has_period,
            expected="Timer period explicitly configured (K_MSEC or K_SECONDS)",
            actual="period set" if has_period else "no explicit timer period",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
