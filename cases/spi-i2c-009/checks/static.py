"""Static analysis checks for multi-device SPI with CS GPIO."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-device SPI code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: SPI header included
    has_spi_h = "zephyr/drivers/spi.h" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_header_included",
            passed=has_spi_h,
            expected="zephyr/drivers/spi.h included",
            actual="present" if has_spi_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: GPIO header included
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

    # Check 3: spi_config struct used (at least one)
    has_spi_config = "spi_config" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_config_struct_used",
            passed=has_spi_config,
            expected="spi_config struct used for device configuration",
            actual="present" if has_spi_config else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CS GPIO field present in config
    has_cs_gpio = ".cs" in generated_code and "gpio" in generated_code
    details.append(
        CheckDetail(
            check_name="cs_gpio_in_spi_config",
            passed=has_cs_gpio,
            expected="CS GPIO configured in spi_config.cs.gpio",
            actual="present" if has_cs_gpio else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: spi_write or spi_transceive used
    has_spi_write = "spi_write" in generated_code or "spi_transceive" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_write_or_transceive_used",
            passed=has_spi_write,
            expected="spi_write() or spi_transceive() used for transfer",
            actual="present" if has_spi_write else "missing",
            check_type="exact_match",
        )
    )

    return details
