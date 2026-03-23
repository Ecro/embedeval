"""Behavioral checks for OTA image confirmation."""

from embedeval.models import CheckDetail


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
            actual="correct order" if check_pos < write_pos else "wrong order",
            check_type="constraint",
        )
    )

    # Check 2: Self-test before confirmation
    # (LLM failure: confirming image without validation)
    has_test = any(
        p in generated_code.lower()
        for p in ["self_test", "selftest", "test(", "validate", "check"]
    )
    details.append(
        CheckDetail(
            check_name="self_test_before_confirm",
            passed=has_test,
            expected="Self-test/validation before image confirmation",
            actual="present" if has_test else "missing (dangerous!)",
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

    # Check 4: Error handling for boot_write_img_confirmed
    has_err = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="confirm_error_handling",
            passed=has_err,
            expected="Error check on boot_write_img_confirmed()",
            actual="present" if has_err else "missing",
            check_type="constraint",
        )
    )

    return details
