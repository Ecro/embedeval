"""Static analysis checks for custom sensor driver registration."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate custom sensor driver code structure."""
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

    has_register_macro = "SENSOR_DEVICE_DT_INST_DEFINE" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_device_dt_inst_define",
            passed=has_register_macro,
            expected="SENSOR_DEVICE_DT_INST_DEFINE macro used",
            actual="present" if has_register_macro else "missing (wrong registration method)",
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

    has_sample_fetch = "sample_fetch" in generated_code
    details.append(
        CheckDetail(
            check_name="sample_fetch_implemented",
            passed=has_sample_fetch,
            expected="sample_fetch callback implemented",
            actual="present" if has_sample_fetch else "missing",
            check_type="exact_match",
        )
    )

    has_channel_get = "channel_get" in generated_code
    details.append(
        CheckDetail(
            check_name="channel_get_implemented",
            passed=has_channel_get,
            expected="channel_get callback implemented",
            actual="present" if has_channel_get else "missing",
            check_type="exact_match",
        )
    )

    has_correct_init_sig = (
        "const struct device *dev" in generated_code
        and "my_sensor_init" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="init_function_signature",
            passed=has_correct_init_sig,
            expected="Init function with (const struct device *dev) signature",
            actual="correct" if has_correct_init_sig else "wrong or missing",
            check_type="exact_match",
        )
    )

    has_enotsup = "ENOTSUP" in generated_code
    details.append(
        CheckDetail(
            check_name="unsupported_channel_error",
            passed=has_enotsup,
            expected="-ENOTSUP returned for unsupported channels",
            actual="present" if has_enotsup else "missing",
            check_type="exact_match",
        )
    )

    return details
