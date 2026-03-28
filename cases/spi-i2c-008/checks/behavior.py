"""Behavioral checks for I2C target (slave) mode implementation."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C target mode behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: write_requested callback implemented
    has_write_requested = "write_requested" in generated_code
    details.append(
        CheckDetail(
            check_name="write_requested_callback",
            passed=has_write_requested,
            expected="write_requested callback implemented",
            actual="present" if has_write_requested else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: read_requested callback implemented
    has_read_requested = "read_requested" in generated_code
    details.append(
        CheckDetail(
            check_name="read_requested_callback",
            passed=has_read_requested,
            expected="read_requested callback implemented",
            actual="present" if has_read_requested else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: write_received callback implemented
    has_write_received = "write_received" in generated_code
    details.append(
        CheckDetail(
            check_name="write_received_callback",
            passed=has_write_received,
            expected="write_received callback implemented",
            actual="present" if has_write_received else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: read_processed callback implemented
    has_read_processed = "read_processed" in generated_code
    details.append(
        CheckDetail(
            check_name="read_processed_callback",
            passed=has_read_processed,
            expected="read_processed callback implemented",
            actual="present" if has_read_processed else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: All 4 callbacks present (composite check)
    all_four_callbacks = (
        has_write_requested
        and has_read_requested
        and has_write_received
        and has_read_processed
    )
    details.append(
        CheckDetail(
            check_name="all_four_callbacks_implemented",
            passed=all_four_callbacks,
            expected="All 4 i2c_target_callbacks implemented",
            actual="all present" if all_four_callbacks else "one or more callbacks missing",
            check_type="constraint",
        )
    )

    # Check 6: Target registered with valid address (0x55 or any 7-bit address)
    has_address = "0x55" in generated_code or "TARGET_ADDR" in generated_code or ".address" in generated_code
    details.append(
        CheckDetail(
            check_name="target_address_set",
            passed=has_address,
            expected="Target address configured in i2c_target_config",
            actual="present" if has_address else "missing",
            check_type="constraint",
        )
    )

    # Check 7: device_is_ready must appear before i2c_target_register (ordering)
    pos_ready = generated_code.find("device_is_ready")
    pos_register = generated_code.find("i2c_target_register")
    ready_before_register = (
        pos_ready != -1 and pos_register != -1 and pos_ready < pos_register
    )
    details.append(
        CheckDetail(
            check_name="device_ready_before_register",
            passed=ready_before_register,
            expected="device_is_ready called before i2c_target_register",
            actual=(
                "correct order"
                if ready_before_register
                else (
                    "device_is_ready missing"
                    if pos_ready == -1
                    else "i2c_target_register missing"
                    if pos_register == -1
                    else "device_is_ready called after i2c_target_register"
                )
            ),
            check_type="ordering",
        )
    )

    # Check 8: i2c_target_register return value must be error-checked
    error_checked = False
    if pos_register != -1:
        window = generated_code[pos_register : pos_register + 150]
        error_checked = any(
            marker in window
            for marker in ("< 0", "!= 0", "if (ret", "if (err")
        )
    details.append(
        CheckDetail(
            check_name="i2c_target_register_error_checked",
            passed=error_checked,
            expected="i2c_target_register return value checked for error",
            actual="error check present" if error_checked else "return value not checked",
            check_type="constraint",
        )
    )

    # Check 9: must NOT use deprecated slave API
    deprecated_apis = ["i2c_slave_register", "i2c_slave_callbacks", "i2c_slave_config"]
    deprecated_found = [api for api in deprecated_apis if api in generated_code]
    no_deprecated = len(deprecated_found) == 0
    details.append(
        CheckDetail(
            check_name="no_deprecated_slave_api",
            passed=no_deprecated,
            expected="No deprecated i2c_slave_* APIs used",
            actual=(
                "no deprecated APIs"
                if no_deprecated
                else f"deprecated APIs found: {', '.join(deprecated_found)}"
            ),
            check_type="constraint",
        )
    )

    # Check 10: all 4 callback fields assigned in i2c_target_callbacks struct
    required_fields = [
        ".write_requested",
        ".read_requested",
        ".write_received",
        ".read_processed",
    ]
    missing_fields = [
        field for field in required_fields
        if not re.search(rf"{re.escape(field)}\s*=", generated_code)
    ]
    callbacks_in_struct = len(missing_fields) == 0
    details.append(
        CheckDetail(
            check_name="callbacks_assigned_in_struct",
            passed=callbacks_in_struct,
            expected="All 4 callback fields assigned in i2c_target_callbacks struct",
            actual=(
                "all 4 fields assigned"
                if callbacks_in_struct
                else f"missing fields: {', '.join(missing_fields)}"
            ),
            check_type="structural",
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
