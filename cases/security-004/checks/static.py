"""Static analysis checks for PSA HKDF key derivation."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PSA key derivation code structure."""
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

    # Check 3: HKDF algorithm with SHA-256 used (LLM failure: wrong algorithm constant)
    has_hkdf = "PSA_ALG_HKDF" in generated_code
    has_sha256 = "PSA_ALG_SHA_256" in generated_code
    details.append(
        CheckDetail(
            check_name="hkdf_sha256_algorithm",
            passed=has_hkdf and has_sha256,
            expected="PSA_ALG_HKDF(PSA_ALG_SHA_256) used",
            actual=f"HKDF={has_hkdf}, SHA256={has_sha256}",
            check_type="exact_match",
        )
    )

    # Check 4: Salt input step present (LLM failure: skips salt, wrong derivation)
    has_salt_input = (
        "PSA_KEY_DERIVATION_INPUT_SALT" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="salt_input_present",
            passed=has_salt_input,
            expected="PSA_KEY_DERIVATION_INPUT_SALT step present",
            actual="present" if has_salt_input else "missing (HKDF will fail or produce wrong key)",
            check_type="exact_match",
        )
    )

    # Check 5: All three derivation input steps present
    has_secret = "PSA_KEY_DERIVATION_INPUT_SECRET" in generated_code
    has_info = "PSA_KEY_DERIVATION_INPUT_INFO" in generated_code
    details.append(
        CheckDetail(
            check_name="all_derivation_inputs_present",
            passed=has_salt_input and has_secret and has_info,
            expected="SALT, SECRET, and INFO inputs all present",
            actual=f"salt={has_salt_input}, secret={has_secret}, info={has_info}",
            check_type="constraint",
        )
    )

    # Check 6: psa_key_derivation_abort called (resource cleanup)
    has_abort = "psa_key_derivation_abort" in generated_code
    details.append(
        CheckDetail(
            check_name="derivation_aborted",
            passed=has_abort,
            expected="psa_key_derivation_abort() called for cleanup",
            actual="present" if has_abort else "missing (operation leaked)",
            check_type="constraint",
        )
    )

    return details
