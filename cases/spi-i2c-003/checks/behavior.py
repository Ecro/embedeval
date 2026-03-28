"""Behavioral checks for I2C multi-register burst read."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C burst read behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: device_is_ready() before I2C operations
    has_ready = "device_is_ready" in generated_code
    burst_pos = max(
        generated_code.find("i2c_burst_read"),
        generated_code.find("i2c_write_read"),
        generated_code.find("i2c_transfer"),
    )
    ready_pos = generated_code.find("device_is_ready")
    order_ok = (
        has_ready
        and ready_pos != -1
        and burst_pos != -1
        and ready_pos < burst_pos
    )
    details.append(
        CheckDetail(
            check_name="ready_check_before_burst",
            passed=order_ok,
            expected="device_is_ready() before burst read operation",
            actual="correct order" if order_ok else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 2: Error handling on burst read return value
    has_error_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="burst_read_error_handling",
            passed=has_error_check,
            expected="Return value of burst read checked for errors",
            actual="present" if has_error_check else "missing",
            check_type="constraint",
        )
    )

    # Check 3: Little-endian axis reconstruction (low byte | high byte shifted)
    # Correct: (raw[1] << 8) | raw[0], etc.
    has_little_endian = bool(re.search(r'<<\s*8', generated_code)) and bool(re.search(r'\|', generated_code))
    # Also accept explicit byte swapping functions
    has_little_endian = has_little_endian or bool(
        re.search(r'__bswap|bswap|htole|letoh|le16_to_cpu', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="little_endian_reconstruction",
            passed=has_little_endian,
            expected="16-bit values reconstructed little-endian (low byte first)",
            actual="present" if has_little_endian else "missing or wrong byte order",
            check_type="constraint",
        )
    )

    # Check 4: I2C address in valid 7-bit range
    addr_matches = re.findall(r"0x([0-9a-fA-F]{2})", generated_code)
    valid_addr = any(
        0x01 <= int(m, 16) <= 0x7F for m in addr_matches
    )
    details.append(
        CheckDetail(
            check_name="valid_i2c_address",
            passed=valid_addr,
            expected="I2C device address in valid 7-bit range (0x01-0x7F)",
            actual=f"addresses found: {['0x' + m for m in addr_matches]}",
            check_type="constraint",
        )
    )

    # Check 5: All 6 bytes used (three axes)
    has_three_axes = (
        (generated_code.count("raw[") >= 6 or generated_code.count("buf[") >= 6)
        or ("x" in generated_code and "y" in generated_code and "z" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="three_axes_parsed",
            passed=has_three_axes,
            expected="All 6 bytes parsed into X, Y, Z axes",
            actual="present" if has_three_axes else "missing",
            check_type="constraint",
        )
    )

    return details
