"""Static analysis checks for sensor fusion (accel + gyro)."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor fusion code structure."""
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

    has_accel_chan = (
        "SENSOR_CHAN_ACCEL_X" in generated_code
        or "SENSOR_CHAN_ACCEL_XYZ" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="accel_channel_used",
            passed=has_accel_chan,
            expected="Accelerometer channel (SENSOR_CHAN_ACCEL_X/XYZ) used",
            actual="present" if has_accel_chan else "missing or wrong channel type",
            check_type="exact_match",
        )
    )

    has_gyro_chan = (
        "SENSOR_CHAN_GYRO_X" in generated_code
        or "SENSOR_CHAN_GYRO_XYZ" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="gyro_channel_used",
            passed=has_gyro_chan,
            expected="Gyroscope channel (SENSOR_CHAN_GYRO_X/XYZ) used",
            actual="present" if has_gyro_chan else "missing or wrong channel type",
            check_type="exact_match",
        )
    )

    has_two_fetches = generated_code.count("sensor_sample_fetch") >= 2
    details.append(
        CheckDetail(
            check_name="two_sensor_fetches",
            passed=has_two_fetches,
            expected="sensor_sample_fetch() called for both accel and gyro devices",
            actual=f"found {generated_code.count('sensor_sample_fetch')} fetch calls",
            check_type="exact_match",
        )
    )

    has_orientation = (
        "orientation" in generated_code.lower()
        or "pitch" in generated_code.lower()
        or "roll" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="orientation_computation",
            passed=has_orientation,
            expected="Orientation/pitch/roll computation after fetching data",
            actual="present" if has_orientation else "missing (no fusion computation)",
            check_type="exact_match",
        )
    )

    no_arduino_api = "IMU.readAcceleration" not in generated_code
    details.append(
        CheckDetail(
            check_name="no_arduino_imu_api",
            passed=no_arduino_api,
            expected="IMU.readAcceleration() NOT used (Arduino API, not Zephyr)",
            actual="absent (correct)" if no_arduino_api else "PRESENT (wrong platform API!)",
            check_type="exact_match",
        )
    )

    no_linux_iio = "iio_channel_read" not in generated_code
    details.append(
        CheckDetail(
            check_name="no_linux_iio_api",
            passed=no_linux_iio,
            expected="iio_channel_read() NOT used (Linux IIO API, not Zephyr)",
            actual="absent (correct)" if no_linux_iio else "PRESENT (wrong platform API!)",
            check_type="exact_match",
        )
    )

    return details
