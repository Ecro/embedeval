"""Static analysis checks for I2C multi-register burst read."""

import re

from embedeval.check_utils import resolve_define
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C burst read code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: I2C header included
    has_i2c_h = "zephyr/drivers/i2c.h" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_header_included",
            passed=has_i2c_h,
            expected="zephyr/drivers/i2c.h included",
            actual="present" if has_i2c_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Device obtained via DT
    has_dev_get = (
        "DEVICE_DT_GET" in generated_code
        or "device_get_binding" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="device_binding",
            passed=has_dev_get,
            expected="DEVICE_DT_GET or device_get_binding used",
            actual="present" if has_dev_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Burst read API used
    has_burst = (
        "i2c_burst_read" in generated_code
        or "i2c_write_read" in generated_code
        or "i2c_transfer" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="burst_read_api_used",
            passed=has_burst,
            expected="i2c_burst_read or i2c_write_read used",
            actual="present" if has_burst else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: 6-byte receive buffer
    has_six_bytes = (
        "[6]" in generated_code
        or "6]" in generated_code
        or ", 6" in generated_code
        or "ACCEL_DATA_LEN" in generated_code
    )
    # Also accept macros that resolve to 6 via #define
    if not has_six_bytes:
        for m in re.finditer(r'\[(\w+)\]', generated_code):
            token = m.group(1)
            if token.isdigit():
                if int(token) == 6:
                    has_six_bytes = True
                    break
            else:
                resolved = resolve_define(generated_code, token)
                if resolved == 6:
                    has_six_bytes = True
                    break
    details.append(
        CheckDetail(
            check_name="six_byte_buffer",
            passed=has_six_bytes,
            expected="6-byte receive buffer for burst read",
            actual="present" if has_six_bytes else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Register base address 0x28 referenced
    has_reg = "0x28" in generated_code
    details.append(
        CheckDetail(
            check_name="start_register_0x28",
            passed=has_reg,
            expected="Start register 0x28 (OUT_X_L) referenced",
            actual="present" if has_reg else "missing",
            check_type="exact_match",
        )
    )

    return details
