"""Behavioral checks for MCUboot Downgrade Protection Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MCUboot downgrade protection Kconfig dependency chains and invariants."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    mcuboot_enabled = config.get("CONFIG_BOOTLOADER_MCUBOOT") == "y"
    build_num_cmp_enabled = config.get("CONFIG_BOOT_VERSION_CMP_USE_BUILD_NUMBER") == "y"
    validate_slot0_enabled = config.get("CONFIG_BOOT_VALIDATE_SLOT0") == "y"
    upgrade_only_enabled = config.get("CONFIG_BOOT_UPGRADE_ONLY") == "y"
    single_slot_enabled = config.get("CONFIG_SINGLE_APPLICATION_SLOT") == "y"

    # Metamorphic: BOOT_VERSION_CMP_USE_BUILD_NUMBER is meaningful only with MCUboot
    build_num_needs_mcuboot = not (build_num_cmp_enabled and not mcuboot_enabled)
    details.append(
        CheckDetail(
            check_name="build_num_cmp_requires_mcuboot",
            passed=build_num_needs_mcuboot,
            expected="BOOT_VERSION_CMP_USE_BUILD_NUMBER requires BOOTLOADER_MCUBOOT=y",
            actual=(
                f"BOOTLOADER_MCUBOOT={config.get('CONFIG_BOOTLOADER_MCUBOOT', 'n')}, "
                f"BOOT_VERSION_CMP_USE_BUILD_NUMBER={config.get('CONFIG_BOOT_VERSION_CMP_USE_BUILD_NUMBER', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Behavioral: downgrade protection requires slot0 validation
    downgrade_needs_validate = not (build_num_cmp_enabled and not validate_slot0_enabled)
    details.append(
        CheckDetail(
            check_name="downgrade_protection_requires_slot0_validation",
            passed=downgrade_needs_validate,
            expected="BOOT_VERSION_CMP_USE_BUILD_NUMBER requires BOOT_VALIDATE_SLOT0=y",
            actual=(
                f"BOOT_VALIDATE_SLOT0={config.get('CONFIG_BOOT_VALIDATE_SLOT0', 'n')}, "
                f"BOOT_VERSION_CMP_USE_BUILD_NUMBER={config.get('CONFIG_BOOT_VERSION_CMP_USE_BUILD_NUMBER', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Constraint: SINGLE_APPLICATION_SLOT incompatible with upgrade protection
    no_single_slot = not single_slot_enabled
    details.append(
        CheckDetail(
            check_name="single_application_slot_absent",
            passed=no_single_slot,
            expected="CONFIG_SINGLE_APPLICATION_SLOT=y absent (incompatible with downgrade protection)",
            actual=(
                "not set"
                if no_single_slot
                else "CONFIG_SINGLE_APPLICATION_SLOT=y set (conflicts with downgrade protection)"
            ),
            check_type="constraint",
        )
    )

    # Summary: all required configs present
    required = [
        "CONFIG_BOOTLOADER_MCUBOOT",
        "CONFIG_BOOT_VALIDATE_SLOT0",
        "CONFIG_BOOT_VERSION_CMP_USE_BUILD_NUMBER",
    ]
    all_present = all(config.get(k) == "y" for k in required)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="BOOTLOADER_MCUBOOT, BOOT_VALIDATE_SLOT0, BOOT_VERSION_CMP_USE_BUILD_NUMBER all =y",
            actual=str({k: config.get(k, "missing") for k in required}),
            check_type="exact_match",
        )
    )

    return details
