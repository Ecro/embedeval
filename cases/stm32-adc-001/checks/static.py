"""Static analysis checks for STM32 HAL ADC + DMA continuous conversion application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL ADC+DMA code structure and required elements."""
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

    # Check 2: ADC_HandleTypeDef used
    has_adc_handle = "ADC_HandleTypeDef" in generated_code
    details.append(
        CheckDetail(
            check_name="adc_handle_typedef_used",
            passed=has_adc_handle,
            expected="ADC_HandleTypeDef struct used",
            actual="present" if has_adc_handle else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: DMA_HandleTypeDef used
    has_dma_handle = "DMA_HandleTypeDef" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_handle_typedef_used",
            passed=has_dma_handle,
            expected="DMA_HandleTypeDef struct used",
            actual="present" if has_dma_handle else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: ADC started with DMA
    has_adc_start_dma = "HAL_ADC_Start_DMA" in generated_code
    details.append(
        CheckDetail(
            check_name="adc_started_with_dma",
            passed=has_adc_start_dma,
            expected="HAL_ADC_Start_DMA called",
            actual="present" if has_adc_start_dma else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: 12-bit resolution configured
    has_12bit = "ADC_RESOLUTION_12B" in generated_code
    details.append(
        CheckDetail(
            check_name="adc_12bit_resolution",
            passed=has_12bit,
            expected="ADC_RESOLUTION_12B configured",
            actual="present" if has_12bit else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: No cross-platform hallucinations
    has_zephyr = any(
        p in generated_code
        for p in ["adc_read", "adc_sequence", "zephyr/", "k_sleep", "DEVICE_DT_GET"]
    )
    has_espidf = any(p in generated_code for p in ["esp_", "adc1_get_raw", "adc_oneshot"])
    has_arduino = any(p in generated_code for p in ["analogRead", "analogReference"])
    no_hallucination = not has_zephyr and not has_espidf and not has_arduino
    details.append(
        CheckDetail(
            check_name="no_cross_platform_hallucination",
            passed=no_hallucination,
            expected="Only STM32 HAL ADC APIs used",
            actual="clean" if no_hallucination else f"zephyr={has_zephyr} espidf={has_espidf} arduino={has_arduino}",
            check_type="constraint",
        )
    )

    return details
