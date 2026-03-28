"""Behavioral checks for sensor calibration offset storage in NVS."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor calibration NVS integration behavioral properties."""
    details: list[CheckDetail] = []

    # Use last occurrence of nvs_read and nvs_write to find the call sites in
    # main() rather than the helper function bodies (which appear earlier in
    # the file and would produce false ordering failures).
    nvs_read_pos = generated_code.rfind("nvs_read")
    # save_calibration() wraps nvs_write; find the save_calibration *call* in
    # main first, fall back to last nvs_write occurrence.
    nvs_write_pos = generated_code.rfind("save_calibration(")
    if nvs_write_pos == -1:
        nvs_write_pos = generated_code.rfind("nvs_write")

    # First sensor_sample_fetch call in main() (used for calibration data
    # collection).  Use the first occurrence that comes after nvs_read.
    sensor_fetch_pos = -1
    candidate = generated_code.find("sensor_sample_fetch")
    while candidate != -1:
        if candidate > nvs_read_pos:
            sensor_fetch_pos = candidate
            break
        candidate = generated_code.find("sensor_sample_fetch", candidate + 1)

    # Check 1: NVS read happens at startup BEFORE any sensor read
    # (LLM failure: reading sensor first, then trying to load calibration to apply — backwards)
    first_fetch_pos = generated_code.find("sensor_sample_fetch")
    details.append(
        CheckDetail(
            check_name="nvs_read_before_sensor_fetch",
            passed=nvs_read_pos != -1 and first_fetch_pos != -1 and nvs_read_pos < first_fetch_pos,
            expected="nvs_read() called at startup BEFORE first sensor_sample_fetch()",
            actual="correct" if (nvs_read_pos != -1 and first_fetch_pos != -1 and nvs_read_pos < first_fetch_pos)
                   else "WRONG ORDER — sensor read before loading stored calibration!",
            check_type="constraint",
        )
    )

    # Check 2: Calibration applied via sensor_attr_set (not post-processing)
    # (LLM failure: subtracting offset from reading in software rather than applying to sensor)
    attr_set_pos = generated_code.find("sensor_attr_set")
    details.append(
        CheckDetail(
            check_name="calibration_via_attr_set",
            passed=attr_set_pos != -1,
            expected="Calibration offset applied via sensor_attr_set() (not manual post-processing)",
            actual="correct" if attr_set_pos != -1
                   else "missing — offset subtracted manually instead of using SENSOR_ATTR_OFFSET",
            check_type="constraint",
        )
    )

    # Check 3: NVS write happens AFTER collecting calibration data (not before)
    # (LLM failure: writing to NVS before actually reading sensor for calibration)
    # sensor_fetch_pos is the first fetch AFTER nvs_read (the calibration measurement).
    details.append(
        CheckDetail(
            check_name="nvs_write_after_calibration",
            passed=sensor_fetch_pos != -1 and nvs_write_pos != -1 and sensor_fetch_pos < nvs_write_pos,
            expected="nvs_write() called AFTER sensor_sample_fetch() for calibration data",
            actual="correct" if (sensor_fetch_pos != -1 and nvs_write_pos != -1 and sensor_fetch_pos < nvs_write_pos)
                   else "WRONG ORDER — writing NVS before reading calibration data!",
            check_type="constraint",
        )
    )

    # Check 4: apply_calibration (attr_set) called after nvs_read on subsequent boots
    # (LLM failure: loading from NVS but never applying to sensor)
    has_apply_after_load = (
        nvs_read_pos != -1
        and attr_set_pos != -1
        and "SENSOR_ATTR_OFFSET" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="apply_loaded_calibration",
            passed=has_apply_after_load,
            expected="Loaded calibration applied via sensor_attr_set(SENSOR_ATTR_OFFSET)",
            actual="correct" if has_apply_after_load
                   else "missing — calibration loaded from NVS but never applied to sensor",
            check_type="constraint",
        )
    )

    # Check 5: NVS read error handled (not found is normal on first boot)
    # (LLM failure: crashing on NVS_NOT_FOUND instead of treating as "no calibration stored")
    has_nvs_error_handling = (
        "nvs_read" in generated_code
        and ("< 0" in generated_code or "<= 0" in generated_code
             or "!= " in generated_code or "if (" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="nvs_read_error_handled",
            passed=has_nvs_error_handling,
            expected="nvs_read() return value checked; missing key handled gracefully on first boot",
            actual="handled" if has_nvs_error_handling
                   else "missing — may crash on first boot when no calibration stored yet",
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
