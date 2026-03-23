"""Static analysis checks for Secure Key Storage with Anti-Tamper."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate non-extractable key storage code structure."""
    details: list[CheckDetail] = []

    # Check 1: psa/crypto.h included
    has_psa_h = "psa/crypto.h" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_crypto_header",
            passed=has_psa_h,
            expected="psa/crypto.h included",
            actual="present" if has_psa_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: psa_crypto_init called
    has_init = "psa_crypto_init" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_crypto_init_called",
            passed=has_init,
            expected="psa_crypto_init() called",
            actual="present" if has_init else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: PSA_KEY_USAGE_EXPORT must NOT be set (LLM failure: always adds it)
    # Strip comments first to avoid matching mentions in comment text
    code_no_comments = re.sub(r'/\*.*?\*/', '', generated_code, flags=re.DOTALL)
    code_no_comments = re.sub(r'//[^\n]*', '', code_no_comments)
    has_export_flag = "PSA_KEY_USAGE_EXPORT" in code_no_comments
    details.append(
        CheckDetail(
            check_name="no_export_usage_flag",
            passed=not has_export_flag,
            expected="PSA_KEY_USAGE_EXPORT must NOT be set (non-extractable key)",
            actual="EXPORT flag present (security violation!)" if has_export_flag else "EXPORT flag absent (correct)",
            check_type="constraint",
        )
    )

    # Check 4: PSA_KEY_LIFETIME_PERSISTENT used
    has_persistent = "PSA_KEY_LIFETIME_PERSISTENT" in generated_code
    details.append(
        CheckDetail(
            check_name="persistent_lifetime",
            passed=has_persistent,
            expected="PSA_KEY_LIFETIME_PERSISTENT set for key lifetime",
            actual="present" if has_persistent else "missing (volatile key only)",
            check_type="exact_match",
        )
    )

    # Check 5: psa_import_key called
    has_import = "psa_import_key" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_import_key_called",
            passed=has_import,
            expected="psa_import_key() called",
            actual="present" if has_import else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Key ID is non-zero (slot ID valid)
    # Reject patterns like psa_set_key_id(&attrs, 0) or psa_set_key_id(&x, 0U)
    zero_id_pattern = r'psa_set_key_id\s*\([^,]+,\s*0[UuLl]*\s*\)'
    has_zero_id = bool(re.search(zero_id_pattern, generated_code))
    details.append(
        CheckDetail(
            check_name="key_id_nonzero",
            passed=not has_zero_id,
            expected="Key ID must be non-zero",
            actual="zero ID detected (invalid!)" if has_zero_id else "non-zero key ID",
            check_type="constraint",
        )
    )

    # Check 7: PSA_SUCCESS checked
    has_psa_success = "PSA_SUCCESS" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_success_checked",
            passed=has_psa_success,
            expected="PSA_SUCCESS used for return value checks",
            actual="present" if has_psa_success else "missing",
            check_type="exact_match",
        )
    )

    return details
