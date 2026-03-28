"""Behavioral checks for multi-device SPI bus with CS GPIO."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-device SPI behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Two separate spi_config structs (one per device)
    config_count = generated_code.count("spi_config")
    has_two_configs = config_count >= 2
    details.append(
        CheckDetail(
            check_name="two_spi_configs_defined",
            passed=has_two_configs,
            expected="Two separate spi_config structs (one per device)",
            actual=f"spi_config count={config_count}",
            check_type="constraint",
        )
    )

    # Check 2: Different CS pins used for each device
    # Look for two different pin numbers in CS configs
    pin_matches = re.findall(r"\.pin\s*=\s*(\d+)", generated_code)
    has_different_pins = len(set(pin_matches)) >= 2
    details.append(
        CheckDetail(
            check_name="different_cs_pins_per_device",
            passed=has_different_pins,
            expected="Different GPIO CS pins used for each device",
            actual=f"pins found: {pin_matches}" if pin_matches else "no pin numbers found",
            check_type="constraint",
        )
    )

    # Check 3: Bus shared (single SPI device reference)
    spi_dev_count = generated_code.count("DEVICE_DT_GET")
    # Should be 1 or 2 (one for SPI, one for GPIO), not 3+ separate SPI controllers
    bus_shared = 0 < spi_dev_count <= 3
    details.append(
        CheckDetail(
            check_name="single_spi_bus_shared",
            passed=bus_shared,
            expected="SPI bus shared between devices (single DT node)",
            actual=f"DEVICE_DT_GET calls={spi_dev_count}",
            check_type="constraint",
        )
    )

    # Check 4: GPIO_ACTIVE_LOW used for CS (correct polarity)
    has_active_low = "GPIO_ACTIVE_LOW" in generated_code
    details.append(
        CheckDetail(
            check_name="cs_gpio_active_low",
            passed=has_active_low,
            expected="GPIO_ACTIVE_LOW polarity for chip select",
            actual="present" if has_active_low else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Two separate write operations
    write_count = generated_code.count("spi_write(") + generated_code.count("spi_transceive(")
    has_two_writes = write_count >= 2
    details.append(
        CheckDetail(
            check_name="two_separate_write_operations",
            passed=has_two_writes,
            expected="At least 2 SPI write/transceive operations (one per device)",
            actual=f"write operations={write_count}",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
