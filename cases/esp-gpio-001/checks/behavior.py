"""Behavioral checks for ESP-IDF GPIO blink."""
from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: Error handling on gpio_config
    # Search for the function call form "gpio_config(" to skip the struct type "gpio_config_t"
    config_pos = generated_code.find("gpio_config(")
    post_config = generated_code[config_pos:config_pos + 200] if config_pos != -1 else ""
    has_error_check = "ESP_OK" in post_config or "!= ESP_OK" in post_config or "ret" in post_config
    details.append(CheckDetail(
        check_name="gpio_config_error_checked",
        passed=has_error_check,
        expected="gpio_config() return value checked",
        actual="present" if has_error_check else "missing",
        check_type="constraint",
    ))

    # Check 2: vTaskDelay used (not busy-wait)
    has_delay = "vTaskDelay" in generated_code
    details.append(CheckDetail(
        check_name="vtaskdelay_used",
        passed=has_delay,
        expected="vTaskDelay() for non-blocking delay",
        actual="present" if has_delay else "missing (busy-wait?)",
        check_type="constraint",
    ))

    # Check 3: pdMS_TO_TICKS or portTICK_PERIOD_MS used (not raw tick count)
    has_tick_macro = (
        "pdMS_TO_TICKS" in generated_code
        or "portTICK_PERIOD_MS" in generated_code
    )
    details.append(CheckDetail(
        check_name="tick_conversion_macro",
        passed=has_tick_macro,
        expected="pdMS_TO_TICKS() or portTICK_PERIOD_MS for portable delays",
        actual="present" if has_tick_macro else "missing (raw tick count is non-portable)",
        check_type="constraint",
    ))

    # Check 4: gpio_config_t struct used (not deprecated individual calls)
    has_config_struct = "gpio_config_t" in generated_code
    details.append(CheckDetail(
        check_name="gpio_config_struct",
        passed=has_config_struct,
        expected="gpio_config_t struct for configuration",
        actual="present" if has_config_struct else "missing (using deprecated API?)",
        check_type="constraint",
    ))

    # Check 5: No Arduino APIs
    arduino_apis = ["digitalWrite", "pinMode", "delay(", "Serial."]
    found = [api for api in arduino_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_arduino_apis",
        passed=not found,
        expected="No Arduino APIs",
        actual="clean" if not found else f"found: {found}",
        check_type="hallucination",
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
