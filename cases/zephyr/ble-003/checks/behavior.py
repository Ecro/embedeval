"""Behavioral checks for BLE peripheral with notifications."""

from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.models import CheckDetail
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code

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
    """Validate BLE notify peripheral behavioral properties."""
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

    # Check 2: bt_enable before advertising (ordering)
    enable_pos = find_in_code(generated_code, "bt_enable")
    adv_pos = find_in_code(generated_code, "bt_le_adv_start")
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

    # Check 3: CCC descriptor present — required for client to enable notifications
    has_ccc = scoped_contains(generated_code, 'BT_GATT_CCC', scope='code_only')
    details.append(
        CheckDetail(
            check_name="ccc_descriptor_present",
            passed=has_ccc,
            expected="BT_GATT_CCC descriptor in service definition",
            actual="present" if has_ccc else "missing — client cannot subscribe to notifications",
            check_type="exact_match",
        )
    )

    # Check 4: BT_GATT_CHRC_NOTIFY flag set (common LLM failure: missing notify flag)
    has_notify_flag = scoped_contains(generated_code, 'BT_GATT_CHRC_NOTIFY', scope='code_only')
    details.append(
        CheckDetail(
            check_name="notify_chrc_flag",
            passed=has_notify_flag,
            expected="BT_GATT_CHRC_NOTIFY flag on characteristic",
            actual="present" if has_notify_flag else "missing — characteristic not notifiable",
            check_type="exact_match",
        )
    )

    # Check 5: bt_gatt_notify called only when connection exists (guard on current_conn)
    notify_idx = find_in_code(generated_code, "bt_gatt_notify")
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

    # Check 6: Connection reference managed (bt_conn_ref / bt_conn_unref)
    has_ref = scoped_contains(generated_code, 'bt_conn_ref', scope='code_only')
    has_unref = scoped_contains(generated_code, 'bt_conn_unref', scope='code_only')
    details.append(
        CheckDetail(
            check_name="conn_reference_managed",
            passed=has_ref and has_unref,
            expected="bt_conn_ref() and bt_conn_unref() both called",
            actual=f"ref={has_ref}, unref={has_unref}",
            check_type="constraint",
        )
    )

    # Check 7: bt_conn_unref in disconnected callback specifically
    # LLM failure: bt_conn_unref present but called in wrong place (e.g. only in main)
    import re
    disconnected_match = re.search(
        r"(?:void\s+disconnected|\.disconnected\s*=)\s*[^{]*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        generated_code,
        re.DOTALL,
    )
    if disconnected_match:
        disconnected_body = disconnected_match.group(1)
        unref_in_disconnected = "bt_conn_unref" in disconnected_body
    else:
        # Fall back: unref must appear somewhere after disconnected definition
        disconnected_pos = find_in_code(generated_code, "void disconnected")
        if disconnected_pos == -1:
            disconnected_pos = find_in_code(generated_code, ".disconnected")
        unref_pos = find_in_code(generated_code, "bt_conn_unref", disconnected_pos) if disconnected_pos != -1 else -1
        unref_in_disconnected = disconnected_pos != -1 and unref_pos != -1
    details.append(
        CheckDetail(
            check_name="conn_unref_in_disconnected_cb",
            passed=unref_in_disconnected,
            expected="bt_conn_unref() called inside disconnected callback",
            actual="present" if unref_in_disconnected else "missing — connection ref leaked",
            check_type="constraint",
        )
    )

    # Check 8: Notify return value checked
    has_notify_check = scoped_contains(generated_code, 'bt_gatt_notify', scope='code_only') and (
        scoped_contains(generated_code, 'if (err', scope='code_only') or scoped_contains(generated_code, 'if (ret', scope='code_only') or scoped_contains(generated_code, '< 0', scope='code_only')
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
