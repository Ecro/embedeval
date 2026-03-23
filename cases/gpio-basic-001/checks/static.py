"""Static analysis checks for GPIO button interrupt application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate GPIO code structure and required elements."""
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

    # Check 3: Uses GPIO_DT_SPEC_GET for devicetree binding
    has_dt_spec = "GPIO_DT_SPEC_GET" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_dt_spec",
            passed=has_dt_spec,
            expected="GPIO_DT_SPEC_GET macro used",
            actual="present" if has_dt_spec else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Has a callback function (gpio_callback struct)
    has_callback_struct = "gpio_callback" in generated_code
    details.append(
        CheckDetail(
            check_name="gpio_callback_struct",
            passed=has_callback_struct,
            expected="struct gpio_callback defined",
            actual="present" if has_callback_struct else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Uses gpio_init_callback
    has_init_cb = "gpio_init_callback" in generated_code
    details.append(
        CheckDetail(
            check_name="gpio_init_callback_called",
            passed=has_init_cb,
            expected="gpio_init_callback() called",
            actual="present" if has_init_cb else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: No direct register manipulation (HAL only)
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
