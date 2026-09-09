"""Behavioral checks for HMAC-SHA256 Message Authentication."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    scoped_contains,
    strip_comments,
)
from embedeval.models import CheckDetail
from embedeval.check_utils import find_in_code


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
    """Validate HMAC-SHA256 behavioral flow properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: init before mac_sign_setup (correct ordering)
    init_pos = find_in_code(generated_code, "psa_crypto_init")
    setup_pos = find_in_code(generated_code, "psa_mac_sign_setup")
    init_before_setup = init_pos != -1 and setup_pos != -1 and init_pos < setup_pos
    details.append(
        CheckDetail(
            check_name="init_before_mac_setup",
            passed=init_before_setup,
            expected="psa_crypto_init() before psa_mac_sign_setup()",
            actual="correct order" if init_before_setup else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: setup -> update -> finish ordering
    update_pos = find_in_code(generated_code, "psa_mac_update")
    finish_pos = find_in_code(generated_code, "psa_mac_sign_finish")
    correct_order = (
        setup_pos != -1
        and update_pos != -1
        and finish_pos != -1
        and setup_pos < update_pos < finish_pos
    )
    details.append(
        CheckDetail(
            check_name="mac_setup_update_finish_order",
            passed=correct_order,
            expected="psa_mac_sign_setup -> psa_mac_update -> psa_mac_sign_finish",
            actual="correct order" if correct_order else "wrong order or missing steps",
            check_type="constraint",
        )
    )

    # Check 3: MAC operation initialized (PSA_MAC_OPERATION_INIT)
    has_op_init = scoped_contains(generated_code, 'PSA_MAC_OPERATION_INIT', scope='code_only')
    details.append(
        CheckDetail(
            check_name="mac_operation_initialized",
            passed=has_op_init,
            expected="psa_mac_operation_t initialized with PSA_MAC_OPERATION_INIT",
            actual="present" if has_op_init else "missing (uninitialized operation risk)",
            check_type="constraint",
        )
    )

    # Check 4: PSA_KEY_TYPE_HMAC used for the key
    has_hmac_key_type = scoped_contains(generated_code, 'PSA_KEY_TYPE_HMAC', scope='code_only')
    details.append(
        CheckDetail(
            check_name="hmac_key_type",
            passed=has_hmac_key_type,
            expected="PSA_KEY_TYPE_HMAC used for HMAC key import",
            actual="present" if has_hmac_key_type else "missing (wrong key type)",
            check_type="constraint",
        )
    )

    # Check 5: Key destroyed after use
    has_destroy = scoped_contains(generated_code, 'psa_destroy_key', scope='code_only')
    details.append(
        CheckDetail(
            check_name="key_destroyed",
            passed=has_destroy,
            expected="psa_destroy_key() called to release key slot",
            actual="present" if has_destroy else "missing (key slot leak)",
            check_type="constraint",
        )
    )

    # Check 6: Result printed
    has_print = scoped_contains(generated_code, 'printk', scope='code_only') or scoped_contains(generated_code, 'printf', scope='code_only')
    details.append(
        CheckDetail(
            check_name="result_printed",
            passed=has_print,
            expected="MAC result or error printed",
            actual="present" if has_print else "missing",
            check_type="constraint",
        )
    )

    # Check 7: Error paths call psa_destroy_key (no key slot leak)
    # LLM failure: hitting error in mac_update, not cleaning up the key slot
    error_blocks = _extract_psa_error_blocks(generated_code)
    error_has_key_cleanup = any("psa_destroy_key" in block for block in error_blocks)
    details.append(
        CheckDetail(
            check_name="error_path_key_destroyed",
            passed=error_has_key_cleanup,
            expected="psa_destroy_key() called in MAC operation error paths",
            actual="key cleanup in error path" if error_has_key_cleanup else "key may leak on error",
            check_type="constraint",
        )
    )

    # Check 8: psa_mac_abort called in error paths (operation cleanup)
    # LLM failure: not aborting the MAC operation on error, leaving it in bad state
    error_has_mac_abort = any("psa_mac_abort" in block for block in error_blocks)
    details.append(
        CheckDetail(
            check_name="mac_abort_in_error_paths",
            passed=error_has_mac_abort,
            expected="psa_mac_abort() called in error paths to clean up MAC operation",
            actual="abort in error path" if error_has_mac_abort else "MAC operation may leak on error",
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
