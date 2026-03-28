"""Static analysis checks for ADC oversampling application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ADC oversampling code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/drivers/adc.h
    has_adc_h = "zephyr/drivers/adc.h" in generated_code
    details.append(
        CheckDetail(
            check_name="adc_header_included",
            passed=has_adc_h,
            expected="zephyr/drivers/adc.h included",
            actual="present" if has_adc_h else "missing",
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

    # Check 3: Uses adc_channel_setup
    has_setup = "adc_channel_setup" in generated_code
    details.append(
        CheckDetail(
            check_name="adc_channel_setup_called",
            passed=has_setup,
            expected="adc_channel_setup() called",
            actual="present" if has_setup else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Oversampling field set in adc_sequence
    has_oversampling = "oversampling" in generated_code
    details.append(
        CheckDetail(
            check_name="oversampling_configured",
            passed=has_oversampling,
            expected="oversampling field set in adc_sequence struct",
            actual="present" if has_oversampling else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Cross-platform — no Arduino analogRead
    has_arduino = "analogRead" in generated_code
    details.append(
        CheckDetail(
            check_name="no_arduino_analogread",
            passed=not has_arduino,
            expected="analogRead() not used (Arduino API, wrong platform)",
            actual="Arduino API found" if has_arduino else "clean",
            check_type="constraint",
        )
    )

    # Check 6: Cross-platform — no STM32 HAL_ADC
    has_hal_adc = "HAL_ADC_Start" in generated_code or "HAL_ADC_GetValue" in generated_code
    details.append(
        CheckDetail(
            check_name="no_stm32_hal_adc",
            passed=not has_hal_adc,
            expected="HAL_ADC_Start/GetValue not used (STM32 HAL, wrong platform)",
            actual="STM32 HAL found" if has_hal_adc else "clean",
            check_type="constraint",
        )
    )

    # Check 7: Uses adc_read
    has_adc_read = "adc_read" in generated_code
    details.append(
        CheckDetail(
            check_name="adc_read_called",
            passed=has_adc_read,
            expected="adc_read() called",
            actual="present" if has_adc_read else "missing",
            check_type="exact_match",
        )
    )

    return details
