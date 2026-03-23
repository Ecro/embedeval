"""Behavioral checks for TLS Mutual Authentication credentials."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate TLS mutual auth credential behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: All three tls_credential_add calls use the same sec_tag
    # Extract all sec_tag arguments from tls_credential_add calls
    # Pattern: tls_credential_add(TAG, TYPE, buf, len)
    call_pattern = re.findall(
        r'tls_credential_add\s*\(\s*([A-Za-z0-9_]+)',
        generated_code
    )
    same_sec_tag = len(set(call_pattern)) <= 1 and len(call_pattern) >= 3
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

    # Check 3: CA cert is CA type, not client cert type (LLM failure: uses wrong type for CA)
    # Ensure TLS_CREDENTIAL_CA_CERTIFICATE is paired with ca_cert variable, not client_cert
    # We check that CA_CERTIFICATE appears and is distinct from SERVER_CERTIFICATE
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

    return details
