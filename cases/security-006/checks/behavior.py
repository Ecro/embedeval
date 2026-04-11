"""Behavioral checks for Secure Key Storage with Anti-Tamper."""

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
    """Validate non-extractable key behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: psa_crypto_init before psa_import_key (correct ordering)
    init_pos = generated_code.find("psa_crypto_init")
    import_pos = generated_code.find("psa_import_key")
    init_before_import = init_pos != -1 and import_pos != -1 and init_pos < import_pos
    details.append(
        CheckDetail(
            check_name="init_before_import",
            passed=init_before_import,
            expected="psa_crypto_init() before psa_import_key()",
            actual="correct order" if init_before_import else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: psa_export_key called to verify denial (anti-tamper verification)
    has_export_call = "psa_export_key" in generated_code
    details.append(
        CheckDetail(
            check_name="export_denial_verified",
            passed=has_export_call,
            expected="psa_export_key() called to verify export is denied",
            actual="present"
            if has_export_call
            else "missing (no verification of non-extractability)",
            check_type="constraint",
        )
    )

    # Check 3: PSA_ERROR_NOT_PERMITTED checked (correct denial status)
    has_not_permitted = "PSA_ERROR_NOT_PERMITTED" in generated_code
    details.append(
        CheckDetail(
            check_name="not_permitted_checked",
            passed=has_not_permitted,
            expected="PSA_ERROR_NOT_PERMITTED checked after psa_export_key()",
            actual="present"
            if has_not_permitted
            else "missing (export denial not detected)",
            check_type="constraint",
        )
    )

    # Check 4: psa_destroy_key called (no key leak)
    has_destroy = "psa_destroy_key" in generated_code
    details.append(
        CheckDetail(
            check_name="key_destroyed",
            passed=has_destroy,
            expected="psa_destroy_key() called to clean up key slot",
            actual="present" if has_destroy else "missing (key slot leak)",
            check_type="constraint",
        )
    )

    # Check 5: Key attributes initialized (PSA_KEY_ATTRIBUTES_INIT)
    has_attrs_init = "PSA_KEY_ATTRIBUTES_INIT" in generated_code
    details.append(
        CheckDetail(
            check_name="attributes_initialized",
            passed=has_attrs_init,
            expected="PSA_KEY_ATTRIBUTES_INIT used to zero-initialize key attributes",
            actual="present"
            if has_attrs_init
            else "missing (uninitialized attributes risk)",
            check_type="constraint",
        )
    )

    # Check 6: Result printed (KEY SECURE or equivalent)
    has_print = "printk" in generated_code or "printf" in generated_code
    details.append(
        CheckDetail(
            check_name="result_printed",
            passed=has_print,
            expected="Result printed (KEY SECURE / KEY EXPOSED)",
            actual="present" if has_print else "missing",
            check_type="constraint",
        )
    )

    # Check 7: Key destruction present (key slot cleaned up after use).
    # LLM failure: importing key but never calling psa_destroy_key, leaking key slot.
    # The reference calls psa_destroy_key unconditionally at end (after export check).
    # We verify it's present AND comes after the import (i.e., not a forward declaration).
    destroy_pos = generated_code.rfind("psa_destroy_key")
    error_path_destroy = has_destroy and import_pos != -1 and destroy_pos > import_pos
    details.append(
        CheckDetail(
            check_name="error_path_key_destroyed",
            passed=error_path_destroy,
            expected="psa_destroy_key() present to clean up key slot after use",
            actual="key cleanup present"
            if error_path_destroy
            else "key may leak on error",
            check_type="constraint",
        )
    )

    # Check 8: No rand()/srand() or insecure patterns in security code
    has_rand = bool(re.search(r"\brand\s*\(|\bsrand\s*\(", stripped))
    has_ecb = bool(re.search(r"\bPSA_ALG_ECB\b(?!_NO_PADDING)", stripped))
    details.append(
        CheckDetail(
            check_name="no_insecure_patterns",
            passed=not has_rand and not has_ecb,
            expected="No rand()/srand() or ECB mode in security code",
            actual="clean"
            if not (has_rand or has_ecb)
            else f"insecure: rand={has_rand}, ECB={has_ecb}",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(
        generated_code, skip_platforms=["Linux_Userspace"]
    )
    details.append(
        CheckDetail(
            check_name="no_cross_platform_apis",
            passed=len(cross_plat) == 0,
            expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
            actual="clean"
            if not cross_plat
            else f"found: {[a for a, _ in cross_plat]}",
            check_type="constraint",
        )
    )

    return details
