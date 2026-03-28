"""Behavioral checks for ESP-IDF SPI master half-duplex write."""
from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: spi_bus_initialize error checked
    init_pos = generated_code.find("spi_bus_initialize")
    post_init = generated_code[init_pos:init_pos + 300] if init_pos != -1 else ""
    has_init_check = "ESP_OK" in post_init or "!= ESP_OK" in post_init or "ret" in post_init
    details.append(CheckDetail(
        check_name="spi_bus_initialize_error_checked",
        passed=has_init_check,
        expected="spi_bus_initialize() return value checked",
        actual="present" if has_init_check else "missing",
        check_type="constraint",
    ))

    # Check 2: spi_device_interface_config_t struct used
    has_dev_cfg = "spi_device_interface_config_t" in generated_code
    details.append(CheckDetail(
        check_name="spi_device_interface_config_struct",
        passed=has_dev_cfg,
        expected="spi_device_interface_config_t for device configuration",
        actual="present" if has_dev_cfg else "missing",
        check_type="constraint",
    ))

    # Check 3: spi_transaction_t used (not raw buffer transfer)
    has_transaction = "spi_transaction_t" in generated_code
    details.append(CheckDetail(
        check_name="spi_transaction_struct",
        passed=has_transaction,
        expected="spi_transaction_t struct for transfer description",
        actual="present" if has_transaction else "missing",
        check_type="constraint",
    ))

    # Check 4: spi_device_transmit error checked
    tx_pos = generated_code.find("spi_device_transmit")
    post_tx = generated_code[tx_pos:tx_pos + 300] if tx_pos != -1 else ""
    has_tx_check = "ESP_OK" in post_tx or "!= ESP_OK" in post_tx or "ret" in post_tx
    details.append(CheckDetail(
        check_name="spi_device_transmit_error_checked",
        passed=has_tx_check,
        expected="spi_device_transmit() return value checked",
        actual="present" if has_tx_check else "missing",
        check_type="constraint",
    ))

    # Check 5: SPI_DMA_CH_AUTO or explicit DMA channel used
    has_dma = "SPI_DMA_CH_AUTO" in generated_code or "SPI_DMA_DISABLED" in generated_code
    details.append(CheckDetail(
        check_name="dma_channel_specified",
        passed=has_dma,
        expected="DMA channel specified (SPI_DMA_CH_AUTO or SPI_DMA_DISABLED)",
        actual="present" if has_dma else "missing (DMA parameter required for spi_bus_initialize)",
        check_type="constraint",
    ))

    # Check 6: No Arduino SPI APIs
    arduino_apis = ["SPI.begin", "SPI.transfer", "SPI.end"]
    found_arduino = [api for api in arduino_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_arduino_spi_apis",
        passed=not found_arduino,
        expected="No Arduino SPI APIs",
        actual="clean" if not found_arduino else f"found: {found_arduino}",
        check_type="hallucination",
    ))

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace", "FreeRTOS"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
