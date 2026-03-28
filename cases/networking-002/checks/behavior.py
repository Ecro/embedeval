"""Behavioral checks for UDP socket send/receive."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate UDP socket behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: AF_INET + SOCK_DGRAM together (not SOCK_STREAM for UDP)
    has_af_inet = "AF_INET" in generated_code
    has_sock_dgram = "SOCK_DGRAM" in generated_code
    details.append(
        CheckDetail(
            check_name="udp_socket_type",
            passed=has_af_inet and has_sock_dgram,
            expected="AF_INET with SOCK_DGRAM for UDP socket",
            actual=f"AF_INET={has_af_inet}, SOCK_DGRAM={has_sock_dgram}",
            check_type="constraint",
        )
    )

    # Check 2: Port converted with htons (common LLM failure: raw integer)
    has_htons = "htons" in generated_code
    details.append(
        CheckDetail(
            check_name="port_byte_order",
            passed=has_htons,
            expected="htons() used for network byte order port conversion",
            actual="present" if has_htons else "missing — port not converted to network byte order",
            check_type="exact_match",
        )
    )

    # Check 3: Socket error check (sock < 0)
    has_sock_check = "< 0" in generated_code
    details.append(
        CheckDetail(
            check_name="socket_error_handling",
            passed=has_sock_check,
            expected="Socket return value checked for error (< 0)",
            actual="present" if has_sock_check else "missing",
            check_type="constraint",
        )
    )

    # Check 4: Both send and receive present
    has_sendto = "zsock_sendto" in generated_code
    has_recvfrom = "zsock_recvfrom" in generated_code
    details.append(
        CheckDetail(
            check_name="send_and_receive",
            passed=has_sendto and has_recvfrom,
            expected="Both zsock_sendto() and zsock_recvfrom() present",
            actual=f"sendto={has_sendto}, recvfrom={has_recvfrom}",
            check_type="constraint",
        )
    )

    # Check 5: Socket closed after use (resource cleanup)
    has_close = "zsock_close" in generated_code
    details.append(
        CheckDetail(
            check_name="socket_closed",
            passed=has_close,
            expected="zsock_close() called to release socket resource",
            actual="present" if has_close else "missing — socket leak",
            check_type="exact_match",
        )
    )

    # Check 6: sockaddr_in used for IPv4 address
    has_sockaddr_in = "sockaddr_in" in generated_code
    details.append(
        CheckDetail(
            check_name="sockaddr_in_used",
            passed=has_sockaddr_in,
            expected="struct sockaddr_in used for IPv4 address",
            actual="present" if has_sockaddr_in else "missing",
            check_type="exact_match",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
