"""Behavioral checks for PSA HKDF key derivation."""

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
    """Validate HKDF key derivation ordering and behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: Correct HKDF input ordering: SALT before SECRET before INFO
    # LLM failure: wrong order causes PSA_ERROR_BAD_STATE at runtime
    salt_pos = generated_code.find("PSA_KEY_DERIVATION_INPUT_SALT")
    secret_pos = generated_code.find("PSA_KEY_DERIVATION_INPUT_SECRET")
    info_pos = generated_code.find("PSA_KEY_DERIVATION_INPUT_INFO")
    correct_order = (
        salt_pos != -1 and secret_pos != -1 and info_pos != -1
        and salt_pos < secret_pos < info_pos
    )
    details.append(
        CheckDetail(
            check_name="hkdf_input_order_correct",
            passed=correct_order,
            expected="SALT -> SECRET -> INFO input order",
            actual="correct" if correct_order else "wrong order or missing steps",
            check_type="constraint",
        )
    )

    # Check 2: psa_key_derivation_output_bytes called (actual key extraction)
    has_output = "psa_key_derivation_output_bytes" in generated_code
    details.append(
        CheckDetail(
            check_name="output_bytes_called",
            passed=has_output,
            expected="psa_key_derivation_output_bytes() called",
            actual="present" if has_output else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: setup called before inputs (operation initialized)
    setup_pos = generated_code.find("psa_key_derivation_setup")
    details.append(
        CheckDetail(
            check_name="setup_before_inputs",
            passed=setup_pos != -1 and salt_pos != -1 and setup_pos < salt_pos,
            expected="psa_key_derivation_setup() before input steps",
            actual="correct" if (setup_pos != -1 and salt_pos != -1 and setup_pos < salt_pos) else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 4: output_bytes appears before the FINAL abort call
    output_pos = generated_code.find("psa_key_derivation_output_bytes")
    last_abort_pos = generated_code.rfind("psa_key_derivation_abort")
    details.append(
        CheckDetail(
            check_name="output_before_final_abort",
            passed=output_pos != -1 and last_abort_pos != -1 and output_pos < last_abort_pos,
            expected="psa_key_derivation_output_bytes() before final psa_key_derivation_abort()",
            actual="correct" if (output_pos != -1 and last_abort_pos != -1 and output_pos < last_abort_pos) else "wrong order or missing",
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

    # Check 6: Derived key output buffer declared (at least 16 bytes)
    sizes = [int(x) for x in re.findall(r"\b(\d+)\b", generated_code)]
    has_adequate_key = (
        any(s >= 16 for s in sizes)
        or "DERIVED_KEY_SIZE" in generated_code
        or "KEY_LEN" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="derived_key_buffer_adequate",
            passed=has_adequate_key,
            expected="Derived key output buffer >= 16 bytes",
            actual="adequate" if has_adequate_key else "buffer may be too small",
            check_type="constraint",
        )
    )

    # Check 7: Abort called in error paths (no operation leak)
    # LLM failure: returning early on error without aborting the derivation operation
    error_blocks = _extract_psa_error_blocks(generated_code)
    error_blocks_abort = any("psa_key_derivation_abort" in block for block in error_blocks)
    details.append(
        CheckDetail(
            check_name="abort_in_error_paths",
            passed=error_blocks_abort,
            expected="psa_key_derivation_abort() in error paths (no operation leak)",
            actual="abort in error paths" if error_blocks_abort else "derivation operation may leak on error",
            check_type="constraint",
        )
    )

    # Check 8: No rand()/srand() in key derivation code
    has_rand = bool(re.search(r"\brand\s*\(|\bsrand\s*\(", stripped))
    details.append(
        CheckDetail(
            check_name="no_insecure_rand",
            passed=not has_rand,
            expected="No rand()/srand() in key derivation code",
            actual="clean" if not has_rand else "rand()/srand() found — insecure",
            check_type="constraint",
        )
    )

    return details
