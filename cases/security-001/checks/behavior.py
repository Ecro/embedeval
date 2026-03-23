"""Behavioral checks for PSA Crypto AES."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PSA Crypto behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: init before import (correct ordering)
    init_pos = generated_code.find("psa_crypto_init")
    import_pos = generated_code.find("psa_import_key")
    details.append(
        CheckDetail(
            check_name="init_before_import",
            passed=init_pos != -1 and import_pos != -1 and init_pos < import_pos,
            expected="psa_crypto_init() before psa_import_key()",
            actual="correct" if init_pos < import_pos else "wrong order",
            check_type="constraint",
        )
    )

    # Check 2: Key type is AES
    has_aes = "PSA_KEY_TYPE_AES" in generated_code
    details.append(
        CheckDetail(
            check_name="key_type_aes",
            passed=has_aes,
            expected="PSA_KEY_TYPE_AES used",
            actual="present" if has_aes else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Key destroyed after use (resource cleanup)
    # (LLM failure: key handle leaked)
    has_destroy = "psa_destroy_key" in generated_code
    details.append(
        CheckDetail(
            check_name="key_destroyed",
            passed=has_destroy,
            expected="psa_destroy_key() called after use",
            actual="present" if has_destroy else "missing (key leaked)",
            check_type="constraint",
        )
    )

    # Check 4: Both encrypt AND decrypt present (round-trip)
    has_enc = "psa_cipher_encrypt" in generated_code
    has_dec = "psa_cipher_decrypt" in generated_code
    details.append(
        CheckDetail(
            check_name="encrypt_decrypt_roundtrip",
            passed=has_enc and has_dec,
            expected="Both encrypt and decrypt for verification",
            actual=f"encrypt={has_enc}, decrypt={has_dec}",
            check_type="constraint",
        )
    )

    # Check 5: PSA_SUCCESS checked (not just != 0)
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

    # Check 6: Usage flags include both ENCRYPT and DECRYPT
    has_enc_flag = "PSA_KEY_USAGE_ENCRYPT" in generated_code
    has_dec_flag = "PSA_KEY_USAGE_DECRYPT" in generated_code
    details.append(
        CheckDetail(
            check_name="usage_flags_both_directions",
            passed=has_enc_flag and has_dec_flag,
            expected="Key usage allows both ENCRYPT and DECRYPT",
            actual=f"enc={has_enc_flag}, dec={has_dec_flag}",
            check_type="constraint",
        )
    )

    return details
