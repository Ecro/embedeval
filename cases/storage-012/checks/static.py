"""Static analysis checks for Flash-Wear-Aware Persistent Data Logger."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate structural requirements for NVS persistent data logger."""
    details: list[CheckDetail] = []

    # Check 1: kernel.h included
    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_h_included",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: NVS or settings header included
    has_nvs_h = (
        "zephyr/fs/nvs.h" in generated_code
        or "zephyr/settings/settings.h" in generated_code
        or "nvs.h" in generated_code
        or "settings.h" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="nvs_header_included",
            passed=has_nvs_h,
            expected="NVS or settings header included (zephyr/fs/nvs.h or zephyr/settings/settings.h)",
            actual="present" if has_nvs_h else "missing — no persistent storage header",
            check_type="exact_match",
        )
    )

    # Check 3: No FreeRTOS contamination
    freertos_apis = [
        "xTaskCreate", "vTaskDelay", "xQueueSend", "FreeRTOS",
        "portTICK_PERIOD_MS", "TaskHandle_t", "QueueHandle_t",
    ]
    found_freertos = [api for api in freertos_apis if api in generated_code]
    details.append(
        CheckDetail(
            check_name="no_freertos_apis",
            passed=len(found_freertos) == 0,
            expected="No FreeRTOS APIs (Zephyr-only implementation)",
            actual="clean" if not found_freertos else f"found: {found_freertos}",
            check_type="constraint",
        )
    )

    # Check 4: main function present
    has_main = bool(re.search(r'\b(?:int|void)\s+main\s*\(', generated_code))
    details.append(
        CheckDetail(
            check_name="main_function_present",
            passed=has_main,
            expected="main() function present",
            actual="present" if has_main else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: No stdio.h (use printk, not printf)
    has_stdio = "#include <stdio.h>" in generated_code
    details.append(
        CheckDetail(
            check_name="no_stdio_h",
            passed=not has_stdio,
            expected="No stdio.h (use printk for Zephyr logging)",
            actual="clean" if not has_stdio else "stdio.h included — use printk instead of printf",
            check_type="constraint",
        )
    )

    return details
