"""Behavioral checks for I2C bus scan."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate I2C bus scan behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: device_is_ready() before scan loop
    has_ready = "device_is_ready" in generated_code
    loop_pos = generated_code.find("for")
    ready_pos = generated_code.find("device_is_ready")
    order_ok = (
        has_ready
        and ready_pos != -1
        and loop_pos != -1
        and ready_pos < loop_pos
    )
    details.append(
        CheckDetail(
            check_name="ready_check_before_scan",
            passed=order_ok,
            expected="device_is_ready() before scan loop",
            actual="correct order" if order_ok else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 2: Reserved low addresses (0x00-0x07) not scanned
    # Scan must start at 0x08 or higher — catch patterns like addr = 0; addr < 0x78
    starts_at_zero = bool(
        re.search(r"=\s*0[xX]?0*[0-7]\b", generated_code)
        and not re.search(r"=\s*0[xX]0*8", generated_code)
        and re.search(r"for.*addr.*=.*0[^x]|for.*=\s*0\b", generated_code)
    )
    # Positive check: lower bound is 0x08 or a named constant near it
    has_valid_lower = bool(
        re.search(r"0[xX]0*8", generated_code)
        or "SCAN_ADDR_MIN" in generated_code
        or "ADDR_MIN" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="reserved_low_addresses_skipped",
            passed=has_valid_lower and not starts_at_zero,
            expected="Scan starts at 0x08, skipping reserved 0x00-0x07",
            actual="correct" if (has_valid_lower and not starts_at_zero) else "scanning reserved range",
            check_type="constraint",
        )
    )

    # Check 3: Reserved high addresses (0x78-0x7F) not scanned
    has_valid_upper = bool(
        re.search(r"0[xX]7[Ff]|0[xX]77", generated_code)
        or "SCAN_ADDR_MAX" in generated_code
        or "ADDR_MAX" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="reserved_high_addresses_skipped",
            passed=has_valid_upper,
            expected="Scan ends at 0x77, skipping reserved 0x78-0x7F",
            actual="present" if has_valid_upper else "missing - may scan reserved range",
            check_type="constraint",
        )
    )

    # Check 4: ACK check distinguishes found from not-found
    has_ack_check = (
        "== 0" in generated_code
        or "ret == 0" in generated_code
        or "!ret" in generated_code
        or "rc == 0" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="ack_check_on_probe",
            passed=has_ack_check,
            expected="Return value == 0 used to detect device ACK",
            actual="present" if has_ack_check else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Found device count reported
    has_count = bool(
        re.search(r"found|count|device", generated_code, re.IGNORECASE)
        and "printk" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="found_count_reported",
            passed=has_count,
            expected="Number of found devices printed after scan",
            actual="present" if has_count else "missing",
            check_type="constraint",
        )
    )

    return details
