"""Static analysis checks for image version check before OTA update."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate image version comparison code structure."""
    details: list[CheckDetail] = []

    has_mcuboot_h = "dfu/mcuboot.h" in generated_code
    details.append(
        CheckDetail(
            check_name="mcuboot_header",
            passed=has_mcuboot_h,
            expected="zephyr/dfu/mcuboot.h included",
            actual="present" if has_mcuboot_h else "missing",
            check_type="exact_match",
        )
    )

    has_flash_map = "flash_map.h" in generated_code
    details.append(
        CheckDetail(
            check_name="flash_map_header",
            passed=has_flash_map,
            expected="zephyr/storage/flash_map.h included",
            actual="present" if has_flash_map else "missing",
            check_type="exact_match",
        )
    )

    has_read_header = "boot_read_bank_header" in generated_code
    details.append(
        CheckDetail(
            check_name="boot_read_bank_header",
            passed=has_read_header,
            expected="boot_read_bank_header() called",
            actual="present" if has_read_header else "missing",
            check_type="exact_match",
        )
    )

    has_sem_ver = "mcuboot_img_sem_ver" in generated_code
    details.append(
        CheckDetail(
            check_name="sem_ver_struct",
            passed=has_sem_ver,
            expected="struct mcuboot_img_sem_ver used",
            actual="present" if has_sem_ver else "missing",
            check_type="exact_match",
        )
    )

    has_img_header = "mcuboot_img_header" in generated_code
    details.append(
        CheckDetail(
            check_name="img_header_struct",
            passed=has_img_header,
            expected="struct mcuboot_img_header declared",
            actual="present" if has_img_header else "missing",
            check_type="exact_match",
        )
    )

    has_slot0 = "slot0_partition" in generated_code
    details.append(
        CheckDetail(
            check_name="slot0_partition",
            passed=has_slot0,
            expected="slot0_partition used with FIXED_PARTITION_ID",
            actual="present" if has_slot0 else "missing",
            check_type="exact_match",
        )
    )

    return details
