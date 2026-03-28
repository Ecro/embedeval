"""Behavioral checks for DFU target flash write."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis, check_return_after_error


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DFU target behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: init before write (mandatory ordering)
    # (LLM failure: calling dfu_target_write without prior init)
    init_pos = generated_code.find("dfu_target_init")
    write_pos = generated_code.find("dfu_target_write")
    details.append(
        CheckDetail(
            check_name="init_before_write",
            passed=init_pos != -1 and write_pos != -1 and init_pos < write_pos,
            expected="dfu_target_init() before dfu_target_write()",
            actual="correct order" if (init_pos != -1 and write_pos != -1 and init_pos < write_pos) else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: done() called after all writes
    # (LLM failure: omitting dfu_target_done entirely)
    write_pos2 = generated_code.rfind("dfu_target_write")
    done_pos = generated_code.find("dfu_target_done")
    details.append(
        CheckDetail(
            check_name="done_after_write",
            passed=done_pos != -1 and write_pos2 != -1 and done_pos > write_pos2,
            expected="dfu_target_done() called after all writes complete",
            actual="correct" if (done_pos != -1 and write_pos2 != -1 and done_pos > write_pos2) else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 3: Error path calls dfu_target_done(false) to abort
    # (LLM failure: leaving DFU in partially initialized state on error)
    has_abort = "dfu_target_done(false)" in generated_code
    details.append(
        CheckDetail(
            check_name="abort_on_error",
            passed=has_abort,
            expected="dfu_target_done(false) called on error path to abort",
            actual="present" if has_abort else "missing (DFU left in bad state on error)",
            check_type="constraint",
        )
    )

    # Check 4: Error handling on init return value
    has_init_err = "dfu_target_init" in generated_code and (
        "< 0" in generated_code or "!= 0" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="init_error_handling",
            passed=has_init_err,
            expected="Return value of dfu_target_init() checked",
            actual="present" if has_init_err else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Reboot called after done(true)
    done_true_pos = generated_code.find("dfu_target_done(true)")
    reboot_pos = generated_code.find("sys_reboot")
    details.append(
        CheckDetail(
            check_name="reboot_after_done",
            passed=done_true_pos != -1 and reboot_pos != -1 and reboot_pos > done_true_pos,
            expected="sys_reboot() called after dfu_target_done(true)",
            actual="correct" if (done_true_pos != -1 and reboot_pos != -1 and reboot_pos > done_true_pos) else "wrong or missing",
            check_type="constraint",
        )
    )

    # Check 6: Error handling on dfu_target_write return value
    # (LLM failure: ignoring write errors — partial flash writes go undetected)
    write_err_handled = (
        "dfu_target_write" in generated_code
        and ("< 0" in generated_code or "!= 0" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="write_error_handling",
            passed=write_err_handled,
            expected="Return value of dfu_target_write() checked (< 0 or != 0)",
            actual="present" if write_err_handled else "missing (write errors silently ignored)",
            check_type="constraint",
        )
    )

    # Check 7: No partial write to flash if error occurs (error path leads to abort, not continue)
    # (LLM failure: continuing to write chunks after a write error)
    # Note: "return" in generated_code is always true for any C code — use
    # check_return_after_error to verify that error-handling blocks contain returns.
    abort_returns = (
        "dfu_target_done(false)" in generated_code
        and check_return_after_error(generated_code)
    )
    details.append(
        CheckDetail(
            check_name="abort_and_return_on_error",
            passed=abort_returns,
            expected="On error: dfu_target_done(false) called AND function returns (no partial write continues)",
            actual="correct" if abort_returns else "missing: may continue writing after error",
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
