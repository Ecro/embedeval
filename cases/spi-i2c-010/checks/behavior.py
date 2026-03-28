"""Behavioral checks for I2C register block write with repeated start."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C repeated start behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Buffer includes register address as first byte
    has_reg_in_buf = (
        "REG_ADDR" in generated_code
        or "0x10" in generated_code
        or "reg_addr" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="register_address_in_write_buffer",
            passed=has_reg_in_buf,
            expected="Register address (0x10 or REG_ADDR) included as first byte of write buffer",
            actual="present" if has_reg_in_buf else "missing register address in buffer",
            check_type="constraint",
        )
    )

    # Check 2: RESTART or STOP flag used (not separate i2c_write calls)
    has_restart_or_stop = (
        "I2C_MSG_RESTART" in generated_code
        or "I2C_MSG_STOP" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="restart_or_stop_flag_used",
            passed=has_restart_or_stop,
            expected="I2C_MSG_RESTART or I2C_MSG_STOP used for proper transaction termination",
            actual="present" if has_restart_or_stop else "missing — may result in incomplete transaction",
            check_type="constraint",
        )
    )

    # Check 3: Device address 0x3C referenced
    has_dev_addr = "0x3C" in generated_code or "0x3c" in generated_code or "DEV_ADDR" in generated_code
    details.append(
        CheckDetail(
            check_name="device_address_0x3c",
            passed=has_dev_addr,
            expected="Device I2C address 0x3C referenced",
            actual="present" if has_dev_addr else "missing or wrong address",
            check_type="exact_match",
        )
    )

    # Check 4: Error checking on i2c_transfer return value
    transfer_pos = generated_code.find("i2c_transfer")
    has_error_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="transfer_return_checked",
            passed=has_error_check and transfer_pos != -1,
            expected="i2c_transfer() return value checked for error",
            actual="present" if (has_error_check and transfer_pos != -1) else "missing error check",
            check_type="constraint",
        )
    )

    # Check 5: Success message printed
    has_success_print = (
        "Register write OK" in generated_code
        or ("printk" in generated_code and ("OK" in generated_code or "success" in generated_code.lower()))
    )
    details.append(
        CheckDetail(
            check_name="success_message_printed",
            passed=has_success_print,
            expected="Success message printed after successful write",
            actual="present" if has_success_print else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Not using raw i2c_write (bypass of message-level control)
    uses_only_i2c_write = (
        "i2c_write(" in generated_code
        and "i2c_transfer" not in generated_code
    )
    details.append(
        CheckDetail(
            check_name="i2c_transfer_not_replaced_by_write",
            passed=not uses_only_i2c_write,
            expected="i2c_transfer() used (not plain i2c_write without RESTART control)",
            actual="correct" if not uses_only_i2c_write else "plain i2c_write used without RESTART flag control",
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
