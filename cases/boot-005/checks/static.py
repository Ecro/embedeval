"""Static analysis checks for Multi-image Boot Configuration Kconfig."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-image boot Kconfig structure."""
    details: list[CheckDetail] = []
    lines = [
        line.strip()
        for line in generated_code.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    # Check 1: valid Kconfig format
    valid_format = all(
        line.startswith("CONFIG_") and "=" in line for line in lines
    )
    details.append(
        CheckDetail(
            check_name="kconfig_format",
            passed=valid_format,
            expected="All lines: CONFIG_*=value",
            actual=f"{len(lines)} lines, valid={valid_format}",
            check_type="exact_match",
        )
    )

    # Check 2: MCUboot enabled
    has_mcuboot = any("CONFIG_BOOTLOADER_MCUBOOT=y" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="mcuboot_enabled",
            passed=has_mcuboot,
            expected="CONFIG_BOOTLOADER_MCUBOOT=y",
            actual="present" if has_mcuboot else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: BOOT_IMAGE_NUMBER=2
    has_image_num = any("CONFIG_BOOT_IMAGE_NUMBER=2" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="boot_image_number_2",
            passed=has_image_num,
            expected="CONFIG_BOOT_IMAGE_NUMBER=2",
            actual="present" if has_image_num else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: PCD_APP enabled
    has_pcd = any("CONFIG_PCD_APP=y" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="pcd_app_enabled",
            passed=has_pcd,
            expected="CONFIG_PCD_APP=y (network core update support)",
            actual="present" if has_pcd else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: SINGLE_APPLICATION_SLOT absent
    no_single = not any("CONFIG_SINGLE_APPLICATION_SLOT=y" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="single_slot_absent",
            passed=no_single,
            expected="CONFIG_SINGLE_APPLICATION_SLOT not set (multi-image)",
            actual="not present" if no_single else "present (conflicts!)",
            check_type="constraint",
        )
    )

    return details
