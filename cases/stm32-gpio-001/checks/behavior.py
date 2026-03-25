"""Behavioral checks for STM32 HAL GPIO LED + button interrupt application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL GPIO behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Clock enabled BEFORE GPIO init (ordering critical)
    rcc_pos = -1
    for token in ["__HAL_RCC_GPIOD_CLK_ENABLE", "__HAL_RCC_GPIOA_CLK_ENABLE", "__HAL_RCC_GPIO"]:
        pos = generated_code.find(token)
        if pos != -1:
            rcc_pos = pos if rcc_pos == -1 else min(rcc_pos, pos)

    gpio_init_pos = generated_code.find("HAL_GPIO_Init")
    clock_before_init = rcc_pos != -1 and gpio_init_pos != -1 and rcc_pos < gpio_init_pos
    details.append(
        CheckDetail(
            check_name="clock_enabled_before_gpio_init",
            passed=clock_before_init,
            expected="RCC clock enable called before HAL_GPIO_Init",
            actual="correct order" if clock_before_init else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: EXTI interrupt mode configured (rising/falling/both edge)
    has_it_mode = any(
        p in generated_code
        for p in [
            "GPIO_MODE_IT_RISING",
            "GPIO_MODE_IT_FALLING",
            "GPIO_MODE_IT_RISING_FALLING",
        ]
    )
    details.append(
        CheckDetail(
            check_name="exti_interrupt_mode_set",
            passed=has_it_mode,
            expected="GPIO configured with GPIO_MODE_IT_RISING or similar",
            actual="present" if has_it_mode else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: NVIC priority set before enabling IRQ
    set_prio_pos = generated_code.find("HAL_NVIC_SetPriority")
    enable_irq_pos = generated_code.find("HAL_NVIC_EnableIRQ")
    nvic_order_ok = (
        set_prio_pos != -1
        and enable_irq_pos != -1
        and set_prio_pos < enable_irq_pos
    )
    details.append(
        CheckDetail(
            check_name="nvic_priority_set_before_enable",
            passed=nvic_order_ok,
            expected="HAL_NVIC_SetPriority called before HAL_NVIC_EnableIRQ",
            actual="correct order" if nvic_order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 4: HAL_GPIO_EXTI_Callback defined (not just IRQHandler alone)
    has_exti_callback = "HAL_GPIO_EXTI_Callback" in generated_code
    details.append(
        CheckDetail(
            check_name="exti_callback_defined",
            passed=has_exti_callback,
            expected="HAL_GPIO_EXTI_Callback override defined",
            actual="present" if has_exti_callback else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: LED toggle done via HAL (not busy-wait polling button in loop)
    has_toggle = "HAL_GPIO_TogglePin" in generated_code
    details.append(
        CheckDetail(
            check_name="led_toggled_via_hal",
            passed=has_toggle,
            expected="HAL_GPIO_TogglePin called for LED",
            actual="present" if has_toggle else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: No busy-wait polling of button pin in main loop
    # (LLM failure: while(1) { if(HAL_GPIO_ReadPin...) toggle } instead of using interrupt)
    has_read_in_loop = "HAL_GPIO_ReadPin" in generated_code
    # If ReadPin is present, check it's not the primary mechanism (callback must also exist)
    no_polling_only = not has_read_in_loop or has_exti_callback
    details.append(
        CheckDetail(
            check_name="no_button_polling_loop",
            passed=no_polling_only,
            expected="Button read via interrupt callback, not polling in main loop",
            actual="interrupt used" if no_polling_only else "polling only, no callback",
            check_type="constraint",
        )
    )

    return details
