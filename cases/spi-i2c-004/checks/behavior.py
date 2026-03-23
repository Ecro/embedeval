"""Behavioral checks for SPI flash write and read verify."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate SPI flash behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Write enable command present (WREN / 0x06)
    has_wren = "WREN" in generated_code or "write_enable" in generated_code
    details.append(
        CheckDetail(
            check_name="write_enable_before_write",
            passed=has_wren,
            expected="Write enable command (WREN/0x06) present",
            actual="present" if has_wren else "missing",
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

    return details
