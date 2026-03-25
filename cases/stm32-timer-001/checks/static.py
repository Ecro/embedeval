"""Static analysis checks for STM32 HAL TIM3 PWM application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL TIM3 PWM code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: STM32 HAL header
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

    # Check 2: TIM_HandleTypeDef used
    has_tim_handle = "TIM_HandleTypeDef" in generated_code
    details.append(
        CheckDetail(
            check_name="tim_handle_typedef_used",
            passed=has_tim_handle,
            expected="TIM_HandleTypeDef struct used",
            actual="present" if has_tim_handle else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: TIM3 instance used
    has_tim3 = "TIM3" in generated_code
    details.append(
        CheckDetail(
            check_name="tim3_instance_used",
            passed=has_tim3,
            expected="TIM3 instance configured",
            actual="present" if has_tim3 else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: PWM started via HAL_TIM_PWM_Start
    has_pwm_start = "HAL_TIM_PWM_Start" in generated_code
    details.append(
        CheckDetail(
            check_name="pwm_start_called",
            passed=has_pwm_start,
            expected="HAL_TIM_PWM_Start called",
            actual="present" if has_pwm_start else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: No cross-platform hallucinations
    has_zephyr = any(
        p in generated_code
        for p in ["pwm_set_dt", "counter_set_top_value", "zephyr/", "k_sleep", "DEVICE_DT_GET"]
    )
    has_espidf = any(p in generated_code for p in ["esp_", "ledc_set_duty", "mcpwm_"])
    has_arduino = any(p in generated_code for p in ["analogWrite", "tone("])
    no_hallucination = not has_zephyr and not has_espidf and not has_arduino
    details.append(
        CheckDetail(
            check_name="no_cross_platform_hallucination",
            passed=no_hallucination,
            expected="Only STM32 HAL timer/PWM APIs used",
            actual="clean" if no_hallucination else f"zephyr={has_zephyr} espidf={has_espidf} arduino={has_arduino}",
            check_type="constraint",
        )
    )

    # Check 6: Timer clock enable
    has_tim_clk = any(
        p in generated_code
        for p in ["__HAL_RCC_TIM3_CLK_ENABLE", "__HAL_RCC_TIM", "RCC_APB1ENR"]
    )
    details.append(
        CheckDetail(
            check_name="timer_clock_enabled",
            passed=has_tim_clk,
            expected="TIM3 peripheral clock enabled",
            actual="present" if has_tim_clk else "missing",
            check_type="exact_match",
        )
    )

    return details
