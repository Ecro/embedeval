"""Static analysis checks for OTA image slot status query."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate OTA slot status query code structure."""
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

    has_swap_type = "mcuboot_swap_type" in generated_code
    details.append(
        CheckDetail(
            check_name="mcuboot_swap_type_called",
            passed=has_swap_type,
            expected="mcuboot_swap_type() called to query swap status",
            actual="present" if has_swap_type else "missing",
            check_type="exact_match",
        )
    )

    has_bank_header = "boot_read_bank_header" in generated_code
    details.append(
        CheckDetail(
            check_name="boot_read_bank_header_called",
            passed=has_bank_header,
            expected="boot_read_bank_header() called to read slot info",
            actual="present" if has_bank_header else "missing",
            check_type="exact_match",
        )
    )

    has_mcuboot_img_header = "mcuboot_img_header" in generated_code
    details.append(
        CheckDetail(
            check_name="mcuboot_img_header_struct",
            passed=has_mcuboot_img_header,
            expected="struct mcuboot_img_header used for bank header data",
            actual="present" if has_mcuboot_img_header else "missing",
            check_type="exact_match",
        )
    )

    has_slot0 = "slot0_partition" in generated_code or "FIXED_PARTITION_ID" in generated_code
    details.append(
        CheckDetail(
            check_name="slot0_referenced",
            passed=has_slot0,
            expected="Primary slot (slot0_partition) referenced",
            actual="present" if has_slot0 else "missing",
            check_type="exact_match",
        )
    )

    has_slot1 = "slot1_partition" in generated_code
    details.append(
        CheckDetail(
            check_name="slot1_referenced",
            passed=has_slot1,
            expected="Secondary slot (slot1_partition) referenced",
            actual="present" if has_slot1 else "missing",
            check_type="exact_match",
        )
    )

    has_confirmed = "boot_is_img_confirmed" in generated_code
    details.append(
        CheckDetail(
            check_name="img_confirmed_reported",
            passed=has_confirmed,
            expected="boot_is_img_confirmed() called to report current image state",
            actual="present" if has_confirmed else "missing",
            check_type="exact_match",
        )
    )

    return details
