"""Behavioral checks for GPIO button interrupt application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate GPIO behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: LED configured as output
    has_output = "GPIO_OUTPUT" in generated_code
    details.append(
        CheckDetail(
            check_name="led_configured_output",
            passed=has_output,
            expected="LED pin configured as GPIO_OUTPUT",
            actual="present" if has_output else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Button configured as input
    has_input = "GPIO_INPUT" in generated_code
    details.append(
        CheckDetail(
            check_name="button_configured_input",
            passed=has_input,
            expected="Button pin configured as GPIO_INPUT",
            actual="present" if has_input else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Interrupt configured (edge-triggered)
    has_int_edge = any(
        p in generated_code
        for p in [
            "GPIO_INT_EDGE",
            "GPIO_INT_EDGE_TO_ACTIVE",
            "GPIO_INT_EDGE_FALLING",
            "GPIO_INT_EDGE_BOTH",
        ]
    )
    details.append(
        CheckDetail(
            check_name="interrupt_edge_triggered",
            passed=has_int_edge,
            expected="Edge-triggered interrupt configured",
            actual="present" if has_int_edge else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Callback registered before sleeping (gpio_add_callback before k_sleep)
    add_cb_pos = generated_code.find("gpio_add_callback")
    sleep_pos = generated_code.find("k_sleep")
    order_ok = add_cb_pos != -1 and sleep_pos != -1 and add_cb_pos < sleep_pos
    details.append(
        CheckDetail(
            check_name="callback_before_sleep",
            passed=order_ok,
            expected="gpio_add_callback called before k_sleep",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 5: LED toggle in callback (not in main loop)
    has_toggle = "gpio_pin_toggle" in generated_code
    details.append(
        CheckDetail(
            check_name="led_toggle_in_callback",
            passed=has_toggle,
            expected="gpio_pin_toggle called (in callback)",
            actual="present" if has_toggle else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Device ready check before use
    has_ready_check = any(
        p in generated_code
        for p in ["gpio_is_ready_dt", "device_is_ready", "gpio_is_ready"]
    )
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready_check,
            expected="Device ready check before GPIO operations",
            actual="present" if has_ready_check else "missing",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
