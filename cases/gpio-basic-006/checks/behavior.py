"""Behavioral checks for GPIO interrupt debounce with timer application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate debounce behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: ISR starts timer, does NOT read GPIO directly inside (debounce pattern)
    # The ISR should call k_timer_start; gpio_pin_get should only be in timer callback
    has_timer_start = "k_timer_start" in generated_code
    details.append(
        CheckDetail(
            check_name="isr_starts_timer",
            passed=has_timer_start,
            expected="k_timer_start called (from ISR to defer GPIO read)",
            actual="present" if has_timer_start else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Timer uses 50ms (or similar short debounce window)
    has_50ms = "K_MSEC(50)" in generated_code or "50" in generated_code
    details.append(
        CheckDetail(
            check_name="debounce_50ms_window",
            passed=has_50ms,
            expected="50ms debounce delay used",
            actual="present" if has_50ms else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: gpio_pin_get_dt used in timer callback to read stable state
    has_pin_get = "gpio_pin_get_dt" in generated_code or "gpio_pin_get" in generated_code
    details.append(
        CheckDetail(
            check_name="stable_state_read_in_callback",
            passed=has_pin_get,
            expected="gpio_pin_get_dt() called (reads stable state after debounce)",
            actual="present" if has_pin_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: gpio_callback registered before k_sleep
    add_cb_pos = generated_code.find("gpio_add_callback")
    sleep_pos = generated_code.find("k_sleep")
    order_ok = add_cb_pos != -1 and sleep_pos != -1 and add_cb_pos < sleep_pos
    details.append(
        CheckDetail(
            check_name="callback_registered_before_sleep",
            passed=order_ok,
            expected="gpio_add_callback called before k_sleep(K_FOREVER)",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 5: Device ready checks present
    has_ready = any(
        p in generated_code for p in ["gpio_is_ready_dt", "device_is_ready"]
    )
    details.append(
        CheckDetail(
            check_name="device_ready_checks",
            passed=has_ready,
            expected="gpio_is_ready_dt() or device_is_ready() called",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Cross-platform — no FreeRTOS timer APIs
    has_freertos = any(
        p in generated_code for p in ["xTimerCreate", "vTimerSetTimerID", "xTimerStart"]
    )
    details.append(
        CheckDetail(
            check_name="no_freertos_timer_apis",
            passed=not has_freertos,
            expected="No FreeRTOS timer APIs (wrong RTOS)",
            actual="FreeRTOS API found" if has_freertos else "clean",
            check_type="constraint",
        )
    )

    return details
