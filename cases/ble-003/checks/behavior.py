"""Behavioral checks for BLE peripheral with notifications."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE notify peripheral behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: CCC descriptor present — required for client to enable notifications
    has_ccc = "BT_GATT_CCC" in generated_code
    details.append(
        CheckDetail(
            check_name="ccc_descriptor_present",
            passed=has_ccc,
            expected="BT_GATT_CCC descriptor in service definition",
            actual="present" if has_ccc else "missing — client cannot subscribe to notifications",
            check_type="exact_match",
        )
    )

    # Check 2: BT_GATT_CHRC_NOTIFY flag set (common LLM failure: missing notify flag)
    has_notify_flag = "BT_GATT_CHRC_NOTIFY" in generated_code
    details.append(
        CheckDetail(
            check_name="notify_chrc_flag",
            passed=has_notify_flag,
            expected="BT_GATT_CHRC_NOTIFY flag on characteristic",
            actual="present" if has_notify_flag else "missing — characteristic not notifiable",
            check_type="exact_match",
        )
    )

    # Check 3: bt_gatt_notify called only when connection exists (guard on current_conn)
    notify_idx = generated_code.find("bt_gatt_notify")
    pre_notify = generated_code[max(0, notify_idx - 100):notify_idx] if notify_idx != -1 else ""
    has_conn_guard = notify_idx != -1 and (
        "current_conn" in pre_notify
        or "if (conn" in pre_notify
        or "conn)" in pre_notify
        or "if (current" in pre_notify
    )
    details.append(
        CheckDetail(
            check_name="notify_guarded_by_connection",
            passed=has_conn_guard,
            expected="bt_gatt_notify() called only when connection is active",
            actual="present" if has_conn_guard else "missing — may notify without connected client",
            check_type="constraint",
        )
    )

    # Check 4: Connection reference managed (bt_conn_ref / bt_conn_unref)
    has_ref = "bt_conn_ref" in generated_code
    has_unref = "bt_conn_unref" in generated_code
    details.append(
        CheckDetail(
            check_name="conn_reference_managed",
            passed=has_ref and has_unref,
            expected="bt_conn_ref() and bt_conn_unref() both called",
            actual=f"ref={has_ref}, unref={has_unref}",
            check_type="constraint",
        )
    )

    # Check 5: bt_enable before advertising
    enable_pos = generated_code.find("bt_enable")
    adv_pos = generated_code.find("bt_le_adv_start")
    enable_first = enable_pos != -1 and adv_pos != -1 and enable_pos < adv_pos
    details.append(
        CheckDetail(
            check_name="enable_before_advertise",
            passed=enable_first,
            expected="bt_enable() before bt_le_adv_start()",
            actual="correct" if enable_first else "wrong order",
            check_type="constraint",
        )
    )

    # Check 6: Notify return value checked
    has_notify_check = "bt_gatt_notify" in generated_code and (
        "if (err" in generated_code or "if (ret" in generated_code or "< 0" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="notify_return_checked",
            passed=has_notify_check,
            expected="bt_gatt_notify() return value checked",
            actual="present" if has_notify_check else "missing",
            check_type="constraint",
        )
    )

    return details
