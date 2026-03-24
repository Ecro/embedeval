"""Behavioral checks for BLE observer (scan)."""

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
    """Validate BLE scanner behavioral properties."""
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

    # Check 2: bt_enable before bt_le_scan_start (common LLM failure: scan without init)
    enable_pos = generated_code.find("bt_enable")
    scan_pos = generated_code.find("bt_le_scan_start")
    order_ok = enable_pos != -1 and scan_pos != -1 and enable_pos < scan_pos
    details.append(
        CheckDetail(
            check_name="enable_before_scan",
            passed=order_ok,
            expected="bt_enable() called before bt_le_scan_start()",
            actual="correct" if order_ok else "wrong order — scan before bt_enable",
            check_type="constraint",
        )
    )

    # Check 3: Scan callback is non-NULL (not passing NULL as callback)
    has_callback_arg = (
        "bt_le_scan_start" in generated_code
        and "NULL" not in generated_code[
            generated_code.find("bt_le_scan_start"):
            generated_code.find("bt_le_scan_start") + 60
        ]
    )
    details.append(
        CheckDetail(
            check_name="scan_callback_not_null",
            passed=has_callback_arg,
            expected="Non-NULL callback passed to bt_le_scan_start()",
            actual="present" if has_callback_arg else "NULL callback — no device reports",
            check_type="constraint",
        )
    )

    # Check 4: Scan params struct used (not NULL params)
    has_params = "bt_le_scan_param" in generated_code
    details.append(
        CheckDetail(
            check_name="scan_params_struct_used",
            passed=has_params,
            expected="struct bt_le_scan_param used for scan configuration",
            actual="present" if has_params else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: bt_enable error checked (strict: must check return near call site)
    enable_idx = generated_code.find("bt_enable")
    post_enable = generated_code[enable_idx:enable_idx + 100] if enable_idx != -1 else ""
    has_enable_check = enable_idx != -1 and (
        "if (err" in post_enable or "if (ret" in post_enable or "if (err)" in post_enable
    )
    details.append(
        CheckDetail(
            check_name="bt_enable_error_checked",
            passed=has_enable_check,
            expected="bt_enable() return value checked for error",
            actual="present" if has_enable_check else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Scan start error checked
    scan_idx = generated_code.find("bt_le_scan_start")
    post_scan = generated_code[scan_idx:scan_idx + 100] if scan_idx != -1 else ""
    has_scan_check = scan_idx != -1 and (
        "if (err" in post_scan or "if (ret" in post_scan or "if (err)" in post_scan
        or "< 0" in post_scan
    )
    details.append(
        CheckDetail(
            check_name="scan_start_error_checked",
            passed=has_scan_check,
            expected="bt_le_scan_start() return value checked",
            actual="present" if has_scan_check else "missing",
            check_type="constraint",
        )
    )

    # Check 7: RSSI printed in callback
    has_rssi = "rssi" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="rssi_printed",
            passed=has_rssi,
            expected="RSSI value printed in scan callback",
            actual="present" if has_rssi else "missing",
            check_type="exact_match",
        )
    )

    # Check 8: Scan type is passive or active (not invalid/omitted)
    # LLM failure: omits scan type or uses a raw integer instead of the constant
    has_scan_type = (
        "BT_LE_SCAN_TYPE_PASSIVE" in generated_code
        or "BT_LE_SCAN_TYPE_ACTIVE" in generated_code
        or "BT_LE_SCAN_ACTIVE" in generated_code
        or "BT_LE_SCAN_PASSIVE" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="scan_type_specified",
            passed=has_scan_type,
            expected="Scan type explicitly set (BT_LE_SCAN_TYPE_PASSIVE or _ACTIVE)",
            actual="present" if has_scan_type else "missing — scan type not specified",
            check_type="constraint",
        )
    )

    return details
