"""Static analysis checks for PSA Protected Storage."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PSA Protected Storage code structure."""
    details: list[CheckDetail] = []

    # Check 1: psa/protected_storage.h included
    has_ps_h = "psa/protected_storage.h" in generated_code
    details.append(
        CheckDetail(
            check_name="protected_storage_header",
            passed=has_ps_h,
            expected="psa/protected_storage.h included",
            actual="present" if has_ps_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: psa_crypto_init called (LLM failure: skips init for PS-only code)
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

    # Check 3: psa_ps_set called
    has_ps_set = "psa_ps_set" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_ps_set_called",
            passed=has_ps_set,
            expected="psa_ps_set() called",
            actual="present" if has_ps_set else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: psa_ps_get called
    has_ps_get = "psa_ps_get" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_ps_get_called",
            passed=has_ps_get,
            expected="psa_ps_get() called",
            actual="present" if has_ps_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: UID is not 0 (UID 0 is reserved — LLM failure: uses 0)
    # Look for literal 0 as the first argument to psa_ps_set/psa_ps_get
    uid_zero_patterns = [
        r'psa_ps_set\s*\(\s*0\s*[,)]',
        r'psa_ps_get\s*\(\s*0\s*[,)]',
    ]
    has_uid_zero = any(re.search(p, generated_code) for p in uid_zero_patterns)
    details.append(
        CheckDetail(
            check_name="uid_not_zero",
            passed=not has_uid_zero,
            expected="UID != 0 (UID 0 is reserved)",
            actual="UID is 0 (reserved!)" if has_uid_zero else "UID appears non-zero",
            check_type="constraint",
        )
    )

    # Check 6: PSA_SUCCESS checked
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
