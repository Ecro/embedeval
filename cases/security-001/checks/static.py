"""Static analysis checks for PSA Crypto AES."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PSA Crypto code structure."""
    details: list[CheckDetail] = []

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

    has_init = "psa_crypto_init" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_init_called",
            passed=has_init,
            expected="psa_crypto_init() called",
            actual="present" if has_init else "missing",
            check_type="exact_match",
        )
    )

    has_import = "psa_import_key" in generated_code
    details.append(
        CheckDetail(
            check_name="key_imported",
            passed=has_import,
            expected="psa_import_key() called",
            actual="present" if has_import else "missing",
            check_type="exact_match",
        )
    )

    has_encrypt = "psa_cipher_encrypt" in generated_code
    details.append(
        CheckDetail(
            check_name="encrypt_called",
            passed=has_encrypt,
            expected="psa_cipher_encrypt() called",
            actual="present" if has_encrypt else "missing",
            check_type="exact_match",
        )
    )

    has_decrypt = "psa_cipher_decrypt" in generated_code
    details.append(
        CheckDetail(
            check_name="decrypt_called",
            passed=has_decrypt,
            expected="psa_cipher_decrypt() called",
            actual="present" if has_decrypt else "missing",
            check_type="exact_match",
        )
    )

    return details
