"""Static analysis checks for MCUboot Kconfig."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MCUboot Kconfig structure."""
    details: list[CheckDetail] = []
    lines = [
        line.strip()
        for line in generated_code.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

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

    has_mcuboot = any(
        "CONFIG_BOOTLOADER_MCUBOOT=y" in l or "CONFIG_MCUBOOT=y" in l
        for l in lines
    )
    details.append(
        CheckDetail(
            check_name="mcuboot_enabled",
            passed=has_mcuboot,
            expected="CONFIG_BOOTLOADER_MCUBOOT=y or CONFIG_MCUBOOT=y",
            actual="present" if has_mcuboot else "missing",
            check_type="exact_match",
        )
    )

    # Accept either IMG_MANAGER (subsys menuconfig) or MCUBOOT_IMG_MANAGER
    # (MCUboot-specific symbol that depends on IMG_MANAGER). Both are valid.
    has_img_mgr = any(
        "CONFIG_IMG_MANAGER=y" in l or "CONFIG_MCUBOOT_IMG_MANAGER=y" in l
        for l in lines
    )
    details.append(
        CheckDetail(
            check_name="img_manager_enabled",
            passed=has_img_mgr,
            expected="CONFIG_IMG_MANAGER=y or CONFIG_MCUBOOT_IMG_MANAGER=y",
            actual="present" if has_img_mgr else "missing",
            check_type="exact_match",
        )
    )

    has_flash = any("CONFIG_FLASH=y" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="flash_enabled",
            passed=has_flash,
            expected="CONFIG_FLASH=y",
            actual="present" if has_flash else "missing",
            check_type="exact_match",
        )
    )

    return details
