"""Static analysis checks for TLS Mutual Authentication credentials."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate TLS mutual auth credential loading code structure."""
    details: list[CheckDetail] = []

    # Check 1: tls_credentials.h included (not OpenSSL header)
    has_tls_creds_h = "tls_credentials.h" in generated_code
    details.append(
        CheckDetail(
            check_name="tls_credentials_header",
            passed=has_tls_creds_h,
            expected="zephyr/net/tls_credentials.h included",
            actual="present" if has_tls_creds_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: No OpenSSL hallucination (LLM failure: uses OpenSSL API on Zephyr)
    openssl_apis = [
        "SSL_CTX_load_verify_locations",
        "SSL_CTX_use_certificate_file",
        "SSL_CTX_use_PrivateKey_file",
        "SSL_CTX_new",
        "openssl/ssl.h",
    ]
    has_openssl = any(api in generated_code for api in openssl_apis)
    details.append(
        CheckDetail(
            check_name="no_openssl_api",
            passed=not has_openssl,
            expected="No OpenSSL API (Zephyr uses tls_credential_add, not SSL_CTX_*)",
            actual="OpenSSL API detected (hallucination!)" if has_openssl else "correct (no OpenSSL)",
            check_type="constraint",
        )
    )

    # Check 3: tls_credential_add called at least 3 times (CA + client cert + key)
    import re
    add_calls = len(re.findall(r'\btls_credential_add\b', generated_code))
    details.append(
        CheckDetail(
            check_name="three_credentials_loaded",
            passed=add_calls >= 3,
            expected="tls_credential_add called at least 3 times (CA cert, client cert, client key)",
            actual=f"found {add_calls} call(s)",
            check_type="constraint",
        )
    )

    # Check 4: CA certificate type used
    has_ca_type = "TLS_CREDENTIAL_CA_CERTIFICATE" in generated_code
    details.append(
        CheckDetail(
            check_name="ca_certificate_type",
            passed=has_ca_type,
            expected="TLS_CREDENTIAL_CA_CERTIFICATE type used for CA cert",
            actual="present" if has_ca_type else "missing (CA cert type wrong or missing)",
            check_type="exact_match",
        )
    )

    # Check 5: Private key type used
    has_key_type = "TLS_CREDENTIAL_PRIVATE_KEY" in generated_code
    details.append(
        CheckDetail(
            check_name="private_key_type",
            passed=has_key_type,
            expected="TLS_CREDENTIAL_PRIVATE_KEY type used for client key",
            actual="present" if has_key_type else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Return value checked (not ignoring tls_credential_add result)
    has_ret_check = "!= 0" in generated_code or "< 0" in generated_code or "== 0" in generated_code
    details.append(
        CheckDetail(
            check_name="return_value_checked",
            passed=has_ret_check,
            expected="Return value of tls_credential_add checked",
            actual="present" if has_ret_check else "missing (errors ignored)",
            check_type="constraint",
        )
    )

    return details
