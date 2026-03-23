"""Behavioral checks for I2C clock stretching timeout handling."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C clock stretching behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Error handling on timeout (negative return value checked)
    has_error_check = (
        "< 0" in generated_code
        or "!= 0" in generated_code
        or "ret ==" in generated_code
        or "ETIMEDOUT" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="timeout_error_handled",
            passed=has_error_check,
            expected="Return value from i2c_read checked for error/timeout",
            actual="present" if has_error_check else "return value not checked",
            check_type="constraint",
        )
    )

    # Check 2: Not using K_FOREVER for timeout (dangerous with clock stretching)
    has_k_forever = "K_FOREVER" in generated_code
    details.append(
        CheckDetail(
            check_name="no_k_forever_timeout",
            passed=not has_k_forever,
            expected="Timeout must not be K_FOREVER — can hang bus with clock stretching",
            actual="safe" if not has_k_forever else "K_FOREVER used — dangerous for clock stretching devices",
            check_type="constraint",
        )
    )

    # Check 3: Finite timeout mechanism present (K_MSEC or similar)
    has_finite_timeout = (
        "K_MSEC" in generated_code
        or "K_SECONDS" in generated_code
        or "TIMEOUT" in generated_code
        or "timeout" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="finite_timeout_used",
            passed=has_finite_timeout,
            expected="Finite timeout (K_MSEC, K_SECONDS, or named timeout) used",
            actual="present" if has_finite_timeout else "missing timeout mechanism",
            check_type="constraint",
        )
    )

    # Check 4: Sensor address 0x48 referenced
    has_sensor_addr = "0x48" in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_address_0x48",
            passed=has_sensor_addr,
            expected="Sensor I2C address 0x48 referenced",
            actual="present" if has_sensor_addr else "missing or wrong address",
            check_type="exact_match",
        )
    )

    # Check 5: Error message printed on failure
    has_error_print = (
        "printk" in generated_code
        and ("error" in generated_code.lower() or "fail" in generated_code.lower()
             or "timeout" in generated_code.lower())
    )
    details.append(
        CheckDetail(
            check_name="error_message_printed",
            passed=has_error_print,
            expected="Error message printed on I2C failure or timeout",
            actual="present" if has_error_print else "missing error output",
            check_type="constraint",
        )
    )

    return details
