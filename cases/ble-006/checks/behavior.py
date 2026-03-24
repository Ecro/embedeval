"""Behavioral checks for BLE secure OTA / DFU service."""

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
    """Validate DFU authentication ordering and image validation safety."""
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

    # Check 2: bt_enable before bt_le_adv_start (ordering)
    enable_pos = generated_code.find("bt_enable")
    adv_pos = generated_code.find("bt_le_adv_start")
    enable_before_adv = enable_pos != -1 and adv_pos != -1 and enable_pos < adv_pos
    details.append(
        CheckDetail(
            check_name="bt_enable_before_adv",
            passed=enable_before_adv,
            expected="bt_enable() before bt_le_adv_start()",
            actual="correct" if enable_before_adv else "wrong order",
            check_type="constraint",
        )
    )

    # Check 3: bt_conn_set_security called in connected callback (not main)
    connected_pos = generated_code.find("void connected")
    if connected_pos == -1:
        connected_pos = generated_code.find(".connected")
    set_sec_pos = generated_code.find("bt_conn_set_security")
    security_in_connected = (
        set_sec_pos != -1
        and connected_pos != -1
        and set_sec_pos > connected_pos
    )
    details.append(
        CheckDetail(
            check_name="security_set_in_connected_cb",
            passed=security_in_connected,
            expected="bt_conn_set_security() inside connected callback",
            actual="present" if security_in_connected else "missing or called in wrong scope",
            check_type="constraint",
        )
    )

    # Check 4: Authentication check before writing firmware data
    auth_check = "is_authenticated" in generated_code or "authenticated" in generated_code
    details.append(
        CheckDetail(
            check_name="auth_check_before_dfu_data",
            passed=auth_check,
            expected="Authentication state checked before accepting DFU data",
            actual="present" if auth_check else "missing — DFU data accepted without auth",
            check_type="constraint",
        )
    )

    # Check 5: BT_ATT_ERR_AUTHORIZATION returned when not authenticated
    has_auth_err = "BT_ATT_ERR_AUTHORIZATION" in generated_code
    details.append(
        CheckDetail(
            check_name="authorization_error_returned",
            passed=has_auth_err,
            expected="BT_ATT_ERR_AUTHORIZATION returned for unauthorized access",
            actual="present" if has_auth_err else "missing — no auth error response",
            check_type="exact_match",
        )
    )

    # Check 6: Image validation before confirming (blank flash / header check)
    has_validation = (
        "validation" in generated_code.lower()
        or "0xFF" in generated_code
        or "0xff" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="image_validated",
            passed=has_validation,
            expected="Firmware image validated before confirming (blank flash check)",
            actual="present" if has_validation else "missing — firmware accepted without validation",
            check_type="constraint",
        )
    )

    # Check 7: Bounds check on firmware buffer write (buffer overflow guard)
    has_bounds_check = (
        "sizeof(firmware_buf)" in generated_code
        or "offset + len" in generated_code
        or "BT_ATT_ERR_INVALID_OFFSET" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="firmware_buf_bounds_check",
            passed=has_bounds_check,
            expected="Firmware buffer write bounded (sizeof check or BT_ATT_ERR_INVALID_OFFSET)",
            actual="present" if has_bounds_check else "missing — buffer overflow risk in DFU write",
            check_type="constraint",
        )
    )

    # Check 8: is_authenticated reset to false on disconnect
    # LLM failure: authenticates once and never resets on disconnect
    disconnected_pos = generated_code.find("void disconnected")
    if disconnected_pos == -1:
        disconnected_pos = generated_code.find(".disconnected")
    auth_reset_in_disconnect = (
        disconnected_pos != -1
        and ("is_authenticated = false" in generated_code[disconnected_pos:]
             or "authenticated = false" in generated_code[disconnected_pos:])
    )
    details.append(
        CheckDetail(
            check_name="auth_state_reset_on_disconnect",
            passed=auth_reset_in_disconnect,
            expected="is_authenticated reset to false in disconnected callback",
            actual="present" if auth_reset_in_disconnect else "missing — auth state persists after disconnect",
            check_type="constraint",
        )
    )

    # Check 9: bt_enable error checked
    enable_idx = generated_code.find("bt_enable")
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
