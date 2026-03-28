"""Behavioral checks for dual-channel watchdog application."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate dual-channel watchdog behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: install_timeout before setup (correct ordering)
    install_pos = generated_code.find("wdt_install_timeout")
    setup_pos = generated_code.find("wdt_setup")
    order_ok = install_pos != -1 and setup_pos != -1 and install_pos < setup_pos
    details.append(
        CheckDetail(
            check_name="install_before_setup",
            passed=order_ok,
            expected="wdt_install_timeout() called before wdt_setup()",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Two different timeout windows (distinct .max values)
    # AI failure: using same timeout for both channels
    max_values = set(int(m.group(1)) for m in re.finditer(r"\.max\s*=\s*(\d+)", generated_code))
    has_distinct_timeouts = len(max_values) >= 2
    details.append(
        CheckDetail(
            check_name="distinct_channel_timeouts",
            passed=has_distinct_timeouts,
            expected="At least 2 distinct .max timeout values for different channels",
            actual=f"found {len(max_values)} distinct value(s): {sorted(max_values)}",
            check_type="exact_match",
        )
    )

    # Check 3: Both channel IDs used in wdt_feed (not just one)
    # AI failure: feeding only one channel
    feed_count = generated_code.count("wdt_feed")
    feeds_both = feed_count >= 2
    details.append(
        CheckDetail(
            check_name="feeds_both_channels",
            passed=feeds_both,
            expected="wdt_feed() called for both channels (at least 2 calls)",
            actual=f"{feed_count} wdt_feed calls found",
            check_type="constraint",
        )
    )

    # Check 4: Channel IDs from install stored separately (two separate variables)
    # Check for two separate assignments from wdt_install_timeout
    install_assignments = re.findall(
        r"(\w+)\s*=\s*wdt_install_timeout\s*\(", generated_code
    )
    has_distinct_ids = len(set(install_assignments)) >= 2
    details.append(
        CheckDetail(
            check_name="channel_ids_stored_separately",
            passed=has_distinct_ids,
            expected="Two distinct variables store the channel IDs",
            actual=(
                f"distinct vars: {set(install_assignments)}"
                if install_assignments
                else "no assignments found"
            ),
            check_type="constraint",
        )
    )

    # Check 5: WDT_FLAG_RESET_SOC used for both channels
    # Accept either: flag appears >= 2 times, or flag appears once + struct reuse
    # (wdt_install_timeout called >= 2 times with shared config)
    reset_flag_count = generated_code.count("WDT_FLAG_RESET_SOC")
    install_count = generated_code.count("wdt_install_timeout")
    has_reset_flags = (
        reset_flag_count >= 2
        or (reset_flag_count >= 1 and install_count >= 2)
    )
    details.append(
        CheckDetail(
            check_name="reset_flag_on_both_channels",
            passed=has_reset_flags,
            expected="WDT_FLAG_RESET_SOC used on both channel configurations",
            actual=f"{reset_flag_count} WDT_FLAG_RESET_SOC, {install_count} wdt_install_timeout",
            check_type="constraint",
        )
    )

    # Check 6: device_is_ready check present
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() check before WDT operations",
            actual="present" if has_ready else "missing",
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
