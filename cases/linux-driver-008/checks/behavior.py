"""Behavioral checks for Linux proc file driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate proc file driver behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: proc_remove or remove_proc_entry called in exit
    # (LLM failure: forgetting to remove proc entry on module unload = kernel panic)
    has_remove = (
        "proc_remove" in generated_code or "remove_proc_entry" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="proc_removed_on_exit",
            passed=has_remove,
            expected="proc_remove() or remove_proc_entry() called in module_exit",
            actual="present" if has_remove else "MISSING (proc entry leaks on unload!)",
            check_type="constraint",
        )
    )

    # Check 2: seq_printf used (NOT sprintf/snprintf to user buffer)
    # (LLM failure: using sprintf(buf, ...) with raw user buffer pointer)
    has_seq_printf = "seq_printf" in generated_code
    details.append(
        CheckDetail(
            check_name="seq_printf_not_raw_sprintf",
            passed=has_seq_printf,
            expected="seq_printf() used (not raw sprintf to user buffer)",
            actual="present" if has_seq_printf else "MISSING (use seq_printf, not sprintf!)",
            check_type="constraint",
        )
    )

    # Check 3: single_open used (standard pattern for simple seq files)
    has_single_open = "single_open" in generated_code
    details.append(
        CheckDetail(
            check_name="single_open_used",
            passed=has_single_open,
            expected="single_open() used in open callback",
            actual="present" if has_single_open else "missing",
            check_type="constraint",
        )
    )

    # Check 4: proc_ops has proc_read = seq_read
    has_seq_read = "seq_read" in generated_code
    details.append(
        CheckDetail(
            check_name="seq_read_in_proc_ops",
            passed=has_seq_read,
            expected="proc_ops has .proc_read = seq_read",
            actual="present" if has_seq_read else "missing",
            check_type="constraint",
        )
    )

    # Check 5: proc_create result checked for NULL
    has_null_check = (
        "!entry" in generated_code
        or "== NULL" in generated_code
        or "IS_ERR" in generated_code
        or "ENOMEM" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="proc_create_result_checked",
            passed=has_null_check,
            expected="proc_create() return value checked for failure",
            actual="present" if has_null_check else "missing",
            check_type="constraint",
        )
    )

    # Check 6: No direct write() to user buffer in show function
    # (negative: should not use copy_to_user or memcpy in a seq show function)
    has_show_fn = "seq_file" in generated_code
    details.append(
        CheckDetail(
            check_name="show_function_uses_seq_file",
            passed=has_show_fn,
            expected="show function takes struct seq_file* parameter",
            actual="present" if has_show_fn else "missing",
            check_type="constraint",
        )
    )

    return details
