"""Behavioral checks for Linux ioctl driver with input validation."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ioctl driver security and behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: _IOC_TYPE validated (critical security check)
    # (LLM failure: processing ioctl without type validation allows wrong-driver commands)
    has_ioc_type = "_IOC_TYPE" in generated_code
    details.append(
        CheckDetail(
            check_name="ioc_type_validated",
            passed=has_ioc_type,
            expected="_IOC_TYPE(cmd) validated against magic number",
            actual="present" if has_ioc_type else "MISSING (accepts commands for other drivers!)",
            check_type="constraint",
        )
    )

    # Check 2: _IOC_NR range check or equivalent bounds check
    # (LLM failure: no bounds check on command number allows out-of-range commands)
    has_ioc_nr = "_IOC_NR" in generated_code
    details.append(
        CheckDetail(
            check_name="ioc_nr_range_checked",
            passed=has_ioc_nr,
            expected="_IOC_NR(cmd) checked against supported range",
            actual="present" if has_ioc_nr else "missing (unbounded command range)",
            check_type="constraint",
        )
    )

    # Check 3: copy_from_user used (NOT direct __user pointer dereference)
    # (Critical LLM security failure: val = *((struct foo*)arg) is wrong)
    has_copy_from = "copy_from_user" in generated_code
    details.append(
        CheckDetail(
            check_name="copy_from_user_for_ioctl_arg",
            passed=has_copy_from,
            expected="copy_from_user() to read ioctl argument from user space",
            actual="present" if has_copy_from else "MISSING (raw __user dereference = security bug!)",
            check_type="constraint",
        )
    )

    # Check 4: -ENOTTY returned for invalid commands
    # (Proper Linux convention for unsupported ioctl)
    has_enotty = "ENOTTY" in generated_code
    details.append(
        CheckDetail(
            check_name="enotty_for_invalid_cmd",
            passed=has_enotty,
            expected="-ENOTTY returned for unrecognized ioctl commands",
            actual="present" if has_enotty else "missing (wrong error code convention)",
            check_type="constraint",
        )
    )

    # Check 5: No raw __user dereference (negative check)
    # Simplified heuristic: look for patterns like *(type*)arg without copy_from_user
    import re
    raw_deref = bool(re.search(r'\*\s*\(\s*\w[^)]*\)\s*arg', generated_code))
    details.append(
        CheckDetail(
            check_name="no_raw_user_pointer_deref",
            passed=not raw_deref,
            expected="No raw dereference of user-space arg pointer",
            actual="clean" if not raw_deref else "POTENTIAL raw dereference detected",
            check_type="constraint",
        )
    )

    # Check 6: -EFAULT returned on copy failure
    has_efault = "EFAULT" in generated_code
    details.append(
        CheckDetail(
            check_name="efault_on_copy_failure",
            passed=has_efault,
            expected="-EFAULT returned when copy_from/to_user fails",
            actual="present" if has_efault else "missing",
            check_type="constraint",
        )
    )

    return details
