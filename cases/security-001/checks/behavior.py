"""Behavioral checks for PSA Crypto AES."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    strip_comments,
)
from embedeval.models import CheckDetail


def _extract_psa_error_blocks(code: str) -> list[str]:
    """Extract PSA-style error blocks: if (status != PSA_SUCCESS) { ... }"""
    blocks = []
    for match in re.finditer(
        r"if\s*\([^)]*(?:PSA_SUCCESS|!=\s*0|<\s*0)[^)]*\)\s*\{",
        code,
    ):
        start = match.end()
        depth = 1
        for i in range(start, len(code)):
            if code[i] == "{":
                depth += 1
            elif code[i] == "}":
                depth -= 1
            if depth == 0:
                blocks.append(code[start:i])
                break
    return blocks


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PSA Crypto behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

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

    # Check 7: Error path key destruction — psa_destroy_key in error blocks
    # LLM failure: importing key, failing on encrypt, then leaking the key slot
    error_blocks = _extract_psa_error_blocks(generated_code)
    error_blocks_destroy = any("psa_destroy_key" in block for block in error_blocks)
    details.append(
        CheckDetail(
            check_name="error_path_key_destroyed",
            passed=error_blocks_destroy,
            expected="psa_destroy_key() called in error paths (not just on success)",
            actual="key cleanup in error path" if error_blocks_destroy else "key leaked on error path",
            check_type="constraint",
        )
    )

    # Check 8: No insecure cipher modes — no ECB mode
    # LLM failure: using PSA_ALG_ECB which is not semantically secure for general use
    has_plain_ecb = bool(re.search(r"\bPSA_ALG_ECB\b(?!_NO_PADDING)", stripped))
    details.append(
        CheckDetail(
            check_name="no_ecb_mode",
            passed=not has_plain_ecb,
            expected="No PSA_ALG_ECB mode (semantically insecure)",
            actual="clean" if not has_plain_ecb else "PSA_ALG_ECB found (insecure block mode)",
            check_type="constraint",
        )
    )

    # Check 9: No OpenSSL/cross-platform crypto APIs
    # LLM failure: mixing in SSL_CTX_*, EVP_*, AES_encrypt() from OpenSSL
    cross_platform = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace", "POSIX"])
    openssl_apis = ["SSL_CTX_", "EVP_", "AES_encrypt", "AES_decrypt", "RAND_bytes"]
    has_openssl = any(api in generated_code for api in openssl_apis)
    details.append(
        CheckDetail(
            check_name="no_openssl_apis",
            passed=not has_openssl and len(cross_platform) == 0,
            expected="No OpenSSL/cross-platform crypto APIs (use PSA Crypto only)",
            actual="clean" if not has_openssl else "OpenSSL APIs found",
            check_type="constraint",
        )
    )

    return details
