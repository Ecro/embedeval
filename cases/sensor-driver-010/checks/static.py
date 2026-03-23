"""Static analysis checks for sensor calibration offset storage in NVS."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor calibration NVS integration code structure."""
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

    has_nvs_h = "zephyr/fs/nvs.h" in generated_code
    details.append(
        CheckDetail(
            check_name="nvs_header",
            passed=has_nvs_h,
            expected="zephyr/fs/nvs.h included",
            actual="present" if has_nvs_h else "missing",
            check_type="exact_match",
        )
    )

    has_nvs_read = "nvs_read" in generated_code
    details.append(
        CheckDetail(
            check_name="nvs_read_called",
            passed=has_nvs_read,
            expected="nvs_read() called to load stored calibration",
            actual="present" if has_nvs_read else "missing (calibration never loaded from storage)",
            check_type="exact_match",
        )
    )

    has_nvs_write = "nvs_write" in generated_code
    details.append(
        CheckDetail(
            check_name="nvs_write_called",
            passed=has_nvs_write,
            expected="nvs_write() called to persist calibration",
            actual="present" if has_nvs_write else "missing (calibration never saved)",
            check_type="exact_match",
        )
    )

    has_nvs_mount = "nvs_mount" in generated_code
    details.append(
        CheckDetail(
            check_name="nvs_mount_called",
            passed=has_nvs_mount,
            expected="nvs_mount() called to initialize NVS filesystem",
            actual="present" if has_nvs_mount else "missing",
            check_type="exact_match",
        )
    )

    has_attr_set = "sensor_attr_set" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_attr_set_for_offset",
            passed=has_attr_set,
            expected="sensor_attr_set() used to apply calibration offset",
            actual="present" if has_attr_set else "missing (offset not applied via sensor API)",
            check_type="exact_match",
        )
    )

    has_offset_attr = "SENSOR_ATTR_OFFSET" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_attr_offset_used",
            passed=has_offset_attr,
            expected="SENSOR_ATTR_OFFSET used as attribute for calibration",
            actual="present" if has_offset_attr else "missing",
            check_type="exact_match",
        )
    )

    has_cal_struct = (
        "sensor_cal" in generated_code
        or ("offset_x" in generated_code and "offset_y" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="calibration_struct_defined",
            passed=has_cal_struct,
            expected="Calibration data struct defined with offset fields",
            actual="present" if has_cal_struct else "missing",
            check_type="exact_match",
        )
    )

    return details
