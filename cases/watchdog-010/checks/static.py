"""Static analysis checks for watchdog with NVS persistent reboot counter."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import has_output_call


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate watchdog + NVS code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: kernel.h included
    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header_included",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: watchdog header included
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

    # Check 3: NVS or settings header included (persistent storage)
    has_nvs_h = "zephyr/fs/nvs.h" in generated_code or "nvs.h" in generated_code
    has_settings_h = "zephyr/settings/settings.h" in generated_code
    has_persistent = has_nvs_h or has_settings_h
    details.append(
        CheckDetail(
            check_name="persistent_storage_header_included",
            passed=has_persistent,
            expected="NVS (nvs.h) or settings (settings.h) header included",
            actual="present"
            if has_persistent
            else "missing — no persistent storage API",
            check_type="exact_match",
        )
    )

    # Check 4: No FreeRTOS contamination
    has_freertos = bool(
        re.search(r"FreeRTOS\.h|xTask|vTask|xSemaphore", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="no_freertos_contamination",
            passed=not has_freertos,
            expected="No FreeRTOS APIs in Zephyr application",
            actual="clean" if not has_freertos else "FreeRTOS APIs found",
            check_type="constraint",
        )
    )

    # Check 5: output call present for status output
    has_output = has_output_call(generated_code)
    details.append(
        CheckDetail(
            check_name="printk_present",
            passed=has_output,
            expected="printk/printf/LOG_* used for status output",
            actual="present" if has_output else "missing",
            check_type="exact_match",
        )
    )

    return details
