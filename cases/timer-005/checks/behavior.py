"""Behavioral checks for multi-timer coordination application."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-timer coordination behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: 100ms timer period present
    has_100ms = bool(re.search(r"K_MSEC\s*\(\s*100\s*\)", generated_code))
    details.append(
        CheckDetail(
            check_name="fast_timer_100ms",
            passed=has_100ms,
            expected="K_MSEC(100) used for fast timer period",
            actual="present" if has_100ms else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: 250ms timer period present
    has_250ms = bool(re.search(r"K_MSEC\s*\(\s*250\s*\)", generated_code))
    details.append(
        CheckDetail(
            check_name="mid_timer_250ms",
            passed=has_250ms,
            expected="K_MSEC(250) used for mid timer period",
            actual="present" if has_250ms else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: 1000ms timer period present
    has_1000ms = bool(
        re.search(r"K_MSEC\s*\(\s*1000\s*\)|K_SECONDS\s*\(\s*1\s*\)", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="slow_timer_1000ms",
            passed=has_1000ms,
            expected="K_MSEC(1000) or K_SECONDS(1) used for slow timer period",
            actual="present" if has_1000ms else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: atomic_inc used in timer callbacks, not ++ on shared state
    # AI failure: using counter++ in timer expiry without atomics
    uses_atomic_inc = "atomic_inc" in generated_code
    uses_bare_increment = bool(
        re.search(r"(?:fast|mid|slow|count)\w*\s*\+\+", generated_code)
        and not uses_atomic_inc
    )
    details.append(
        CheckDetail(
            check_name="atomic_increment_in_callbacks",
            passed=uses_atomic_inc and not uses_bare_increment,
            expected="atomic_inc() used in timer callbacks (not bare ++ on shared state)",
            actual=(
                "correct atomic" if uses_atomic_inc
                else "bare ++ detected - race condition risk"
            ),
            check_type="constraint",
        )
    )

    # Check 5: Three separate expiry functions (one per timer)
    expiry_fn_count = len(re.findall(
        r"void\s+\w+\s*\(\s*struct\s+k_timer\s*\*", generated_code
    ))
    has_three_expiry = expiry_fn_count >= 3
    details.append(
        CheckDetail(
            check_name="three_expiry_functions",
            passed=has_three_expiry,
            expected="3 expiry functions defined (one per timer)",
            actual=f"{expiry_fn_count} expiry functions found",
            check_type="exact_match",
        )
    )

    # Check 6: Main loop uses k_sleep (not busy-wait between prints)
    has_sleep_in_loop = "k_sleep" in generated_code and (
        "while" in generated_code or "for" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="main_loop_with_sleep",
            passed=has_sleep_in_loop,
            expected="Main loop uses k_sleep between counter prints",
            actual="present" if has_sleep_in_loop else "missing or busy-wait",
            check_type="constraint",
        )
    )

    return details
