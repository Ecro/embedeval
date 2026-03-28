"""Behavioral checks for watchdog timer application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis, has_sleep_call


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate watchdog behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: install_timeout before setup (correct ordering)
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

    # Check 2: setup before feed (correct ordering)
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

    # Check 3: Device ready check present
    has_ready = "device_is_ready" in generated_code or "gpio_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() check before WDT operations",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 4: WDT_FLAG_RESET_SOC used (proper reset action)
    has_reset_flag = "WDT_FLAG_RESET_SOC" in generated_code
    details.append(
        CheckDetail(
            check_name="reset_soc_flag",
            passed=has_reset_flag,
            expected="WDT_FLAG_RESET_SOC flag used",
            actual="present" if has_reset_flag else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Feed in a loop (periodic feeding)
    has_loop = "while" in generated_code or "for" in generated_code
    has_sleep_in_loop = has_sleep_call(generated_code) and has_loop
    details.append(
        CheckDetail(
            check_name="periodic_feed_in_loop",
            passed=has_sleep_in_loop,
            expected="wdt_feed in loop with k_sleep/k_msleep (periodic feeding)",
            actual=f"loop={has_loop}, sleep={has_sleep_in_loop}",
            check_type="constraint",
        )
    )

    # Check 6: Error handling for install/setup return values
    has_error_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="error_handling",
            passed=has_error_check,
            expected="Return value error checking for WDT APIs",
            actual="present" if has_error_check else "missing",
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
