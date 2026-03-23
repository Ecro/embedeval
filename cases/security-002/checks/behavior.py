"""Behavioral checks for PSA Crypto SHA-256 hash."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate SHA-256 behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: init before hash compute (correct ordering)
    init_pos = generated_code.find("psa_crypto_init")
    hash_pos = generated_code.find("psa_hash_compute")
    if hash_pos == -1:
        hash_pos = generated_code.find("psa_hash_setup")
    details.append(
        CheckDetail(
            check_name="init_before_hash",
            passed=init_pos != -1 and hash_pos != -1 and init_pos < hash_pos,
            expected="psa_crypto_init() before hash operation",
            actual="correct order" if (init_pos != -1 and hash_pos != -1 and init_pos < hash_pos) else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: psa_hash_compute or equivalent multi-step API used
    has_hash_compute = "psa_hash_compute" in generated_code
    has_hash_multipart = (
        "psa_hash_setup" in generated_code
        and "psa_hash_update" in generated_code
        and "psa_hash_finish" in generated_code
    )
    has_hash_api = has_hash_compute or has_hash_multipart
    details.append(
        CheckDetail(
            check_name="psa_hash_api_used",
            passed=has_hash_api,
            expected="psa_hash_compute() or psa_hash_setup/update/finish()",
            actual="present" if has_hash_api else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Result compared to expected value (verification step)
    has_memcmp = "memcmp" in generated_code
    details.append(
        CheckDetail(
            check_name="hash_result_verified",
            passed=has_memcmp,
            expected="memcmp() used to verify hash against expected value",
            actual="present" if has_memcmp else "missing (no verification)",
            check_type="constraint",
        )
    )

    # Check 4: hash_len / output length checked or used
    import re
    has_len_var = bool(re.search(r'\b\w*hash_len\w*\b|\bdigest_len\b|\boutput_len\b|\bhash_length\b', generated_code))
    details.append(
        CheckDetail(
            check_name="hash_length_captured",
            passed=has_len_var,
            expected="Hash output length variable captured from psa_hash_compute",
            actual="present" if has_len_var else "missing (length unchecked)",
            check_type="constraint",
        )
    )

    # Check 5: Success or failure printed
    has_print = "printk" in generated_code or "printf" in generated_code
    details.append(
        CheckDetail(
            check_name="result_printed",
            passed=has_print,
            expected="Result printed (success or failure)",
            actual="present" if has_print else "missing",
            check_type="constraint",
        )
    )

    return details
