"""Behavioral checks for LittleFS Mount with Format-on-Failure Recovery."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate LittleFS mount recovery behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: fs_mount return value checked (not ignored)
    import re
    mount_checked = bool(
        re.search(r'(ret|rc|err|result)\s*=\s*fs_mount', generated_code)
        or re.search(r'if\s*\(\s*fs_mount', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="mount_return_checked",
            passed=mount_checked,
            expected="fs_mount() return value captured and checked",
            actual="checked" if mount_checked else "return value may be ignored",
            check_type="constraint",
        )
    )

    # Check 2: fs_mkfs after failed mount (correct recovery ordering)
    mount_pos = generated_code.find("fs_mount")
    mkfs_pos = generated_code.find("fs_mkfs")
    mkfs_after_mount = mkfs_pos != -1 and mount_pos != -1 and mount_pos < mkfs_pos
    details.append(
        CheckDetail(
            check_name="mkfs_after_failed_mount",
            passed=mkfs_after_mount,
            expected="fs_mkfs() called after fs_mount() failure",
            actual="correct order" if mkfs_after_mount else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: fs_mkfs return value checked
    mkfs_checked = bool(
        re.search(r'(ret|rc|err|result)\s*=\s*fs_mkfs', generated_code)
        or re.search(r'if\s*\(\s*fs_mkfs', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="mkfs_return_checked",
            passed=mkfs_checked,
            expected="fs_mkfs() return value checked",
            actual="checked" if mkfs_checked else "format errors ignored",
            check_type="constraint",
        )
    )

    # Check 4: Success message after mount
    has_ok = "FS MOUNTED OK" in generated_code or "MOUNTED" in generated_code or "mounted" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="mount_success_printed",
            passed=has_ok,
            expected="Success message printed after mount",
            actual="present" if has_ok else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Warning message on first mount failure
    has_warning = (
        "formatting" in generated_code.lower()
        or "format" in generated_code.lower()
        or ("failed" in generated_code.lower() and "mount" in generated_code.lower())
    )
    details.append(
        CheckDetail(
            check_name="warning_on_mount_failure",
            passed=has_warning,
            expected="Warning message printed when first mount fails",
            actual="present" if has_warning else "missing (silent failure path)",
            check_type="constraint",
        )
    )

    # Check 6: File I/O after mount (fs_open or fs_write)
    has_file_io = "fs_open" in generated_code or "fs_write" in generated_code
    details.append(
        CheckDetail(
            check_name="file_io_after_mount",
            passed=has_file_io,
            expected="File I/O performed after successful mount",
            actual="present" if has_file_io else "missing (no filesystem use after mount)",
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
