"""Behavioral checks for STM32 HAL I2C sensor read application."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL I2C behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Device ready check before read (HAL_I2C_IsDeviceReady)
    has_device_ready = "HAL_I2C_IsDeviceReady" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check_before_read",
            passed=has_device_ready,
            expected="HAL_I2C_IsDeviceReady called before data read",
            actual="present" if has_device_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 2: Device ready check BEFORE Mem_Read (ordering)
    ready_pos = generated_code.find("HAL_I2C_IsDeviceReady")
    mem_read_pos = generated_code.find("HAL_I2C_Mem_Read")
    ready_before_read = (
        ready_pos != -1 and mem_read_pos != -1 and ready_pos < mem_read_pos
    )
    details.append(
        CheckDetail(
            check_name="device_ready_before_mem_read",
            passed=ready_before_read,
            expected="HAL_I2C_IsDeviceReady called before HAL_I2C_Mem_Read",
            actual="correct order" if ready_before_read else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: 8-bit addressing size specified for register read
    has_8bit_addr = "I2C_MEMADD_SIZE_8BIT" in generated_code
    details.append(
        CheckDetail(
            check_name="mem_addr_size_8bit",
            passed=has_8bit_addr,
            expected="I2C_MEMADD_SIZE_8BIT used for register address size",
            actual="present" if has_8bit_addr else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Error handling on Mem_Read return value
    has_error_check = any(
        p in generated_code
        for p in ["!= HAL_OK", "== HAL_OK", "HAL_ERROR", "HAL_TIMEOUT"]
    )
    details.append(
        CheckDetail(
            check_name="i2c_error_handling",
            passed=has_error_check,
            expected="HAL_I2C_Mem_Read return value checked",
            actual="present" if has_error_check else "missing",
            check_type="constraint",
        )
    )

    # Check 5: 100kHz clock speed configured
    # Accept "100000" or "I2C_SPEED_STANDARD" or "100kHz" in comments
    has_100khz = any(
        p in generated_code
        for p in ["100000", "I2C_SPEED_STANDARD", "100kHz", "100 kHz"]
    )
    details.append(
        CheckDetail(
            check_name="i2c_100khz_speed",
            passed=has_100khz,
            expected="I2C speed set to 100kHz (100000)",
            actual="present" if has_100khz else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: I2C address left-shifted for STM32 HAL (8-bit format)
    has_shifted = bool(re.search(r'0x68\s*<<\s*1', generated_code)) or \
                  bool(re.search(r'0xD0', generated_code, re.IGNORECASE)) or \
                  bool(re.search(r'0xd0', generated_code))
    details.append(
        CheckDetail(
            check_name="i2c_address_left_shifted",
            passed=has_shifted,
            expected="I2C address left-shifted for STM32 HAL (0x68 << 1 = 0xD0)",
            actual="correct 8-bit address format" if has_shifted else "possible 7-bit address used directly",
            check_type="constraint",
        )
    )

    # Check 7: I2C clock enabled before HAL_I2C_Init
    clk_pos = -1
    for token in ["__HAL_RCC_I2C1_CLK_ENABLE", "__HAL_RCC_I2C"]:
        pos = generated_code.find(token)
        if pos != -1:
            clk_pos = pos if clk_pos == -1 else min(clk_pos, pos)
    i2c_init_pos = generated_code.find("HAL_I2C_Init")
    clock_before_init = clk_pos != -1 and i2c_init_pos != -1 and clk_pos < i2c_init_pos
    details.append(
        CheckDetail(
            check_name="i2c_clock_before_init",
            passed=clock_before_init,
            expected="I2C clock enabled before HAL_I2C_Init",
            actual="correct order" if clock_before_init else "wrong order or missing",
            check_type="constraint",
        )
    )

    return details
