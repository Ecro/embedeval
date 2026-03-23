"""Static analysis checks for I2C bus scan."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C bus scan code structure and required elements."""
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

    # Check 3: i2c_write used for probing
    has_i2c_write = (
        "i2c_write" in generated_code
        or "i2c_transfer" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="i2c_probe_api_used",
            passed=has_i2c_write,
            expected="i2c_write or i2c_transfer used for probing",
            actual="present" if has_i2c_write else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: A loop over address range exists
    has_loop = "for" in generated_code or "while" in generated_code
    details.append(
        CheckDetail(
            check_name="scan_loop_present",
            passed=has_loop,
            expected="Loop iterating over I2C addresses",
            actual="present" if has_loop else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Lower scan bound 0x08 referenced
    has_lower = "0x08" in generated_code or "0x07" in generated_code
    details.append(
        CheckDetail(
            check_name="lower_bound_referenced",
            passed=has_lower,
            expected="Lower scan bound 0x08 (skip 0x00-0x07 reserved) referenced",
            actual="present" if has_lower else "missing",
            check_type="exact_match",
        )
    )

    return details
