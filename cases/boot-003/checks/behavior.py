"""Behavioral checks for Secure Boot with Signing Kconfig."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate secure boot Kconfig behavioral properties."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    # Check 1: signature type specified (insecure without it)
    has_sig_type = config.get("CONFIG_BOOT_SIGNATURE_TYPE_RSA") == "y" or any(
        k.startswith("CONFIG_BOOT_SIGNATURE_TYPE_") and v == "y"
        for k, v in config.items()
    )
    details.append(
        CheckDetail(
            check_name="signature_type_set",
            passed=has_sig_type,
            expected="CONFIG_BOOT_SIGNATURE_TYPE_* set (e.g. RSA)",
            actual="present" if has_sig_type else "missing (insecure!)",
            check_type="constraint",
        )
    )

    # Check 2: key file specified
    key_file = config.get("CONFIG_BOOT_SIGNATURE_KEY_FILE", "")
    has_key_file = bool(key_file.strip('"').strip())
    details.append(
        CheckDetail(
            check_name="key_file_specified",
            passed=has_key_file,
            expected="CONFIG_BOOT_SIGNATURE_KEY_FILE=<path> non-empty",
            actual=f"value={key_file!r}" if key_file else "missing",
            check_type="constraint",
        )
    )

    # Check 3: slot0 validation enabled
    validate_slot0 = config.get("CONFIG_BOOT_VALIDATE_SLOT0") == "y"
    details.append(
        CheckDetail(
            check_name="validate_slot0_enabled",
            passed=validate_slot0,
            expected="CONFIG_BOOT_VALIDATE_SLOT0=y (secure: validate primary slot)",
            actual="enabled" if validate_slot0 else "disabled or missing (insecure!)",
            check_type="constraint",
        )
    )

    # Check 4: MCUboot enabled (required for signing)
    mcuboot_ok = config.get("CONFIG_BOOTLOADER_MCUBOOT") == "y"
    details.append(
        CheckDetail(
            check_name="mcuboot_enabled",
            passed=mcuboot_ok,
            expected="CONFIG_BOOTLOADER_MCUBOOT=y",
            actual="present" if mcuboot_ok else "missing",
            check_type="constraint",
        )
    )

    # Check 5: FLASH enabled (required for secure boot image storage)
    flash_ok = config.get("CONFIG_FLASH") == "y"
    details.append(
        CheckDetail(
            check_name="flash_enabled",
            passed=flash_ok,
            expected="CONFIG_FLASH=y for image storage",
            actual="present" if flash_ok else "missing",
            check_type="constraint",
        )
    )

    return details
