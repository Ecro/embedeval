"""Static analysis checks for BLE GATT custom service."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE GATT code structure."""
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

    has_gatt_h = "zephyr/bluetooth/gatt.h" in generated_code
    details.append(
        CheckDetail(
            check_name="gatt_header",
            passed=has_gatt_h,
            expected="zephyr/bluetooth/gatt.h included",
            actual="present" if has_gatt_h else "missing",
            check_type="exact_match",
        )
    )

    has_svc_def = "BT_GATT_SERVICE_DEFINE" in generated_code
    details.append(
        CheckDetail(
            check_name="gatt_service_defined",
            passed=has_svc_def,
            expected="BT_GATT_SERVICE_DEFINE macro used",
            actual="present" if has_svc_def else "missing",
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

    has_adv = "bt_le_adv_start" in generated_code
    details.append(
        CheckDetail(
            check_name="advertising_started",
            passed=has_adv,
            expected="bt_le_adv_start() called",
            actual="present" if has_adv else "missing",
            check_type="exact_match",
        )
    )

    return details
