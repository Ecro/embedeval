"""Behavioral checks for custom sensor driver registration."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate custom sensor driver behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: sample_fetch and channel_get wired into api struct
    # (LLM failure: defining functions but not assigning them in the api struct)
    has_fetch_wired = bool(re.search(r'\.sample_fetch\s*=\s*\w+', generated_code))
    has_get_wired = bool(re.search(r'\.channel_get\s*=\s*\w+', generated_code))
    details.append(
        CheckDetail(
            check_name="api_struct_populated",
            passed=has_fetch_wired and has_get_wired,
            expected="sample_fetch and channel_get assigned in sensor_driver_api struct",
            actual=f"fetch_wired={has_fetch_wired}, get_wired={has_get_wired}" if not (has_fetch_wired and has_get_wired) else "correct",
            check_type="constraint",
        )
    )

    # Check 2: channel_get handles unsupported channels with -ENOTSUP
    # (LLM failure: returning 0 for all channels, no error for unsupported)
    has_enotsup = "ENOTSUP" in generated_code
    details.append(
        CheckDetail(
            check_name="unsupported_channel_returns_enotsup",
            passed=has_enotsup,
            expected="-ENOTSUP returned for unsupported sensor channels",
            actual="present" if has_enotsup else "missing (silently ignoring unsupported channels)",
            check_type="constraint",
        )
    )

    # Check 3: data->last_sample or similar field read in channel_get
    # (LLM failure: channel_get that ignores the fetched data)
    has_data_read = (
        "last_sample" in generated_code or
        "data->" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="channel_get_reads_data",
            passed=has_data_read,
            expected="channel_get reads from driver data struct (e.g., data->last_sample)",
            actual="present" if has_data_read else "missing (returning hardcoded value without fetched data)",
            check_type="constraint",
        )
    )

    # Check 4: sample_fetch writes to driver data struct
    # (LLM failure: sample_fetch that returns 0 without storing anything)
    has_data_write = (
        "last_sample" in generated_code and
        "=" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="sample_fetch_stores_data",
            passed=has_data_write,
            expected="sample_fetch stores sample into driver data struct",
            actual="present" if has_data_write else "missing (fetch does not store data)",
            check_type="constraint",
        )
    )

    # Check 5: Init function returns 0
    has_init_return_zero = (
        "my_sensor_init" in generated_code and
        "return 0" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="init_returns_zero",
            passed=has_init_return_zero,
            expected="Init function returns 0 on success",
            actual="present" if has_init_return_zero else "missing",
            check_type="constraint",
        )
    )

    # Check 6: val->val1 set in channel_get (correct sensor_value population)
    # (LLM failure: setting val = data->sample directly without val->val1)
    has_val1 = "val->val1" in generated_code or "val1" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_value_val1_set",
            passed=has_val1,
            expected="val->val1 set in channel_get to populate sensor_value",
            actual="present" if has_val1 else "missing (not properly populating sensor_value)",
            check_type="constraint",
        )
    )

    return details
