"""Behavioral checks for watchdog pre-timeout ISR callback application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate watchdog ISR callback behavioral properties and ISR constraints."""
    details: list[CheckDetail] = []

    # Check 1: ISR callback does NOT call k_sleep (blocking in ISR is forbidden)
    import re
    # Find callback function body heuristically
    callback_match = re.search(
        r"(static\s+)?void\s+wdt_callback\s*\([^)]*\)\s*\{([^}]*)\}",
        generated_code,
    )
    isr_has_sleep = False
    isr_has_wdt_feed = False
    if callback_match:
        isr_body = callback_match.group(2)
        isr_has_sleep = "k_sleep" in isr_body
        isr_has_wdt_feed = "wdt_feed" in isr_body
    details.append(
        CheckDetail(
            check_name="isr_no_k_sleep",
            passed=not isr_has_sleep,
            expected="ISR callback does not call k_sleep (blocking forbidden in ISR)",
            actual="blocking call found" if isr_has_sleep else "non-blocking",
            check_type="constraint",
        )
    )

    # Check 2: ISR callback does NOT call wdt_feed (feeding in pre-timeout callback is wrong)
    details.append(
        CheckDetail(
            check_name="isr_no_wdt_feed",
            passed=not isr_has_wdt_feed,
            expected="ISR callback does not call wdt_feed (pre-timeout callback, not feed point)",
            actual="wdt_feed in ISR" if isr_has_wdt_feed else "clean",
            check_type="constraint",
        )
    )

    # Check 3: wdt_install_timeout before wdt_setup (correct ordering)
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

    # Check 5: Error handling for wdt_install_timeout return value
    has_error_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="error_handling_present",
            passed=has_error_check,
            expected="Return value error checking present",
            actual="present" if has_error_check else "missing",
            check_type="constraint",
        )
    )

    # Check 6: wdt_feed called at some point in the main code path
    has_wdt_feed = "wdt_feed" in generated_code
    details.append(
        CheckDetail(
            check_name="wdt_feed_called_in_main",
            passed=has_wdt_feed,
            expected="wdt_feed() called (normal feeding path)",
            actual="present" if has_wdt_feed else "missing",
            check_type="exact_match",
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
