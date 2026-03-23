"""Static analysis checks for DFU target flash write."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DFU target code structure."""
    details: list[CheckDetail] = []

    has_dfu_target_h = "dfu/dfu_target.h" in generated_code
    details.append(
        CheckDetail(
            check_name="dfu_target_header",
            passed=has_dfu_target_h,
            expected="zephyr/dfu/dfu_target.h included",
            actual="present" if has_dfu_target_h else "missing",
            check_type="exact_match",
        )
    )

    has_init = "dfu_target_init" in generated_code
    details.append(
        CheckDetail(
            check_name="dfu_target_init",
            passed=has_init,
            expected="dfu_target_init() called",
            actual="present" if has_init else "missing",
            check_type="exact_match",
        )
    )

    has_write = "dfu_target_write" in generated_code
    details.append(
        CheckDetail(
            check_name="dfu_target_write",
            passed=has_write,
            expected="dfu_target_write() called",
            actual="present" if has_write else "missing",
            check_type="exact_match",
        )
    )

    has_done = "dfu_target_done" in generated_code
    details.append(
        CheckDetail(
            check_name="dfu_target_done",
            passed=has_done,
            expected="dfu_target_done() called",
            actual="present" if has_done else "missing",
            check_type="exact_match",
        )
    )

    has_mcuboot_type = "DFU_TARGET_IMAGE_TYPE_MCUBOOT" in generated_code
    details.append(
        CheckDetail(
            check_name="mcuboot_image_type",
            passed=has_mcuboot_type,
            expected="DFU_TARGET_IMAGE_TYPE_MCUBOOT used",
            actual="present" if has_mcuboot_type else "missing or wrong type",
            check_type="exact_match",
        )
    )

    has_reboot = "sys_reboot" in generated_code
    details.append(
        CheckDetail(
            check_name="sys_reboot_after_dfu",
            passed=has_reboot,
            expected="sys_reboot() called after DFU complete",
            actual="present" if has_reboot else "missing",
            check_type="exact_match",
        )
    )

    return details
