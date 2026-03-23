"""Behavioral checks for differential (delta) OTA patch application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate delta OTA patch behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Patch verification BEFORE apply_patch and BEFORE dfu_target_write
    # (LLM failure: applying patch then verifying — too late if patch is corrupt)
    verify_pos = generated_code.find("verify_patch")
    if verify_pos == -1:
        verify_pos = generated_code.find("crc32_ieee")
    apply_pos = generated_code.find("apply_patch")
    write_pos = generated_code.find("dfu_target_write")
    details.append(
        CheckDetail(
            check_name="verify_before_apply",
            passed=verify_pos != -1 and apply_pos != -1 and verify_pos < apply_pos,
            expected="Patch integrity verified BEFORE apply_patch() is called",
            actual="correct order" if (verify_pos != -1 and apply_pos != -1 and verify_pos < apply_pos)
                   else "WRONG ORDER or missing — applying unverified patch!",
            check_type="constraint",
        )
    )

    # Check 2: apply_patch called BEFORE dfu_target_write
    # (LLM failure: writing source image to flash instead of patched target)
    details.append(
        CheckDetail(
            check_name="apply_before_flash_write",
            passed=apply_pos != -1 and write_pos != -1 and apply_pos < write_pos,
            expected="apply_patch() called BEFORE dfu_target_write() (write patched result)",
            actual="correct" if (apply_pos != -1 and write_pos != -1 and apply_pos < write_pos)
                   else "WRONG ORDER or missing — not writing patched image!",
            check_type="constraint",
        )
    )

    # Check 3: Abort path if patch verification fails
    # (LLM failure: ignoring CRC mismatch return code, continuing to apply)
    has_abort_on_verify_fail = (
        "verify" in generated_code.lower()
        and ("return" in generated_code or "abort" in generated_code.lower())
        and ("!= 0" in generated_code or "< 0" in generated_code or "EBADMSG" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="abort_on_verify_failure",
            passed=has_abort_on_verify_fail,
            expected="Explicit abort / early return when patch integrity check fails",
            actual="present" if has_abort_on_verify_fail
                   else "missing — applies corrupt patch without aborting!",
            check_type="constraint",
        )
    )

    # Check 4: Source + patch -> target pattern (not just copying patch over source)
    # (LLM failure: applying patch in-place to source, corrupting original image)
    has_source = "source_image" in generated_code or ("src" in generated_code and "patch" in generated_code)
    has_target = "target_image" in generated_code or "target" in generated_code
    details.append(
        CheckDetail(
            check_name="source_patch_to_target_pattern",
            passed=has_source and has_target,
            expected="Pattern: source + patch -> separate target buffer",
            actual="correct" if (has_source and has_target)
                   else "missing separate target buffer (may corrupt source image!)",
            check_type="constraint",
        )
    )

    # Check 5: dfu_target_done(false) called on any failure path
    # (LLM failure: leaving DFU target in open state on error)
    has_done_false = "dfu_target_done(false)" in generated_code
    details.append(
        CheckDetail(
            check_name="dfu_done_false_on_error",
            passed=has_done_false,
            expected="dfu_target_done(false) called on error paths to abort DFU session",
            actual="present" if has_done_false else "missing (DFU session left open on error)",
            check_type="constraint",
        )
    )

    return details
