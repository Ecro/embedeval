"""Behavioral checks for BLE observer (scan)."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE scanner behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: bt_enable before bt_le_scan_start (common LLM failure: scan without init)
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

    # Check 2: Scan callback is non-NULL (not passing NULL as callback)
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

    # Check 3: Scan params struct used (not NULL params)
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

    # Check 4: bt_enable error checked
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

    # Check 5: Scan start error checked
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

    # Check 6: RSSI printed in callback
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

    return details
