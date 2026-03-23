"""Behavioral checks for BLE secure OTA / DFU service."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DFU authentication ordering and image validation safety."""
    details: list[CheckDetail] = []

    # Check 1: bt_conn_set_security called in connected callback (not main)
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

    # Check 2: Authentication check before writing firmware data
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

    # Check 3: BT_ATT_ERR_AUTHORIZATION returned when not authenticated
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

    # Check 4: Image validation before confirming
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

    # Check 5: Bounds check on firmware buffer write
    has_bounds_check = (
        "sizeof(firmware_buf)" in generated_code
        or "offset + len" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="firmware_buf_bounds_check",
            passed=has_bounds_check,
            expected="Firmware buffer write bounded to prevent overflow",
            actual="present" if has_bounds_check else "missing — buffer overflow risk in DFU write",
            check_type="constraint",
        )
    )

    # Check 6: bt_enable and bt_le_adv_start in main
    has_enable = "bt_enable" in generated_code
    has_adv = "bt_le_adv_start" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_enable_and_adv",
            passed=has_enable and has_adv,
            expected="bt_enable() and bt_le_adv_start() called",
            actual=f"enable={has_enable}, adv={has_adv}",
            check_type="constraint",
        )
    )

    return details
