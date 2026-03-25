"""Static analysis checks for STM32 HAL I2C sensor read application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL I2C code structure and required elements."""
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

    # Check 2: I2C_HandleTypeDef used
    has_i2c_handle = "I2C_HandleTypeDef" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_handle_typedef_used",
            passed=has_i2c_handle,
            expected="I2C_HandleTypeDef struct used",
            actual="present" if has_i2c_handle else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: I2C1 instance configured
    has_i2c1 = "I2C1" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c1_instance_configured",
            passed=has_i2c1,
            expected="I2C1 instance used",
            actual="present" if has_i2c1 else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Register read via HAL_I2C_Mem_Read (not raw byte read)
    has_mem_read = "HAL_I2C_Mem_Read" in generated_code
    details.append(
        CheckDetail(
            check_name="hal_i2c_mem_read_used",
            passed=has_mem_read,
            expected="HAL_I2C_Mem_Read used for register read",
            actual="present" if has_mem_read else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: No cross-platform hallucinations
    has_zephyr = any(
        p in generated_code
        for p in ["i2c_write", "i2c_read", "i2c_burst_read", "zephyr/", "k_sleep", "DEVICE_DT_GET"]
    )
    has_espidf = any(p in generated_code for p in ["esp_", "i2c_master_write"])
    has_arduino = any(p in generated_code for p in ["Wire.begin", "Wire.read", "Wire.write"])
    no_hallucination = not has_zephyr and not has_espidf and not has_arduino
    details.append(
        CheckDetail(
            check_name="no_cross_platform_hallucination",
            passed=no_hallucination,
            expected="Only STM32 HAL I2C APIs used",
            actual="clean" if no_hallucination else f"zephyr={has_zephyr} espidf={has_espidf} arduino={has_arduino}",
            check_type="constraint",
        )
    )

    # Check 6: I2C clock enable
    has_i2c_clk = any(
        p in generated_code
        for p in ["__HAL_RCC_I2C1_CLK_ENABLE", "__HAL_RCC_I2C", "RCC_APB1ENR"]
    )
    details.append(
        CheckDetail(
            check_name="i2c_clock_enabled",
            passed=has_i2c_clk,
            expected="I2C1 peripheral clock enabled",
            actual="present" if has_i2c_clk else "missing",
            check_type="exact_match",
        )
    )

    return details
