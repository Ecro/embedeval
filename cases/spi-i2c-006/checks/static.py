"""Static analysis checks for I2C clock stretching timeout."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C clock stretching code structure and required elements."""
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
    has_dev_get = "DEVICE_DT_GET" in generated_code
    details.append(
        CheckDetail(
            check_name="device_dt_get_used",
            passed=has_dev_get,
            expected="DEVICE_DT_GET used to obtain I2C device",
            actual="present" if has_dev_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: i2c_read used
    has_i2c_read = "i2c_read" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_read_used",
            passed=has_i2c_read,
            expected="i2c_read() called to read from device",
            actual="present" if has_i2c_read else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: device_is_ready check present
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_is_ready_check",
            passed=has_ready,
            expected="device_is_ready() called before I2C operation",
            actual="present" if has_ready else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: No non-existent i2c_set_timeout() (hallucination guard)
    has_fake_api = "i2c_set_timeout" in generated_code
    details.append(
        CheckDetail(
            check_name="no_fake_i2c_set_timeout",
            passed=not has_fake_api,
            expected="No non-existent i2c_set_timeout() — use retry or K_MSEC timeout instead",
            actual="clean" if not has_fake_api else "i2c_set_timeout() used — not a real Zephyr API",
            check_type="hallucination",
        )
    )

    return details
