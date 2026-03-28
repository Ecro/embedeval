"""Behavioral checks for Zephyr sensor API temperature read."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: fetch before get (mandatory ordering)
    # (LLM failure: calling channel_get without fetch)
    fetch_pos = generated_code.find("sensor_sample_fetch")
    get_pos = generated_code.find("sensor_channel_get")
    details.append(
        CheckDetail(
            check_name="fetch_before_get",
            passed=fetch_pos != -1 and get_pos != -1 and fetch_pos < get_pos,
            expected="sensor_sample_fetch() before sensor_channel_get()",
            actual="correct" if fetch_pos < get_pos else "wrong order",
            check_type="constraint",
        )
    )

    # Check 2: device_is_ready check
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() before sensor operations",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 3: Uses SENSOR_CHAN_AMBIENT_TEMP (correct channel)
    has_temp_chan = "SENSOR_CHAN_AMBIENT_TEMP" in generated_code
    details.append(
        CheckDetail(
            check_name="correct_temp_channel",
            passed=has_temp_chan,
            expected="SENSOR_CHAN_AMBIENT_TEMP for temperature",
            actual="present" if has_temp_chan else "wrong channel",
            check_type="exact_match",
        )
    )

    # Check 4: Error handling for fetch and get
    has_err = "< 0" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_error_handling",
            passed=has_err,
            expected="Error checks on sensor API returns",
            actual="present" if has_err else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Periodic read in loop (not one-shot)
    has_loop = "while" in generated_code or "for" in generated_code
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="periodic_read_loop",
            passed=has_loop and has_sleep,
            expected="Periodic sensor read with sleep",
            actual=f"loop={has_loop}, sleep={has_sleep}",
            check_type="constraint",
        )
    )

    # Check 6: sensor value converted for display (val1/val2 extraction)
    # (LLM failure: printing the raw struct pointer or ignoring val1/val2 fields)
    has_conversion = bool(re.search(r'\.val1|\.val2|sensor_value_to', generated_code))
    details.append(CheckDetail(
        check_name="raw_to_physical_conversion",
        passed=has_conversion,
        expected="Sensor value fields (val1/val2) used for physical unit conversion",
        actual="conversion found" if has_conversion else "no sensor value field access",
        check_type="constraint",
    ))

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
