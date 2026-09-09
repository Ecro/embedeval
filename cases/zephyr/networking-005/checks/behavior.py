"""Behavioral checks for HTTP client with TLS."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate HTTPS client behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: TLS credential registered BEFORE socket connect
    cred_pos = find_in_code(generated_code, "tls_credential_add")
    connect_pos = find_in_code(generated_code, "zsock_connect")
    cred_before_connect = (
        cred_pos != -1 and connect_pos != -1 and cred_pos < connect_pos
    )
    details.append(
        CheckDetail(
            check_name="credential_before_connect",
            passed=cred_before_connect,
            expected="tls_credential_add() called before zsock_connect()",
            actual="correct" if cred_before_connect else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: TLS socket (not plain TCP)
    has_tls = (
        scoped_contains(generated_code, 'IPPROTO_TLS_1_2', scope='code_only')
        or scoped_contains(generated_code, 'IPPROTO_TLS_1_3', scope='code_only')
    )
    details.append(
        CheckDetail(
            check_name="tls_socket_used",
            passed=has_tls,
            expected="TLS socket protocol (IPPROTO_TLS_1_2/1_3) used",
            actual="present" if has_tls else "missing — HTTP without TLS",
            check_type="exact_match",
        )
    )

    # Check 3: Security tag set on socket (links cert to socket)
    has_sec_tag = scoped_contains(generated_code, 'TLS_SEC_TAG_LIST', scope='code_only')
    details.append(
        CheckDetail(
            check_name="sec_tag_set_on_socket",
            passed=has_sec_tag,
            expected="TLS_SEC_TAG_LIST setsockopt applied to socket",
            actual="present" if has_sec_tag else "missing — cert not linked to socket",
            check_type="exact_match",
        )
    )

    # Check 4: Response callback defined and assigned
    has_response_cb = (
        scoped_contains(generated_code, 'response', scope='code_only')
        and (scoped_contains(generated_code, 'HTTP_DATA_FINAL', scope='code_only') or scoped_contains(generated_code, 'data_len', scope='code_only')
             or scoped_contains(generated_code, 'http_status', scope='code_only') or scoped_contains(generated_code, 'response_cb', scope='code_only'))
    )
    details.append(
        CheckDetail(
            check_name="response_callback_defined",
            passed=has_response_cb,
            expected="HTTP response callback defined and assigned",
            actual="present" if has_response_cb else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Timeout specified in http_client_req (not 0 or negative)
    has_timeout = scoped_contains(generated_code, 'http_client_req', scope='code_only') and (
        scoped_contains(generated_code, '5000', scope='code_only')
        or scoped_contains(generated_code, 'K_SECONDS', scope='code_only')
        or "timeout" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="request_timeout_set",
            passed=has_timeout,
            expected="Non-zero timeout passed to http_client_req()",
            actual="present" if has_timeout else "missing — may block forever",
            check_type="constraint",
        )
    )

    # Check 6: Port 443 used (HTTPS standard port)
    has_port_443 = scoped_contains(generated_code, '443', scope='code_only')
    details.append(
        CheckDetail(
            check_name="https_port_443",
            passed=has_port_443,
            expected="Port 443 used for HTTPS",
            actual="present" if has_port_443 else "missing — wrong port for HTTPS",
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
