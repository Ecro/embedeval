"""Behavioral checks for PSA Crypto SHA-256 hash."""

import re

from embedeval.check_utils import (check_no_cross_platform_apis,
    extract_error_blocks,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate SHA-256 behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

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

    # Check 6: No insecure hash algorithms used
    # LLM failure: using MD5 or SHA-1 instead of SHA-256 for security contexts
    has_md5 = bool(re.search(r'\bPSA_ALG_MD5\b|\bMD5\b', stripped))
    has_sha1 = bool(re.search(r'\bPSA_ALG_SHA_1\b|\bSHA_1\b|\bSHA1\b', stripped))
    details.append(
        CheckDetail(
            check_name="no_insecure_hash",
            passed=not has_md5 and not has_sha1,
            expected="No MD5 or SHA-1 (insecure; use SHA-256 or stronger)",
            actual="clean" if not (has_md5 or has_sha1) else f"insecure hash found: md5={has_md5}, sha1={has_sha1}",
            check_type="constraint",
        )
    )

    # Check 7: No rand()/srand() (insecure PRNG usage in security code)
    # LLM failure: using C stdlib rand() in security-sensitive code
    has_rand = bool(re.search(r'\brand\s*\(|\bsrand\s*\(', stripped))
    details.append(
        CheckDetail(
            check_name="no_insecure_rand",
            passed=not has_rand,
            expected="No rand()/srand() in security code (use PSA CSPRNG)",
            actual="clean" if not has_rand else "rand()/srand() found in security code",
            check_type="constraint",
        )
    )

    # Check 8: Error path does not silently discard PSA errors
    # LLM failure: ignoring return value of psa_hash_compute entirely
    psa_calls = re.findall(r'\bpsa_\w+\s*\(', generated_code)
    # At least one PSA call should have its return value checked
    has_return_check = bool(re.search(r'(status|ret|rc)\s*=\s*psa_', generated_code))
    details.append(
        CheckDetail(
            check_name="psa_return_values_checked",
            passed=has_return_check,
            expected="PSA function return values stored and checked",
            actual="present" if has_return_check else "PSA return values may be discarded",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
