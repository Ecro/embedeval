"""Behavioral checks for NVS key-value store."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate NVS behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: mount before write/read (correct ordering)
    mount_pos = find_in_code(generated_code, "nvs_mount")
    write_pos = find_in_code(generated_code, "nvs_write")
    read_pos = find_in_code(generated_code, "nvs_read")
    mount_first = (
        mount_pos != -1
        and write_pos != -1
        and read_pos != -1
        and mount_pos < write_pos
        and mount_pos < read_pos
    )
    details.append(
        CheckDetail(
            check_name="mount_before_io",
            passed=mount_first,
            expected="nvs_mount() before nvs_write/nvs_read",
            actual="correct order" if mount_first else "wrong order",
            check_type="constraint",
        )
    )

    # Check 2: write before read (write-then-verify pattern)
    write_before_read = (
        write_pos != -1 and read_pos != -1 and write_pos < read_pos
    )
    details.append(
        CheckDetail(
            check_name="write_before_read",
            passed=write_before_read,
            expected="nvs_write() before nvs_read() (verify pattern)",
            actual="correct" if write_before_read else "wrong order",
            check_type="constraint",
        )
    )

    # Check 3: sector_size configured
    has_sector_size = scoped_contains(generated_code, 'sector_size', scope='code_only')
    details.append(
        CheckDetail(
            check_name="sector_size_configured",
            passed=has_sector_size,
            expected="NVS sector_size set in nvs_fs config",
            actual="present" if has_sector_size else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Error handling for mount/write/read
    has_error = scoped_contains(generated_code, '< 0', scope='code_only')
    details.append(
        CheckDetail(
            check_name="nvs_error_handling",
            passed=has_error,
            expected="Error checks on NVS API return values",
            actual="present" if has_error else "missing",
            check_type="constraint",
        )
    )

    # Check 5: NVS ID > 0 (ID 0 is reserved in some implementations)
    has_id = scoped_contains(generated_code, 'NVS_ID', scope='code_only') or "nvs_id" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="nvs_id_defined",
            passed=has_id,
            expected="NVS ID defined for key identification",
            actual="present" if has_id else "missing",
            check_type="exact_match",
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
