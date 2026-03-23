"""Behavioral checks for BLE advertising with manufacturer data."""

import re
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate manufacturer data structure validity and size constraints."""
    details: list[CheckDetail] = []

    # Check 1: Company ID is present (at least 2 bytes as per BT spec)
    # Look for two consecutive hex bytes that could be a company ID
    has_two_byte_company_id = (
        "0x59, 0x00" in generated_code
        or "0x59,0x00" in generated_code
        or "COMPANY_ID" in generated_code
        or re.search(r"BT_DATA_MANUFACTURER_DATA.*0x[0-9a-fA-F]{2}.*0x[0-9a-fA-F]{2}", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="company_id_two_bytes",
            passed=bool(has_two_byte_company_id),
            expected="Company ID present as 2 bytes (little-endian) in manufacturer data",
            actual="present" if has_two_byte_company_id else "missing — BT spec requires 2-byte company ID",
            check_type="constraint",
        )
    )

    # Check 2: Advertising data has FLAGS entry
    has_flags = "BT_DATA_FLAGS" in generated_code
    details.append(
        CheckDetail(
            check_name="ad_flags_present",
            passed=has_flags,
            expected="BT_DATA_FLAGS present in advertising data",
            actual="present" if has_flags else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: bt_enable before bt_le_adv_start (ordering)
    enable_pos = generated_code.find("bt_enable")
    adv_pos = generated_code.find("bt_le_adv_start")
    enable_before_adv = (
        enable_pos != -1 and adv_pos != -1 and enable_pos < adv_pos
    )
    details.append(
        CheckDetail(
            check_name="bt_enable_before_adv",
            passed=enable_before_adv,
            expected="bt_enable() called before bt_le_adv_start()",
            actual="correct" if enable_before_adv else "wrong order",
            check_type="constraint",
        )
    )

    # Check 4: Error check on bt_enable or bt_le_adv_start
    has_err_check = (
        "if (err)" in generated_code
        or "if (ret)" in generated_code
        or "< 0" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="error_handling",
            passed=has_err_check,
            expected="Error handling on bt_enable or bt_le_adv_start",
            actual="present" if has_err_check else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Advertising data uses ARRAY_SIZE for count (safe API usage)
    has_array_size = "ARRAY_SIZE" in generated_code
    details.append(
        CheckDetail(
            check_name="array_size_used",
            passed=has_array_size,
            expected="ARRAY_SIZE macro used for ad array count",
            actual="present" if has_array_size else "missing — hardcoded count is fragile",
            check_type="exact_match",
        )
    )

    return details
