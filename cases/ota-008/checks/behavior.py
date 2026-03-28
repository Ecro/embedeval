"""Behavioral checks for OTA rollback with timeout."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate OTA rollback timeout behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Timer/deadline started AFTER detecting unconfirmed image
    # (LLM failure: no deadline set, or set unconditionally before the check)
    confirmed_pos = generated_code.find("boot_is_img_confirmed")
    deadline_pos = generated_code.find("deadline")
    if deadline_pos == -1:
        deadline_pos = generated_code.find("k_uptime_get")
    details.append(
        CheckDetail(
            check_name="timer_started_after_detection",
            passed=confirmed_pos != -1 and deadline_pos != -1 and confirmed_pos < deadline_pos,
            expected="Deadline/timer set AFTER boot_is_img_confirmed() detects unconfirmed image",
            actual="correct" if (confirmed_pos != -1 and deadline_pos != -1 and confirmed_pos < deadline_pos)
                   else "missing deadline or wrong order",
            check_type="constraint",
        )
    )

    # Check 2: sys_reboot called on timeout — not just printk
    # (LLM failure: printing "timeout" but not actually resetting — MCUboot never rolls back)
    reboot_pos = generated_code.find("sys_reboot")
    timeout_ref_pos = generated_code.lower().find("timeout")
    details.append(
        CheckDetail(
            check_name="reboot_on_timeout",
            passed=reboot_pos != -1 and timeout_ref_pos != -1,
            expected="sys_reboot() called when timeout occurs (not just a log message)",
            actual="correct" if (reboot_pos != -1 and timeout_ref_pos != -1)
                   else "missing — timeout logged but system never resets!",
            check_type="constraint",
        )
    )

    # Check 3: Timeout value is reasonable (between 5s and 300s encoded as ms)
    # (LLM failure: setting 0ms or negative timeout that fires immediately)
    reasonable_timeout = False
    for candidate in ["60000", "30000", "120000", "CONFIRM_TIMEOUT_MS", "timeout"]:
        if candidate in generated_code:
            reasonable_timeout = True
            break
    # Also reject obvious zero-timeout
    has_zero_timeout = (
        "CONFIRM_TIMEOUT_MS 0" in generated_code
        or "TIMEOUT_MS 0" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="reasonable_timeout_value",
            passed=reasonable_timeout and not has_zero_timeout,
            expected="Timeout value is reasonable (5000–300000 ms range or named constant)",
            actual="reasonable" if (reasonable_timeout and not has_zero_timeout)
                   else "missing or zero timeout (never waits for confirmation!)",
            check_type="constraint",
        )
    )

    # Check 4: self_test called before boot_write_img_confirmed
    # (LLM failure: confirming immediately on boot without any self-test)
    self_test_pos = generated_code.find("self_test")
    write_pos = generated_code.find("boot_write_img_confirmed")
    details.append(
        CheckDetail(
            check_name="self_test_before_confirm",
            passed=self_test_pos != -1 and write_pos != -1 and self_test_pos < write_pos,
            expected="self_test() called before boot_write_img_confirmed()",
            actual="correct" if (self_test_pos != -1 and write_pos != -1 and self_test_pos < write_pos)
                   else "missing self-test or confirming before testing!",
            check_type="constraint",
        )
    )

    # Check 5: boot_is_img_confirmed checked first (conditional confirmation)
    # (LLM failure: unconditionally calling boot_write_img_confirmed every boot)
    has_conditional = (
        "boot_is_img_confirmed" in generated_code
        and "if" in generated_code
        and "boot_write_img_confirmed" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="conditional_confirmation",
            passed=has_conditional,
            expected="boot_write_img_confirmed() only called conditionally after check",
            actual="conditional (correct)" if has_conditional
                   else "unconditional — confirms on every boot!",
            check_type="constraint",
        )
    )

    # Check 6: self_test return value checked before confirming
    # (LLM failure: calling self_test() but ignoring its return, always confirming)
    self_test_ret_checked = (
        "self_test" in generated_code
        and "boot_write_img_confirmed" in generated_code
        and ("!= 0" in generated_code or "if (ret" in generated_code or "< 0" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="self_test_return_checked",
            passed=self_test_ret_checked,
            expected="self_test() return value checked before confirming (failure triggers rollback)",
            actual="present" if self_test_ret_checked else "missing (self-test result ignored!)",
            check_type="constraint",
        )
    )

    # Check 7: sys_reboot on self-test failure (not just return) — triggers MCUboot rollback
    # (LLM failure: returning from main on failure — doesn't trigger MCUboot rollback)
    reboot_on_fail = (
        "self_test" in generated_code
        and "sys_reboot" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="reboot_on_self_test_failure",
            passed=reboot_on_fail,
            expected="sys_reboot() called on self-test failure to trigger MCUboot rollback",
            actual="present" if reboot_on_fail else "missing (return from main won't trigger rollback!)",
            check_type="constraint",
        )
    )

    # Check 8: boot_write_img_confirmed return value checked
    # (LLM failure: ignoring confirm failure — image not actually confirmed)
    confirm_err_checked = (
        "boot_write_img_confirmed" in generated_code
        and ("< 0" in generated_code or "!= 0" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="confirm_return_value_checked",
            passed=confirm_err_checked,
            expected="boot_write_img_confirmed() return value checked",
            actual="present" if confirm_err_checked else "missing (confirm may silently fail!)",
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
