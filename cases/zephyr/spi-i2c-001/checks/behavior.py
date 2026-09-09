"""Behavioral checks for I2C sensor register read."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Device ready check before I2C operations
    has_ready = (
        scoped_contains(generated_code, 'device_is_ready', scope='code_only')
        or scoped_contains(generated_code, 'gpio_is_ready', scope='code_only')
    )
    i2c_api_pos = max(
        find_in_code(generated_code, "i2c_reg_read"),
        find_in_code(generated_code, "i2c_read"),
        find_in_code(generated_code, "i2c_write_read"),
        find_in_code(generated_code, "i2c_transfer"),
    )
    ready_pos = find_in_code(generated_code, "device_is_ready")
    order_ok = (
        has_ready and ready_pos != -1
        and i2c_api_pos != -1 and ready_pos < i2c_api_pos
    )
    details.append(
        CheckDetail(
            check_name="ready_check_before_io",
            passed=order_ok,
            expected="device_is_ready() before I2C operations",
            actual="correct order" if order_ok else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 2: I2C address in valid 7-bit range (0x00-0x7F)
    addr_matches = re.findall(
        r"(?:SENSOR_ADDR|I2C_ADDR|ADDR)\s*(?:=\s*|,\s*)?(0x[0-9a-fA-F]+)",
        generated_code,
    )
    if not addr_matches:
        addr_matches = re.findall(r"0x([0-9a-fA-F]{2})", generated_code)
    valid_addr = False
    if addr_matches:
        for m in addr_matches:
            val_str = m if m.startswith("0x") else f"0x{m}"
            try:
                val = int(val_str, 16)
                if 0x01 <= val <= 0x7F:
                    valid_addr = True
                    break
            except ValueError:
                pass
    details.append(
        CheckDetail(
            check_name="i2c_address_7bit_range",
            passed=valid_addr,
            expected="I2C address in 7-bit range (0x01-0x7F)",
            actual=f"addresses found: {addr_matches}" if addr_matches else "no address",
            check_type="constraint",
        )
    )

    # Check 3: Error handling for I2C read return value
    has_ret_check = (
        scoped_contains(generated_code, '< 0', scope='code_only')
        or scoped_contains(generated_code, '!= 0', scope='code_only')
        or scoped_contains(generated_code, 'ret < 0', scope='code_only')
        or scoped_contains(generated_code, 'rc < 0', scope='code_only')
        or scoped_contains(generated_code, 'err < 0', scope='code_only')
    )
    details.append(
        CheckDetail(
            check_name="i2c_error_handling",
            passed=has_ret_check,
            expected="Return value checked for I2C read errors",
            actual="present" if has_ret_check else "missing",
            check_type="constraint",
        )
    )

    # Check 4: WHO_AM_I register address defined
    has_reg_addr = (
        scoped_contains(generated_code, 'WHO_AM_I', scope='code_only')
        or scoped_contains(generated_code, '0x75', scope='code_only')
        or scoped_contains(generated_code, 'REG', scope='code_only')
    )
    details.append(
        CheckDetail(
            check_name="register_address_defined",
            passed=has_reg_addr,
            expected="Register address defined (WHO_AM_I or 0x75)",
            actual="present" if has_reg_addr else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Read result stored in a variable (not discarded)
    has_output_var = bool(
        re.search(r"uint8_t\s+\w+", generated_code)
        or re.search(r"&\w+\s*\)", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="read_result_stored",
            passed=has_output_var,
            expected="Read result stored in uint8_t variable",
            actual="present" if has_output_var else "missing",
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
