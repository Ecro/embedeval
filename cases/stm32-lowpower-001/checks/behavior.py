"""Behavioral checks for STM32 HAL Stop mode + RTC alarm wakeup application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL low-power behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: SystemClock_Config called AFTER HAL_PWR_EnterSTOPMode
    # CRITICAL implicit requirement: Stop mode disables PLL/HSE. Must re-init clock.
    # LLM failure: wakeup but forget to reconfigure clock → runs at 16MHz HSI only.
    stop_mode_pos = generated_code.find("HAL_PWR_EnterSTOPMode")
    sysclk_after_stop = False
    if stop_mode_pos != -1:
        code_after_stop = generated_code[stop_mode_pos + len("HAL_PWR_EnterSTOPMode"):]
        sysclk_after_stop = any(
            p in code_after_stop
            for p in ["SystemClock_Config", "HAL_RCC_OscConfig", "HAL_RCC_ClockConfig"]
        )
    details.append(
        CheckDetail(
            check_name="sysclock_reconfigured_after_stop_wakeup",
            passed=sysclk_after_stop,
            expected="SystemClock_Config called after HAL_PWR_EnterSTOPMode (PLL off in Stop)",
            actual="present" if sysclk_after_stop else "missing — clock not restored after wakeup",
            check_type="constraint",
        )
    )

    # Check 2: LED toggle after wakeup (after EnterSTOPMode returns)
    led_toggle_after_stop = False
    if stop_mode_pos != -1:
        code_after_stop = generated_code[stop_mode_pos + len("HAL_PWR_EnterSTOPMode"):]
        led_toggle_after_stop = "HAL_GPIO_TogglePin" in code_after_stop
    details.append(
        CheckDetail(
            check_name="led_toggled_after_wakeup",
            passed=led_toggle_after_stop,
            expected="HAL_GPIO_TogglePin called after Stop mode wakeup",
            actual="present" if led_toggle_after_stop else "missing or before stop entry",
            check_type="constraint",
        )
    )

    # Check 3: RTC alarm callback defined
    has_alarm_callback = any(
        p in generated_code
        for p in ["HAL_RTC_AlarmAEventCallback", "HAL_RTCEx_AlarmBEventCallback"]
    )
    details.append(
        CheckDetail(
            check_name="rtc_alarm_callback_defined",
            passed=has_alarm_callback,
            expected="HAL_RTC_AlarmAEventCallback override defined",
            actual="present" if has_alarm_callback else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: RTC alarm IRQ handler defined
    has_alarm_irq = "RTC_Alarm_IRQHandler" in generated_code
    details.append(
        CheckDetail(
            check_name="rtc_alarm_irq_handler_defined",
            passed=has_alarm_irq,
            expected="RTC_Alarm_IRQHandler defined",
            actual="present" if has_alarm_irq else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: RTC clock source configured (LSE or LSI required for Stop mode survival)
    # LSE is preferred (more accurate), LSI acceptable
    has_rtc_clksrc = any(
        p in generated_code
        for p in [
            "RCC_RTCCLKSOURCE_LSE",
            "RCC_RTCCLKSOURCE_LSI",
            "RTCClockSelection",
        ]
    )
    details.append(
        CheckDetail(
            check_name="rtc_clock_source_configured",
            passed=has_rtc_clksrc,
            expected="RTC clock source set to LSE or LSI (survives Stop mode)",
            actual="present" if has_rtc_clksrc else "missing",
            check_type="constraint",
        )
    )

    # Check 6: RTC alarm NVIC configured somewhere in the code
    # (LLM failure: configures alarm but forgets to enable the NVIC — alarm fires but ISR never runs)
    # We check that the NVIC enable is present AND that it appears before the stop call
    # (either directly or via a helper function called before EnterSTOPMode).
    # Since helper functions are defined after main() textually in C, we look at:
    # - whether NVIC enable is present at all, AND
    # - whether the helper init function (MX_RTC_Init, RTC_Init, etc.) is called before stop.
    has_rtc_nvic = "RTC_Alarm_IRQn" in generated_code and "HAL_NVIC_EnableIRQ" in generated_code

    # Check that any RTC init call precedes the stop mode call
    rtc_init_before_stop = False
    if stop_mode_pos != -1:
        code_before_stop = generated_code[:stop_mode_pos]
        rtc_init_before_stop = any(
            p in code_before_stop
            for p in ["MX_RTC_Init", "RTC_Init", "HAL_RTC_Init", "HAL_RTC_SetAlarm_IT"]
        )

    details.append(
        CheckDetail(
            check_name="rtc_nvic_configured_before_stop",
            passed=has_rtc_nvic and rtc_init_before_stop,
            expected="RTC Alarm IRQ enabled before entering Stop mode",
            actual="correct" if (has_rtc_nvic and rtc_init_before_stop) else f"nvic={'present' if has_rtc_nvic else 'missing'} rtc_init_before_stop={rtc_init_before_stop}",
            check_type="constraint",
        )
    )

    # Check 7: SystemClock_Config re-called AFTER Stop mode wakeup
    # This is THE critical implicit requirement — PLL is disabled in Stop mode.
    # Without clock restore, all peripherals run at wrong speed after wakeup.
    clock_after_stop = False
    if stop_mode_pos != -1 and "SystemClock_Config" in generated_code:
        code_after_stop = generated_code[stop_mode_pos:]
        clock_after_stop = "SystemClock_Config" in code_after_stop
    details.append(
        CheckDetail(
            check_name="clock_restored_after_stop_wakeup",
            passed=clock_after_stop,
            expected="SystemClock_Config() called after HAL_PWR_EnterSTOPMode returns",
            actual="present" if clock_after_stop else "missing — PLL not restored after Stop mode wakeup",
            check_type="constraint",
        )
    )

    return details
