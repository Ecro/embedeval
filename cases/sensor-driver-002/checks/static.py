"""Static analysis checks for sensor data-ready trigger."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor trigger code structure."""
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

    has_trigger_set = "sensor_trigger_set" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_trigger_set",
            passed=has_trigger_set,
            expected="sensor_trigger_set() called",
            actual="present" if has_trigger_set else "missing",
            check_type="exact_match",
        )
    )

    has_data_ready = "SENSOR_TRIG_DATA_READY" in generated_code
    details.append(
        CheckDetail(
            check_name="data_ready_trigger_type",
            passed=has_data_ready,
            expected="SENSOR_TRIG_DATA_READY trigger type used",
            actual="present" if has_data_ready else "wrong or missing trigger type",
            check_type="exact_match",
        )
    )

    has_sensor_trigger_struct = "sensor_trigger" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_trigger_struct",
            passed=has_sensor_trigger_struct,
            expected="struct sensor_trigger declared",
            actual="present" if has_sensor_trigger_struct else "missing",
            check_type="exact_match",
        )
    )

    has_callback = (
        "const struct device *dev" in generated_code
        and "const struct sensor_trigger *trig" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="callback_signature",
            passed=has_callback,
            expected="Callback with correct Zephyr trigger signature",
            actual="correct" if has_callback else "missing or wrong signature",
            check_type="exact_match",
        )
    )

    has_device_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_device_ready,
            expected="device_is_ready() called",
            actual="present" if has_device_ready else "missing",
            check_type="exact_match",
        )
    )

    return details
