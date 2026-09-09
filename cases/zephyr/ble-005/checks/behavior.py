"""Behavioral checks for BLE pairing with security."""

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
    """Validate BLE pairing/security behavioral properties."""
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

    # Check 2: bt_enable before auth callbacks and advertising
    enable_pos = find_in_code(generated_code, "bt_enable")
    auth_pos = find_in_code(generated_code, "bt_conn_auth_cb_register")
    adv_pos = find_in_code(generated_code, "bt_le_adv_start")
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

    # Check 3: Auth callbacks registered BEFORE advertising starts (critical ordering)
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

    # Check 4: Security level L3 or higher (MITM required)
    has_l3_or_higher = (
        scoped_contains(generated_code, 'BT_SECURITY_L3', scope='code_only')
        or scoped_contains(generated_code, 'BT_SECURITY_L4', scope='code_only')
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

    # Check 5: passkey_display callback prints passkey
    has_passkey_print = (
        scoped_contains(generated_code, 'passkey_display', scope='code_only')
        and scoped_contains(generated_code, 'printk', scope='code_only')
        and scoped_contains(generated_code, 'passkey', scope='code_only')
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

    # Check 6: bt_conn_set_security called in connected callback (not in main)
    connected_idx = find_in_code(generated_code, "void connected")
    if connected_idx == -1:
        connected_idx = find_in_code(generated_code, ".connected")
    set_sec_idx = find_in_code(generated_code, "bt_conn_set_security")
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

    # Check 7: pairing_complete and pairing_failed callbacks defined
    has_complete = scoped_contains(generated_code, 'pairing_complete', scope='code_only')
    has_failed = scoped_contains(generated_code, 'pairing_failed', scope='code_only')
    details.append(
        CheckDetail(
            check_name="pairing_result_callbacks",
            passed=has_complete and has_failed,
            expected="Both pairing_complete and pairing_failed callbacks defined",
            actual=f"complete={has_complete}, failed={has_failed}",
            check_type="constraint",
        )
    )

    # Check 8: bt_conn_unref in disconnected callback if bt_conn_ref is used
    has_ref = scoped_contains(generated_code, 'bt_conn_ref', scope='code_only')
    has_unref = scoped_contains(generated_code, 'bt_conn_unref', scope='code_only')
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

    # Check 9: bt_enable error checked (strict)
    enable_idx = find_in_code(generated_code, "bt_enable")
    post_enable = generated_code[enable_idx:enable_idx + 100] if enable_idx != -1 else ""
    has_enable_check = enable_idx != -1 and (
        "if (err" in post_enable or "if (ret" in post_enable
    )
    details.append(
        CheckDetail(
            check_name="bt_enable_error_checked",
            passed=has_enable_check,
            expected="bt_enable() return value checked for error",
            actual="present" if has_enable_check else "missing",
            check_type="constraint",
        )
    )

    return details
