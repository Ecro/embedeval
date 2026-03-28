"""Behavioral checks for LittleFS file read/write."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate LittleFS behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: fs_mount before fs_open (correct ordering)
    mount_pos = generated_code.find("fs_mount")
    open_pos = generated_code.find("fs_open")
    write_pos = generated_code.find("fs_write")
    mount_first = (
        mount_pos != -1
        and open_pos != -1
        and write_pos != -1
        and mount_pos < open_pos
        and mount_pos < write_pos
    )
    details.append(
        CheckDetail(
            check_name="mount_before_open",
            passed=mount_first,
            expected="fs_mount() before fs_open/fs_write",
            actual="correct order" if mount_first else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: write before read (write-then-verify pattern)
    read_pos = generated_code.find("fs_read")
    write_before_read = (
        write_pos != -1 and read_pos != -1 and write_pos < read_pos
    )
    details.append(
        CheckDetail(
            check_name="write_before_read",
            passed=write_before_read,
            expected="fs_write() before fs_read() (verify pattern)",
            actual="correct" if write_before_read else "wrong order",
            check_type="constraint",
        )
    )

    # Check 3: FS_O_CREATE flag present for file creation
    has_create = "FS_O_CREATE" in generated_code
    details.append(
        CheckDetail(
            check_name="fs_o_create_present",
            passed=has_create,
            expected="FS_O_CREATE flag in fs_open() for new file",
            actual="present" if has_create else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: fs_close called (resource cleanup)
    close_pos = generated_code.find("fs_close")
    has_close = close_pos != -1
    details.append(
        CheckDetail(
            check_name="fs_close_called",
            passed=has_close,
            expected="fs_close() called to release file handle",
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
            expected="Error checks on FS API return values",
            actual="present" if has_error else "missing",
            check_type="constraint",
        )
    )

    # Check 6: fs_seek called before reading back written data
    has_seek = "fs_seek" in generated_code or "lfs_file_seek" in generated_code
    details.append(
        CheckDetail(
            check_name="seek_before_read",
            passed=has_seek,
            expected="fs_seek() called before reading back written data",
            actual="seek found" if has_seek else "no seek — will read from end of file",
            check_type="constraint",
        )
    )

    return details
