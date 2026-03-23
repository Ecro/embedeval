"""Behavioral checks for BLE L2CAP Connection-Oriented Channel (CoC)."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate L2CAP CoC server setup, PSM validity, and data handling."""
    details: list[CheckDetail] = []

    # Check 1: PSM value is in valid range for LE CoC (0x0080 - 0x00FF for dynamic)
    # Accept any hex value that is >= 0x40 (below 0x40 are reserved/SIG)
    import re
    psm_match = re.search(r"(?:L2CAP_PSM|\.psm)\s*[=\s]+0x([0-9a-fA-F]+)", generated_code)
    psm_valid = False
    if psm_match:
        psm_val = int(psm_match.group(1), 16)
        psm_valid = 0x40 <= psm_val <= 0xFF
    else:
        # Fall back to any psm definition
        psm_valid = "psm" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="psm_value_valid",
            passed=psm_valid,
            expected="PSM value in valid dynamic range (0x40-0xFF for LE CoC)",
            actual="valid" if psm_valid else "PSM missing or out of valid range",
            check_type="constraint",
        )
    )

    # Check 2: bt_l2cap_server_register before bt_le_adv_start
    register_pos = generated_code.find("bt_l2cap_server_register")
    adv_pos = generated_code.find("bt_le_adv_start")
    register_before_adv = (
        register_pos != -1
        and (adv_pos == -1 or register_pos < adv_pos)
    )
    details.append(
        CheckDetail(
            check_name="server_registered_before_advertising",
            passed=register_before_adv,
            expected="bt_l2cap_server_register() before bt_le_adv_start()",
            actual="correct" if register_before_adv else "wrong order — clients could connect before server ready",
            check_type="constraint",
        )
    )

    # Check 3: accept callback assigns channel ops
    has_ops_assign = "chan.ops" in generated_code or "l2cap_ops" in generated_code
    details.append(
        CheckDetail(
            check_name="channel_ops_assigned_in_accept",
            passed=has_ops_assign,
            expected="Channel ops struct assigned in accept callback",
            actual="present" if has_ops_assign else "missing — channel has no callbacks",
            check_type="constraint",
        )
    )

    # Check 4: recv callback returns 0 (credits released to peer)
    recv_pos = generated_code.find("l2cap_recv")
    # Look for 'return 0' after the recv function definition
    return_zero_in_recv = False
    if recv_pos != -1:
        recv_body = generated_code[recv_pos:recv_pos + 500]
        return_zero_in_recv = "return 0" in recv_body
    details.append(
        CheckDetail(
            check_name="recv_returns_zero",
            passed=return_zero_in_recv,
            expected="recv callback returns 0 to release flow control credits",
            actual="present" if return_zero_in_recv else "missing — credits not released, peer flow-controlled",
            check_type="constraint",
        )
    )

    # Check 5: bt_enable before bt_l2cap_server_register
    enable_pos = generated_code.find("bt_enable")
    register_pos2 = generated_code.find("bt_l2cap_server_register")
    enable_before_register = (
        enable_pos != -1
        and (register_pos2 == -1 or enable_pos < register_pos2)
    )
    details.append(
        CheckDetail(
            check_name="bt_enable_before_l2cap_register",
            passed=enable_before_register,
            expected="bt_enable() called before bt_l2cap_server_register()",
            actual="correct" if enable_before_register else "wrong order — BT stack not initialized",
            check_type="constraint",
        )
    )

    return details
