"""Static analysis checks for SPI flash write and read verify."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate SPI flash code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: SPI header included
    has_spi_h = "zephyr/drivers/spi.h" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_header_included",
            passed=has_spi_h,
            expected="zephyr/drivers/spi.h included",
            actual="present" if has_spi_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Write enable command present (0x06)
    has_wren = "0x06" in generated_code or "WREN" in generated_code
    details.append(
        CheckDetail(
            check_name="write_enable_command",
            passed=has_wren,
            expected="Write enable command (0x06) present",
            actual="present" if has_wren else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Write command present (0x02)
    has_write_cmd = "0x02" in generated_code
    details.append(
        CheckDetail(
            check_name="write_command_0x02",
            passed=has_write_cmd,
            expected="SPI flash write command (0x02) present",
            actual="present" if has_write_cmd else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Read command present (0x03)
    has_read_cmd = "0x03" in generated_code
    details.append(
        CheckDetail(
            check_name="read_command_0x03",
            passed=has_read_cmd,
            expected="SPI flash read command (0x03) present",
            actual="present" if has_read_cmd else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Busy-wait polling loop present
    has_poll = (
        "WIP" in generated_code
        or "0x05" in generated_code
        or "RDSR" in generated_code
        or ("for" in generated_code and "poll" in generated_code.lower())
        or ("while" in generated_code and ("status" in generated_code.lower()
                                           or "busy" in generated_code.lower()))
    )
    details.append(
        CheckDetail(
            check_name="busy_wait_polling",
            passed=has_poll,
            expected="Status register poll / WIP busy-wait present",
            actual="present" if has_poll else "missing",
            check_type="exact_match",
        )
    )

    return details
