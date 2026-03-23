"""Static analysis checks for MCUboot Swap with Revert Kconfig."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MCUboot swap-revert Kconfig structure."""
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

    # Check 3: SWAP_USING_MOVE enabled
    has_swap = any("CONFIG_BOOT_SWAP_USING_MOVE=y" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="swap_using_move_enabled",
            passed=has_swap,
            expected="CONFIG_BOOT_SWAP_USING_MOVE=y",
            actual="present" if has_swap else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: MAX_IMG_SECTORS set
    has_sectors = any("CONFIG_BOOT_MAX_IMG_SECTORS=" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="max_img_sectors_set",
            passed=has_sectors,
            expected="CONFIG_BOOT_MAX_IMG_SECTORS=<value>",
            actual="present" if has_sectors else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: UPGRADE_ONLY absent or not set to y
    no_upgrade_only = not any("CONFIG_BOOT_UPGRADE_ONLY=y" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="upgrade_only_absent",
            passed=no_upgrade_only,
            expected="CONFIG_BOOT_UPGRADE_ONLY not set (conflicts with swap)",
            actual="not present" if no_upgrade_only else "present (conflicts!)",
            check_type="constraint",
        )
    )

    return details
