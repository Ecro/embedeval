"""Behavioral checks for U-Boot Environment Kconfig."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate U-Boot Kconfig behavioral properties."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    # Check 1: MCUboot not enabled (U-Boot path, no mixing)
    no_mcuboot = config.get("CONFIG_BOOTLOADER_MCUBOOT") != "y"
    details.append(
        CheckDetail(
            check_name="no_mcuboot_mixing",
            passed=no_mcuboot,
            expected="CONFIG_BOOTLOADER_MCUBOOT not enabled for U-Boot path",
            actual="not set" if no_mcuboot else "set (conflicts with U-Boot!)",
            check_type="constraint",
        )
    )

    # Check 2: BOOT_DELAY is a positive integer
    boot_delay_val = config.get("CONFIG_BOOT_DELAY", "")
    boot_delay_ok = boot_delay_val.isdigit() and int(boot_delay_val) > 0
    details.append(
        CheckDetail(
            check_name="boot_delay_positive",
            passed=boot_delay_ok,
            expected="CONFIG_BOOT_DELAY=<positive integer>",
            actual=f"CONFIG_BOOT_DELAY={boot_delay_val!r}",
            check_type="constraint",
        )
    )

    # Check 3: CMD_ENV enabled
    cmd_env_ok = config.get("CONFIG_CMD_ENV") == "y"
    details.append(
        CheckDetail(
            check_name="cmd_env_enabled",
            passed=cmd_env_ok,
            expected="CONFIG_CMD_ENV=y",
            actual=f"CONFIG_CMD_ENV={config.get('CONFIG_CMD_ENV', 'missing')}",
            check_type="constraint",
        )
    )

    # Check 4: No MCUboot-specific options mixed in
    no_img_mgr = config.get("CONFIG_MCUBOOT_IMG_MANAGER") != "y"
    details.append(
        CheckDetail(
            check_name="no_mcuboot_img_manager",
            passed=no_img_mgr,
            expected="CONFIG_MCUBOOT_IMG_MANAGER not set (U-Boot path)",
            actual="not set" if no_img_mgr else "set (wrong bootloader mix!)",
            check_type="constraint",
        )
    )

    return details
