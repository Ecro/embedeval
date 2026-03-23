"""Static analysis checks for HMAC-SHA256 Message Authentication."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate HMAC-SHA256 PSA MAC code structure."""
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
            expected="psa_crypto_init() called before MAC operations",
            actual="present" if has_init else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: psa_mac_sign_setup called (NOT psa_hash_setup — LLM failure)
    has_mac_setup = "psa_mac_sign_setup" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_mac_sign_setup_called",
            passed=has_mac_setup,
            expected="psa_mac_sign_setup() called (not psa_hash_setup)",
            actual="present" if has_mac_setup else "missing (LLM may have used psa_hash_setup)",
            check_type="exact_match",
        )
    )

    # Check 4: psa_mac_update called
    has_mac_update = "psa_mac_update" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_mac_update_called",
            passed=has_mac_update,
            expected="psa_mac_update() called",
            actual="present" if has_mac_update else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: psa_mac_sign_finish called
    has_mac_finish = "psa_mac_sign_finish" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_mac_sign_finish_called",
            passed=has_mac_finish,
            expected="psa_mac_sign_finish() called",
            actual="present" if has_mac_finish else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Correct algorithm PSA_ALG_HMAC(PSA_ALG_SHA_256)
    has_hmac_sha256 = (
        "PSA_ALG_HMAC" in generated_code and "PSA_ALG_SHA_256" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="hmac_sha256_algorithm",
            passed=has_hmac_sha256,
            expected="PSA_ALG_HMAC(PSA_ALG_SHA_256) used as algorithm",
            actual="present" if has_hmac_sha256 else "missing (wrong algorithm)",
            check_type="exact_match",
        )
    )

    # Check 7: Not using psa_hash_* instead of psa_mac_* (LLM failure pattern)
    uses_hash_instead = (
        "psa_hash_setup" in generated_code
        or "psa_hash_update" in generated_code
        or "psa_hash_finish" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="no_hash_api_for_hmac",
            passed=not uses_hash_instead,
            expected="psa_mac_* API used (not psa_hash_* which computes plain hash, not HMAC)",
            actual="hash API misused for HMAC!" if uses_hash_instead else "correct MAC API used",
            check_type="constraint",
        )
    )

    return details
