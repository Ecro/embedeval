"""Static analysis checks for BLE peripheral with notifications."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE notify peripheral code structure."""
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

    has_notify_flag = "BT_GATT_CHRC_NOTIFY" in generated_code
    details.append(
        CheckDetail(
            check_name="chrc_notify_flag",
            passed=has_notify_flag,
            expected="BT_GATT_CHRC_NOTIFY property set on characteristic",
            actual="present" if has_notify_flag else "missing",
            check_type="exact_match",
        )
    )

    has_ccc = "BT_GATT_CCC" in generated_code
    details.append(
        CheckDetail(
            check_name="ccc_descriptor",
            passed=has_ccc,
            expected="BT_GATT_CCC descriptor added to service",
            actual="present" if has_ccc else "missing — client cannot enable notifications",
            check_type="exact_match",
        )
    )

    has_notify = "bt_gatt_notify" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_gatt_notify_called",
            passed=has_notify,
            expected="bt_gatt_notify() called",
            actual="present" if has_notify else "missing",
            check_type="exact_match",
        )
    )

    has_svc_define = "BT_GATT_SERVICE_DEFINE" in generated_code
    details.append(
        CheckDetail(
            check_name="gatt_service_defined",
            passed=has_svc_define,
            expected="BT_GATT_SERVICE_DEFINE macro used",
            actual="present" if has_svc_define else "missing",
            check_type="exact_match",
        )
    )

    has_conn_ref = "bt_conn_ref" in generated_code
    details.append(
        CheckDetail(
            check_name="conn_ref_called",
            passed=has_conn_ref,
            expected="bt_conn_ref() called to hold connection reference",
            actual="present" if has_conn_ref else "missing",
            check_type="exact_match",
        )
    )

    return details
