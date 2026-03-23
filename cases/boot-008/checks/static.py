"""Static analysis checks for MCUboot Downgrade Protection Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MCUboot downgrade protection Kconfig fragment format and required options."""
    details: list[CheckDetail] = []
    lines = [
        line.strip()
        for line in generated_code.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    # Check 1: All lines use CONFIG_ prefix and contain =
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

    # Check 2: CONFIG_BOOTLOADER_MCUBOOT=y present
    has_mcuboot = any("CONFIG_BOOTLOADER_MCUBOOT=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="mcuboot_enabled",
            passed=has_mcuboot,
            expected="CONFIG_BOOTLOADER_MCUBOOT=y",
            actual="present" if has_mcuboot else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_BOOT_VERSION_CMP_USE_BUILD_NUMBER=y present
    has_build_num_cmp = any("CONFIG_BOOT_VERSION_CMP_USE_BUILD_NUMBER=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="boot_version_cmp_build_number_enabled",
            passed=has_build_num_cmp,
            expected="CONFIG_BOOT_VERSION_CMP_USE_BUILD_NUMBER=y",
            actual="present" if has_build_num_cmp else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_BOOT_VALIDATE_SLOT0=y present (required for downgrade protection)
    has_validate_slot0 = any("CONFIG_BOOT_VALIDATE_SLOT0=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="boot_validate_slot0_enabled",
            passed=has_validate_slot0,
            expected="CONFIG_BOOT_VALIDATE_SLOT0=y",
            actual="present" if has_validate_slot0 else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: CONFIG_SINGLE_APPLICATION_SLOT must NOT be present
    no_single_slot = not any("CONFIG_SINGLE_APPLICATION_SLOT=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="single_application_slot_absent",
            passed=no_single_slot,
            expected="CONFIG_SINGLE_APPLICATION_SLOT=y absent (incompatible with upgrade protection)",
            actual="not present" if no_single_slot else "present (conflicts with downgrade protection)",
            check_type="constraint",
        )
    )

    return details
