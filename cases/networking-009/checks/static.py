"""Static analysis checks for WebSocket client over TLS."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate WebSocket TLS code structure."""
    details: list[CheckDetail] = []

    has_ws_h = "zephyr/net/websocket.h" in generated_code
    details.append(
        CheckDetail(
            check_name="websocket_header",
            passed=has_ws_h,
            expected="zephyr/net/websocket.h included",
            actual="present" if has_ws_h else "missing",
            check_type="exact_match",
        )
    )

    has_tls_cred_h = "zephyr/net/tls_credentials.h" in generated_code
    details.append(
        CheckDetail(
            check_name="tls_credentials_header",
            passed=has_tls_cred_h,
            expected="zephyr/net/tls_credentials.h included",
            actual="present" if has_tls_cred_h else "missing",
            check_type="exact_match",
        )
    )

    has_tls_socket = (
        "IPPROTO_TLS_1_2" in generated_code
        or "IPPROTO_TLS_1_3" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="tls_socket_used",
            passed=has_tls_socket,
            expected="IPPROTO_TLS_1_2 or IPPROTO_TLS_1_3 socket used",
            actual="present" if has_tls_socket else "missing — plain TCP socket, no TLS",
            check_type="exact_match",
        )
    )

    has_sec_tag = "TLS_SEC_TAG_LIST" in generated_code
    details.append(
        CheckDetail(
            check_name="sec_tag_list_set",
            passed=has_sec_tag,
            expected="TLS_SEC_TAG_LIST socket option set",
            actual="present" if has_sec_tag else "missing",
            check_type="exact_match",
        )
    )

    has_tls_hostname = "TLS_HOSTNAME" in generated_code
    details.append(
        CheckDetail(
            check_name="tls_hostname_set",
            passed=has_tls_hostname,
            expected="TLS_HOSTNAME set for SNI",
            actual="present" if has_tls_hostname else "missing",
            check_type="exact_match",
        )
    )

    has_ws_connect = "websocket_connect" in generated_code
    details.append(
        CheckDetail(
            check_name="websocket_connect_called",
            passed=has_ws_connect,
            expected="websocket_connect() called",
            actual="present" if has_ws_connect else "missing",
            check_type="exact_match",
        )
    )

    has_tls_cred_add = "tls_credential_add" in generated_code
    details.append(
        CheckDetail(
            check_name="tls_credential_registered",
            passed=has_tls_cred_add,
            expected="tls_credential_add() called to register CA cert",
            actual="present" if has_tls_cred_add else "missing — no TLS credentials registered",
            check_type="exact_match",
        )
    )

    return details
