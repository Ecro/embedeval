"""Behavioral checks for BLE connection callbacks."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE connection callback behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: conn_callbacks struct is static (common LLM failure: non-static struct)
    has_static_cb = (
        "static struct bt_conn_cb" in generated_code
        or "BT_CONN_CB_DEFINE" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="conn_cb_struct_static",
            passed=has_static_cb,
            expected="struct bt_conn_cb declared static (or BT_CONN_CB_DEFINE used)",
            actual="present" if has_static_cb else "missing — non-static struct may be freed",
            check_type="constraint",
        )
    )

    # Check 2: bt_conn_cb_register AFTER bt_enable (common LLM failure: register before enable)
    register_pos = generated_code.find("bt_conn_cb_register")
    enable_pos = generated_code.find("bt_enable")
    if register_pos == -1:
        # BT_CONN_CB_DEFINE is static registration, order doesn't matter
        register_order_ok = "BT_CONN_CB_DEFINE" in generated_code
    else:
        register_order_ok = enable_pos != -1 and enable_pos < register_pos
    details.append(
        CheckDetail(
            check_name="register_after_enable",
            passed=register_order_ok,
            expected="bt_conn_cb_register() called after bt_enable()",
            actual="correct" if register_order_ok else "wrong order — registered before bt_enable",
            check_type="constraint",
        )
    )

    # Check 3: Disconnect reason printed
    has_reason = "reason" in generated_code
    details.append(
        CheckDetail(
            check_name="disconnect_reason_printed",
            passed=has_reason,
            expected="Disconnect reason printed in disconnected callback",
            actual="present" if has_reason else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Connection state tracked (connected_flag or equivalent)
    has_state_track = (
        "connected_flag" in generated_code
        or "is_connected" in generated_code
        or "conn_state" in generated_code
        or ("connected" in generated_code and "= true" in generated_code)
        or ("connected" in generated_code and "= false" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="connection_state_tracked",
            passed=has_state_track,
            expected="Connection state variable tracked across callbacks",
            actual="present" if has_state_track else "missing",
            check_type="constraint",
        )
    )

    # Check 5: bt_enable error checked
    enable_idx = generated_code.find("bt_enable")
    post_enable = generated_code[enable_idx:enable_idx + 100] if enable_idx != -1 else ""
    has_enable_check = enable_idx != -1 and (
        "if (err" in post_enable or "if (ret" in post_enable
    )
    details.append(
        CheckDetail(
            check_name="bt_enable_error_checked",
            passed=has_enable_check,
            expected="bt_enable() return value checked",
            actual="present" if has_enable_check else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Connection error param checked in connected callback
    has_conn_err_check = (
        "if (err)" in generated_code
        or "if (err " in generated_code
        or "if (err\n" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="connected_cb_error_checked",
            passed=has_conn_err_check,
            expected="err parameter checked in connected() callback",
            actual="present" if has_conn_err_check else "missing",
            check_type="constraint",
        )
    )

    return details
