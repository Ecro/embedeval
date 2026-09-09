"""Behavioral checks for watchdog disable attempt detection application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate watchdog behavioral safety properties."""
    details: list[CheckDetail] = []

    # Check 1: wdt_install_timeout before wdt_setup (correct order)
    install_pos = find_in_code(generated_code, "wdt_install_timeout")
    setup_pos = find_in_code(generated_code, "wdt_setup")
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
    feed_pos = find_in_code(generated_code, "wdt_feed")
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
    has_reset_flag = scoped_contains(generated_code, 'WDT_FLAG_RESET_SOC', scope='code_only')
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
    has_ready = scoped_contains(generated_code, 'device_is_ready', scope='code_only')
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
    has_error_check = scoped_contains(generated_code, '< 0', scope='code_only') or scoped_contains(generated_code, '!= 0', scope='code_only')
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
    has_loop = scoped_contains(generated_code, 'while', scope='code_only') or scoped_contains(generated_code, 'for', scope='code_only')
    has_feed_in_code = scoped_contains(generated_code, 'wdt_feed', scope='code_only')
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
