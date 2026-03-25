"""Static analysis checks for STM32 HAL GPIO LED + button interrupt application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL GPIO code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Correct STM32 HAL header (not Zephyr, not Arduino)
    has_hal_header = "stm32f4xx_hal.h" in generated_code
    details.append(
        CheckDetail(
            check_name="stm32_hal_header_included",
            passed=has_hal_header,
            expected="stm32f4xx_hal.h included",
            actual="present" if has_hal_header else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: GPIO_InitTypeDef used for configuration
    has_gpio_init_typedef = "GPIO_InitTypeDef" in generated_code
    details.append(
        CheckDetail(
            check_name="gpio_init_typedef_used",
            passed=has_gpio_init_typedef,
            expected="GPIO_InitTypeDef struct used",
            actual="present" if has_gpio_init_typedef else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: HAL_GPIO_Init called
    has_hal_gpio_init = "HAL_GPIO_Init" in generated_code
    details.append(
        CheckDetail(
            check_name="hal_gpio_init_called",
            passed=has_hal_gpio_init,
            expected="HAL_GPIO_Init() called",
            actual="present" if has_hal_gpio_init else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: RCC clock enable for GPIO (any GPIO port clock enable)
    has_rcc_clk = any(
        p in generated_code
        for p in [
            "__HAL_RCC_GPIOD_CLK_ENABLE",
            "__HAL_RCC_GPIOA_CLK_ENABLE",
            "__HAL_RCC_GPIO",
            "RCC_AHB1ENR",
        ]
    )
    details.append(
        CheckDetail(
            check_name="gpio_clock_enabled",
            passed=has_rcc_clk,
            expected="GPIO peripheral clock enabled via RCC",
            actual="present" if has_rcc_clk else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: NVIC configured for interrupt
    has_nvic = "HAL_NVIC_SetPriority" in generated_code or "HAL_NVIC_EnableIRQ" in generated_code
    details.append(
        CheckDetail(
            check_name="nvic_configured",
            passed=has_nvic,
            expected="NVIC priority and enable configured for EXTI",
            actual="present" if has_nvic else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: No cross-platform hallucinations (Zephyr, ESP-IDF, Arduino)
    has_zephyr = any(
        p in generated_code
        for p in ["k_sleep", "DEVICE_DT_GET", "gpio_pin_configure", "printk(", "zephyr/"]
    )
    has_espidf = any(
        p in generated_code
        for p in ["esp_", "gpio_set_level", "gpio_get_level", "esp-idf"]
    )
    has_arduino = any(
        p in generated_code
        for p in ["digitalWrite", "digitalRead", "pinMode", "Serial."]
    )
    no_hallucination = not has_zephyr and not has_espidf and not has_arduino
    details.append(
        CheckDetail(
            check_name="no_cross_platform_hallucination",
            passed=no_hallucination,
            expected="Only STM32 HAL APIs used",
            actual="clean" if no_hallucination else f"zephyr={has_zephyr} espidf={has_espidf} arduino={has_arduino}",
            check_type="constraint",
        )
    )

    return details
