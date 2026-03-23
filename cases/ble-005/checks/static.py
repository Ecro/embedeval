"""Static analysis checks for BLE pairing with security."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE pairing/security code structure."""
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

    has_conn_h = "zephyr/bluetooth/conn.h" in generated_code
    details.append(
        CheckDetail(
            check_name="conn_header",
            passed=has_conn_h,
            expected="zephyr/bluetooth/conn.h included",
            actual="present" if has_conn_h else "missing",
            check_type="exact_match",
        )
    )

    has_auth_cb = "bt_conn_auth_cb" in generated_code
    details.append(
        CheckDetail(
            check_name="auth_cb_struct_defined",
            passed=has_auth_cb,
            expected="struct bt_conn_auth_cb defined",
            actual="present" if has_auth_cb else "missing",
            check_type="exact_match",
        )
    )

    has_auth_register = "bt_conn_auth_cb_register" in generated_code
    details.append(
        CheckDetail(
            check_name="auth_cb_registered",
            passed=has_auth_register,
            expected="bt_conn_auth_cb_register() called",
            actual="present" if has_auth_register else "missing",
            check_type="exact_match",
        )
    )

    has_passkey_display = "passkey_display" in generated_code
    details.append(
        CheckDetail(
            check_name="passkey_display_cb",
            passed=has_passkey_display,
            expected="passkey_display callback defined",
            actual="present" if has_passkey_display else "missing",
            check_type="exact_match",
        )
    )

    has_set_security = "bt_conn_set_security" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_conn_set_security_called",
            passed=has_set_security,
            expected="bt_conn_set_security() called",
            actual="present" if has_set_security else "missing",
            check_type="exact_match",
        )
    )

    has_security_l3 = "BT_SECURITY_L3" in generated_code or "BT_SECURITY_L4" in generated_code
    details.append(
        CheckDetail(
            check_name="security_level_mitm",
            passed=has_security_l3,
            expected="BT_SECURITY_L3 (or L4) used for MITM protection",
            actual="present" if has_security_l3 else "missing — L1/L2 does not enforce MITM",
            check_type="exact_match",
        )
    )

    return details
