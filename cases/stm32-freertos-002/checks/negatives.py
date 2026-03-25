"""Negative tests for STM32 FreeRTOS ISR-to-task communication.

Reference: cases/stm32-freertos-002/reference/main.c
Checks:    cases/stm32-freertos-002/checks/behavior.py

The reference:
  - Uses xQueueSendFromISR inside HAL_TIM_PeriodElapsedCallback (ISR context).
  - Calls portYIELD_FROM_ISR(higher_priority_woken) after the send.

Check names targeted
--------------------
* froomisr_used_not_blocking_send : behavior check; passes when xQueueSendFromISR
  is present AND no bare xQueueSend( is found inside the ISR callback body (~500 chars).
* isr_yield_after_queue_send      : behavior check; passes when portYIELD_FROM_ISR
  or portEND_SWITCHING_ISR appears anywhere in the code.

Mutation strategy
-----------------
* blocking_queue_send_in_isr : replaces the ISR-safe xQueueSendFromISR with the
  blocking xQueueSend.  The behavior check then finds 'xQueueSend(' (bare) inside
  the callback body and no FromISR variant → froomisr_used_not_blocking_send fails.
  The &higher_priority_woken argument is replaced with portMAX_DELAY to make the
  call syntactically plausible.

* missing_yield_from_isr : removes the portYIELD_FROM_ISR line.
  The behavior check looks for portYIELD_FROM_ISR or portEND_SWITCHING_ISR
  anywhere in the file → isr_yield_after_queue_send fails.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "blocking_queue_send_in_isr",
        "description": (
            "xQueueSend (blocking) used in ISR instead of xQueueSendFromISR — "
            "undefined behaviour; may corrupt FreeRTOS internals"
        ),
        "mutation": lambda code: code.replace(
            "xQueueSendFromISR(isr_queue, &isr_counter, &higher_priority_woken);",
            "xQueueSend(isr_queue, &isr_counter, portMAX_DELAY);",
        ),
        "must_fail": ["froomisr_used_not_blocking_send"],
    },
    {
        "name": "missing_yield_from_isr",
        "description": (
            "portYIELD_FROM_ISR removed — receiver task will not preempt immediately "
            "after the ISR sends data, causing latency spikes"
        ),
        "mutation": lambda code: _remove_lines(code, "portYIELD_FROM_ISR"),
        "must_fail": ["isr_yield_after_queue_send"],
    },
    # --- Subtle ---
    {
        "name": "from_isr_with_null_wake_flag",
        "mutation": lambda code: code.replace(
            "&higher_priority_woken", "NULL"
        ),
        "should_fail": ["isr_yield_after_queue_send"],
        "bug_description": "xQueueSendFromISR with NULL pxHigherPriorityTaskWoken — portYIELD_FROM_ISR gets garbage value",
    },
]
