"""Static analysis checks for NVS wear-leveling awareness."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate NVS wear-leveling code structure."""
    details: list[CheckDetail] = []

    # Check 1: NVS header included
    has_nvs_h = "zephyr/fs/nvs.h" in generated_code
    details.append(
        CheckDetail(
            check_name="nvs_header_included",
            passed=has_nvs_h,
            expected="zephyr/fs/nvs.h included",
            actual="present" if has_nvs_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: nvs_mount called
    has_mount = "nvs_mount" in generated_code
    details.append(
        CheckDetail(
            check_name="nvs_mount_called",
            passed=has_mount,
            expected="nvs_mount() called",
            actual="present" if has_mount else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: nvs_calc_free_space called
    has_free_space = "nvs_calc_free_space" in generated_code
    details.append(
        CheckDetail(
            check_name="nvs_calc_free_space_called",
            passed=has_free_space,
            expected="nvs_calc_free_space() called",
            actual="present" if has_free_space else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: nvs_delete called
    has_delete = "nvs_delete" in generated_code
    details.append(
        CheckDetail(
            check_name="nvs_delete_called",
            passed=has_delete,
            expected="nvs_delete() called to remove old entries",
            actual="present" if has_delete else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: ENOSPC referenced
    has_enospc = "ENOSPC" in generated_code
    details.append(
        CheckDetail(
            check_name="enospc_handled",
            passed=has_enospc,
            expected="ENOSPC error code referenced for storage-full handling",
            actual="present" if has_enospc else "missing",
            check_type="exact_match",
        )
    )

    return details
