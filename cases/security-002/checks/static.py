"""Static analysis checks for PSA Crypto SHA-256 hash."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PSA Crypto SHA-256 code structure."""
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

    # Check 2: psa_crypto_init called (common LLM failure: omitted entirely)
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

    # Check 3: SHA-256 algorithm constant used (not SHA_512, MD5, etc.)
    has_sha256_alg = "PSA_ALG_SHA_256" in generated_code
    details.append(
        CheckDetail(
            check_name="sha256_algorithm_constant",
            passed=has_sha256_alg,
            expected="PSA_ALG_SHA_256 used",
            actual="present" if has_sha256_alg else "missing or wrong algorithm",
            check_type="exact_match",
        )
    )

    # Check 4: Hash output buffer is at least 32 bytes
    # LLM failure: buffer declared too small (e.g. 16 bytes)
    import re
    buf_sizes = re.findall(r'\b(\d+)\b', generated_code)
    has_32_or_macro = (
        "32" in buf_sizes
        or "SHA256_DIGEST_SIZE" in generated_code
        or "PSA_HASH_LENGTH" in generated_code
        or "PSA_HASH_MAX_SIZE" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="output_buffer_adequate_size",
            passed=has_32_or_macro,
            expected="Hash output buffer >= 32 bytes (SHA-256 digest size)",
            actual="adequate size found" if has_32_or_macro else "buffer may be too small",
            check_type="constraint",
        )
    )

    # Check 5: PSA_SUCCESS checked
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

    # Check 6: No use of standard C rand()/srand() or MD5 (wrong crypto primitives)
    bad_primitives = ["rand()", "srand(", "MD5", "md5"]
    has_bad = any(p in generated_code for p in bad_primitives)
    details.append(
        CheckDetail(
            check_name="no_wrong_crypto_primitives",
            passed=not has_bad,
            expected="No rand()/MD5 usage (must use PSA API)",
            actual="bad primitives found" if has_bad else "clean",
            check_type="constraint",
        )
    )

    return details
