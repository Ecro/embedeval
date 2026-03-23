"""Static analysis checks for BLE observer (scan)."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE scanner code structure."""
    details: list[CheckDetail] = []

    has_bt_h = "zephyr/bluetooth/bluetooth.h" in generated_code
    details.append(
        CheckDetail(
            check_name="bluetooth_header",
            passed=has_bt_h,
            expected="zephyr/bluetooth/bluetooth.h included",
            actual="present" if has_bt_h else "missing",
            check_type="exact_match",
        )
    )

    has_bt_enable = "bt_enable" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_enable_called",
            passed=has_bt_enable,
            expected="bt_enable() called",
            actual="present" if has_bt_enable else "missing",
            check_type="exact_match",
        )
    )

    has_scan_start = "bt_le_scan_start" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_le_scan_start_called",
            passed=has_scan_start,
            expected="bt_le_scan_start() called",
            actual="present" if has_scan_start else "missing",
            check_type="exact_match",
        )
    )

    has_scan_param = "bt_le_scan_param" in generated_code
    details.append(
        CheckDetail(
            check_name="scan_param_defined",
            passed=has_scan_param,
            expected="struct bt_le_scan_param defined",
            actual="present" if has_scan_param else "missing",
            check_type="exact_match",
        )
    )

    has_callback = "device_found" in generated_code or "scan_cb" in generated_code or "bt_addr_le_t" in generated_code
    details.append(
        CheckDetail(
            check_name="scan_callback_defined",
            passed=has_callback,
            expected="Scan callback function defined",
            actual="present" if has_callback else "missing",
            check_type="exact_match",
        )
    )

    has_addr_str = "bt_addr_le_to_str" in generated_code
    details.append(
        CheckDetail(
            check_name="addr_to_str_called",
            passed=has_addr_str,
            expected="bt_addr_le_to_str() called to format address",
            actual="present" if has_addr_str else "missing",
            check_type="exact_match",
        )
    )

    return details
