"""Behavioral checks for STM32 HAL SPI master communication application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL SPI behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: CS asserted (low) before transfer
    # Pattern: GPIO_PIN_RESET before HAL_SPI_Transmit/TransmitReceive
    cs_low_pos = -1
    for token in ["GPIO_PIN_RESET", "GPIO_PIN_Reset"]:
        pos = generated_code.find(token)
        if pos != -1:
            cs_low_pos = pos if cs_low_pos == -1 else min(cs_low_pos, pos)

    spi_tx_pos = -1
    for token in ["HAL_SPI_Transmit", "HAL_SPI_TransmitReceive"]:
        pos = generated_code.find(token)
        if pos != -1:
            spi_tx_pos = pos if spi_tx_pos == -1 else min(spi_tx_pos, pos)

    cs_before_tx = cs_low_pos != -1 and spi_tx_pos != -1 and cs_low_pos < spi_tx_pos
    details.append(
        CheckDetail(
            check_name="cs_asserted_before_transfer",
            passed=cs_before_tx,
            expected="CS pin driven low (GPIO_PIN_RESET) before SPI transfer",
            actual="correct order" if cs_before_tx else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: CS deasserted (high) after transfer
    cs_high_pos = generated_code.rfind("GPIO_PIN_SET")
    spi_last_pos = -1
    for token in ["HAL_SPI_Transmit", "HAL_SPI_Receive", "HAL_SPI_TransmitReceive"]:
        pos = generated_code.rfind(token)
        if pos != -1 and pos > spi_last_pos:
            spi_last_pos = pos

    cs_after_tx = cs_high_pos != -1 and spi_last_pos != -1 and cs_high_pos > spi_last_pos
    details.append(
        CheckDetail(
            check_name="cs_deasserted_after_transfer",
            passed=cs_after_tx,
            expected="CS pin driven high (GPIO_PIN_SET) after SPI transfer",
            actual="correct order" if cs_after_tx else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: HAL return value checked (error handling)
    has_hal_ok_check = any(
        p in generated_code
        for p in ["HAL_OK", "!= HAL_OK", "== HAL_OK", "HAL_ERROR"]
    )
    details.append(
        CheckDetail(
            check_name="hal_return_checked",
            passed=has_hal_ok_check,
            expected="HAL_SPI return value checked (HAL_OK)",
            actual="present" if has_hal_ok_check else "missing",
            check_type="constraint",
        )
    )

    # Check 4: Master mode configured
    has_master_mode = "SPI_MODE_MASTER" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_master_mode_set",
            passed=has_master_mode,
            expected="SPI_MODE_MASTER configured",
            actual="present" if has_master_mode else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Clock enable before HAL_SPI_Init
    clk_pos = -1
    for token in ["__HAL_RCC_SPI1_CLK_ENABLE", "__HAL_RCC_SPI"]:
        pos = generated_code.find(token)
        if pos != -1:
            clk_pos = pos if clk_pos == -1 else min(clk_pos, pos)
    spi_init_pos = generated_code.find("HAL_SPI_Init")
    clock_before_init = clk_pos != -1 and spi_init_pos != -1 and clk_pos < spi_init_pos
    details.append(
        CheckDetail(
            check_name="spi_clock_before_init",
            passed=clock_before_init,
            expected="SPI clock enabled before HAL_SPI_Init",
            actual="correct order" if clock_before_init else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace", "STM32_HAL"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/POSIX APIs (STM32 HAL is expected)",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
