"""Behavioral checks for watchdog with callback application."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate watchdog callback behavioral properties and domain invariants."""
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

    # Check 2: Callback function does NOT block (no k_sleep, printk-heavy loops allowed)
    # AI failure: doing heavy work or blocking in WDT callback
    callback_fn_match = re.search(
        r"void\s+\w+\s*\(\s*const\s+struct\s+device\s*\*[^)]*\)\s*\{([^}]*)\}",
        generated_code,
        re.DOTALL,
    )
    callback_body = callback_fn_match.group(1) if callback_fn_match else ""
    callback_blocks = bool(
        re.search(r"k_sleep|k_msleep|while\s*\(|for\s*\(", callback_body)
    )
    details.append(
        CheckDetail(
            check_name="callback_does_not_block",
            passed=not callback_blocks,
            expected="WDT callback does not block (no k_sleep or loops)",
            actual="no blocking" if not callback_blocks else "blocking detected in callback",
            check_type="constraint",
        )
    )

    # Check 3: WDT_FLAG_RESET_SOC used
    has_reset_flag = "WDT_FLAG_RESET_SOC" in generated_code
    details.append(
        CheckDetail(
            check_name="reset_soc_flag",
            passed=has_reset_flag,
            expected="WDT_FLAG_RESET_SOC flag used in timeout config",
            actual="present" if has_reset_flag else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: wdt_feed called in main before eventually stopping
    feed_pos = generated_code.find("wdt_feed")
    setup_pos2 = generated_code.find("wdt_setup")
    feed_after_setup = (
        feed_pos != -1 and setup_pos2 != -1 and feed_pos > setup_pos2
    )
    details.append(
        CheckDetail(
            check_name="feed_after_setup",
            passed=feed_after_setup,
            expected="wdt_feed() called after wdt_setup() in main",
            actual="correct order" if feed_after_setup else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 5: Callback is non-NULL in wdt_timeout_cfg (assigned a function pointer)
    # More robust check: a function is defined that matches the WDT callback signature
    has_callback_fn = bool(
        re.search(
            r"void\s+\w+\s*\(\s*const\s+struct\s+device\s*\*\s*\w*\s*,\s*int\s+\w*",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="callback_function_defined",
            passed=has_callback_fn,
            expected="WDT callback function defined with correct signature",
            actual="present" if has_callback_fn else "missing or wrong signature",
            check_type="exact_match",
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
