"""Behavioral checks for SPI flash write and read verify."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate SPI flash behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Write enable command present AND ordered before write operation
    wren_pos = max(generated_code.find("WREN"), generated_code.lower().find("write_enable"))
    write_pos = max(generated_code.find("spi_write"), generated_code.find("spi_transceive"))
    has_wren_before = wren_pos != -1 and (write_pos == -1 or wren_pos < write_pos)
    details.append(
        CheckDetail(
            check_name="write_enable_before_write",
            passed=has_wren_before,
            expected="Write enable command (WREN/0x06) before write operation",
            actual="correct order" if has_wren_before else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 2: Status register polling / busy-wait after write
    has_poll = any(
        p in generated_code
        for p in ["WIP", "RDSR", "wait_ready", "flash_wait", "busy"]
    )
    details.append(
        CheckDetail(
            check_name="busy_wait_between_write_read",
            passed=has_poll,
            expected="Status register poll / busy-wait after write",
            actual="present" if has_poll else "missing",
            check_type="constraint",
        )
    )

    # Check 3: Verification comparison after read
    has_compare = (
        "==" in generated_code
        or "!=" in generated_code
        or "memcmp" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="read_back_verification",
            passed=has_compare,
            expected="Read-back data compared to expected value",
            actual="present" if has_compare else "missing",
            check_type="constraint",
        )
    )

    # Check 4: device_is_ready() called
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() called before SPI operations",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Poll loop has upper bound (no infinite loop)
    has_bound = bool(
        re.search(r"for\s*\(.*<.*\)", generated_code)
        or re.search(r"while\s*\(.*<.*\)", generated_code)
        or re.search(r"POLL_MAX|MAX_POLL|MAX_RETRY|MAX_WAIT", generated_code)
        or re.search(r"i\s*<\s*\d+", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="poll_loop_bounded",
            passed=has_bound,
            expected="Polling loop has upper iteration bound",
            actual="present" if has_bound else "missing",
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
