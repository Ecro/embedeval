"""Static analysis checks for differential (delta) OTA patch application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate delta OTA patch code structure."""
    details: list[CheckDetail] = []

    has_crc_h = "zephyr/sys/crc.h" in generated_code
    details.append(
        CheckDetail(
            check_name="crc_header",
            passed=has_crc_h,
            expected="zephyr/sys/crc.h included",
            actual="present" if has_crc_h else "missing",
            check_type="exact_match",
        )
    )

    has_dfu_target = "dfu/dfu_target.h" in generated_code
    details.append(
        CheckDetail(
            check_name="dfu_target_header",
            passed=has_dfu_target,
            expected="zephyr/dfu/dfu_target.h included",
            actual="present" if has_dfu_target else "missing",
            check_type="exact_match",
        )
    )

    has_crc32 = "crc32_ieee" in generated_code
    details.append(
        CheckDetail(
            check_name="crc32_ieee_used",
            passed=has_crc32,
            expected="crc32_ieee() used for patch integrity check",
            actual="present" if has_crc32 else "missing",
            check_type="exact_match",
        )
    )

    has_verify_patch = (
        "verify_patch" in generated_code
        or "patch_integrity" in generated_code
        or "patch_crc" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="patch_verification_function",
            passed=has_verify_patch,
            expected="Patch integrity verification function implemented",
            actual="present" if has_verify_patch else "missing",
            check_type="exact_match",
        )
    )

    has_apply_patch = "apply_patch" in generated_code
    details.append(
        CheckDetail(
            check_name="apply_patch_function",
            passed=has_apply_patch,
            expected="apply_patch() function implemented",
            actual="present" if has_apply_patch else "missing",
            check_type="exact_match",
        )
    )

    has_dfu_write = "dfu_target_write" in generated_code
    details.append(
        CheckDetail(
            check_name="dfu_target_write_present",
            passed=has_dfu_write,
            expected="dfu_target_write() called to write patched image",
            actual="present" if has_dfu_write else "missing",
            check_type="exact_match",
        )
    )

    has_source_buf = "source_image" in generated_code or "src" in generated_code
    has_target_buf = "target_image" in generated_code or "target" in generated_code
    details.append(
        CheckDetail(
            check_name="source_and_target_buffers",
            passed=has_source_buf and has_target_buf,
            expected="Both source and target image buffers declared",
            actual="present" if (has_source_buf and has_target_buf) else "missing source or target buffer",
            check_type="exact_match",
        )
    )

    return details
