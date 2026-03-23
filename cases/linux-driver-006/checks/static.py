"""Static analysis checks for Linux ioctl driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ioctl driver code structure."""
    details: list[CheckDetail] = []

    has_ioctl_h = "linux/ioctl.h" in generated_code
    details.append(
        CheckDetail(
            check_name="ioctl_header_included",
            passed=has_ioctl_h,
            expected="linux/ioctl.h included",
            actual="present" if has_ioctl_h else "missing",
            check_type="exact_match",
        )
    )

    has_uaccess = "linux/uaccess.h" in generated_code
    details.append(
        CheckDetail(
            check_name="uaccess_header_included",
            passed=has_uaccess,
            expected="linux/uaccess.h included",
            actual="present" if has_uaccess else "missing",
            check_type="exact_match",
        )
    )

    has_magic = "_IOW(" in generated_code or "_IOR(" in generated_code or "_IO(" in generated_code or "_IOWR(" in generated_code
    details.append(
        CheckDetail(
            check_name="ioctl_command_defined",
            passed=has_magic,
            expected="ioctl command defined with _IOW/_IOR/_IO/_IOWR macro",
            actual="present" if has_magic else "missing",
            check_type="exact_match",
        )
    )

    has_unlocked_ioctl = "unlocked_ioctl" in generated_code
    details.append(
        CheckDetail(
            check_name="unlocked_ioctl_in_fops",
            passed=has_unlocked_ioctl,
            expected=".unlocked_ioctl in file_operations",
            actual="present" if has_unlocked_ioctl else "missing",
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

    return details
