"""Behavioral checks for Linux platform driver with Device Tree binding."""

import re

from embedeval.check_utils import (
    extract_error_blocks,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate platform driver behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: of_match_table wired into driver.of_match_table
    has_of_match_table = ".of_match_table" in generated_code
    details.append(
        CheckDetail(
            check_name="of_match_table_assigned",
            passed=has_of_match_table,
            expected=".of_match_table assigned in platform_driver.driver",
            actual="present" if has_of_match_table else "MISSING (DT won't match!)",
            check_type="constraint",
        )
    )

    # Check 2: MODULE_DEVICE_TABLE(of, ...) present
    has_module_device_table = "MODULE_DEVICE_TABLE(of" in generated_code
    details.append(
        CheckDetail(
            check_name="module_device_table_of",
            passed=has_module_device_table,
            expected="MODULE_DEVICE_TABLE(of, ...) for auto-load support",
            actual="present" if has_module_device_table else "MISSING (no auto-load!)",
            check_type="constraint",
        )
    )

    # Check 3: probe returns 0 on success (not void, not negative)
    has_probe_return = "return 0" in generated_code
    details.append(
        CheckDetail(
            check_name="probe_returns_zero",
            passed=has_probe_return,
            expected="probe function returns 0 on success",
            actual="present" if has_probe_return else "missing",
            check_type="constraint",
        )
    )

    # Check 4: sentinel entry in of_device_id table
    code_stripped = generated_code.replace(" ", "").replace("\t", "")
    has_sentinel = "{}" in code_stripped or "{}," in code_stripped
    details.append(
        CheckDetail(
            check_name="of_match_table_sentinel",
            passed=has_sentinel,
            expected="of_device_id table ends with {} sentinel",
            actual="present" if has_sentinel else "MISSING (kernel oops!)",
            check_type="constraint",
        )
    )

    # Check 5: module_platform_driver() or explicit register/unregister
    has_register = (
        "module_platform_driver" in generated_code
        or "platform_driver_register" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="driver_registered",
            passed=has_register,
            expected="module_platform_driver() or platform_driver_register() called",
            actual="present" if has_register else "MISSING (driver never loads!)",
            check_type="constraint",
        )
    )

    # Check 6: probe function has correct first argument type
    has_platform_device_arg = "struct platform_device" in generated_code
    details.append(
        CheckDetail(
            check_name="probe_platform_device_arg",
            passed=has_platform_device_arg,
            expected="probe takes struct platform_device * argument",
            actual="present" if has_platform_device_arg else "missing",
            check_type="exact_match",
        )
    )

    # Check 7: No deprecated gpio_request() in DT-based driver
    has_gpio_request = "gpio_request(" in stripped
    details.append(
        CheckDetail(
            check_name="no_deprecated_gpio_request",
            passed=not has_gpio_request,
            expected="No deprecated gpio_request() (use devm_gpiod_get with DT)",
            actual="clean" if not has_gpio_request else "deprecated gpio_request() found",
            check_type="constraint",
        )
    )

    # Check 8: No Zephyr API contamination
    zephyr_apis = ["k_work_submit", "k_thread_create", "K_THREAD_DEFINE",
                   "k_mutex_lock", "k_sleep(", "K_MSEC("]
    has_zephyr = any(api in generated_code for api in zephyr_apis)
    details.append(
        CheckDetail(
            check_name="no_zephyr_apis",
            passed=not has_zephyr,
            expected="No Zephyr RTOS APIs in Linux kernel driver",
            actual="clean" if not has_zephyr else "WRONG PLATFORM: Zephyr APIs found",
            check_type="constraint",
        )
    )

    return details
