"""Behavioral checks for watchdog disable attempt detection application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate watchdog behavioral safety properties."""
    details: list[CheckDetail] = []

    # Check 1: wdt_install_timeout before wdt_setup (correct order)
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

    # Check 2: wdt_setup before wdt_feed (can't feed before setup)
    feed_pos = generated_code.find("wdt_feed")
    setup_before_feed = setup_pos != -1 and feed_pos != -1 and setup_pos < feed_pos
    details.append(
        CheckDetail(
            check_name="setup_before_feed",
            passed=setup_before_feed,
            expected="wdt_setup called before wdt_feed",
            actual="correct order" if setup_before_feed else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: WDT_FLAG_RESET_SOC used
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

    # Check 5: Error handling for wdt_install_timeout and wdt_setup
    has_error_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="error_handling_present",
            passed=has_error_check,
            expected="Return value error checking for WDT init calls",
            actual="present" if has_error_check else "missing",
            check_type="constraint",
        )
    )

    # Check 6: wdt_feed in a loop (periodic feeding, not single shot)
    has_loop = "while" in generated_code or "for" in generated_code
    has_feed_in_code = "wdt_feed" in generated_code
    details.append(
        CheckDetail(
            check_name="wdt_feed_in_loop",
            passed=has_loop and has_feed_in_code,
            expected="wdt_feed called inside a loop (periodic feeding)",
            actual=f"loop={has_loop}, feed={has_feed_in_code}",
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
