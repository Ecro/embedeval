"""Static checks for ESP-IDF GPIO blink."""
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    details.append(CheckDetail(
        check_name="gpio_header",
        passed="driver/gpio.h" in generated_code,
        expected="driver/gpio.h included",
        actual="present" if "driver/gpio.h" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="app_main_defined",
        passed="app_main" in generated_code,
        expected="app_main() entry point",
        actual="present" if "app_main" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="gpio_config_used",
        passed="gpio_config" in generated_code,
        expected="gpio_config() or gpio_set_direction()",
        actual="present" if "gpio_config" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="gpio_set_level_used",
        passed="gpio_set_level" in generated_code,
        expected="gpio_set_level() called",
        actual="present" if "gpio_set_level" in generated_code else "missing",
        check_type="exact_match",
    ))

    # Cross-platform hallucination check: no Zephyr APIs
    zephyr_apis = ["k_sleep", "gpio_pin_configure", "DEVICE_DT_GET", "printk"]
    found = [api for api in zephyr_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_zephyr_apis",
        passed=not found,
        expected="No Zephyr APIs in ESP-IDF code",
        actual="clean" if not found else f"found Zephyr APIs: {found}",
        check_type="hallucination",
    ))

    return details
