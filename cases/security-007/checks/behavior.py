"""Behavioral checks for TLS Mutual Authentication credentials."""

import re

from embedeval.check_utils import (check_no_cross_platform_apis,
    extract_error_blocks,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate TLS mutual auth credential behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: All three tls_credential_add calls use the same sec_tag
    # Extract first argument up to first comma, strip casts like (sec_tag_t)
    raw_args = re.findall(
        r'tls_credential_add\s*\(\s*([^,]+)',
        generated_code
    )
    # Normalize: strip whitespace and cast expressions e.g. "(sec_tag_t) FOO" -> "FOO"
    normalized_tags = [
        re.sub(r'\(\s*\w+\s*\)\s*', '', arg).strip() for arg in raw_args
    ]
    call_pattern = normalized_tags
    same_sec_tag = len(set(normalized_tags)) <= 1 and len(normalized_tags) >= 3
    details.append(
        CheckDetail(
            check_name="same_sec_tag_all_credentials",
            passed=same_sec_tag,
            expected="All 3 tls_credential_add calls use the same sec_tag",
            actual=f"tags used: {list(set(call_pattern))}" if call_pattern else "no calls found",
            check_type="constraint",
        )
    )

    # Check 2: CA cert registered before client cert (logical ordering)
    ca_pos = generated_code.find("TLS_CREDENTIAL_CA_CERTIFICATE")
    client_cert_pos = generated_code.find("TLS_CREDENTIAL_SERVER_CERTIFICATE")
    ca_before_client = ca_pos != -1 and client_cert_pos != -1 and ca_pos < client_cert_pos
    details.append(
        CheckDetail(
            check_name="ca_cert_registered_first",
            passed=ca_before_client,
            expected="CA cert registered before client cert",
            actual="correct order" if ca_before_client else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: CA cert is CA type, not client cert type
    has_separate_types = (
        "TLS_CREDENTIAL_CA_CERTIFICATE" in generated_code
        and "TLS_CREDENTIAL_SERVER_CERTIFICATE" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="ca_and_client_types_distinct",
            passed=has_separate_types,
            expected="CA cert uses TLS_CREDENTIAL_CA_CERTIFICATE, client cert uses TLS_CREDENTIAL_SERVER_CERTIFICATE",
            actual="both types present" if has_separate_types else "types mixed up or missing",
            check_type="constraint",
        )
    )

    # Check 4: Error handling present — print on failure
    has_error_print = bool(
        re.search(r'(printk|printf)\s*\([^)]*FAILED[^)]*\)', generated_code)
        or re.search(r'(printk|printf)\s*\([^)]*[Ff]ail[^)]*\)', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="error_printed_on_failure",
            passed=has_error_print,
            expected="Failure message printed when tls_credential_add fails",
            actual="present" if has_error_print else "missing (silent failure)",
            check_type="constraint",
        )
    )

    # Check 5: Success message printed
    has_ok_print = bool(
        re.search(r'(printk|printf)\s*\([^)]*OK[^)]*\)', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="success_printed",
            passed=has_ok_print,
            expected="Success message printed when all credentials loaded",
            actual="present" if has_ok_print else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Error paths return early on credential failure
    # LLM failure: continuing after tls_credential_add fails, then using broken TLS config
    error_blocks = extract_error_blocks(generated_code)
    error_returns = any("return" in block for block in error_blocks)
    details.append(
        CheckDetail(
            check_name="error_path_returns_early",
            passed=error_returns,
            expected="Error path returns early when tls_credential_add fails",
            actual="present" if error_returns else "missing (may continue with failed credentials)",
            check_type="constraint",
        )
    )

    # Check 7: No rand()/srand() in TLS credential setup
    has_rand = bool(re.search(r'\brand\s*\(|\bsrand\s*\(', stripped))
    details.append(
        CheckDetail(
            check_name="no_insecure_rand",
            passed=not has_rand,
            expected="No rand()/srand() in TLS setup code",
            actual="clean" if not has_rand else "rand()/srand() found",
            check_type="constraint",
        )
    )

    # Check 8: No OpenSSL SSL_CTX_ APIs (wrong platform, Zephyr uses tls_credentials)
    # LLM failure: mixing OpenSSL APIs into Zephyr TLS code
    openssl_apis = ["SSL_CTX_", "SSL_new(", "SSL_connect(", "EVP_", "X509_"]
    has_openssl = any(api in generated_code for api in openssl_apis)
    details.append(
        CheckDetail(
            check_name="no_openssl_apis",
            passed=not has_openssl,
            expected="No OpenSSL SSL_CTX_* APIs (use Zephyr tls_credentials)",
            actual="clean" if not has_openssl else "OpenSSL APIs found (wrong platform)",
            check_type="constraint",
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
