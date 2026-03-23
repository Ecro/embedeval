"""Static analysis checks for sensor power management (low-power mode)."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor power management code structure."""
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
            check_name="sensor_attr_set_used",
            passed=has_attr_set,
            expected="sensor_attr_set() used to change sensor mode",
            actual="present" if has_attr_set else "missing (power mode not controlled via attribute API)",
            check_type="exact_match",
        )
    )

    has_sampling_freq = "SENSOR_ATTR_SAMPLING_FREQUENCY" in generated_code
    details.append(
        CheckDetail(
            check_name="sampling_frequency_attribute",
            passed=has_sampling_freq,
            expected="SENSOR_ATTR_SAMPLING_FREQUENCY used as attribute",
            actual="present" if has_sampling_freq else "missing",
            check_type="exact_match",
        )
    )

    has_low_power = (
        ".val1 = 0" in generated_code
        or "freq_hz = 0" in generated_code
        or ", 0)" in generated_code
        or "= 0," in generated_code
    )
    details.append(
        CheckDetail(
            check_name="low_power_freq_zero",
            passed=has_low_power,
            expected="Frequency set to 0 for low-power/idle mode",
            actual="present" if has_low_power else "missing (never enters low-power mode)",
            check_type="exact_match",
        )
    )

    has_sample_fetch = "sensor_sample_fetch" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_sample_fetch",
            passed=has_sample_fetch,
            expected="sensor_sample_fetch() called to read sensor data",
            actual="present" if has_sample_fetch else "missing",
            check_type="exact_match",
        )
    )

    has_channel_get = "sensor_channel_get" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_channel_get",
            passed=has_channel_get,
            expected="sensor_channel_get() called to retrieve value",
            actual="present" if has_channel_get else "missing",
            check_type="exact_match",
        )
    )

    return details
