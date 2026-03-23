"""Behavioral checks for PSA Crypto random number generation."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate RNG behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: init before generate (correct ordering)
    init_pos = generated_code.find("psa_crypto_init")
    rng_pos = generated_code.find("psa_generate_random")
    details.append(
        CheckDetail(
            check_name="init_before_generate",
            passed=init_pos != -1 and rng_pos != -1 and init_pos < rng_pos,
            expected="psa_crypto_init() before psa_generate_random()",
            actual="correct order" if (init_pos != -1 and rng_pos != -1 and init_pos < rng_pos) else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Buffer initialized to zero before use (proves RNG actually wrote data)
    has_memset_zero = (
        'memset' in generated_code and '0' in generated_code
        or '{0}' in generated_code
        or '= {0}' in generated_code
    )
    details.append(
        CheckDetail(
            check_name="buffer_zeroed_before_rng",
            passed=has_memset_zero,
            expected="Buffer initialized to zero before psa_generate_random",
            actual="zeroed" if has_memset_zero else "not zeroed (cannot verify RNG output)",
            check_type="constraint",
        )
    )

    # Check 3: Non-zero check performed on result
    import re
    has_nonzero_check = bool(
        re.search(r'!=\s*0\b|>\s*0\b', generated_code)
        or "nonzero" in generated_code.lower()
        or "non_zero" in generated_code.lower()
        or "non-zero" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="nonzero_verification",
            passed=has_nonzero_check,
            expected="At least one non-zero byte check on RNG output",
            actual="check found" if has_nonzero_check else "no verification of RNG output",
            check_type="constraint",
        )
    )

    # Check 4: Result printed
    has_print = "printk" in generated_code or "printf" in generated_code
    details.append(
        CheckDetail(
            check_name="result_printed",
            passed=has_print,
            expected="Result printed (RNG OK / RNG FAILED)",
            actual="present" if has_print else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Buffer size is at least 16 bytes (meaningful RNG test)
    import re as re2
    sizes = [int(x) for x in re2.findall(r'\b(\d+)\b', generated_code)]
    has_adequate_size = any(s >= 16 for s in sizes) or "RNG_BUF_SIZE" in generated_code
    details.append(
        CheckDetail(
            check_name="buffer_size_adequate",
            passed=has_adequate_size,
            expected="RNG buffer >= 16 bytes",
            actual="adequate" if has_adequate_size else "buffer may be too small",
            check_type="constraint",
        )
    )

    return details
