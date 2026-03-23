"""Behavioral checks for WebSocket client over TLS."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate WebSocket TLS ordering, security, and correctness."""
    details: list[CheckDetail] = []

    # Check 1: TLS credential registered BEFORE socket creation
    cred_pos = generated_code.find("tls_credential_add")
    sock_pos = generated_code.find("zsock_socket")
    tls_before_socket = (
        cred_pos != -1 and sock_pos != -1 and cred_pos < sock_pos
    )
    details.append(
        CheckDetail(
            check_name="tls_credential_before_socket",
            passed=tls_before_socket,
            expected="tls_credential_add() called before zsock_socket()",
            actual="correct" if tls_before_socket else "wrong order — credential must be registered first",
            check_type="constraint",
        )
    )

    # Check 2: TCP connect before WebSocket upgrade
    connect_pos = generated_code.find("zsock_connect")
    ws_conn_pos = generated_code.find("websocket_connect")
    tcp_before_ws = (
        connect_pos != -1 and ws_conn_pos != -1 and connect_pos < ws_conn_pos
    )
    details.append(
        CheckDetail(
            check_name="tcp_connect_before_websocket",
            passed=tcp_before_ws,
            expected="zsock_connect() called before websocket_connect()",
            actual="correct" if tcp_before_ws else "wrong order — TCP must be established before WS upgrade",
            check_type="constraint",
        )
    )

    # Check 3: websocket_send_msg uses correct opcode
    has_text_opcode = "WEBSOCKET_OPCODE_DATA_TEXT" in generated_code
    details.append(
        CheckDetail(
            check_name="websocket_text_opcode",
            passed=has_text_opcode,
            expected="WEBSOCKET_OPCODE_DATA_TEXT used for text frames",
            actual="present" if has_text_opcode else "missing — no text frame opcode",
            check_type="exact_match",
        )
    )

    # Check 4: Error check on websocket_connect
    has_err_check = "< 0" in generated_code
    details.append(
        CheckDetail(
            check_name="websocket_connect_error_check",
            passed=has_err_check,
            expected="websocket_connect() return value checked for error",
            actual="present" if has_err_check else "missing — errors not handled",
            check_type="constraint",
        )
    )

    # Check 5: websocket_disconnect called (proper cleanup)
    has_ws_disconnect = "websocket_disconnect" in generated_code
    details.append(
        CheckDetail(
            check_name="websocket_disconnect_called",
            passed=has_ws_disconnect,
            expected="websocket_disconnect() called for cleanup",
            actual="present" if has_ws_disconnect else "missing — resource leak",
            check_type="exact_match",
        )
    )

    # Check 6: No hardcoded credentials in code body (credentials in named constant)
    # If BEGIN CERTIFICATE appears in a named static array that's acceptable;
    # reject if the cert string is embedded directly in a function call argument.
    has_named_cert = "static const char" in generated_code or "static char" in generated_code
    has_cert_data = "BEGIN CERTIFICATE" in generated_code
    cert_safely_stored = has_cert_data and has_named_cert
    details.append(
        CheckDetail(
            check_name="credentials_in_named_constant",
            passed=cert_safely_stored or not has_cert_data,
            expected="TLS credentials stored in named constant array, not inline string literal",
            actual="safe" if (cert_safely_stored or not has_cert_data) else "unsafe — inline certificate",
            check_type="constraint",
        )
    )

    return details
