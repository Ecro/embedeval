"""Static analysis checks for TCP server with buffer overflow protection."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate TCP server buffer safety."""
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

    # Buffer must be declared (any reasonable static buffer)
    has_recv_buf = "recv_buf" in generated_code
    details.append(
        CheckDetail(
            check_name="recv_buffer_declared",
            passed=has_recv_buf,
            expected="recv_buf array declared",
            actual="present" if has_recv_buf else "missing",
            check_type="exact_match",
        )
    )

    # recv call must not use an unbounded size (no recv(sock, buf, 9999 or large literal)
    # Positive check: uses sizeof(recv_buf) or sizeof(recv_buf) - 1
    has_bounded_recv = "sizeof(recv_buf)" in generated_code
    details.append(
        CheckDetail(
            check_name="recv_size_bounded",
            passed=has_bounded_recv,
            expected="zsock_recv size argument uses sizeof(recv_buf)",
            actual="present" if has_bounded_recv else "missing — buffer size not bounded by sizeof",
            check_type="exact_match",
        )
    )

    # No unsafe sprintf
    has_sprintf = "sprintf(" in generated_code and "snprintf(" not in generated_code
    details.append(
        CheckDetail(
            check_name="no_unsafe_sprintf",
            passed=not has_sprintf,
            expected="snprintf used instead of sprintf",
            actual="safe" if not has_sprintf else "unsafe — sprintf without bounds",
            check_type="exact_match",
        )
    )

    has_listen = "zsock_listen" in generated_code or "listen(" in generated_code
    details.append(
        CheckDetail(
            check_name="listen_called",
            passed=has_listen,
            expected="listen() called for TCP server",
            actual="present" if has_listen else "missing",
            check_type="exact_match",
        )
    )

    has_accept = "zsock_accept" in generated_code or "accept(" in generated_code
    details.append(
        CheckDetail(
            check_name="accept_called",
            passed=has_accept,
            expected="accept() called to receive client connections",
            actual="present" if has_accept else "missing",
            check_type="exact_match",
        )
    )

    return details
