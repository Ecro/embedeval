"""Static analysis checks for STM32 HAL SPI master communication application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL SPI code structure and required elements."""
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

    # Check 2: SPI_HandleTypeDef used
    has_spi_handle = "SPI_HandleTypeDef" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_handle_typedef_used",
            passed=has_spi_handle,
            expected="SPI_HandleTypeDef struct used",
            actual="present" if has_spi_handle else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: SPI1 instance configured
    has_spi1 = "SPI1" in generated_code
    details.append(
        CheckDetail(
            check_name="spi1_instance_configured",
            passed=has_spi1,
            expected="SPI1 instance used",
            actual="present" if has_spi1 else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Manual NSS (software CS) — not hardware NSS
    has_soft_nss = "SPI_NSS_SOFT" in generated_code
    details.append(
        CheckDetail(
            check_name="software_nss_used",
            passed=has_soft_nss,
            expected="SPI_NSS_SOFT used for manual chip-select",
            actual="present" if has_soft_nss else "missing or hardware NSS",
            check_type="exact_match",
        )
    )

    # Check 5: No cross-platform hallucinations
    has_zephyr = any(
        p in generated_code
        for p in ["spi_write", "spi_read", "spi_transceive", "zephyr/", "k_sleep"]
    )
    has_espidf = any(p in generated_code for p in ["esp_", "spi_device_transmit"])
    has_arduino = any(p in generated_code for p in ["SPI.begin", "SPI.transfer"])
    no_hallucination = not has_zephyr and not has_espidf and not has_arduino
    details.append(
        CheckDetail(
            check_name="no_cross_platform_hallucination",
            passed=no_hallucination,
            expected="Only STM32 HAL SPI APIs used",
            actual="clean" if no_hallucination else f"zephyr={has_zephyr} espidf={has_espidf} arduino={has_arduino}",
            check_type="constraint",
        )
    )

    # Check 6: SPI clock enable
    has_spi_clk = any(
        p in generated_code
        for p in ["__HAL_RCC_SPI1_CLK_ENABLE", "__HAL_RCC_SPI", "RCC_APB2ENR"]
    )
    details.append(
        CheckDetail(
            check_name="spi_clock_enabled",
            passed=has_spi_clk,
            expected="SPI1 peripheral clock enabled",
            actual="present" if has_spi_clk else "missing",
            check_type="exact_match",
        )
    )

    return details
