"""Behavioral checks for full OTA flow with rollback safety."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate full OTA state machine behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: State machine structure (loop with state dispatch)
    # (LLM failure: linear flow without state machine)
    has_while = scoped_contains(generated_code, 'while', scope='code_only')
    has_switch_or_if_states = (
        scoped_contains(generated_code, 'switch', scope='code_only') and scoped_contains(generated_code, 'OTA_', scope='code_only')
    ) or (
        scoped_contains(generated_code, 'OTA_DOWNLOADING', scope='code_only') and scoped_contains(generated_code, 'OTA_VERIFYING', scope='code_only')
        and scoped_contains(generated_code, 'if', scope='code_only')
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
    done_pos = find_in_code(generated_code, "dfu_target_done")
    reboot_pos = find_in_code(generated_code, "sys_reboot")
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
    has_self_test = scoped_contains(generated_code, 'self_test', scope='code_only') or scoped_contains(generated_code, 'selftest', scope='code_only')
    self_test_pos = find_in_code(generated_code, "self_test")
    confirm_pos = find_in_code(generated_code, "boot_write_img_confirmed")
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
    check_pos = find_in_code(generated_code, "boot_is_img_confirmed")
    write_pos = find_in_code(generated_code, "boot_write_img_confirmed")
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
    has_idle_on_error = scoped_contains(generated_code, 'OTA_IDLE', scope='code_only') and (
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
    has_rollback_abort = scoped_contains(generated_code, 'dfu_target_done(false)', scope='code_only')
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
    import re as _re
    self_test_ret_checked = (
        scoped_contains(generated_code, 'self_test', scope='code_only')
        and scoped_contains(generated_code, 'boot_write_img_confirmed', scope='code_only')
        and (scoped_contains(generated_code, '!= 0', scope='code_only') or scoped_contains(generated_code, '< 0', scope='code_only')
             or bool(_re.search(r'if\s*\(\s*(?:ret|rc|result|err|status)\b', generated_code)))
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

    # Check 10: Rollback on error path — Factor E7 OTA pipeline
    # Accepts MCUboot (dfu_target_done false / boot_write_img_invalid) or ESP-IDF rollback API
    has_rollback = (
        scoped_contains(generated_code, 'boot_write_img_invalid', scope='code_only')
        or scoped_contains(generated_code, 'mark_app_invalid', scope='code_only')
        or scoped_contains(generated_code, 'esp_ota_mark_app_invalid', scope='code_only')
        or scoped_contains(generated_code, 'dfu_target_done(false)', scope='code_only')
    )
    details.append(CheckDetail(
        check_name="rollback_on_error",
        passed=has_rollback,
        expected="Rollback API called on error path (image invalidation or dfu_target_done abort)",
        actual="rollback present" if has_rollback else "no rollback on error",
        check_type="constraint",
    ))

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
