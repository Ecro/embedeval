"""Behavioral checks for ESP-IDF deep sleep with GPIO wakeup."""
from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: Wakeup source configured before entering sleep
    wakeup_cfg_pos = -1
    for fn in ["esp_sleep_enable_ext0_wakeup", "esp_sleep_enable_ext1_wakeup",
               "esp_sleep_enable_gpio_wakeup"]:
        pos = generated_code.find(fn)
        if pos != -1:
            wakeup_cfg_pos = pos
            break

    sleep_pos = generated_code.find("esp_deep_sleep_start")
    wakeup_before_sleep = wakeup_cfg_pos != -1 and sleep_pos != -1 and wakeup_cfg_pos < sleep_pos
    details.append(CheckDetail(
        check_name="wakeup_source_configured_before_sleep",
        passed=wakeup_before_sleep,
        expected="Wakeup source configured before esp_deep_sleep_start()",
        actual="correct order" if wakeup_before_sleep else "wrong order or missing configuration",
        check_type="constraint",
    ))

    # Check 2: Wakeup cause checked on boot
    has_wakeup_cause_check = "esp_sleep_get_wakeup_cause" in generated_code
    details.append(CheckDetail(
        check_name="wakeup_cause_checked",
        passed=has_wakeup_cause_check,
        expected="esp_sleep_get_wakeup_cause() called to determine boot reason",
        actual="present" if has_wakeup_cause_check else "missing",
        check_type="constraint",
    ))

    # Check 3: GPIO pull configured for proper low-level detection
    has_pullup = (
        "GPIO_PULLUP_ENABLE" in generated_code
        or "pull_up_en" in generated_code
        or "gpio_pullup_en" in generated_code
    )
    details.append(CheckDetail(
        check_name="gpio_pull_configured",
        passed=has_pullup,
        expected="GPIO pull-up configured for low-level wakeup detection",
        actual="present" if has_pullup else "missing (floating input may cause spurious wakeups)",
        check_type="constraint",
    ))

    # Check 4: EXT0 wakeup level is 0 (low) for GPIO 0 button press
    has_low_level = (
        "ext0_wakeup" in generated_code
        and ", 0)" in generated_code
    )
    details.append(CheckDetail(
        check_name="ext0_wakeup_level_low",
        passed=has_low_level,
        expected="EXT0 wakeup configured with level=0 (active-low button)",
        actual="present" if has_low_level else "missing or wrong level",
        check_type="constraint",
    ))

    # Check 5: No FreeRTOS vTaskDelay used as the sleep mechanism
    # vTaskDelay is acceptable for pre-sleep delay, but must not replace esp_deep_sleep_start
    has_deep_sleep = "esp_deep_sleep_start" in generated_code
    details.append(CheckDetail(
        check_name="deep_sleep_not_replaced_by_delay",
        passed=has_deep_sleep,
        expected="esp_deep_sleep_start() used, not a delay loop",
        actual="present" if has_deep_sleep else "missing — vTaskDelay is not deep sleep",
        check_type="constraint",
    ))

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace", "FreeRTOS"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
