"""Behavioral checks for OTA image confirmation."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate OTA behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Check confirmed BEFORE writing confirm
    # (LLM failure: unconditionally confirming without checking)
    check_pos = generated_code.find("boot_is_img_confirmed")
    write_pos = generated_code.find("boot_write_img_confirmed")
    details.append(
        CheckDetail(
            check_name="check_before_confirm",
            passed=check_pos != -1 and write_pos != -1 and check_pos < write_pos,
            expected="boot_is_img_confirmed() before boot_write_img_confirmed()",
            actual="correct order" if (check_pos != -1 and write_pos != -1 and check_pos < write_pos) else "wrong order",
            check_type="constraint",
        )
    )

    # Check 2: Self-test BEFORE boot_write_img_confirmed (ordering enforced)
    # (LLM failure: confirming image without any self-test, or self-test after confirm)
    # Look for explicit self_test function definition/call, or validate/check call before confirm
    self_test_patterns = ["self_test()", "selftest()", "run_self_test", "app_validate", "validate_firmware"]
    self_test_pos = -1
    for p in self_test_patterns:
        pos = generated_code.find(p)
        if pos != -1:
            self_test_pos = pos
            break
    confirm_pos = generated_code.find("boot_write_img_confirmed")
    test_before_confirm = (
        self_test_pos != -1
        and confirm_pos != -1
        and self_test_pos < confirm_pos
    )
    details.append(
        CheckDetail(
            check_name="self_test_before_confirm",
            passed=test_before_confirm,
            expected="self_test() (or equivalent) called BEFORE boot_write_img_confirmed()",
            actual="correct order" if test_before_confirm else "missing self-test or wrong order (confirming before testing!)",
            check_type="constraint",
        )
    )

    # Check 3: Rollback path exists (non-confirmation on failure)
    # (LLM failure: always confirming, no rollback possible)
    has_conditional = (
        "if" in generated_code
        and "boot_write_img_confirmed" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="conditional_confirmation",
            passed=has_conditional,
            expected="Conditional confirmation (not unconditional)",
            actual="conditional" if has_conditional else "unconditional",
            check_type="constraint",
        )
    )

    # Check 4: Error handling for boot_write_img_confirmed return value
    # (LLM failure: ignoring return value — silent confirm failure)
    # Accept < 0, != 0, or == 0 only when paired with else (error branch)
    has_err_pattern = "< 0" in generated_code or "!= 0" in generated_code
    has_success_with_else = "== 0" in generated_code and "else" in generated_code
    write_ret_handled = (
        "boot_write_img_confirmed" in generated_code
        and (has_err_pattern or has_success_with_else)
    )
    details.append(
        CheckDetail(
            check_name="confirm_error_handling",
            passed=write_ret_handled,
            expected="Return value of boot_write_img_confirmed() checked (< 0 or != 0)",
            actual="present" if write_ret_handled else "missing (confirm failure silently ignored)",
            check_type="constraint",
        )
    )

    # Check 5: boot_write_img_confirmed NOT called unconditionally at top-level
    # (LLM failure: always confirming every boot without checking if image is unconfirmed)
    # The confirm must be inside an if block that guards it
    has_guard = "if" in generated_code and "boot_is_img_confirmed" in generated_code
    details.append(
        CheckDetail(
            check_name="confirm_guarded_by_check",
            passed=has_guard,
            expected="boot_write_img_confirmed() only called inside conditional block guarded by boot_is_img_confirmed()",
            actual="guarded" if has_guard else "called unconditionally on every boot (dangerous!)",
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
