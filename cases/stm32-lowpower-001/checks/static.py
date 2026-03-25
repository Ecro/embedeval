"""Static analysis checks for STM32 HAL Stop mode + RTC wakeup application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL low-power code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: STM32 HAL header
    has_hal_header = "stm32f4xx_hal.h" in generated_code
    details.append(
        CheckDetail(
            check_name="stm32_hal_header_included",
            passed=has_hal_header,
            expected="stm32f4xx_hal.h included",
            actual="present" if has_hal_header else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: HAL_PWR_EnterSTOPMode used
    has_stop_mode = "HAL_PWR_EnterSTOPMode" in generated_code
    details.append(
        CheckDetail(
            check_name="stop_mode_api_used",
            passed=has_stop_mode,
            expected="HAL_PWR_EnterSTOPMode called",
            actual="present" if has_stop_mode else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: RTC_HandleTypeDef used
    has_rtc_handle = "RTC_HandleTypeDef" in generated_code
    details.append(
        CheckDetail(
            check_name="rtc_handle_typedef_used",
            passed=has_rtc_handle,
            expected="RTC_HandleTypeDef struct used",
            actual="present" if has_rtc_handle else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: RTC alarm set with interrupt (HAL_RTC_SetAlarm_IT)
    has_alarm_it = "HAL_RTC_SetAlarm_IT" in generated_code
    details.append(
        CheckDetail(
            check_name="rtc_alarm_interrupt_used",
            passed=has_alarm_it,
            expected="HAL_RTC_SetAlarm_IT used for wakeup alarm",
            actual="present" if has_alarm_it else "missing or polling alarm",
            check_type="exact_match",
        )
    )

    # Check 5: No cross-platform hallucinations
    has_zephyr = any(
        p in generated_code
        for p in ["pm_device", "pm_suspend", "zephyr/", "k_sleep", "DEVICE_DT_GET"]
    )
    has_espidf = any(
        p in generated_code
        for p in ["esp_", "esp_sleep_enable", "esp_light_sleep_start"]
    )
    no_hallucination = not has_zephyr and not has_espidf
    details.append(
        CheckDetail(
            check_name="no_cross_platform_hallucination",
            passed=no_hallucination,
            expected="Only STM32 HAL low-power APIs used",
            actual="clean" if no_hallucination else f"zephyr={has_zephyr} espidf={has_espidf}",
            check_type="constraint",
        )
    )

    # Check 6: WFI entry mode specified
    has_wfi = "PWR_STOPENTRY_WFI" in generated_code
    details.append(
        CheckDetail(
            check_name="wfi_entry_mode_specified",
            passed=has_wfi,
            expected="PWR_STOPENTRY_WFI specified in HAL_PWR_EnterSTOPMode",
            actual="present" if has_wfi else "missing",
            check_type="exact_match",
        )
    )

    return details
