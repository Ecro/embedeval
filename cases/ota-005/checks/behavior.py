"""Behavioral checks for full OTA flow with rollback safety."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate full OTA state machine behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: State machine structure (loop with state dispatch)
    # (LLM failure: linear flow without state machine)
    has_while = "while" in generated_code
    has_switch_or_if_states = (
        "switch" in generated_code and "OTA_" in generated_code
    ) or (
        "OTA_DOWNLOADING" in generated_code and "OTA_VERIFYING" in generated_code
        and "if" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="state_machine_loop",
            passed=has_while and has_switch_or_if_states,
            expected="while loop with switch/if dispatching on OTA state",
            actual="present" if (has_while and has_switch_or_if_states) else "missing (linear flow without state machine)",
            check_type="constraint",
        )
    )

    # Check 2: Verify phase (dfu_target_done) before reboot
    # (LLM failure: rebooting without calling dfu_target_done)
    done_pos = generated_code.find("dfu_target_done")
    reboot_pos = generated_code.find("sys_reboot")
    details.append(
        CheckDetail(
            check_name="verify_before_reboot",
            passed=done_pos != -1 and reboot_pos != -1 and done_pos < reboot_pos,
            expected="dfu_target_done() (verify phase) before sys_reboot()",
            actual="correct" if (done_pos != -1 and reboot_pos != -1 and done_pos < reboot_pos) else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 3: Self-test before confirmation
    # (LLM failure: calling boot_write_img_confirmed without self-test)
    has_self_test = "self_test" in generated_code or "selftest" in generated_code
    self_test_pos = generated_code.find("self_test")
    confirm_pos = generated_code.find("boot_write_img_confirmed")
    details.append(
        CheckDetail(
            check_name="self_test_before_confirm",
            passed=has_self_test and self_test_pos != -1 and confirm_pos != -1 and self_test_pos < confirm_pos,
            expected="self_test() called before boot_write_img_confirmed()",
            actual="correct" if (has_self_test and self_test_pos < confirm_pos) else "missing or wrong order (confirming before self-test!)",
            check_type="constraint",
        )
    )

    # Check 4: Rollback path (boot_is_img_confirmed check before writing confirm)
    # (LLM failure: confirming unconditionally, no rollback possible)
    check_pos = generated_code.find("boot_is_img_confirmed")
    write_pos = generated_code.find("boot_write_img_confirmed")
    details.append(
        CheckDetail(
            check_name="check_before_confirm",
            passed=check_pos != -1 and write_pos != -1 and check_pos < write_pos,
            expected="boot_is_img_confirmed() checked before boot_write_img_confirmed()",
            actual="correct" if (check_pos != -1 and write_pos != -1 and check_pos < write_pos) else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 5: Timeout or bounded confirm window
    # (LLM failure: infinite wait with no rollback timeout)
    has_timeout = any(
        t in generated_code
        for t in ["timeout", "TIMEOUT", "deadline", "k_uptime", "K_TIMEOUT", "ETIMEDOUT"]
    )
    details.append(
        CheckDetail(
            check_name="confirm_timeout",
            passed=has_timeout,
            expected="Confirmation timeout implemented (allow rollback if hung)",
            actual="present" if has_timeout else "missing (no rollback timeout — dangerous!)",
            check_type="constraint",
        )
    )

    # Check 6: Error path returns to IDLE rather than hanging
    has_idle_on_error = "OTA_IDLE" in generated_code and (
        "failed" in generated_code.lower() or "error" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="idle_on_error",
            passed=has_idle_on_error,
            expected="On error, state machine returns to OTA_IDLE",
            actual="present" if has_idle_on_error else "missing (hangs on error?)",
            check_type="constraint",
        )
    )

    # Check 7: State machine completeness — all required OTA states defined
    # (LLM failure: missing states like CONFIRMING or REBOOTING — incomplete state machine)
    required_states = [
        "OTA_IDLE",
        "OTA_DOWNLOADING",
        "OTA_VERIFYING",
        "OTA_REBOOTING",
        "OTA_CONFIRMING",
    ]
    missing_states = [s for s in required_states if s not in generated_code]
    details.append(
        CheckDetail(
            check_name="state_machine_complete",
            passed=len(missing_states) == 0,
            expected=f"All OTA states defined: {', '.join(required_states)}",
            actual="complete" if not missing_states else f"missing states: {missing_states}",
            check_type="constraint",
        )
    )

    # Check 8: Rollback path — dfu_target_done(false) on download error
    # (LLM failure: only happy path — no abort if download chunk fails)
    has_rollback_abort = "dfu_target_done(false)" in generated_code
    details.append(
        CheckDetail(
            check_name="rollback_abort_on_download_error",
            passed=has_rollback_abort,
            expected="dfu_target_done(false) called to abort DFU on error (rollback path)",
            actual="present" if has_rollback_abort else "missing (no rollback path on download failure!)",
            check_type="constraint",
        )
    )

    # Check 9: Self-test return value checked before confirming
    # (LLM failure: calling self_test() but ignoring its return value, always confirming)
    self_test_ret_checked = (
        "self_test" in generated_code
        and "boot_write_img_confirmed" in generated_code
        and ("!= 0" in generated_code or "< 0" in generated_code or "if (ret" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="self_test_return_checked",
            passed=self_test_ret_checked,
            expected="self_test() return value checked before boot_write_img_confirmed()",
            actual="present" if self_test_ret_checked else "missing (self-test result ignored!)",
            check_type="constraint",
        )
    )

    return details
