"""Static analysis checks for GPIO wakeup from deep sleep application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate GPIO deep sleep wakeup code structure."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/pm/pm.h
    has_pm_h = "zephyr/pm/pm.h" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_header_included",
            passed=has_pm_h,
            expected="zephyr/pm/pm.h included",
            actual="present" if has_pm_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Includes zephyr/drivers/gpio.h
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

    # Check 3: Uses pm_state_force (correct Zephyr API for forcing sleep state)
    has_pm_force = "pm_state_force" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_pm_state_force",
            passed=has_pm_force,
            expected="pm_state_force() used to enter deep sleep",
            actual="present" if has_pm_force else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Hallucination — gpio_wakeup_enable() does not exist in Zephyr
    has_fake_wakeup = "gpio_wakeup_enable" in generated_code
    details.append(
        CheckDetail(
            check_name="no_gpio_wakeup_enable_hallucination",
            passed=not has_fake_wakeup,
            expected="gpio_wakeup_enable() not used (does not exist in Zephyr)",
            actual="hallucinated API found" if has_fake_wakeup else "clean",
            check_type="constraint",
        )
    )

    # Check 5: Hallucination — deepsleep() does not exist in Zephyr
    has_fake_deepsleep = "deepsleep(" in generated_code
    details.append(
        CheckDetail(
            check_name="no_deepsleep_hallucination",
            passed=not has_fake_deepsleep,
            expected="deepsleep() not used (does not exist in Zephyr)",
            actual="hallucinated API found" if has_fake_deepsleep else "clean",
            check_type="constraint",
        )
    )

    # Check 6: Cross-platform — no STM32 HAL power APIs
    has_hal_pwr = "HAL_PWR_Enter" in generated_code or "HAL_PWR_EnterSTANDBY" in generated_code
    details.append(
        CheckDetail(
            check_name="no_stm32_hal_power",
            passed=not has_hal_pwr,
            expected="HAL_PWR_Enter* not used (STM32 HAL, wrong platform)",
            actual="STM32 HAL found" if has_hal_pwr else "clean",
            check_type="constraint",
        )
    )

    # Check 7: Uses GPIO_DT_SPEC_GET
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

    return details
