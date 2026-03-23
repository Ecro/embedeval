"""Static analysis checks for HTTP client with TLS."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate HTTPS client code structure."""
    details: list[CheckDetail] = []

    has_http_h = "zephyr/net/http/client.h" in generated_code
    details.append(
        CheckDetail(
            check_name="http_client_header",
            passed=has_http_h,
            expected="zephyr/net/http/client.h included",
            actual="present" if has_http_h else "missing",
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

    has_tls_cred_add = "tls_credential_add" in generated_code
    details.append(
        CheckDetail(
            check_name="tls_credential_add_called",
            passed=has_tls_cred_add,
            expected="tls_credential_add() called to register CA cert",
            actual="present" if has_tls_cred_add else "missing",
            check_type="exact_match",
        )
    )

    has_tls_socket = "IPPROTO_TLS_1_2" in generated_code or "IPPROTO_TLS_1_3" in generated_code
    details.append(
        CheckDetail(
            check_name="tls_socket_protocol",
            passed=has_tls_socket,
            expected="IPPROTO_TLS_1_2 or IPPROTO_TLS_1_3 used for TLS socket",
            actual="present" if has_tls_socket else "missing — plain TCP socket used",
            check_type="exact_match",
        )
    )

    has_sec_tag_list = "TLS_SEC_TAG_LIST" in generated_code
    details.append(
        CheckDetail(
            check_name="tls_sec_tag_list_set",
            passed=has_sec_tag_list,
            expected="TLS_SEC_TAG_LIST socket option set",
            actual="present" if has_sec_tag_list else "missing",
            check_type="exact_match",
        )
    )

    has_hostname = "TLS_HOSTNAME" in generated_code
    details.append(
        CheckDetail(
            check_name="tls_hostname_set",
            passed=has_hostname,
            expected="TLS_HOSTNAME socket option set for SNI",
            actual="present" if has_hostname else "missing",
            check_type="exact_match",
        )
    )

    has_http_req = "http_client_req" in generated_code
    details.append(
        CheckDetail(
            check_name="http_client_req_called",
            passed=has_http_req,
            expected="http_client_req() called",
            actual="present" if has_http_req else "missing",
            check_type="exact_match",
        )
    )

    has_ca_cert = "TLS_CREDENTIAL_CA_CERTIFICATE" in generated_code
    details.append(
        CheckDetail(
            check_name="ca_certificate_type",
            passed=has_ca_cert,
            expected="TLS_CREDENTIAL_CA_CERTIFICATE type used",
            actual="present" if has_ca_cert else "missing",
            check_type="exact_match",
        )
    )

    return details
