"""Behavioral checks for PSA Crypto random number generation."""

import re

from embedeval.check_utils import (
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
    """Validate RNG behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

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
        "memset" in generated_code and "0" in generated_code
        or "{0}" in generated_code
        or "= {0}" in generated_code
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
    has_nonzero_check = bool(
        re.search(r"!=\s*0\b|>\s*0\b", generated_code)
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
    sizes = [int(x) for x in re.findall(r"\b(\d+)\b", generated_code)]
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

    # Check 6: No rand()/srand() used (insecure PRNG, not cryptographic)
    # LLM failure: using C stdlib rand() instead of PSA CSPRNG
    has_rand = bool(re.search(r"\brand\s*\(|\bsrand\s*\(", stripped))
    details.append(
        CheckDetail(
            check_name="no_insecure_rand",
            passed=not has_rand,
            expected="No rand()/srand() — use psa_generate_random() for security",
            actual="clean" if not has_rand else "rand()/srand() found — insecure PRNG",
            check_type="constraint",
        )
    )

    # Check 7: PSA return value stored and checked (not silently discarded)
    # LLM failure: calling psa_generate_random without checking return value
    has_return_check = bool(re.search(r"(status|ret|rc)\s*=\s*psa_generate_random", generated_code))
    details.append(
        CheckDetail(
            check_name="rng_return_value_checked",
            passed=has_return_check,
            expected="psa_generate_random() return value stored and checked",
            actual="present" if has_return_check else "return value may be discarded",
            check_type="constraint",
        )
    )

    # Check 8: Error path handled (failure message printed when RNG fails)
    # LLM failure: ignoring psa_generate_random failure, using uninitialized buffer
    error_blocks = _extract_psa_error_blocks(generated_code)
    has_error_print = any(
        "printk" in block or "printf" in block
        for block in error_blocks
    )
    details.append(
        CheckDetail(
            check_name="error_path_handled",
            passed=has_error_print,
            expected="Error path prints failure message when psa_generate_random fails",
            actual="present" if has_error_print else "missing (silent failure on error)",
            check_type="constraint",
        )
    )

    return details
