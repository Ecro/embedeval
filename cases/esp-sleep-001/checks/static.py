"""Static checks for ESP-IDF deep sleep with GPIO wakeup."""
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: Sleep header present
    has_sleep_header = "esp_sleep.h" in generated_code
    details.append(CheckDetail(
        check_name="esp_sleep_header",
        passed=has_sleep_header,
        expected="esp_sleep.h included",
        actual="present" if has_sleep_header else "missing",
        check_type="exact_match",
    ))

    # Check 2: app_main entry point
    details.append(CheckDetail(
        check_name="app_main_defined",
        passed="app_main" in generated_code,
        expected="app_main() entry point",
        actual="present" if "app_main" in generated_code else "missing",
        check_type="exact_match",
    ))

    # Check 3: Deep sleep used (not light sleep — task requires lowest-power mode)
    has_deep_sleep = "esp_deep_sleep_start" in generated_code
    details.append(CheckDetail(
        check_name="deep_sleep_used",
        passed=has_deep_sleep,
        expected="esp_deep_sleep_start() called for lowest-power sleep",
        actual="present" if has_deep_sleep else "missing (using light sleep instead?)",
        check_type="exact_match",
    ))

    # Check 4: EXT0 or EXT1 wakeup configured (GPIO-based wakeup)
    has_gpio_wakeup = (
        "esp_sleep_enable_ext0_wakeup" in generated_code
        or "esp_sleep_enable_ext1_wakeup" in generated_code
        or "esp_sleep_enable_gpio_wakeup" in generated_code
    )
    details.append(CheckDetail(
        check_name="gpio_wakeup_configured",
        passed=has_gpio_wakeup,
        expected="GPIO wakeup source configured (ext0/ext1/gpio_wakeup)",
        actual="present" if has_gpio_wakeup else "missing",
        check_type="exact_match",
    ))

    # Check 5: No Zephyr PM APIs
    zephyr_pm_apis = ["pm_device_action_run", "k_sleep", "pm_state_set", "PM_STATE_SOFT_OFF"]
    found = [api for api in zephyr_pm_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_zephyr_pm_apis",
        passed=not found,
        expected="No Zephyr power management APIs in ESP-IDF code",
        actual="clean" if not found else f"found Zephyr PM APIs: {found}",
        check_type="hallucination",
    ))

    return details
