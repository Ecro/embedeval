"""Behavioral checks for PSA Protected Storage."""

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
    """Validate PSA Protected Storage behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: init before ps_set (correct ordering)
    init_pos = generated_code.find("psa_crypto_init")
    set_pos = generated_code.find("psa_ps_set")
    details.append(
        CheckDetail(
            check_name="init_before_ps_set",
            passed=init_pos != -1 and set_pos != -1 and init_pos < set_pos,
            expected="psa_crypto_init() before psa_ps_set()",
            actual="correct order" if (init_pos != -1 and set_pos != -1 and init_pos < set_pos) else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: ps_set before ps_get (must store before retrieve)
    get_pos = generated_code.find("psa_ps_get")
    details.append(
        CheckDetail(
            check_name="ps_set_before_ps_get",
            passed=set_pos != -1 and get_pos != -1 and set_pos < get_pos,
            expected="psa_ps_set() before psa_ps_get()",
            actual="correct order" if (set_pos != -1 and get_pos != -1 and set_pos < get_pos) else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: actual_length variable captured from psa_ps_get
    # LLM failure: no size output variable, can't detect truncation
    has_actual_len = bool(
        re.search(r'\b\w*(actual|out|result)\w*_len\w*\b|\bactual_length\b|\bout_len\b', generated_code)
        or re.search(r'psa_ps_get\s*\([^)]*&', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="actual_length_captured",
            passed=has_actual_len,
            expected="actual_length output parameter captured from psa_ps_get",
            actual="present" if has_actual_len else "missing (buffer overrun risk)",
            check_type="constraint",
        )
    )

    # Check 4: Retrieved data verified against original (memcmp)
    has_memcmp = "memcmp" in generated_code
    details.append(
        CheckDetail(
            check_name="data_verified_after_get",
            passed=has_memcmp,
            expected="memcmp() verifies retrieved data matches stored data",
            actual="present" if has_memcmp else "missing (no data integrity check)",
            check_type="constraint",
        )
    )

    # Check 5: Result printed
    has_print = "printk" in generated_code or "printf" in generated_code
    details.append(
        CheckDetail(
            check_name="result_printed",
            passed=has_print,
            expected="Result printed (PS OK / PS FAILED)",
            actual="present" if has_print else "missing",
            check_type="constraint",
        )
    )

    # Check 6: PSA_STORAGE_FLAG_NONE used (or a valid flag constant)
    has_storage_flag = (
        "PSA_STORAGE_FLAG_NONE" in generated_code
        or "PSA_STORAGE_FLAG_" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="storage_flag_specified",
            passed=has_storage_flag,
            expected="PSA_STORAGE_FLAG_NONE or valid flag in psa_ps_set",
            actual="present" if has_storage_flag else "missing (0 used as flag?)",
            check_type="constraint",
        )
    )

    # Check 7: Error path handles failures — returns early on failure
    # LLM failure: ignoring psa_ps_set failure and proceeding to psa_ps_get
    error_blocks = _extract_psa_error_blocks(generated_code)
    has_error_handling = len(error_blocks) > 0 and any(
        "return" in block for block in error_blocks
    )
    details.append(
        CheckDetail(
            check_name="error_paths_return_early",
            passed=has_error_handling,
            expected="Error paths return early on psa_ps_set/get failure",
            actual="present" if has_error_handling else "missing (may continue after failure)",
            check_type="constraint",
        )
    )

    # Check 8: No rand()/srand() in storage security code
    has_rand = bool(re.search(r'\brand\s*\(|\bsrand\s*\(', stripped))
    details.append(
        CheckDetail(
            check_name="no_insecure_rand",
            passed=not has_rand,
            expected="No rand()/srand() in security storage code",
            actual="clean" if not has_rand else "rand()/srand() found",
            check_type="constraint",
        )
    )

    return details
