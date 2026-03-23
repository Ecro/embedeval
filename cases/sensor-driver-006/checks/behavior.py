"""Behavioral checks for custom sensor driver with I2C backend."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C-backed custom sensor driver behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: WHO_AM_I read BEFORE any data register read
    # (LLM failure: init reads data register or skips WHO_AM_I entirely)
    who_am_i_pos = generated_code.find("WHO_AM_I")
    data_reg_pos = generated_code.find("DATA_REG")
    if data_reg_pos == -1:
        data_reg_pos = generated_code.find("0x28")
    details.append(
        CheckDetail(
            check_name="who_am_i_before_data_read",
            passed=who_am_i_pos != -1 and (data_reg_pos == -1 or who_am_i_pos < data_reg_pos),
            expected="WHO_AM_I register read during init before any data register access",
            actual="correct" if (who_am_i_pos != -1 and (data_reg_pos == -1 or who_am_i_pos < data_reg_pos))
                   else "missing WHO_AM_I check or wrong order",
            check_type="constraint",
        )
    )

    # Check 2: -ENODEV returned on WHO_AM_I mismatch (not silently passing)
    # (LLM failure: printing a warning but returning 0 — driver binds to wrong hardware)
    has_enodev_on_mismatch = (
        "ENODEV" in generated_code
        and ("!=" in generated_code or "!=" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="enodev_on_who_am_i_mismatch",
            passed=has_enodev_on_mismatch,
            expected="-ENODEV returned when WHO_AM_I value does not match expected",
            actual="correct" if has_enodev_on_mismatch
                   else "missing — init always succeeds even with wrong device on bus!",
            check_type="constraint",
        )
    )

    # Check 3: sample_fetch AND channel_get both wired into sensor_driver_api
    # (LLM failure: defining functions but forgetting to assign them in api struct)
    has_fetch_in_api = (
        "sample_fetch" in generated_code
        and "sensor_driver_api" in generated_code
    )
    has_get_in_api = (
        "channel_get" in generated_code
        and "sensor_driver_api" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="api_struct_fully_populated",
            passed=has_fetch_in_api and has_get_in_api,
            expected="Both sample_fetch and channel_get assigned in sensor_driver_api struct",
            actual="correct" if (has_fetch_in_api and has_get_in_api)
                   else "missing — one or both callbacks not wired into api struct",
            check_type="constraint",
        )
    )

    # Check 4: dev->config used to get i2c_dev and i2c_addr
    # (LLM failure: hardcoding I2C device name or address instead of using device config)
    has_dev_config = "dev->config" in generated_code or "cfg->i2c" in generated_code
    details.append(
        CheckDetail(
            check_name="config_from_device_struct",
            passed=has_dev_config,
            expected="I2C device/address obtained from dev->config (DT-driven)",
            actual="correct" if has_dev_config
                   else "missing — hardcoded I2C device or address (not DT-driven)",
            check_type="constraint",
        )
    )

    # Check 5: channel_get returns -ENOTSUP for unsupported channels
    has_enotsup = "ENOTSUP" in generated_code
    details.append(
        CheckDetail(
            check_name="enotsup_for_unsupported_channel",
            passed=has_enotsup,
            expected="-ENOTSUP returned for unsupported sensor channels in channel_get",
            actual="present" if has_enotsup else "missing (silently ignoring unsupported channels)",
            check_type="constraint",
        )
    )

    # Check 6: No sensor_register() hallucination
    no_sensor_register = "sensor_register(" not in generated_code
    details.append(
        CheckDetail(
            check_name="no_sensor_register_hallucination",
            passed=no_sensor_register,
            expected="sensor_register() NOT called (API does not exist in Zephyr)",
            actual="absent (correct)" if no_sensor_register
                   else "PRESENT — hallucinated API that does not exist!",
            check_type="constraint",
        )
    )

    return details
