"""Behavioral checks for BLE pairing with security."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE pairing/security behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Auth callbacks registered BEFORE advertising starts (critical ordering)
    auth_pos = generated_code.find("bt_conn_auth_cb_register")
    adv_pos = generated_code.find("bt_le_adv_start")
    auth_before_adv = auth_pos != -1 and adv_pos != -1 and auth_pos < adv_pos
    details.append(
        CheckDetail(
            check_name="auth_cb_before_advertising",
            passed=auth_before_adv,
            expected="bt_conn_auth_cb_register() called before bt_le_adv_start()",
            actual="correct" if auth_before_adv else "wrong order — pairing may fail if client connects immediately",
            check_type="constraint",
        )
    )

    # Check 2: bt_enable BEFORE auth callbacks registered
    enable_pos = generated_code.find("bt_enable")
    enable_before_auth = (
        enable_pos != -1 and auth_pos != -1 and enable_pos < auth_pos
    )
    details.append(
        CheckDetail(
            check_name="enable_before_auth_register",
            passed=enable_before_auth,
            expected="bt_enable() called before bt_conn_auth_cb_register()",
            actual="correct" if enable_before_auth else "wrong order",
            check_type="constraint",
        )
    )

    # Check 3: Security level L3 or higher (MITM required)
    has_l3_or_higher = (
        "BT_SECURITY_L3" in generated_code
        or "BT_SECURITY_L4" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="mitm_security_level",
            passed=has_l3_or_higher,
            expected="BT_SECURITY_L3 or BT_SECURITY_L4 for MITM protection",
            actual="present" if has_l3_or_higher else "missing — lower level lacks MITM",
            check_type="exact_match",
        )
    )

    # Check 4: passkey_display callback prints passkey
    has_passkey_print = (
        "passkey_display" in generated_code
        and "printk" in generated_code
        and "passkey" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="passkey_displayed",
            passed=has_passkey_print,
            expected="passkey_display callback prints passkey value",
            actual="present" if has_passkey_print else "missing — user cannot see passkey",
            check_type="constraint",
        )
    )

    # Check 5: bt_conn_set_security called in connected callback (not in main)
    connected_idx = generated_code.find("void connected")
    if connected_idx == -1:
        connected_idx = generated_code.find(".connected")
    set_sec_idx = generated_code.find("bt_conn_set_security")
    # set_security should appear after connected function definition
    security_in_connected = (
        set_sec_idx != -1
        and connected_idx != -1
        and set_sec_idx > connected_idx
    )
    details.append(
        CheckDetail(
            check_name="security_set_in_connected_cb",
            passed=security_in_connected,
            expected="bt_conn_set_security() called inside connected callback",
            actual="present" if security_in_connected else "missing or called in wrong scope",
            check_type="constraint",
        )
    )

    # Check 6: pairing_complete and pairing_failed callbacks defined
    has_complete = "pairing_complete" in generated_code
    has_failed = "pairing_failed" in generated_code
    details.append(
        CheckDetail(
            check_name="pairing_result_callbacks",
            passed=has_complete and has_failed,
            expected="Both pairing_complete and pairing_failed callbacks defined",
            actual=f"complete={has_complete}, failed={has_failed}",
            check_type="constraint",
        )
    )

    return details
