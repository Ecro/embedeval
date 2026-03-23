"""Behavioral checks for Linux sysfs attribute driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sysfs attribute driver behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: sysfs_remove_group called in remove
    # (LLM failure: creates group in probe but never removes in remove)
    has_remove_group = "sysfs_remove_group" in generated_code
    details.append(
        CheckDetail(
            check_name="sysfs_remove_group_in_remove",
            passed=has_remove_group,
            expected="sysfs_remove_group() called in remove to match create",
            actual="present" if has_remove_group else "MISSING (kernel warning on unload!)",
            check_type="constraint",
        )
    )

    # Check 2: show uses sysfs_emit (not sprintf or snprintf)
    # (LLM failure: using sprintf into buf can overflow the PAGE_SIZE sysfs buffer)
    has_sysfs_emit = "sysfs_emit" in generated_code
    has_raw_sprintf = "sprintf(" in generated_code and "sysfs_emit" not in generated_code
    details.append(
        CheckDetail(
            check_name="sysfs_emit_in_show",
            passed=has_sysfs_emit and not has_raw_sprintf,
            expected="sysfs_emit() used in show (safe, bounds-checked)",
            actual="sysfs_emit present" if has_sysfs_emit else "missing (raw sprintf unsafe)",
            check_type="constraint",
        )
    )

    # Check 3: store uses kstrtoint or kstrtol (not sscanf or atoi)
    # (LLM failure: sscanf without error check, or atoi with no bounds check)
    has_kstrtoint = (
        "kstrtoint" in generated_code
        or "kstrtol" in generated_code
        or "kstrtou" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="kstrtoint_in_store",
            passed=has_kstrtoint,
            expected="kstrtoint/kstrtol used in store (safe integer parsing)",
            actual="present" if has_kstrtoint else "missing (sscanf/atoi has no error return)",
            check_type="constraint",
        )
    )

    # Check 4: store returns count on success (not 0 or length)
    # (LLM failure: returning 0 from store causes infinite write loop in userspace)
    has_return_count = "return count" in generated_code
    details.append(
        CheckDetail(
            check_name="store_returns_count",
            passed=has_return_count,
            expected="store returns count on success (not 0)",
            actual="present" if has_return_count else "MISSING (infinite write loop!)",
            check_type="constraint",
        )
    )

    # Check 5: show output is newline-terminated (sysfs convention)
    # (LLM failure: missing \n causes shell to print prompt on same line as value)
    # sysfs_emit(buf, "%d\n", ...) or sysfs_emit(buf, "%s\n", ...) both contain \n
    has_newline = "\\n" in generated_code
    details.append(
        CheckDetail(
            check_name="show_newline_terminated",
            passed=has_newline,
            expected="show output contains \\n (sysfs convention)",
            actual="present" if has_newline else "missing (no newline in output)",
            check_type="constraint",
        )
    )

    # Check 6: attribute_group wired up to sysfs_create_group
    has_group_used = "sysfs_create_group" in generated_code and "attribute_group" in generated_code
    details.append(
        CheckDetail(
            check_name="attr_group_used_in_create",
            passed=has_group_used,
            expected="sysfs_create_group uses the attribute_group struct",
            actual="present" if has_group_used else "missing",
            check_type="constraint",
        )
    )

    return details
