"""Static analysis checks for STM32 HAL DMA memory-to-memory transfer application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL DMA M2M code structure and required elements."""
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

    # Check 2: DMA_HandleTypeDef used
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

    # Check 3: DMA2 Stream 0 used (only DMA2 supports M2M on STM32F4)
    has_dma2_s0 = "DMA2_Stream0" in generated_code
    details.append(
        CheckDetail(
            check_name="dma2_stream0_used",
            passed=has_dma2_s0,
            expected="DMA2_Stream0 used (DMA2 required for M2M)",
            actual="present" if has_dma2_s0 else "missing or wrong stream",
            check_type="exact_match",
        )
    )

    # Check 4: Memory-to-memory direction configured
    has_m2m = "DMA_MEMORY_TO_MEMORY" in generated_code
    details.append(
        CheckDetail(
            check_name="m2m_direction_configured",
            passed=has_m2m,
            expected="DMA_MEMORY_TO_MEMORY direction configured",
            actual="present" if has_m2m else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: HAL_DMA_Start_IT used (interrupt-driven, not polling)
    has_start_it = "HAL_DMA_Start_IT" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_start_it_used",
            passed=has_start_it,
            expected="HAL_DMA_Start_IT used for interrupt-driven transfer",
            actual="present" if has_start_it else "missing or polling only",
            check_type="exact_match",
        )
    )

    # Check 6: No cross-platform hallucinations
    has_zephyr = any(
        p in generated_code
        for p in ["dma_config", "dma_start", "zephyr/", "k_sleep", "DEVICE_DT_GET"]
    )
    has_espidf = any(p in generated_code for p in ["esp_", "gdma_", "spi_dma"])
    no_hallucination = not has_zephyr and not has_espidf
    details.append(
        CheckDetail(
            check_name="no_cross_platform_hallucination",
            passed=no_hallucination,
            expected="Only STM32 HAL DMA APIs used",
            actual="clean" if no_hallucination else f"zephyr={has_zephyr} espidf={has_espidf}",
            check_type="constraint",
        )
    )

    return details
