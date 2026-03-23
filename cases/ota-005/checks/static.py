"""Static analysis checks for full OTA flow with rollback safety."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate full OTA state machine code structure."""
    details: list[CheckDetail] = []

    has_mcuboot_h = "dfu/mcuboot.h" in generated_code
    details.append(
        CheckDetail(
            check_name="mcuboot_header",
            passed=has_mcuboot_h,
            expected="zephyr/dfu/mcuboot.h included",
            actual="present" if has_mcuboot_h else "missing",
            check_type="exact_match",
        )
    )

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

    # Check all five state enum values are present
    states = ["OTA_IDLE", "OTA_DOWNLOADING", "OTA_VERIFYING", "OTA_REBOOTING", "OTA_CONFIRMING"]
    all_states = all(s in generated_code for s in states)
    details.append(
        CheckDetail(
            check_name="all_five_states",
            passed=all_states,
            expected="All 5 OTA states defined: IDLE, DOWNLOADING, VERIFYING, REBOOTING, CONFIRMING",
            actual="all present" if all_states else f"missing: {[s for s in states if s not in generated_code]}",
            check_type="exact_match",
        )
    )

    has_init = "dfu_target_init" in generated_code
    details.append(
        CheckDetail(
            check_name="dfu_target_init",
            passed=has_init,
            expected="dfu_target_init() called in download phase",
            actual="present" if has_init else "missing",
            check_type="exact_match",
        )
    )

    has_done = "dfu_target_done" in generated_code
    details.append(
        CheckDetail(
            check_name="dfu_target_done",
            passed=has_done,
            expected="dfu_target_done() called in verify phase",
            actual="present" if has_done else "missing",
            check_type="exact_match",
        )
    )

    has_confirmed = "boot_is_img_confirmed" in generated_code
    details.append(
        CheckDetail(
            check_name="img_confirmed_check",
            passed=has_confirmed,
            expected="boot_is_img_confirmed() checked in confirm phase",
            actual="present" if has_confirmed else "missing",
            check_type="exact_match",
        )
    )

    has_write_confirmed = "boot_write_img_confirmed" in generated_code
    details.append(
        CheckDetail(
            check_name="write_img_confirmed",
            passed=has_write_confirmed,
            expected="boot_write_img_confirmed() called after self-test",
            actual="present" if has_write_confirmed else "missing",
            check_type="exact_match",
        )
    )

    has_reboot = "sys_reboot" in generated_code
    details.append(
        CheckDetail(
            check_name="sys_reboot",
            passed=has_reboot,
            expected="sys_reboot() called in reboot phase",
            actual="present" if has_reboot else "missing",
            check_type="exact_match",
        )
    )

    return details
