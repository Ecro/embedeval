"""Static analysis checks for BLE secure OTA / DFU service."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE DFU service code structure."""
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

    has_gatt_svc = "BT_GATT_SERVICE_DEFINE" in generated_code
    details.append(
        CheckDetail(
            check_name="gatt_service_defined",
            passed=has_gatt_svc,
            expected="BT_GATT_SERVICE_DEFINE macro used",
            actual="present" if has_gatt_svc else "missing",
            check_type="exact_match",
        )
    )

    has_bt_set_security = "bt_conn_set_security" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_conn_set_security_called",
            passed=has_bt_set_security,
            expected="bt_conn_set_security() called for authenticated connection",
            actual="present" if has_bt_set_security else "missing — no security upgrade",
            check_type="exact_match",
        )
    )

    # Hallucination check: ble_dfu_start() does not exist in Zephyr
    uses_ble_dfu_start = "ble_dfu_start" in generated_code
    details.append(
        CheckDetail(
            check_name="no_ble_dfu_start",
            passed=not uses_ble_dfu_start,
            expected="ble_dfu_start() NOT used (does not exist in Zephyr)",
            actual="clean" if not uses_ble_dfu_start else "HALLUCINATION: ble_dfu_start() does not exist",
            check_type="exact_match",
        )
    )

    # Hallucination check: ota_update() does not exist in Zephyr
    uses_ota_update = "ota_update" in generated_code
    details.append(
        CheckDetail(
            check_name="no_ota_update",
            passed=not uses_ota_update,
            expected="ota_update() NOT used (does not exist in Zephyr)",
            actual="clean" if not uses_ota_update else "HALLUCINATION: ota_update() does not exist",
            check_type="exact_match",
        )
    )

    return details
