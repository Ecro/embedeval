"""Behavioral checks for OTA image hash verification."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis, check_return_after_error


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate OTA hash verification behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Hash computed BEFORE dfu_target_write (the critical ordering rule)
    # (LLM failure: writing to flash first, then verifying — too late!)
    hash_pos = generated_code.find("psa_hash_compute")
    write_pos = generated_code.find("dfu_target_write")
    details.append(
        CheckDetail(
            check_name="hash_before_flash_write",
            passed=hash_pos != -1 and write_pos != -1 and hash_pos < write_pos,
            expected="psa_hash_compute() called BEFORE dfu_target_write()",
            actual="correct order" if (hash_pos != -1 and write_pos != -1 and hash_pos < write_pos)
                   else "WRONG ORDER or missing — writing flash before verifying hash!",
            check_type="constraint",
        )
    )

    # Check 2: Hash comparison present BEFORE dfu_target_write
    # (LLM failure: computing hash but not comparing before writing)
    memcmp_pos = generated_code.find("memcmp")
    details.append(
        CheckDetail(
            check_name="hash_comparison_before_write",
            passed=memcmp_pos != -1 and write_pos != -1 and memcmp_pos < write_pos,
            expected="memcmp() hash comparison before dfu_target_write()",
            actual="correct" if (memcmp_pos != -1 and write_pos != -1 and memcmp_pos < write_pos)
                   else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 3: Abort path when hash mismatches (no flash write on bad hash)
    # (LLM failure: ignoring hash mismatch result, writing anyway)
    # Note: "return" in generated_code is always true for any C code — use
    # check_return_after_error to verify that error blocks contain actual returns.
    has_abort_path = (
        "mismatch" in generated_code.lower()
        or "hash failed" in generated_code.lower()
        or "aborting" in generated_code.lower()
        or ("memcmp" in generated_code and check_return_after_error(generated_code))
    )
    details.append(
        CheckDetail(
            check_name="abort_on_hash_mismatch",
            passed=has_abort_path,
            expected="Explicit abort / early return when hash does not match",
            actual="present" if has_abort_path else "missing (no abort path — writes even with bad hash!)",
            check_type="constraint",
        )
    )

    # Check 4: psa_hash_compute used — NOT a custom SHA-256 implementation
    # (LLM failure: hand-rolling SHA-256 instead of using PSA API)
    has_psa_api = "psa_hash_compute" in generated_code
    has_custom_sha = (
        "sha256_init" in generated_code.lower()
        or "sha256_update" in generated_code.lower()
        or "sha256_transform" in generated_code.lower()
        or "sha256_process" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="uses_psa_not_custom_sha",
            passed=has_psa_api and not has_custom_sha,
            expected="psa_hash_compute() used (not custom SHA-256 implementation)",
            actual="correct" if (has_psa_api and not has_custom_sha)
                   else "wrong — custom SHA-256 or missing PSA call",
            check_type="constraint",
        )
    )

    # Check 5: dfu_target_done called to finalize (or abort) flash write
    has_dfu_done = "dfu_target_done" in generated_code
    details.append(
        CheckDetail(
            check_name="dfu_target_done_called",
            passed=has_dfu_done,
            expected="dfu_target_done() called to finalize or abort DFU target",
            actual="present" if has_dfu_done else "missing (DFU session never closed)",
            check_type="constraint",
        )
    )

    # Check 6: psa_hash_compute return value checked (PSA_SUCCESS)
    # (LLM failure: calling psa_hash_compute but not checking if it succeeded)
    psa_ret_checked = (
        "psa_hash_compute" in generated_code
        and ("PSA_SUCCESS" in generated_code or "!= 0" in generated_code or "status" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="psa_hash_return_checked",
            passed=psa_ret_checked,
            expected="psa_hash_compute() return value checked (PSA_SUCCESS or != 0)",
            actual="present" if psa_ret_checked else "missing (hash error ignored — invalid hash used!)",
            check_type="constraint",
        )
    )

    # Check 7: dfu_target_done(false) on hash mismatch — rollback path
    # (LLM failure: only happy path — no abort if hash verification fails)
    has_done_false = "dfu_target_done(false)" in generated_code
    details.append(
        CheckDetail(
            check_name="dfu_done_false_on_mismatch",
            passed=has_done_false,
            expected="dfu_target_done(false) called on hash mismatch to abort DFU",
            actual="present" if has_done_false else "missing (no rollback on hash failure — corrupt image written!)",
            check_type="constraint",
        )
    )

    # Check 8: Hash length verified (output length matches 32 bytes for SHA-256)
    # (LLM failure: not checking that hash_len == 32 after psa_hash_compute)
    has_len_check = (
        "hash_len" in generated_code
        or "32" in generated_code
        or "PSA_HASH_LENGTH" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="hash_length_verified",
            passed=has_len_check,
            expected="Hash output length verified (32 bytes for SHA-256)",
            actual="present" if has_len_check else "missing (truncated hash may pass comparison!)",
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
