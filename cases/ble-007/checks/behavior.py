"""Behavioral checks for BLE advertising with manufacturer data."""

import re

from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.models import CheckDetail

_BLE_HALLUCINATED_APIS = [
    "BLEDevice.connect",
    "BLEDevice.init",
    "gap_connect(",
    "ble_gap_connect(",
    "esp_ble_gap_",
    "esp_bt_",
    "nimble_port_",
]


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate manufacturer data structure validity and size constraints."""
    details: list[CheckDetail] = []

    # Check 1: No cross-platform BLE API hallucinations
    cross_platform_hits = check_no_cross_platform_apis(
        generated_code, skip_platforms=["POSIX", "Linux_Userspace"]
    )
    ble_hallucinations = [
        api for api in _BLE_HALLUCINATED_APIS if api in generated_code
    ]
    no_wrong_apis = not cross_platform_hits and not ble_hallucinations
    details.append(
        CheckDetail(
            check_name="no_cross_platform_ble_apis",
            passed=no_wrong_apis,
            expected="Only Zephyr BLE APIs; no Arduino/NimBLE/ESP-IDF APIs",
            actual=(
                "clean"
                if no_wrong_apis
                else f"found: {[x[0] for x in cross_platform_hits] + ble_hallucinations}"
            ),
            check_type="hallucination",
        )
    )

    # Check 2: bt_enable before bt_le_adv_start (ordering)
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

    # Check 3: Company ID is present (at least 2 bytes as per BT spec)
    has_two_byte_company_id = (
        "0x59, 0x00" in generated_code
        or "0x59,0x00" in generated_code
        or "COMPANY_ID" in generated_code
        or bool(re.search(r"BT_DATA_MANUFACTURER_DATA.*0x[0-9a-fA-F]{2}.*0x[0-9a-fA-F]{2}", generated_code))
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

    # Check 4: Advertising data has FLAGS entry
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

    # Check 5: BT_DATA_MANUFACTURER_DATA type used (hallucination: using wrong type constant)
    has_mfr_data = "BT_DATA_MANUFACTURER_DATA" in generated_code
    details.append(
        CheckDetail(
            check_name="manufacturer_data_type_correct",
            passed=has_mfr_data,
            expected="BT_DATA_MANUFACTURER_DATA used for manufacturer data AD type",
            actual="present" if has_mfr_data else "missing — wrong or omitted AD type",
            check_type="exact_match",
        )
    )

    # Check 6: Error check on bt_enable or bt_le_adv_start
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

    # Check 7: Advertising data uses ARRAY_SIZE for count (safe API usage)
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

    # Check 8: Total AD payload does not exceed 31 bytes
    # Hallucination: LLMs sometimes generate enormous manufacturer data payloads
    # We detect if the manufacturer data macro has > 25 hex bytes inside
    mfr_match = re.search(
        r"BT_DATA_BYTES\s*\(\s*BT_DATA_MANUFACTURER_DATA\s*,([^)]+)\)",
        generated_code,
        re.DOTALL,
    )
    if mfr_match:
        payload_str = mfr_match.group(1)
        hex_bytes = re.findall(r"0x[0-9a-fA-F]{2}", payload_str)
        # AD structure overhead: 1 byte length + 1 byte type; max data = 29 bytes
        payload_fits = len(hex_bytes) <= 29
    else:
        payload_fits = True  # If no match, cannot determine, pass
    details.append(
        CheckDetail(
            check_name="manufacturer_payload_fits_ad",
            passed=payload_fits,
            expected="Manufacturer data payload fits in 29 bytes (31 - 2 overhead)",
            actual=(
                "fits"
                if payload_fits
                else f"too large — {len(hex_bytes) if mfr_match else '?'} bytes exceeds 29"
            ),
            check_type="constraint",
        )
    )

    return details
