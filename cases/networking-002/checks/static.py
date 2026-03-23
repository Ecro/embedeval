"""Static analysis checks for UDP socket send/receive."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate UDP socket code structure."""
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

    has_socket = "zsock_socket" in generated_code
    details.append(
        CheckDetail(
            check_name="zsock_socket_called",
            passed=has_socket,
            expected="zsock_socket() called",
            actual="present" if has_socket else "missing",
            check_type="exact_match",
        )
    )

    has_af_inet = "AF_INET" in generated_code
    details.append(
        CheckDetail(
            check_name="af_inet_used",
            passed=has_af_inet,
            expected="AF_INET address family used",
            actual="present" if has_af_inet else "missing",
            check_type="exact_match",
        )
    )

    has_sock_dgram = "SOCK_DGRAM" in generated_code
    details.append(
        CheckDetail(
            check_name="sock_dgram_used",
            passed=has_sock_dgram,
            expected="SOCK_DGRAM socket type used for UDP",
            actual="present" if has_sock_dgram else "missing",
            check_type="exact_match",
        )
    )

    has_htons = "htons" in generated_code
    details.append(
        CheckDetail(
            check_name="htons_for_port",
            passed=has_htons,
            expected="htons() used for port byte order conversion",
            actual="present" if has_htons else "missing",
            check_type="exact_match",
        )
    )

    has_sendto = "zsock_sendto" in generated_code
    details.append(
        CheckDetail(
            check_name="zsock_sendto_called",
            passed=has_sendto,
            expected="zsock_sendto() called",
            actual="present" if has_sendto else "missing",
            check_type="exact_match",
        )
    )

    has_recvfrom = "zsock_recvfrom" in generated_code
    details.append(
        CheckDetail(
            check_name="zsock_recvfrom_called",
            passed=has_recvfrom,
            expected="zsock_recvfrom() called",
            actual="present" if has_recvfrom else "missing",
            check_type="exact_match",
        )
    )

    has_close = "zsock_close" in generated_code
    details.append(
        CheckDetail(
            check_name="zsock_close_called",
            passed=has_close,
            expected="zsock_close() called to release socket",
            actual="present" if has_close else "missing",
            check_type="exact_match",
        )
    )

    return details
