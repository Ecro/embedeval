"""Static analysis checks for multi-LED sequential blink application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-LED GPIO code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/drivers/gpio.h
    has_gpio_h = "zephyr/drivers/gpio.h" in generated_code
    details.append(
        CheckDetail(
            check_name="gpio_header_included",
            passed=has_gpio_h,
            expected="zephyr/drivers/gpio.h included",
            actual="present" if has_gpio_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Includes zephyr/kernel.h
    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header_included",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Uses GPIO_DT_SPEC_GET for all 4 LEDs (devicetree binding)
    has_dt_spec = "GPIO_DT_SPEC_GET" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_gpio_dt_spec",
            passed=has_dt_spec,
            expected="GPIO_DT_SPEC_GET used to get LED devices from devicetree",
            actual="present" if has_dt_spec else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: All 4 LED aliases referenced (led0..led3)
    has_all_leds = all(
        f"led{i}" in generated_code for i in range(4)
    )
    details.append(
        CheckDetail(
            check_name="all_four_leds_referenced",
            passed=has_all_leds,
            expected="Aliases led0, led1, led2, led3 all referenced",
            actual="all present" if has_all_leds else "one or more missing",
            check_type="exact_match",
        )
    )

    # Check 5: Uses gpio_pin_set_dt or gpio_pin_toggle_dt (not raw GPIO set)
    has_gpio_set = any(
        p in generated_code
        for p in ["gpio_pin_set_dt", "gpio_pin_toggle_dt", "gpio_pin_set("]
    )
    details.append(
        CheckDetail(
            check_name="uses_gpio_pin_set_api",
            passed=has_gpio_set,
            expected="gpio_pin_set_dt() or gpio_pin_toggle_dt() used",
            actual="present" if has_gpio_set else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: No raw register access
    has_raw_register = any(
        p in generated_code for p in ["volatile uint32_t", "*(uint32_t*)", "MMIO"]
    )
    details.append(
        CheckDetail(
            check_name="no_raw_register_access",
            passed=not has_raw_register,
            expected="Uses GPIO API, not raw register access",
            actual="raw register found" if has_raw_register else "API only",
            check_type="constraint",
        )
    )

    return details
