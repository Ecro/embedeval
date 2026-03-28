"""Behavioral checks for STM32 FreeRTOS ISR-to-task communication application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ISR-safe synchronization behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: FromISR variant used inside the timer callback/ISR
    # (LLM critical failure: using blocking xQueueSend in ISR context)
    has_from_isr = any(
        p in generated_code
        for p in ["xQueueSendFromISR", "xQueueSendToBackFromISR", "xQueueOverwriteFromISR"]
    )
    # Check that the non-ISR-safe version is NOT the only send in ISR context
    has_blocking_in_isr = False
    isr_callback_pos = -1
    for token in ["HAL_TIM_PeriodElapsedCallback", "TIM2_IRQHandler", "PeriodElapsedCallback"]:
        pos = generated_code.find(token)
        if pos != -1:
            isr_callback_pos = pos
            break

    if isr_callback_pos != -1:
        # Check within ~500 chars of ISR callback for blocking xQueueSend
        isr_body = generated_code[isr_callback_pos:isr_callback_pos + 500]
        # xQueueSend followed by ( not FromISR
        import re
        blocking_send = re.search(r"xQueueSend\s*\(", isr_body)
        from_isr_send = re.search(r"xQueueSend\w*FromISR\s*\(", isr_body)
        if blocking_send and not from_isr_send:
            has_blocking_in_isr = True

    details.append(
        CheckDetail(
            check_name="froomisr_used_not_blocking_send",
            passed=has_from_isr and not has_blocking_in_isr,
            expected="xQueueSendFromISR used in ISR (not blocking xQueueSend)",
            actual="correct" if (has_from_isr and not has_blocking_in_isr) else "blocking send in ISR or missing FromISR",
            check_type="constraint",
        )
    )

    # Check 2 removed — duplicate of Check 7 (isr_yield_after_queue_send)

    # Check 3: Receiver task uses blocking receive (portMAX_DELAY)
    has_blocking_receive = any(
        p in generated_code
        for p in ["portMAX_DELAY", "osWaitForever"]
    )
    details.append(
        CheckDetail(
            check_name="receiver_uses_blocking_receive",
            passed=has_blocking_receive,
            expected="Receiver task uses portMAX_DELAY on xQueueReceive",
            actual="present" if has_blocking_receive else "missing or non-blocking",
            check_type="constraint",
        )
    )

    # Check 4: No blocking calls in ISR (vTaskDelay, xQueueSend, HAL_Delay)
    isr_has_blocking = False
    if isr_callback_pos != -1:
        isr_body = generated_code[isr_callback_pos:isr_callback_pos + 500]
        isr_has_blocking = any(
            p in isr_body
            for p in ["vTaskDelay", "HAL_Delay", "osDelay"]
        )
    details.append(
        CheckDetail(
            check_name="no_blocking_calls_in_isr",
            passed=not isr_has_blocking,
            expected="No blocking calls (vTaskDelay, HAL_Delay) in ISR/callback",
            actual="clean" if not isr_has_blocking else "blocking call found in ISR",
            check_type="constraint",
        )
    )

    # Check 5: Timer interrupt enabled (HAL_TIM_Base_Start_IT)
    has_tim_it_start = any(
        p in generated_code
        for p in ["HAL_TIM_Base_Start_IT", "HAL_TIM_Base_Start_IT"]
    )
    details.append(
        CheckDetail(
            check_name="timer_interrupt_started",
            passed=has_tim_it_start,
            expected="HAL_TIM_Base_Start_IT called to enable timer interrupt",
            actual="present" if has_tim_it_start else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Queue created before scheduler starts
    queue_pos = -1
    for token in ["xQueueCreate", "osMessageQueueNew"]:
        pos = generated_code.find(token)
        if pos != -1:
            queue_pos = pos if queue_pos == -1 else min(queue_pos, pos)
    scheduler_pos = -1
    for token in ["vTaskStartScheduler", "osKernelStart"]:
        pos = generated_code.find(token)
        if pos != -1:
            scheduler_pos = pos if scheduler_pos == -1 else min(scheduler_pos, pos)
    queue_before_scheduler = queue_pos != -1 and scheduler_pos != -1 and queue_pos < scheduler_pos
    details.append(
        CheckDetail(
            check_name="queue_created_before_scheduler",
            passed=queue_before_scheduler,
            expected="Queue created before vTaskStartScheduler",
            actual="correct order" if queue_before_scheduler else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 7: portYIELD_FROM_ISR called after xQueueSendFromISR
    # Without this, the high-priority receiver task won't preempt immediately after ISR
    has_yield_from_isr = any(
        p in generated_code
        for p in ["portYIELD_FROM_ISR", "portEND_SWITCHING_ISR"]
    )
    details.append(
        CheckDetail(
            check_name="isr_yield_after_queue_send",
            passed=has_yield_from_isr,
            expected="portYIELD_FROM_ISR called after xQueueSendFromISR",
            actual="present" if has_yield_from_isr else "missing — receiver may not preempt ISR return",
            check_type="constraint",
        )
    )

    # Check 8: BaseType_t wake-flag variable declared for xQueueSendFromISR
    # LLM blind spot: passing NULL instead of &higher_priority_woken means
    # portYIELD_FROM_ISR receives an undefined/garbage value → incorrect preemption.
    # If NULL is passed, the variable declaration will be absent from the generated code.
    has_woken_var = bool(re.search(
        r'BaseType_t\s+\w*(?:higher|woken|priority)\w*',
        generated_code,
        re.IGNORECASE,
    ))
    details.append(
        CheckDetail(
            check_name="higher_priority_woken_declared",
            passed=has_woken_var,
            expected="BaseType_t higher_priority_woken (or similar) declared for xQueueSendFromISR",
            actual="present" if has_woken_var else "missing — NULL likely passed to xQueueSendFromISR",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace", "STM32_HAL", "FreeRTOS"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No Arduino/POSIX APIs (STM32 HAL and FreeRTOS are expected)",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
