"""Behavioral checks for GPIO wakeup from deep sleep application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate GPIO deep sleep behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: GPIO configured before pm_state_force (wakeup source set before sleep)
    gpio_cfg_pos = generated_code.find("gpio_pin_configure_dt")
    pm_force_pos = generated_code.find("pm_state_force")
    order_ok = gpio_cfg_pos != -1 and pm_force_pos != -1 and gpio_cfg_pos < pm_force_pos
    details.append(
        CheckDetail(
            check_name="gpio_configured_before_sleep",
            passed=order_ok,
            expected="GPIO configured before pm_state_force() is called",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Callback registered before sleep
    add_cb_pos = generated_code.find("gpio_add_callback")
    cb_before_sleep = add_cb_pos != -1 and pm_force_pos != -1 and add_cb_pos < pm_force_pos
    details.append(
        CheckDetail(
            check_name="callback_registered_before_sleep",
            passed=cb_before_sleep,
            expected="gpio_add_callback called before pm_state_force",
            actual="correct order" if cb_before_sleep else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: PM_STATE_SOFT_OFF or similar deep sleep state used
    has_sleep_state = any(
        p in generated_code
        for p in ["PM_STATE_SOFT_OFF", "PM_STATE_SUSPEND_TO_RAM", "PM_STATE_SUSPEND_TO_DISK"]
    )
    details.append(
        CheckDetail(
            check_name="deep_sleep_state_specified",
            passed=has_sleep_state,
            expected="PM_STATE_SOFT_OFF or deep sleep state specified",
            actual="present" if has_sleep_state else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Device ready check before GPIO operations
    has_ready = any(
        p in generated_code for p in ["gpio_is_ready_dt", "device_is_ready"]
    )
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="gpio_is_ready_dt() or device_is_ready() called",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 5: GPIO interrupt configured (wakeup requires interrupt)
    has_int = "gpio_pin_interrupt_configure_dt" in generated_code
    details.append(
        CheckDetail(
            check_name="gpio_interrupt_configured",
            passed=has_int,
            expected="gpio_pin_interrupt_configure_dt() called to enable wakeup interrupt",
            actual="present" if has_int else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: No busy-wait polling (use interrupt, not polling)
    has_busy_wait = "while (gpio_pin_get" in generated_code
    details.append(
        CheckDetail(
            check_name="no_busy_wait_polling",
            passed=not has_busy_wait,
            expected="No busy-wait GPIO polling loop (use interrupt)",
            actual="busy-wait found" if has_busy_wait else "clean",
            check_type="constraint",
        )
    )

    return details
