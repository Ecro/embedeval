"""Behavioral checks for ESP-IDF high-resolution periodic timer."""
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: Callback function defined (must be a proper function, not a lambda)
    has_callback_fn = ".callback" in generated_code and "void" in generated_code
    details.append(CheckDetail(
        check_name="callback_function_defined",
        passed=has_callback_fn,
        expected="Callback function defined and assigned via .callback field",
        actual="present" if has_callback_fn else "missing",
        check_type="constraint",
    ))

    # Check 2: esp_timer_create error checked
    create_pos = generated_code.find("esp_timer_create")
    post_create = generated_code[create_pos:create_pos + 300] if create_pos != -1 else ""
    has_create_check = "ESP_OK" in post_create or "!= ESP_OK" in post_create or "ret" in post_create
    details.append(CheckDetail(
        check_name="esp_timer_create_error_checked",
        passed=has_create_check,
        expected="esp_timer_create() return value checked",
        actual="present" if has_create_check else "missing",
        check_type="constraint",
    ))

    # Check 3: esp_timer_start_periodic error checked
    start_pos = generated_code.find("esp_timer_start_periodic")
    post_start = generated_code[start_pos:start_pos + 300] if start_pos != -1 else ""
    has_start_check = "ESP_OK" in post_start or "!= ESP_OK" in post_start or "ret" in post_start
    details.append(CheckDetail(
        check_name="esp_timer_start_error_checked",
        passed=has_start_check,
        expected="esp_timer_start_periodic() return value checked",
        actual="present" if has_start_check else "missing",
        check_type="constraint",
    ))

    # Check 4: esp_timer_stop called (timer stopped when done)
    has_stop = "esp_timer_stop" in generated_code
    details.append(CheckDetail(
        check_name="esp_timer_stop_called",
        passed=has_stop,
        expected="esp_timer_stop() called to stop the timer",
        actual="present" if has_stop else "missing (timer never stopped)",
        check_type="constraint",
    ))

    # Check 5: No FreeRTOS software timer mixing
    freertos_timer_apis = ["xTimerCreate", "xTimerStart", "xTimerStop"]
    found_freertos = [api for api in freertos_timer_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_freertos_timer_mixing",
        passed=not found_freertos,
        expected="Use esp_timer only (not FreeRTOS xTimer)",
        actual="clean" if not found_freertos else f"found FreeRTOS timer APIs: {found_freertos}",
        check_type="constraint",
    ))

    # Check 6: Timer period uses microseconds (1,000,000 for 1 second)
    # Allow for various forms: 1000000, 1000000ULL, 1000000LL, etc.
    import re
    has_1s_period = bool(re.search(r"1[_,]?000[_,]?000", generated_code))
    details.append(CheckDetail(
        check_name="timer_period_1_second",
        passed=has_1s_period,
        expected="Timer period = 1,000,000 us (1 second)",
        actual="present" if has_1s_period else "missing or wrong period value",
        check_type="constraint",
    ))

    # Check 7: No Zephyr timer APIs
    zephyr_timer_apis = ["k_timer_start", "k_timer_init", "k_timer_stop"]
    found_zephyr = [api for api in zephyr_timer_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_zephyr_timer_apis",
        passed=not found_zephyr,
        expected="No Zephyr timer APIs",
        actual="clean" if not found_zephyr else f"found Zephyr: {found_zephyr}",
        check_type="hallucination",
    ))

    return details
