"""Static analysis checks for STM32 FreeRTOS producer-consumer application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 FreeRTOS code structure and required elements."""
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

    # Check 2: FreeRTOS headers included (native or CMSIS-RTOS)
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

    # Check 3: Task creation (native xTaskCreate or CMSIS osThreadNew)
    has_task_create = any(
        p in generated_code
        for p in ["xTaskCreate", "osThreadNew", "osThreadDef"]
    )
    details.append(
        CheckDetail(
            check_name="task_creation_used",
            passed=has_task_create,
            expected="xTaskCreate or osThreadNew used to create tasks",
            actual="present" if has_task_create else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Queue created and used
    has_queue = any(
        p in generated_code
        for p in ["xQueueCreate", "osMessageQueueNew"]
    )
    details.append(
        CheckDetail(
            check_name="queue_created",
            passed=has_queue,
            expected="xQueueCreate or osMessageQueueNew used",
            actual="present" if has_queue else "missing",
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

    # Check 6: No Zephyr RTOS hallucinations (k_thread, K_MSGQ_DEFINE etc.)
    has_zephyr = any(
        p in generated_code
        for p in ["k_thread", "K_MSGQ_DEFINE", "k_msgq_put", "k_sleep", "zephyr/", "K_THREAD_DEFINE"]
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
