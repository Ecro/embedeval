"""Static analysis checks for Cryptographically Secure RNG."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate CSPRNG usage code structure."""
    details: list[CheckDetail] = []

    # Check 1: Uses sys_csrand_get OR psa_generate_random (secure sources)
    has_csrand = "sys_csrand_get" in generated_code
    has_psa_random = "psa_generate_random" in generated_code
    uses_secure_rng = has_csrand or has_psa_random
    details.append(
        CheckDetail(
            check_name="secure_rng_used",
            passed=uses_secure_rng,
            expected="sys_csrand_get() or psa_generate_random() used (CSPRNG)",
            actual="secure RNG present" if uses_secure_rng else "missing (no CSPRNG call found)",
            check_type="exact_match",
        )
    )

    # Check 2: Does NOT use rand() (insecure PRNG — LLM failure)
    # Strip comments to avoid matching mentions like "/* Never use rand() */"
    import re
    code_no_comments = re.sub(r'/\*.*?\*/', '', generated_code, flags=re.DOTALL)
    code_no_comments = re.sub(r'//[^\n]*', '', code_no_comments)
    uses_rand = bool(re.search(r'\brand\s*\(', code_no_comments))
    details.append(
        CheckDetail(
            check_name="no_rand_function",
            passed=not uses_rand,
            expected="rand() must NOT be used (not cryptographically secure)",
            actual="rand() detected (security failure!)" if uses_rand else "rand() not used (correct)",
            check_type="constraint",
        )
    )

    # Check 3: Does NOT use srand() (insecure seed — LLM failure)
    uses_srand = bool(re.search(r'\bsrand\s*\(', code_no_comments))
    details.append(
        CheckDetail(
            check_name="no_srand_function",
            passed=not uses_srand,
            expected="srand() must NOT be used",
            actual="srand() detected!" if uses_srand else "srand() not used (correct)",
            check_type="constraint",
        )
    )

    # Check 4: Does NOT use sys_rand_get (non-cryptographic Zephyr RNG)
    uses_sys_rand = "sys_rand_get" in generated_code and "sys_csrand_get" not in generated_code
    # Allow sys_rand_get only if csrand is also present (defensive check)
    uses_only_insecure = "sys_rand_get" in generated_code and not has_csrand and not has_psa_random
    details.append(
        CheckDetail(
            check_name="no_sys_rand_get",
            passed=not uses_only_insecure,
            expected="sys_rand_get() must NOT be sole RNG (non-cryptographic)",
            actual="sys_rand_get() used without CSPRNG!" if uses_only_insecure else "correct",
            check_type="constraint",
        )
    )

    # Check 5: Return value checked
    has_ret_check = "< 0" in generated_code or "!= 0" in generated_code or "PSA_SUCCESS" in generated_code
    details.append(
        CheckDetail(
            check_name="return_value_checked",
            passed=has_ret_check,
            expected="Return value of RNG function checked for errors",
            actual="present" if has_ret_check else "missing (errors ignored)",
            check_type="constraint",
        )
    )

    # Check 6: At least 32 bytes generated
    import re
    # Look for buffer size definition >= 32 or literal >= 32 in csrand_get call
    size_matches = re.findall(r'\b(\d+)\b', generated_code)
    has_32_bytes = any(int(m) >= 32 for m in size_matches)
    details.append(
        CheckDetail(
            check_name="minimum_32_bytes",
            passed=has_32_bytes,
            expected="At least 32 bytes of random data generated",
            actual="32+ byte value found" if has_32_bytes else "buffer may be too small",
            check_type="constraint",
        )
    )

    return details
