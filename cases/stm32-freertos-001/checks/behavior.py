"""Behavioral checks for STM32 FreeRTOS producer-consumer application."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 FreeRTOS producer-consumer behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Producer sends to queue (xQueueSend or osMessageQueuePut)
    has_send = any(
        p in generated_code
        for p in ["xQueueSend", "xQueueSendToBack", "osMessageQueuePut"]
    )
    details.append(
        CheckDetail(
            check_name="producer_sends_to_queue",
            passed=has_send,
            expected="xQueueSend or osMessageQueuePut used in producer",
            actual="present" if has_send else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Consumer receives from queue (xQueueReceive or osMessageQueueGet)
    has_receive = any(
        p in generated_code
        for p in ["xQueueReceive", "osMessageQueueGet"]
    )
    details.append(
        CheckDetail(
            check_name="consumer_receives_from_queue",
            passed=has_receive,
            expected="xQueueReceive or osMessageQueueGet used in consumer",
            actual="present" if has_receive else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Producer has delay (not tight loop)
    has_delay = any(
        p in generated_code
        for p in ["vTaskDelay", "osDelay", "pdMS_TO_TICKS"]
    )
    details.append(
        CheckDetail(
            check_name="producer_has_delay",
            passed=has_delay,
            expected="Producer uses vTaskDelay or osDelay (not tight loop)",
            actual="present" if has_delay else "missing — busy loop",
            check_type="constraint",
        )
    )

    # Check 4: Consumer uses blocking receive (portMAX_DELAY or osWaitForever)
    has_blocking = any(
        p in generated_code
        for p in ["portMAX_DELAY", "osWaitForever"]
    )
    details.append(
        CheckDetail(
            check_name="consumer_blocking_receive",
            passed=has_blocking,
            expected="Consumer uses portMAX_DELAY or osWaitForever on receive",
            actual="present" if has_blocking else "missing or non-blocking",
            check_type="constraint",
        )
    )

    # Check 5: Different priorities for producer and consumer
    # Native API: xTaskCreate(..., priority, ...)
    priority_matches = re.findall(
        r"xTaskCreate\s*\([^,]+,\s*[^,]+,\s*\d+,\s*[^,]+,\s*(\d+)",
        generated_code,
    )
    if len(priority_matches) < 2:
        # CMSIS-RTOS: osThreadAttr_t or osThreadNew with priority
        priority_matches = re.findall(
            r"osPriority\w+\s*(\d+)|\.priority\s*=\s*(\w+)",
            generated_code,
        )
        priority_matches = [m[0] or m[1] for m in priority_matches]
    different_prio = len(priority_matches) >= 2 and len(set(priority_matches)) >= 2
    details.append(
        CheckDetail(
            check_name="different_task_priorities",
            passed=different_prio,
            expected="Producer and consumer have different task priorities",
            actual=f"priorities found: {priority_matches}",
            check_type="constraint",
        )
    )

    # Check 6: Queue created before tasks start using it
    queue_create_pos = -1
    for token in ["xQueueCreate", "osMessageQueueNew"]:
        pos = generated_code.find(token)
        if pos != -1:
            queue_create_pos = pos if queue_create_pos == -1 else min(queue_create_pos, pos)

    task_create_pos = -1
    for token in ["xTaskCreate", "osThreadNew"]:
        pos = generated_code.find(token)
        if pos != -1:
            task_create_pos = pos if task_create_pos == -1 else min(task_create_pos, pos)

    queue_before_tasks = (
        queue_create_pos != -1
        and task_create_pos != -1
        and queue_create_pos < task_create_pos
    )
    details.append(
        CheckDetail(
            check_name="queue_created_before_tasks",
            passed=queue_before_tasks,
            expected="Queue created before tasks are started",
            actual="correct order" if queue_before_tasks else "wrong order or missing",
            check_type="constraint",
        )
    )

    return details
