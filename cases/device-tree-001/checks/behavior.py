"""Behavioral checks for Device Tree I2C sensor overlay."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree overlay behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Sensor node with correct compatible
    has_bme280 = 'compatible = "bosch,bme280"' in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_compatible",
            passed=has_bme280,
            expected='compatible = "bosch,bme280"',
            actual="present" if has_bme280 else "missing or wrong",
            check_type="exact_match",
        )
    )

    # Check 2: reg matches 0x76
    has_reg_76 = "reg = <0x76>" in generated_code
    details.append(
        CheckDetail(
            check_name="reg_address_0x76",
            passed=has_reg_76,
            expected="reg = <0x76>",
            actual="present" if has_reg_76 else "missing or wrong",
            check_type="exact_match",
        )
    )

    # Check 3: GPIO interrupt connected (int-gpios present)
    has_int_gpios = "int-gpios" in generated_code
    details.append(
        CheckDetail(
            check_name="interrupt_gpio_present",
            passed=has_int_gpios,
            expected="int-gpios property present",
            actual="present" if has_int_gpios else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: GPIO active low polarity
    has_active_low = "GPIO_ACTIVE_LOW" in generated_code
    details.append(
        CheckDetail(
            check_name="gpio_active_low",
            passed=has_active_low,
            expected="GPIO_ACTIVE_LOW polarity",
            actual="present" if has_active_low else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: status = "okay"
    has_status_okay = 'status = "okay"' in generated_code
    details.append(
        CheckDetail(
            check_name="status_okay",
            passed=has_status_okay,
            expected='status = "okay"',
            actual="present" if has_status_okay else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Node is child of i2c bus (i2c0 reference)
    has_i2c_bus = "i2c0" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_bus_parent",
            passed=has_i2c_bus,
            expected="Node under i2c0 bus",
            actual="i2c0 referenced" if has_i2c_bus else "i2c0 not found",
            check_type="constraint",
        )
    )

    return details
