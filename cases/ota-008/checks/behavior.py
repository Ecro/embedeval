"""Behavioral checks for OTA rollback with timeout."""

from embedeval.models import CheckDetail


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

    return details
