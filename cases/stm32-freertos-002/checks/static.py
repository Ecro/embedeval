"""Static analysis checks for STM32 FreeRTOS ISR-to-task communication application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 FreeRTOS ISR-safe queue code structure."""
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

    # Check 2: FreeRTOS headers
    has_freertos = any(
        p in generated_code
        for p in ["FreeRTOS.h", "cmsis_os.h", "cmsis_os2.h"]
    )
    details.append(
        CheckDetail(
            check_name="freertos_header_included",
            passed=has_freertos,
            expected="FreeRTOS.h or cmsis_os.h included",
            actual="present" if has_freertos else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: ISR-safe queue send variant used
    has_from_isr = any(
        p in generated_code
        for p in [
            "xQueueSendFromISR",
            "xQueueSendToBackFromISR",
            "xQueueOverwriteFromISR",
        ]
    )
    details.append(
        CheckDetail(
            check_name="isr_safe_queue_send_used",
            passed=has_from_isr,
            expected="xQueueSendFromISR (or variant) used in ISR context",
            actual="present" if has_from_isr else "missing — blocking xQueueSend in ISR is undefined behavior",
            check_type="exact_match",
        )
    )

    # Check 4: TIM2 used for interrupt source
    has_tim2 = "TIM2" in generated_code
    details.append(
        CheckDetail(
            check_name="tim2_interrupt_source",
            passed=has_tim2,
            expected="TIM2 configured as interrupt source",
            actual="present" if has_tim2 else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Scheduler started
    has_scheduler = any(
        p in generated_code
        for p in ["vTaskStartScheduler", "osKernelStart"]
    )
    details.append(
        CheckDetail(
            check_name="scheduler_started",
            passed=has_scheduler,
            expected="vTaskStartScheduler or osKernelStart called",
            actual="present" if has_scheduler else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: No Zephyr RTOS hallucinations
    has_zephyr = any(
        p in generated_code
        for p in ["k_thread", "K_MSGQ_DEFINE", "k_msgq", "k_sem", "zephyr/", "K_THREAD_DEFINE"]
    )
    details.append(
        CheckDetail(
            check_name="no_zephyr_hallucination",
            passed=not has_zephyr,
            expected="No Zephyr RTOS APIs used",
            actual="clean" if not has_zephyr else "Zephyr API detected",
            check_type="constraint",
        )
    )

    return details
