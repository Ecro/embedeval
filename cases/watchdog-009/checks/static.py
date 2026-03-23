"""Static analysis checks for window watchdog application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate window watchdog code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/drivers/watchdog.h
    has_wdt_h = "zephyr/drivers/watchdog.h" in generated_code
    details.append(
        CheckDetail(
            check_name="watchdog_header_included",
            passed=has_wdt_h,
            expected="zephyr/drivers/watchdog.h included",
            actual="present" if has_wdt_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: window.min is set and is > 0
    import re
    min_match = re.search(r"window\.min\s*=\s*(\d+)", generated_code)
    min_nonzero = bool(min_match and int(min_match.group(1)) > 0)
    details.append(
        CheckDetail(
            check_name="window_min_greater_than_zero",
            passed=min_nonzero,
            expected="window.min > 0 (enforces minimum feed time)",
            actual=min_match.group(0) if min_match else "window.min not found",
            check_type="constraint",
        )
    )

    # Check 3: window.max is set and is > 0
    max_match = re.search(r"window\.max\s*=\s*(\d+)", generated_code)
    max_nonzero = bool(max_match and int(max_match.group(1)) > 0)
    details.append(
        CheckDetail(
            check_name="window_max_greater_than_zero",
            passed=max_nonzero,
            expected="window.max > 0",
            actual=max_match.group(0) if max_match else "window.max not found",
            check_type="constraint",
        )
    )

    # Check 4: window.min < window.max (valid window constraint)
    valid_window = False
    if min_match and max_match:
        min_val = int(min_match.group(1))
        max_val = int(max_match.group(1))
        valid_window = min_val > 0 and min_val < max_val
    details.append(
        CheckDetail(
            check_name="window_min_less_than_max",
            passed=valid_window,
            expected="window.min > 0 AND window.min < window.max",
            actual=f"min={min_match.group(1) if min_match else '?'}, max={max_match.group(1) if max_match else '?'}",
            check_type="constraint",
        )
    )

    # Check 5: wdt_install_timeout and wdt_setup called
    has_install = "wdt_install_timeout" in generated_code
    has_setup = "wdt_setup" in generated_code
    details.append(
        CheckDetail(
            check_name="wdt_configured",
            passed=has_install and has_setup,
            expected="wdt_install_timeout() and wdt_setup() both called",
            actual=f"install={has_install}, setup={has_setup}",
            check_type="exact_match",
        )
    )

    # Check 6: wdt_feed called
    has_feed = "wdt_feed" in generated_code
    details.append(
        CheckDetail(
            check_name="wdt_feed_called",
            passed=has_feed,
            expected="wdt_feed() called",
            actual="present" if has_feed else "missing",
            check_type="exact_match",
        )
    )

    return details
