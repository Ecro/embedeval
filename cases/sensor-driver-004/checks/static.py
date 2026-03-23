"""Static analysis checks for sensor attribute configuration before read."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor attribute configuration code structure."""
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

    has_attr_set = "sensor_attr_set" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_attr_set",
            passed=has_attr_set,
            expected="sensor_attr_set() called",
            actual="present" if has_attr_set else "missing",
            check_type="exact_match",
        )
    )

    has_sampling_freq = "SENSOR_ATTR_SAMPLING_FREQUENCY" in generated_code
    details.append(
        CheckDetail(
            check_name="sampling_frequency_attr",
            passed=has_sampling_freq,
            expected="SENSOR_ATTR_SAMPLING_FREQUENCY used",
            actual="present" if has_sampling_freq else "wrong or missing attribute",
            check_type="exact_match",
        )
    )

    has_full_scale = "SENSOR_ATTR_FULL_SCALE" in generated_code
    details.append(
        CheckDetail(
            check_name="full_scale_attr",
            passed=has_full_scale,
            expected="SENSOR_ATTR_FULL_SCALE used",
            actual="present" if has_full_scale else "wrong or missing attribute",
            check_type="exact_match",
        )
    )

    has_fetch = "sensor_sample_fetch" in generated_code
    details.append(
        CheckDetail(
            check_name="sample_fetch",
            passed=has_fetch,
            expected="sensor_sample_fetch() called",
            actual="present" if has_fetch else "missing",
            check_type="exact_match",
        )
    )

    has_sensor_value = "sensor_value" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_value_struct",
            passed=has_sensor_value,
            expected="struct sensor_value used for attribute and reading",
            actual="present" if has_sensor_value else "missing",
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
