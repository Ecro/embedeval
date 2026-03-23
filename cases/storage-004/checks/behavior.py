"""Behavioral checks for Flash Area erase and write."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate flash area behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: erase before write (mandatory for flash)
    erase_pos = generated_code.find("flash_area_erase")
    write_pos = generated_code.find("flash_area_write")
    erase_before_write = (
        erase_pos != -1 and write_pos != -1 and erase_pos < write_pos
    )
    details.append(
        CheckDetail(
            check_name="erase_before_write",
            passed=erase_before_write,
            expected="flash_area_erase() before flash_area_write()",
            actual="correct order" if erase_before_write else "wrong order or missing erase",
            check_type="constraint",
        )
    )

    # Check 2: write before read (write-then-verify pattern)
    read_pos = generated_code.find("flash_area_read")
    write_before_read = (
        write_pos != -1 and read_pos != -1 and write_pos < read_pos
    )
    details.append(
        CheckDetail(
            check_name="write_before_read",
            passed=write_before_read,
            expected="flash_area_write() before flash_area_read() (verify pattern)",
            actual="correct" if write_before_read else "wrong order",
            check_type="constraint",
        )
    )

    # Check 3: flash_area_open before other operations
    open_pos = generated_code.find("flash_area_open")
    open_first = (
        open_pos != -1
        and erase_pos != -1
        and write_pos != -1
        and open_pos < erase_pos
        and open_pos < write_pos
    )
    details.append(
        CheckDetail(
            check_name="open_before_operations",
            passed=open_first,
            expected="flash_area_open() before erase/write/read",
            actual="correct order" if open_first else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 4: flash_area_close called (resource cleanup)
    has_close = "flash_area_close" in generated_code
    details.append(
        CheckDetail(
            check_name="flash_area_close_called",
            passed=has_close,
            expected="flash_area_close() called after operations",
            actual="present" if has_close else "missing",
            check_type="constraint",
        )
    )

    # Check 5: error handling present
    has_error = "< 0" in generated_code
    details.append(
        CheckDetail(
            check_name="error_handling",
            passed=has_error,
            expected="Error checks on flash area API return values",
            actual="present" if has_error else "missing",
            check_type="constraint",
        )
    )

    return details
