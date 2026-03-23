"""Static analysis checks for Linux character device driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Linux driver code structure."""
    details: list[CheckDetail] = []

    has_module_h = "linux/module.h" in generated_code
    details.append(
        CheckDetail(
            check_name="module_header",
            passed=has_module_h,
            expected="linux/module.h included",
            actual="present" if has_module_h else "missing",
            check_type="exact_match",
        )
    )

    has_fs_h = "linux/fs.h" in generated_code
    details.append(
        CheckDetail(
            check_name="fs_header",
            passed=has_fs_h,
            expected="linux/fs.h included",
            actual="present" if has_fs_h else "missing",
            check_type="exact_match",
        )
    )

    has_license = "MODULE_LICENSE" in generated_code
    details.append(
        CheckDetail(
            check_name="module_license",
            passed=has_license,
            expected="MODULE_LICENSE defined",
            actual="present" if has_license else "missing",
            check_type="exact_match",
        )
    )

    has_fops = "file_operations" in generated_code
    details.append(
        CheckDetail(
            check_name="file_operations_struct",
            passed=has_fops,
            expected="struct file_operations defined",
            actual="present" if has_fops else "missing",
            check_type="exact_match",
        )
    )

    has_init = "module_init" in generated_code
    has_exit = "module_exit" in generated_code
    details.append(
        CheckDetail(
            check_name="init_exit_macros",
            passed=has_init and has_exit,
            expected="module_init() and module_exit() macros",
            actual=f"init={has_init}, exit={has_exit}",
            check_type="exact_match",
        )
    )

    return details
