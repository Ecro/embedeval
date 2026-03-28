"""Behavioral checks for PSA ECDSA P-256 Key Pair Generation."""

import re

from embedeval.check_utils import (check_no_cross_platform_apis,
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
    """Validate ECDSA P-256 key generation behavioral flow."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: init before generate
    init_pos = generated_code.find("psa_crypto_init")
    generate_pos = generated_code.find("psa_generate_key")
    init_before_gen = init_pos != -1 and generate_pos != -1 and init_pos < generate_pos
    details.append(
        CheckDetail(
            check_name="init_before_generate",
            passed=init_before_gen,
            expected="psa_crypto_init() before psa_generate_key()",
            actual="correct order" if init_before_gen else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: generate before export_public_key
    export_pub_pos = generated_code.find("psa_export_public_key")
    gen_before_export = (
        generate_pos != -1
        and export_pub_pos != -1
        and generate_pos < export_pub_pos
    )
    details.append(
        CheckDetail(
            check_name="generate_before_export_public",
            passed=gen_before_export,
            expected="psa_generate_key() before psa_export_public_key()",
            actual="correct order" if gen_before_export else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: Key attributes initialized
    has_attrs_init = "PSA_KEY_ATTRIBUTES_INIT" in generated_code
    details.append(
        CheckDetail(
            check_name="attributes_initialized",
            passed=has_attrs_init,
            expected="PSA_KEY_ATTRIBUTES_INIT used",
            actual="present" if has_attrs_init else "missing",
            check_type="constraint",
        )
    )

    # Check 4: Key destroyed after use
    has_destroy = "psa_destroy_key" in generated_code
    details.append(
        CheckDetail(
            check_name="key_destroyed",
            passed=has_destroy,
            expected="psa_destroy_key() called to release key slot",
            actual="present" if has_destroy else "missing (key slot leak)",
            check_type="constraint",
        )
    )

    # Check 5: PSA_SUCCESS used for return value checks
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

    # Check 6: Result printed
    has_print = "printk" in generated_code or "printf" in generated_code
    details.append(
        CheckDetail(
            check_name="result_printed",
            passed=has_print,
            expected="Result or key info printed",
            actual="present" if has_print else "missing",
            check_type="constraint",
        )
    )

    # Check 7: Error paths call psa_destroy_key (key slot cleanup)
    # LLM failure: generating key, failing on export, leaking the key slot
    error_blocks = _extract_psa_error_blocks(generated_code)
    error_path_destroy = any("psa_destroy_key" in block for block in error_blocks)
    details.append(
        CheckDetail(
            check_name="error_path_key_destroyed",
            passed=error_path_destroy,
            expected="psa_destroy_key() in error paths after successful key generation",
            actual="key cleanup in error path" if error_path_destroy else "key may leak on export failure",
            check_type="constraint",
        )
    )

    # Check 8: No rand()/srand() or ECB mode in ECDSA code
    has_rand = bool(re.search(r'\brand\s*\(|\bsrand\s*\(', stripped))
    has_ecb = bool(re.search(r'\bPSA_ALG_ECB\b(?!_NO_PADDING)', stripped))
    details.append(
        CheckDetail(
            check_name="no_insecure_patterns",
            passed=not has_rand and not has_ecb,
            expected="No rand()/srand() or ECB mode in ECDSA code",
            actual="clean" if not (has_rand or has_ecb) else f"insecure: rand={has_rand}, ECB={has_ecb}",
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
