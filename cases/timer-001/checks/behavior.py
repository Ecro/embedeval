"""Behavioral checks for periodic kernel timer application."""

import re

from embedeval.models import CheckDetail


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

    return details
