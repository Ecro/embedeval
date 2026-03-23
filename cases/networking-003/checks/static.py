"""Static analysis checks for TCP client with connection retry."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate TCP retry client code structure."""
    details: list[CheckDetail] = []

    has_socket_h = "zephyr/net/socket.h" in generated_code
    details.append(
        CheckDetail(
            check_name="socket_header",
            passed=has_socket_h,
            expected="zephyr/net/socket.h included",
            actual="present" if has_socket_h else "missing",
            check_type="exact_match",
        )
    )

    has_errno_h = "errno.h" in generated_code
    details.append(
        CheckDetail(
            check_name="errno_header",
            passed=has_errno_h,
            expected="errno.h included",
            actual="present" if has_errno_h else "missing",
            check_type="exact_match",
        )
    )

    has_sock_stream = "SOCK_STREAM" in generated_code
    details.append(
        CheckDetail(
            check_name="sock_stream_used",
            passed=has_sock_stream,
            expected="SOCK_STREAM used for TCP socket",
            actual="present" if has_sock_stream else "missing",
            check_type="exact_match",
        )
    )

    has_connect = "zsock_connect" in generated_code
    details.append(
        CheckDetail(
            check_name="zsock_connect_called",
            passed=has_connect,
            expected="zsock_connect() called",
            actual="present" if has_connect else "missing",
            check_type="exact_match",
        )
    )

    has_max_retries = "MAX_RETRIES" in generated_code or "max_retries" in generated_code or "3" in generated_code
    details.append(
        CheckDetail(
            check_name="max_retries_defined",
            passed=has_max_retries,
            expected="MAX_RETRIES or equivalent constant defined",
            actual="present" if has_max_retries else "missing",
            check_type="exact_match",
        )
    )

    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="backoff_sleep",
            passed=has_sleep,
            expected="k_sleep() used for backoff delay between retries",
            actual="present" if has_sleep else "missing",
            check_type="exact_match",
        )
    )

    has_close = "zsock_close" in generated_code
    details.append(
        CheckDetail(
            check_name="zsock_close_called",
            passed=has_close,
            expected="zsock_close() called",
            actual="present" if has_close else "missing",
            check_type="exact_match",
        )
    )

    return details
