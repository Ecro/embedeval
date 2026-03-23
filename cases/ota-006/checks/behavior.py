"""Behavioral checks for OTA image hash verification."""

from embedeval.models import CheckDetail


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
    has_abort_path = (
        "mismatch" in generated_code.lower()
        or "hash failed" in generated_code.lower()
        or "aborting" in generated_code.lower()
        or ("memcmp" in generated_code and "return" in generated_code)
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

    return details
