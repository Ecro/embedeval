"""Static analysis checks for custom sensor driver with I2C backend."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C-backed custom sensor driver code structure."""
    details: list[CheckDetail] = []

    has_sensor_h = "zephyr/drivers/sensor.h" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_header",
            passed=has_sensor_h,
            expected="zephyr/drivers/sensor.h included",
            actual="present" if has_sensor_h else "missing",
            check_type="exact_match",
        )
    )

    has_i2c_h = "zephyr/drivers/i2c.h" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_header",
            passed=has_i2c_h,
            expected="zephyr/drivers/i2c.h included",
            actual="present" if has_i2c_h else "missing",
            check_type="exact_match",
        )
    )

    has_register_macro = "SENSOR_DEVICE_DT_INST_DEFINE" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_device_dt_inst_define",
            passed=has_register_macro,
            expected="SENSOR_DEVICE_DT_INST_DEFINE macro used (not sensor_register())",
            actual="present" if has_register_macro else "missing or wrong registration method",
            check_type="exact_match",
        )
    )

    no_sensor_register = "sensor_register(" not in generated_code
    details.append(
        CheckDetail(
            check_name="no_sensor_register_hallucination",
            passed=no_sensor_register,
            expected="sensor_register() NOT used (it does not exist in Zephyr)",
            actual="absent (correct)" if no_sensor_register else "PRESENT (hallucinated API!)",
            check_type="exact_match",
        )
    )

    has_driver_api = "sensor_driver_api" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_driver_api_struct",
            passed=has_driver_api,
            expected="struct sensor_driver_api used for API table",
            actual="present" if has_driver_api else "wrong struct name or missing",
            check_type="exact_match",
        )
    )

    has_who_am_i = "WHO_AM_I" in generated_code or "who_am_i" in generated_code
    details.append(
        CheckDetail(
            check_name="who_am_i_register_read",
            passed=has_who_am_i,
            expected="WHO_AM_I register read during init",
            actual="present" if has_who_am_i else "missing (init does not verify device identity)",
            check_type="exact_match",
        )
    )

    has_i2c_read = (
        "i2c_reg_read_byte" in generated_code
        or "i2c_read" in generated_code
        or "i2c_write_read" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="i2c_read_call",
            passed=has_i2c_read,
            expected="I2C read function called (i2c_reg_read_byte or i2c_read)",
            actual="present" if has_i2c_read else "missing (no I2C communication)",
            check_type="exact_match",
        )
    )

    has_enodev = "ENODEV" in generated_code
    details.append(
        CheckDetail(
            check_name="enodev_on_bad_who_am_i",
            passed=has_enodev,
            expected="-ENODEV returned when WHO_AM_I does not match",
            actual="present" if has_enodev else "missing (init always succeeds even with wrong device)",
            check_type="exact_match",
        )
    )

    return details
