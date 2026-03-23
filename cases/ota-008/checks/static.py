"""Static analysis checks for OTA rollback with timeout."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate OTA rollback timeout code structure."""
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

    has_reboot_h = "sys/reboot.h" in generated_code
    details.append(
        CheckDetail(
            check_name="reboot_header",
            passed=has_reboot_h,
            expected="zephyr/sys/reboot.h included",
            actual="present" if has_reboot_h else "missing",
            check_type="exact_match",
        )
    )

    has_confirmed_check = "boot_is_img_confirmed" in generated_code
    details.append(
        CheckDetail(
            check_name="img_confirmed_check",
            passed=has_confirmed_check,
            expected="boot_is_img_confirmed() called to detect newly swapped image",
            actual="present" if has_confirmed_check else "missing",
            check_type="exact_match",
        )
    )

    has_write_confirmed = "boot_write_img_confirmed" in generated_code
    details.append(
        CheckDetail(
            check_name="write_img_confirmed",
            passed=has_write_confirmed,
            expected="boot_write_img_confirmed() called to confirm image",
            actual="present" if has_write_confirmed else "missing",
            check_type="exact_match",
        )
    )

    has_sys_reboot = "sys_reboot" in generated_code
    details.append(
        CheckDetail(
            check_name="sys_reboot_for_rollback",
            passed=has_sys_reboot,
            expected="sys_reboot() called on timeout to trigger MCUboot rollback",
            actual="present" if has_sys_reboot else "missing (rollback never happens!)",
            check_type="exact_match",
        )
    )

    has_timeout = (
        "CONFIRM_TIMEOUT" in generated_code
        or "timeout" in generated_code.lower()
        or "deadline" in generated_code
        or "k_uptime" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="timeout_mechanism",
            passed=has_timeout,
            expected="Timeout mechanism defined (CONFIRM_TIMEOUT_MS, deadline, k_uptime)",
            actual="present" if has_timeout else "missing (no timeout — rollback never happens!)",
            check_type="exact_match",
        )
    )

    has_self_test = "self_test" in generated_code or "selftest" in generated_code
    details.append(
        CheckDetail(
            check_name="self_test_function",
            passed=has_self_test,
            expected="self_test() function implemented",
            actual="present" if has_self_test else "missing",
            check_type="exact_match",
        )
    )

    return details
