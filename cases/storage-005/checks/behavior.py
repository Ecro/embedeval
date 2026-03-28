"""Behavioral checks for NVS wear-leveling awareness."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate NVS wear-leveling behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: nvs_mount before write/delete (correct ordering)
    mount_pos = generated_code.find("nvs_mount")
    write_pos = generated_code.find("nvs_write")
    delete_pos = generated_code.find("nvs_delete")
    mount_first = (
        mount_pos != -1
        and write_pos != -1
        and delete_pos != -1
        and mount_pos < write_pos
        and mount_pos < delete_pos
    )
    details.append(
        CheckDetail(
            check_name="mount_before_io",
            passed=mount_first,
            expected="nvs_mount() before nvs_write/nvs_delete",
            actual="correct order" if mount_first else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: nvs_calc_free_space called after writes
    free_pos = generated_code.find("nvs_calc_free_space")
    free_after_write = (
        free_pos != -1 and write_pos != -1 and write_pos < free_pos
    )
    details.append(
        CheckDetail(
            check_name="free_space_checked_after_write",
            passed=free_after_write,
            expected="nvs_calc_free_space() called after nvs_write()",
            actual="correct" if free_after_write else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: nvs_delete before second free-space check
    free_pos2 = generated_code.rfind("nvs_calc_free_space")
    delete_before_second_free = (
        delete_pos != -1
        and free_pos2 != -1
        and free_pos != free_pos2
        and delete_pos < free_pos2
    )
    details.append(
        CheckDetail(
            check_name="delete_before_second_free_check",
            passed=delete_before_second_free,
            expected="nvs_delete() before second nvs_calc_free_space() call",
            actual="correct" if delete_before_second_free else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 4: ENOSPC handled gracefully (not aborting on it)
    has_enospc = "ENOSPC" in generated_code
    details.append(
        CheckDetail(
            check_name="enospc_graceful_handling",
            passed=has_enospc,
            expected="ENOSPC checked and handled gracefully",
            actual="present" if has_enospc else "missing (may abort on full storage)",
            check_type="constraint",
        )
    )

    # Check 5: sector_count small enough to trigger wear awareness (<=4)
    import re
    sector_count_match = re.search(r"sector_count\s*=\s*(\d+)", generated_code)
    sector_count_ok = False
    actual_count = "not found"
    if sector_count_match:
        count = int(sector_count_match.group(1))
        actual_count = str(count)
        sector_count_ok = count <= 4
    details.append(
        CheckDetail(
            check_name="small_sector_count",
            passed=sector_count_ok,
            expected="sector_count <= 4 (small, to trigger wear awareness)",
            actual=f"sector_count={actual_count}",
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
