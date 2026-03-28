"""Behavioral checks for sensor fusion (accel + gyro to orientation)."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor fusion behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Both sensor_sample_fetch calls happen (one per device)
    # (LLM failure: fetching only one sensor or using a single shared fetch)
    fetch_count = generated_code.count("sensor_sample_fetch")
    details.append(
        CheckDetail(
            check_name="both_sensors_fetched",
            passed=fetch_count >= 2,
            expected="sensor_sample_fetch() called for BOTH accel and gyro devices",
            actual=f"found {fetch_count} fetch call(s)" + (" (correct)" if fetch_count >= 2 else " (only one — gyro or accel missed!)"),
            check_type="constraint",
        )
    )

    # Check 2: Accel and gyro use different sensor channel enums
    # (LLM failure: using SENSOR_CHAN_ACCEL_X for both, or mixing up channels)
    has_accel_chan = (
        "SENSOR_CHAN_ACCEL_X" in generated_code
        or "SENSOR_CHAN_ACCEL_XYZ" in generated_code
    )
    has_gyro_chan = (
        "SENSOR_CHAN_GYRO_X" in generated_code
        or "SENSOR_CHAN_GYRO_XYZ" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="different_channels_for_accel_gyro",
            passed=has_accel_chan and has_gyro_chan,
            expected="SENSOR_CHAN_ACCEL_* used for accel, SENSOR_CHAN_GYRO_* for gyro",
            actual="correct" if (has_accel_chan and has_gyro_chan)
                   else f"wrong — {'missing ACCEL channel' if not has_accel_chan else 'missing GYRO channel'}",
            check_type="constraint",
        )
    )

    # Check 3: compute_orientation called AFTER both fetches
    # (LLM failure: computing orientation before fetching gyro data)
    orientation_pos = generated_code.find("compute_orientation")
    if orientation_pos == -1:
        orientation_pos = generated_code.lower().find("pitch")
    last_fetch_pos = generated_code.rfind("sensor_sample_fetch")
    details.append(
        CheckDetail(
            check_name="orientation_after_both_fetches",
            passed=orientation_pos != -1 and last_fetch_pos != -1 and orientation_pos > last_fetch_pos,
            expected="Orientation computation AFTER the last sensor_sample_fetch()",
            actual="correct" if (orientation_pos != -1 and last_fetch_pos != -1 and orientation_pos > last_fetch_pos)
                   else "missing or computed before all sensor data is fetched",
            check_type="constraint",
        )
    )

    # Check 4: No Arduino IMU API used
    # (LLM failure: using IMU.readAcceleration() from Arduino_LSM9DS1 library)
    no_arduino = "IMU.readAcceleration" not in generated_code and "IMU.readGyroscope" not in generated_code
    details.append(
        CheckDetail(
            check_name="no_arduino_api_used",
            passed=no_arduino,
            expected="Arduino IMU API (IMU.readAcceleration) NOT used",
            actual="absent (correct)" if no_arduino
                   else "PRESENT — Arduino API used in Zephyr code!",
            check_type="constraint",
        )
    )

    # Check 5: No Linux IIO API used
    # (LLM failure: using iio_channel_read from Linux industrial I/O)
    no_iio = "iio_channel_read" not in generated_code and "iio_read_channel" not in generated_code
    details.append(
        CheckDetail(
            check_name="no_linux_iio_api_used",
            passed=no_iio,
            expected="Linux IIO API (iio_channel_read) NOT used",
            actual="absent (correct)" if no_iio
                   else "PRESENT — Linux IIO API used in Zephyr code!",
            check_type="constraint",
        )
    )

    # Check 6: sensor_value_to_double or manual conversion used for computation
    has_float_conversion = (
        "sensor_value_to_double" in generated_code
        or "sensor_value_to_float" in generated_code
        or "val1" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="sensor_value_converted_for_math",
            passed=has_float_conversion,
            expected="sensor_value converted to float/double before math (sensor_value_to_double or val1)",
            actual="present" if has_float_conversion
                   else "missing (computing orientation on raw sensor_value struct?)",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
