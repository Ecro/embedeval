"""Behavioral checks for sensor attribute configuration before read."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor attribute configuration behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: sensor_attr_set called before sensor_sample_fetch
    # (LLM failure: reading data before configuring the sensor)
    attr_pos = generated_code.find("sensor_attr_set")
    fetch_pos = generated_code.find("sensor_sample_fetch")
    details.append(
        CheckDetail(
            check_name="attr_set_before_fetch",
            passed=attr_pos != -1 and fetch_pos != -1 and attr_pos < fetch_pos,
            expected="sensor_attr_set() before sensor_sample_fetch()",
            actual="correct" if (attr_pos != -1 and fetch_pos != -1 and attr_pos < fetch_pos) else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Both sampling frequency and full-scale configured
    has_odr = "SENSOR_ATTR_SAMPLING_FREQUENCY" in generated_code
    has_fs = "SENSOR_ATTR_FULL_SCALE" in generated_code
    details.append(
        CheckDetail(
            check_name="both_attributes_set",
            passed=has_odr and has_fs,
            expected="Both SENSOR_ATTR_SAMPLING_FREQUENCY and SENSOR_ATTR_FULL_SCALE set",
            actual=f"ODR={has_odr}, FS={has_fs}",
            check_type="constraint",
        )
    )

    # Check 3: Error handling on sensor_attr_set
    attr_set_count = generated_code.count("sensor_attr_set")
    has_attr_err = attr_set_count >= 1 and (
        "< 0" in generated_code or "!= 0" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="attr_set_error_handling",
            passed=has_attr_err,
            expected="Return value of sensor_attr_set() checked",
            actual="present" if has_attr_err else "missing",
            check_type="constraint",
        )
    )

    # Check 4: sensor_value struct used for attribute values, not raw int
    # (LLM failure: passing integer directly instead of struct sensor_value)
    has_sensor_value_for_attr = (
        "sensor_value" in generated_code
        and "val1" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="sensor_value_for_attribute",
            passed=has_sensor_value_for_attr,
            expected="struct sensor_value with val1 used for attribute value",
            actual="present" if has_sensor_value_for_attr else "missing or using raw integer",
            check_type="constraint",
        )
    )

    # Check 5: device_is_ready before anything
    ready_pos = generated_code.find("device_is_ready")
    details.append(
        CheckDetail(
            check_name="device_ready_before_attr",
            passed=ready_pos != -1 and (attr_pos == -1 or ready_pos < attr_pos),
            expected="device_is_ready() before sensor_attr_set()",
            actual="correct" if (ready_pos != -1 and (attr_pos == -1 or ready_pos < attr_pos)) else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 6: Configured message printed
    has_configured_msg = "configured" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="configuration_message",
            passed=has_configured_msg,
            expected="'Sensor configured' message printed after attribute setup",
            actual="present" if has_configured_msg else "missing",
            check_type="constraint",
        )
    )

    return details
