"""Behavioral checks for multi-peripheral board Device Tree overlay."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-peripheral overlay behavioral properties."""
    details: list[CheckDetail] = []

    # --- I2C / BME680 checks ---

    # Check 1: i2c0 enabled (AI failure: configures sensor but forgets to enable parent bus)
    has_i2c0_enabled = "&i2c0" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c0_enabled",
            passed=has_i2c0_enabled,
            expected="&i2c0 node reference present",
            actual="present" if has_i2c0_enabled else "missing — parent bus not enabled",
            check_type="constraint",
        )
    )

    # Check 2: BME680 compatible string (AI failure: uses bme280 address 0x76 instead of bme680 at 0x77)
    has_bme680_compatible = 'compatible = "bosch,bme680"' in generated_code
    details.append(
        CheckDetail(
            check_name="bme680_compatible",
            passed=has_bme680_compatible,
            expected='compatible = "bosch,bme680"',
            actual="present" if has_bme680_compatible else "missing or wrong compatible (check: bme680 not bme280)",
            check_type="exact_match",
        )
    )

    # Check 3: BME680 at address 0x77 (AI failure: uses 0x76 which is the BME280 address)
    has_bme680_addr = (
        "reg = <0x77>" in generated_code or "bme680@77" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="bme680_address_0x77",
            passed=has_bme680_addr,
            expected="BME680 at address 0x77 (reg = <0x77> or bme680@77)",
            actual="present" if has_bme680_addr else "missing or wrong address (0x77 required, not 0x76)",
            check_type="exact_match",
        )
    )

    # --- SPI / Flash checks ---

    # Check 4: spi0 enabled (AI failure: adds flash child but forgets to enable parent spi0)
    has_spi0_enabled = "&spi0" in generated_code
    details.append(
        CheckDetail(
            check_name="spi0_enabled",
            passed=has_spi0_enabled,
            expected="&spi0 node reference present",
            actual="present" if has_spi0_enabled else "missing — parent SPI bus not enabled",
            check_type="constraint",
        )
    )

    # Check 5: SPI flash with jedec,spi-nor compatible
    has_spi_nor = 'compatible = "jedec,spi-nor"' in generated_code
    details.append(
        CheckDetail(
            check_name="spi_nor_compatible",
            passed=has_spi_nor,
            expected='compatible = "jedec,spi-nor"',
            actual="present" if has_spi_nor else "missing or wrong SPI flash compatible",
            check_type="exact_match",
        )
    )

    # Check 6: SPI flash at chip select 0 (reg = <0>)
    has_flash_cs0 = "reg = <0>" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_flash_chip_select_0",
            passed=has_flash_cs0,
            expected="reg = <0> for SPI flash chip select 0",
            actual="present" if has_flash_cs0 else "missing or wrong chip select",
            check_type="exact_match",
        )
    )

    # --- GPIO checks ---

    # Check 7: gpio0 enabled (AI failure: references gpio0 pins without enabling the controller)
    has_gpio0_enabled = "&gpio0" in generated_code
    details.append(
        CheckDetail(
            check_name="gpio0_enabled",
            passed=has_gpio0_enabled,
            expected="&gpio0 node reference present",
            actual="present" if has_gpio0_enabled else "missing — GPIO controller not enabled",
            check_type="constraint",
        )
    )

    # Check 8: Two GPIO pins configured (AI failure: only configures one pin)
    # Count gpio0 pin references in angle-bracket cells
    gpio_pin_refs = generated_code.count("<&gpio0")
    has_two_gpio_pins = gpio_pin_refs >= 2
    details.append(
        CheckDetail(
            check_name="two_gpio_pins_configured",
            passed=has_two_gpio_pins,
            expected="At least 2 GPIO pin references (<&gpio0 ...>)",
            actual=f"{gpio_pin_refs} GPIO pin references found",
            check_type="constraint",
        )
    )

    # Check 9: All three bus parent nodes have status = "okay"
    # (AI failure: sets status on children only, leaves parents disabled)
    status_okay_count = generated_code.count('status = "okay"')
    has_enough_status = status_okay_count >= 3
    details.append(
        CheckDetail(
            check_name="parent_buses_all_enabled",
            passed=has_enough_status,
            expected="At least 3 status = \"okay\" entries (i2c0 + spi0 + gpio0 minimum)",
            actual=f"{status_okay_count} status = \"okay\" entries found",
            check_type="constraint",
        )
    )

    # Check 10: No conflicting reg addresses (BME680 at 0x77, not 0x76)
    # If code has both 0x76 and "bme680" that indicates the AI used the wrong address
    has_bme680_wrong_addr = (
        "bosch,bme680" in generated_code and "reg = <0x76>" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="bme680_no_wrong_address",
            passed=not has_bme680_wrong_addr,
            expected="BME680 must use 0x77, not 0x76 (0x76 is BME280)",
            actual="correct" if not has_bme680_wrong_addr else "wrong: bme680 with reg = <0x76>",
            check_type="constraint",
        )
    )

    return details
