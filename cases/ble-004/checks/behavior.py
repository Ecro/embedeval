"""Behavioral checks for BLE connection callbacks."""

from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.models import CheckDetail

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
    """Validate BLE connection callback behavioral properties."""
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

    # Check 2: bt_enable before bt_conn_cb_register / advertising
    enable_pos = generated_code.find("bt_enable")
    adv_pos = generated_code.find("bt_le_adv_start")
    enable_before_adv = enable_pos != -1 and adv_pos != -1 and enable_pos < adv_pos
    details.append(
        CheckDetail(
            check_name="enable_before_advertise",
            passed=enable_before_adv,
            expected="bt_enable() before bt_le_adv_start()",
            actual="correct" if enable_before_adv else "wrong order",
            check_type="constraint",
        )
    )

    # Check 3: conn_callbacks struct is static (common LLM failure: non-static struct)
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

    # Check 4: bt_conn_cb_register AFTER bt_enable (common LLM failure: register before enable)
    register_pos = generated_code.find("bt_conn_cb_register")
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

    # Check 5: Disconnect reason printed
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

    # Check 6: Connection state tracked (connected_flag or equivalent)
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

    # Check 7: bt_enable error checked
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

    # Check 8: Connection error param checked in connected callback
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

    # Check 9: bt_conn_unref in disconnected callback
    # LLM failure: tracks connection but forgets to unref in disconnect
    import re
    disconnected_match = re.search(
        r"(?:void\s+disconnected|\.disconnected\s*=)\s*[^{]*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        generated_code,
        re.DOTALL,
    )
    # For this case the reference does NOT use bt_conn_ref/unref (uses connected_flag only)
    # so we only check if the LLM uses bt_conn_ref that it also uses bt_conn_unref
    has_ref = "bt_conn_ref" in generated_code
    has_unref = "bt_conn_unref" in generated_code
    # If ref is used, unref must also appear (no leak)
    no_ref_leak = (not has_ref) or (has_ref and has_unref)
    details.append(
        CheckDetail(
            check_name="no_conn_ref_leak",
            passed=no_ref_leak,
            expected="If bt_conn_ref() used, bt_conn_unref() must also be called",
            actual="no leak" if no_ref_leak else "bt_conn_ref() without bt_conn_unref() — ref leak",
            check_type="constraint",
        )
    )

    return details
