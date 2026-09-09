"""Behavioral checks for BLE GATT custom service."""

import re

from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.models import CheckDetail
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code

# BLE-specific cross-platform hallucination patterns (not in check_utils)
_BLE_HALLUCINATED_APIS = [
    "BLEDevice.connect",
    "BLEDevice.init",
    "BLEServer.createService",
    "gap_connect(",
    "ble_gap_connect(",
    "esp_ble_gap_",
    "esp_bt_",
    "nimble_port_",
]


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE GATT behavioral properties."""
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
            expected="Only Zephyr BLE APIs (bt_*); no Arduino/NimBLE/ESP-IDF APIs",
            actual=(
                "clean"
                if no_wrong_apis
                else f"found: {[x[0] for x in cross_platform_hits] + ble_hallucinations}"
            ),
            check_type="hallucination",
        )
    )

    # Check 2: bt_enable before bt_le_adv_start (ordering by source position)
    enable_pos = find_in_code(generated_code, "bt_enable")
    adv_pos = find_in_code(generated_code, "bt_le_adv_start")
    order_ok = enable_pos != -1 and adv_pos != -1 and enable_pos < adv_pos
    details.append(
        CheckDetail(
            check_name="enable_before_advertise",
            passed=order_ok,
            expected="bt_enable() before bt_le_adv_start()",
            actual="correct" if order_ok else "wrong order",
            check_type="constraint",
        )
    )

    # Check 3: Custom 128-bit UUID defined (not standard 16-bit)
    has_128bit = (
        scoped_contains(generated_code, 'BT_UUID_128_ENCODE', scope='code_only')
        or scoped_contains(generated_code, 'BT_UUID_INIT_128', scope='code_only')
        or scoped_contains(generated_code, 'BT_UUID_DECLARE_128', scope='code_only')
    )
    details.append(
        CheckDetail(
            check_name="custom_128bit_uuid",
            passed=has_128bit,
            expected="128-bit custom UUID defined",
            actual="present" if has_128bit else "missing (using 16-bit?)",
            check_type="exact_match",
        )
    )

    # Check 4: Characteristic has both READ and WRITE
    has_read = scoped_contains(generated_code, 'BT_GATT_CHRC_READ', scope='code_only')
    has_write = scoped_contains(generated_code, 'BT_GATT_CHRC_WRITE', scope='code_only')
    details.append(
        CheckDetail(
            check_name="read_write_characteristic",
            passed=has_read and has_write,
            expected="Characteristic with READ and WRITE properties",
            actual=f"read={has_read}, write={has_write}",
            check_type="constraint",
        )
    )

    # Check 5: Read callback uses bt_gatt_attr_read (not raw memcpy without bounds)
    has_attr_read = scoped_contains(generated_code, 'bt_gatt_attr_read', scope='code_only')
    details.append(
        CheckDetail(
            check_name="read_uses_attr_read",
            passed=has_attr_read,
            expected="Read callback uses bt_gatt_attr_read()",
            actual="present" if has_attr_read else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Write callback has offset+len bounds check
    # LLM failure: raw memcpy without checking offset + len > sizeof(buf)
    has_bounds_check = (
        scoped_contains(generated_code, 'offset + len', scope='code_only')
        or scoped_contains(generated_code, 'offset+len', scope='code_only')
        or scoped_contains(generated_code, 'BT_ATT_ERR_INVALID_OFFSET', scope='code_only')
    )
    details.append(
        CheckDetail(
            check_name="write_offset_bounds_check",
            passed=has_bounds_check,
            expected="Write callback checks (offset + len > sizeof) or BT_ATT_ERR_INVALID_OFFSET",
            actual="present" if has_bounds_check else "missing — buffer overflow risk",
            check_type="constraint",
        )
    )

    # Check 7: Error handling for bt_enable (scoped: check within 200 chars after bt_enable)
    bt_enable_pos = find_in_code(generated_code, "bt_enable")
    if bt_enable_pos != -1:
        window = generated_code[bt_enable_pos:bt_enable_pos + 200]
        has_err_check = bool(re.search(r'if\s*\(\s*(?:err|ret|rc)\b', window))
    else:
        has_err_check = False
    details.append(
        CheckDetail(
            check_name="bt_enable_error_check",
            passed=has_err_check,
            expected="Error check on bt_enable() return",
            actual="present" if has_err_check else "missing",
            check_type="constraint",
        )
    )

    # Check 8: BT_GATT_PRIMARY_SERVICE in service definition
    has_primary = scoped_contains(generated_code, 'BT_GATT_PRIMARY_SERVICE', scope='code_only')
    details.append(
        CheckDetail(
            check_name="primary_service_attribute",
            passed=has_primary,
            expected="BT_GATT_PRIMARY_SERVICE in service definition",
            actual="present" if has_primary else "missing",
            check_type="exact_match",
        )
    )

    # Check 9: Write callback validates attribute length
    # LLM failure: accepts any write length without validating against expected size
    has_write_len_check = (
        scoped_contains(generated_code, 'BT_ATT_ERR_INVALID_ATTRIBUTE_LEN', scope='code_only')
        or (
            scoped_contains(generated_code, 'sizeof', scope='code_only')
            and ("write" in generated_code.lower() or scoped_contains(generated_code, 'len', scope='code_only'))
            and (scoped_contains(generated_code, '>', scope='code_only') or scoped_contains(generated_code, '!=', scope='code_only'))
        )
    )
    details.append(
        CheckDetail(
            check_name="write_attribute_len_validated",
            passed=has_write_len_check,
            expected="Write callback validates 'len' using sizeof or BT_ATT_ERR_INVALID_ATTRIBUTE_LEN",
            actual="present" if has_write_len_check else "missing — accepts arbitrary write sizes",
            check_type="constraint",
        )
    )

    return details
