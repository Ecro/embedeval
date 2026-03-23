"""Static analysis checks for BLE L2CAP Connection-Oriented Channel (CoC)."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE L2CAP CoC code structure."""
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

    has_l2cap_h = "zephyr/bluetooth/l2cap.h" in generated_code
    details.append(
        CheckDetail(
            check_name="l2cap_header",
            passed=has_l2cap_h,
            expected="zephyr/bluetooth/l2cap.h included",
            actual="present" if has_l2cap_h else "missing",
            check_type="exact_match",
        )
    )

    has_server_register = "bt_l2cap_server_register" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_l2cap_server_register_called",
            passed=has_server_register,
            expected="bt_l2cap_server_register() called",
            actual="present" if has_server_register else "missing — server not registered",
            check_type="exact_match",
        )
    )

    has_psm = "L2CAP_PSM" in generated_code or ".psm" in generated_code
    details.append(
        CheckDetail(
            check_name="psm_value_set",
            passed=has_psm,
            expected="PSM value defined and set in server struct",
            actual="present" if has_psm else "missing — PSM not configured",
            check_type="exact_match",
        )
    )

    has_chan_send = "bt_l2cap_chan_send" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_l2cap_chan_send_used",
            passed=has_chan_send,
            expected="bt_l2cap_chan_send() used for sending data",
            actual="present" if has_chan_send else "missing",
            check_type="exact_match",
        )
    )

    # Hallucination: l2cap_connect() does not exist in Zephyr
    uses_l2cap_connect = "l2cap_connect(" in generated_code
    details.append(
        CheckDetail(
            check_name="no_l2cap_connect",
            passed=not uses_l2cap_connect,
            expected="l2cap_connect() NOT used (does not exist in Zephyr)",
            actual="clean" if not uses_l2cap_connect else "HALLUCINATION: l2cap_connect() does not exist",
            check_type="exact_match",
        )
    )

    has_recv_cb = "l2cap_recv" in generated_code or ".recv" in generated_code
    details.append(
        CheckDetail(
            check_name="recv_callback_defined",
            passed=has_recv_cb,
            expected="L2CAP recv callback defined",
            actual="present" if has_recv_cb else "missing — no data receive handling",
            check_type="exact_match",
        )
    )

    return details
