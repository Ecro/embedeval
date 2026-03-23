"""Behavioral checks for Linux character device driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Linux driver behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Uses copy_to_user (NOT raw pointer access)
    # (Critical LLM failure: accessing __user pointer directly = security vuln)
    has_copy_to = "copy_to_user" in generated_code
    details.append(
        CheckDetail(
            check_name="copy_to_user_used",
            passed=has_copy_to,
            expected="copy_to_user() for kernel→user data transfer",
            actual="present" if has_copy_to else "MISSING (security!)",
            check_type="constraint",
        )
    )

    # Check 2: Uses copy_from_user (NOT raw pointer access)
    has_copy_from = "copy_from_user" in generated_code
    details.append(
        CheckDetail(
            check_name="copy_from_user_used",
            passed=has_copy_from,
            expected="copy_from_user() for user→kernel data transfer",
            actual="present" if has_copy_from else "MISSING (security!)",
            check_type="constraint",
        )
    )

    # Check 3: Cleanup in exit matches init resources
    # (LLM failure: register in init but forget to unregister in exit)
    has_register = (
        "alloc_chrdev_region" in generated_code
        or "register_chrdev" in generated_code
    )
    has_unregister = (
        "unregister_chrdev_region" in generated_code
        or "unregister_chrdev" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="register_unregister_balanced",
            passed=has_register and has_unregister,
            expected="chrdev registered in init AND unregistered in exit",
            actual=f"register={has_register}, unregister={has_unregister}",
            check_type="constraint",
        )
    )

    # Check 4: file_operations has .read and .write
    has_dot_read = ".read" in generated_code
    has_dot_write = ".write" in generated_code
    details.append(
        CheckDetail(
            check_name="fops_read_write",
            passed=has_dot_read and has_dot_write,
            expected="file_operations has .read and .write",
            actual=f"read={has_dot_read}, write={has_dot_write}",
            check_type="exact_match",
        )
    )

    # Check 5: .owner = THIS_MODULE (prevents module unload while in use)
    has_owner = "THIS_MODULE" in generated_code
    details.append(
        CheckDetail(
            check_name="this_module_owner",
            passed=has_owner,
            expected=".owner = THIS_MODULE in file_operations",
            actual="present" if has_owner else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Error handling in init (rollback on failure)
    has_err_init = (
        "< 0" in generated_code or "IS_ERR" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="init_error_handling",
            passed=has_err_init,
            expected="Error handling with rollback in init",
            actual="present" if has_err_init else "missing",
            check_type="constraint",
        )
    )

    return details
