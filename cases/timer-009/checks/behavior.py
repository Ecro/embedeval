"""Behavioral checks for semaphore timeout pattern application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate semaphore timeout behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: k_sem_give called in timer callback (correct event source)
    has_sem_give = "k_sem_give" in generated_code
    details.append(
        CheckDetail(
            check_name="sem_give_in_timer_callback",
            passed=has_sem_give,
            expected="k_sem_give() called (event source, likely in timer callback)",
            actual="present" if has_sem_give else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: k_timer_start called before k_sem_take (timer started before wait)
    timer_start_pos = generated_code.find("k_timer_start")
    sem_take_pos = generated_code.find("k_sem_take")
    order_ok = (
        timer_start_pos != -1
        and sem_take_pos != -1
        and timer_start_pos < sem_take_pos
    )
    details.append(
        CheckDetail(
            check_name="timer_started_before_wait",
            passed=order_ok,
            expected="k_timer_start called before k_sem_take",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: K_SEM_DEFINE used (static semaphore definition)
    has_sem_define = "K_SEM_DEFINE" in generated_code or "k_sem_init" in generated_code
    details.append(
        CheckDetail(
            check_name="semaphore_properly_defined",
            passed=has_sem_define,
            expected="K_SEM_DEFINE or k_sem_init used",
            actual="present" if has_sem_define else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Both success and failure branches present
    has_success_path = "Event received" in generated_code or "ret == 0" in generated_code or "== 0" in generated_code
    has_failure_path = "Timeout" in generated_code or "-EAGAIN" in generated_code
    has_both_paths = has_success_path and has_failure_path
    details.append(
        CheckDetail(
            check_name="both_success_and_timeout_handled",
            passed=has_both_paths,
            expected="Both event-received and timeout paths handled",
            actual=f"success={has_success_path}, timeout={has_failure_path}",
            check_type="constraint",
        )
    )

    # Check 5: Cross-platform — no FreeRTOS semaphore APIs
    has_freertos = any(
        p in generated_code
        for p in ["xSemaphoreCreateBinary", "xSemaphoreTake", "xSemaphoreGive"]
    )
    details.append(
        CheckDetail(
            check_name="no_freertos_semaphore_apis",
            passed=not has_freertos,
            expected="No FreeRTOS semaphore APIs (wrong RTOS)",
            actual="FreeRTOS API found" if has_freertos else "clean",
            check_type="constraint",
        )
    )

    # Check 6: Real-time constraint — no busy-wait before semaphore
    import re
    has_rt_busywait = bool(re.search(r"while\s*\(\s*1\s*\)[^}]*k_sem_take", generated_code, re.DOTALL))
    details.append(
        CheckDetail(
            check_name="no_rt_busywait_loop",
            passed=not has_rt_busywait,
            expected="No busy-wait loop around k_sem_take",
            actual="busy-wait found" if has_rt_busywait else "clean",
            check_type="constraint",
        )
    )

    return details
