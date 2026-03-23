"""Static analysis checks for I2C target (slave) mode implementation."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C target mode code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: I2C header included
    has_i2c_h = "zephyr/drivers/i2c.h" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_header_included",
            passed=has_i2c_h,
            expected="zephyr/drivers/i2c.h included",
            actual="present" if has_i2c_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: i2c_target_register used (not deprecated i2c_slave_register)
    has_target_register = "i2c_target_register" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_target_register_used",
            passed=has_target_register,
            expected="i2c_target_register() used (not deprecated i2c_slave_register)",
            actual="present" if has_target_register else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: No deprecated i2c_slave_register (hallucination guard)
    has_slave_register = "i2c_slave_register" in generated_code
    details.append(
        CheckDetail(
            check_name="no_deprecated_i2c_slave_register",
            passed=not has_slave_register,
            expected="i2c_slave_register() not used — deprecated, use i2c_target_register()",
            actual="clean" if not has_slave_register else "deprecated i2c_slave_register() used",
            check_type="hallucination",
        )
    )

    # Check 4: struct i2c_target_config used
    has_target_config = "i2c_target_config" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_target_config_struct_used",
            passed=has_target_config,
            expected="struct i2c_target_config defined",
            actual="present" if has_target_config else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: DEVICE_DT_GET used
    has_dev_get = "DEVICE_DT_GET" in generated_code
    details.append(
        CheckDetail(
            check_name="device_dt_get_used",
            passed=has_dev_get,
            expected="DEVICE_DT_GET used to obtain I2C device",
            actual="present" if has_dev_get else "missing",
            check_type="exact_match",
        )
    )

    return details
