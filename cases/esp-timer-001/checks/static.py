"""Static checks for ESP-IDF high-resolution periodic timer."""
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    details.append(CheckDetail(
        check_name="esp_timer_header",
        passed="esp_timer.h" in generated_code,
        expected="esp_timer.h included",
        actual="present" if "esp_timer.h" in generated_code else "missing",
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
        check_name="esp_timer_create_called",
        passed="esp_timer_create" in generated_code,
        expected="esp_timer_create() called",
        actual="present" if "esp_timer_create" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="esp_timer_start_periodic_called",
        passed="esp_timer_start_periodic" in generated_code,
        expected="esp_timer_start_periodic() called",
        actual="present" if "esp_timer_start_periodic" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="esp_timer_delete_called",
        passed="esp_timer_delete" in generated_code,
        expected="esp_timer_delete() called for cleanup",
        actual="present" if "esp_timer_delete" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="callback_defined",
        passed="esp_timer_create_args_t" in generated_code,
        expected="esp_timer_create_args_t with .callback field",
        actual="present" if "esp_timer_create_args_t" in generated_code else "missing",
        check_type="exact_match",
    ))

    # Cross-platform hallucination checks
    zephyr_apis = ["k_timer_start", "k_timer_init", "k_sleep", "K_MSEC"]
    found_zephyr = [api for api in zephyr_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_zephyr_timer_apis",
        passed=not found_zephyr,
        expected="No Zephyr timer APIs in ESP-IDF code",
        actual="clean" if not found_zephyr else f"found Zephyr APIs: {found_zephyr}",
        check_type="hallucination",
    ))

    stm32_apis = ["HAL_TIM_Base_Start", "TIM_HandleTypeDef", "HAL_Init"]
    found_stm32 = [api for api in stm32_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_stm32_hal_apis",
        passed=not found_stm32,
        expected="No STM32 HAL timer APIs",
        actual="clean" if not found_stm32 else f"found STM32 HAL: {found_stm32}",
        check_type="hallucination",
    ))

    return details
