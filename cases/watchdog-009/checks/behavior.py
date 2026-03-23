"""Behavioral checks for window watchdog application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate window watchdog behavioral properties and timing constraints."""
    details: list[CheckDetail] = []

    # Check 1: Sleep between feeds respects window minimum
    # Heuristic: sleep duration in ms must be >= window.min
    import re
    min_match = re.search(r"window\.min\s*=\s*(\d+)", generated_code)
    max_match = re.search(r"window\.max\s*=\s*(\d+)", generated_code)
    sleep_ms_match = re.search(r"K_MSEC\s*\(\s*(\d+)\s*\)", generated_code)
    sleep_s_match = re.search(r"K_SECONDS\s*\(\s*(\d+)\s*\)", generated_code)

    sleep_ms = 0
    if sleep_ms_match:
        sleep_ms = int(sleep_ms_match.group(1))
    elif sleep_s_match:
        sleep_ms = int(sleep_s_match.group(1)) * 1000

    window_min = int(min_match.group(1)) if min_match else 0
    window_max = int(max_match.group(1)) if max_match else 0

    sleep_in_window = sleep_ms >= window_min and (window_max == 0 or sleep_ms < window_max)
    details.append(
        CheckDetail(
            check_name="feed_sleep_within_window",
            passed=sleep_in_window or sleep_ms == 0,
            expected=f"Sleep duration [{sleep_ms}ms] within window [{window_min}ms, {window_max}ms]",
            actual=f"sleep={sleep_ms}ms, min={window_min}ms, max={window_max}ms",
            check_type="constraint",
        )
    )

    # Check 2: wdt_install_timeout before wdt_setup
    install_pos = generated_code.find("wdt_install_timeout")
    setup_pos = generated_code.find("wdt_setup")
    order_ok = install_pos != -1 and setup_pos != -1 and install_pos < setup_pos
    details.append(
        CheckDetail(
            check_name="install_before_setup",
            passed=order_ok,
            expected="wdt_install_timeout called before wdt_setup",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: wdt_feed in loop (periodic with sleep for windowed feeding)
    feed_pos = generated_code.find("wdt_feed")
    loop_pos = max(generated_code.find("while"), generated_code.find("for ("))
    feed_in_loop = feed_pos != -1 and loop_pos != -1 and feed_pos > loop_pos
    details.append(
        CheckDetail(
            check_name="wdt_feed_in_loop",
            passed=feed_in_loop,
            expected="wdt_feed called inside a loop (periodic windowed feeding)",
            actual="inside loop" if feed_in_loop else "outside loop or missing",
            check_type="constraint",
        )
    )

    # Check 4: device_is_ready check present
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() called before WDT operations",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 5: WDT_FLAG_RESET_SOC used
    has_reset_flag = "WDT_FLAG_RESET_SOC" in generated_code
    details.append(
        CheckDetail(
            check_name="reset_soc_flag",
            passed=has_reset_flag,
            expected="WDT_FLAG_RESET_SOC used",
            actual="present" if has_reset_flag else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Error handling present
    has_error_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="error_handling_present",
            passed=has_error_check,
            expected="Return value error checking for WDT APIs",
            actual="present" if has_error_check else "missing",
            check_type="constraint",
        )
    )

    return details
