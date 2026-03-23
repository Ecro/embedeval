"""Static analysis checks for LittleFS Mount with Format-on-Failure Recovery."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate LittleFS mount and recovery code structure."""
    details: list[CheckDetail] = []

    # Check 1: fs/fs.h included
    has_fs_h = "zephyr/fs/fs.h" in generated_code
    details.append(
        CheckDetail(
            check_name="fs_header_included",
            passed=has_fs_h,
            expected="zephyr/fs/fs.h included",
            actual="present" if has_fs_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: fs/littlefs.h included
    has_lfs_h = "zephyr/fs/littlefs.h" in generated_code
    details.append(
        CheckDetail(
            check_name="littlefs_header_included",
            passed=has_lfs_h,
            expected="zephyr/fs/littlefs.h included",
            actual="present" if has_lfs_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: fs_mount called
    has_mount = "fs_mount" in generated_code
    details.append(
        CheckDetail(
            check_name="fs_mount_called",
            passed=has_mount,
            expected="fs_mount() called",
            actual="present" if has_mount else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: fs_mkfs called for format-on-failure recovery (LLM failure: no recovery)
    has_mkfs = "fs_mkfs" in generated_code
    details.append(
        CheckDetail(
            check_name="fs_mkfs_on_failure",
            passed=has_mkfs,
            expected="fs_mkfs() called to format on mount failure",
            actual="present" if has_mkfs else "missing (no format-on-failure recovery)",
            check_type="exact_match",
        )
    )

    # Check 5: Mount retried after format (two fs_mount calls)
    import re
    mount_calls = len(re.findall(r'\bfs_mount\b', generated_code))
    details.append(
        CheckDetail(
            check_name="mount_retried_after_format",
            passed=mount_calls >= 2,
            expected="fs_mount() called at least twice (initial + retry after format)",
            actual=f"found {mount_calls} fs_mount call(s)",
            check_type="constraint",
        )
    )

    # Check 6: FS_LITTLEFS type referenced
    has_lfs_type = "FS_LITTLEFS" in generated_code
    details.append(
        CheckDetail(
            check_name="fs_littlefs_type",
            passed=has_lfs_type,
            expected="FS_LITTLEFS type used for mount and/or format",
            actual="present" if has_lfs_type else "missing",
            check_type="exact_match",
        )
    )

    return details
