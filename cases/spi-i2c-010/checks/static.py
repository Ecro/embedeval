"""Static analysis checks for I2C register block write with repeated start."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C repeated start code structure and required elements."""
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

    # Check 2: i2c_transfer used
    has_i2c_transfer = "i2c_transfer" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_transfer_used",
            passed=has_i2c_transfer,
            expected="i2c_transfer() used for message-level I2C control",
            actual="present" if has_i2c_transfer else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: struct i2c_msg used
    has_i2c_msg = "i2c_msg" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_msg_struct_used",
            passed=has_i2c_msg,
            expected="struct i2c_msg used",
            actual="present" if has_i2c_msg else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: I2C_MSG_WRITE flag used
    has_write_flag = "I2C_MSG_WRITE" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_msg_write_flag",
            passed=has_write_flag,
            expected="I2C_MSG_WRITE flag set in message",
            actual="present" if has_write_flag else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: I2C_MSG_STOP flag used
    has_stop_flag = "I2C_MSG_STOP" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_msg_stop_flag",
            passed=has_stop_flag,
            expected="I2C_MSG_STOP flag used to terminate transaction",
            actual="present" if has_stop_flag else "missing",
            check_type="exact_match",
        )
    )

    return details
