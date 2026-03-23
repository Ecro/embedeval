"""Static analysis checks for Zephyr sensor API temperature read."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor code structure."""
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

    has_get = "sensor_channel_get" in generated_code
    details.append(
        CheckDetail(
            check_name="channel_get",
            passed=has_get,
            expected="sensor_channel_get() called",
            actual="present" if has_get else "missing",
            check_type="exact_match",
        )
    )

    has_sv = "sensor_value" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_value_struct",
            passed=has_sv,
            expected="struct sensor_value used",
            actual="present" if has_sv else "missing",
            check_type="exact_match",
        )
    )

    has_chan = "SENSOR_CHAN" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_channel_enum",
            passed=has_chan,
            expected="SENSOR_CHAN_* enum used",
            actual="present" if has_chan else "missing",
            check_type="exact_match",
        )
    )

    return details
