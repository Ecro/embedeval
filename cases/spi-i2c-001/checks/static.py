"""Static analysis checks for I2C sensor register read."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C code structure and required elements."""
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

    # Check 2: Uses DEVICE_DT_GET or device_get_binding
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

    # Check 3: I2C address defined (hex constant 0x00-0x7F range)
    has_addr = bool(
        re.search(r"0x[0-9a-fA-F]{1,2}", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="i2c_address_defined",
            passed=has_addr,
            expected="I2C address defined as hex constant",
            actual="present" if has_addr else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Uses an I2C read API
    i2c_read_apis = [
        "i2c_reg_read_byte",
        "i2c_read",
        "i2c_write_read",
        "i2c_burst_read",
        "i2c_transfer",
    ]
    has_read = any(api in generated_code for api in i2c_read_apis)
    details.append(
        CheckDetail(
            check_name="i2c_read_api_used",
            passed=has_read,
            expected="I2C read API called",
            actual="present" if has_read else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: No raw I2C register manipulation
    has_raw = any(
        p in generated_code
        for p in ["I2C_BASE", "->DR", "->CR1", "*(volatile"]
    )
    details.append(
        CheckDetail(
            check_name="no_raw_i2c_access",
            passed=not has_raw,
            expected="Uses I2C API, not raw register access",
            actual="raw access found" if has_raw else "API only",
            check_type="constraint",
        )
    )

    return details
