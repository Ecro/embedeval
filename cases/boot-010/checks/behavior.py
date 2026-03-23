"""Behavioral checks for Basic MCUboot Logging Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate basic MCUboot logging Kconfig dependency chains and conflict invariants."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    mcuboot_enabled = config.get("CONFIG_BOOTLOADER_MCUBOOT") == "y"
    log_enabled = config.get("CONFIG_LOG") == "y"
    log_level_dbg_enabled = config.get("CONFIG_MCUBOOT_LOG_LEVEL_DBG") == "y"
    boot_banner_enabled = config.get("CONFIG_BOOT_BANNER") == "y"
    log_minimal_enabled = config.get("CONFIG_LOG_MINIMAL") == "y"

    # Metamorphic: MCUBOOT_LOG_LEVEL_DBG requires LOG=y
    log_level_needs_log = not (log_level_dbg_enabled and not log_enabled)
    details.append(
        CheckDetail(
            check_name="mcuboot_log_level_dbg_requires_log",
            passed=log_level_needs_log,
            expected="MCUBOOT_LOG_LEVEL_DBG requires LOG=y",
            actual=(
                f"LOG={config.get('CONFIG_LOG', 'n')}, "
                f"MCUBOOT_LOG_LEVEL_DBG={config.get('CONFIG_MCUBOOT_LOG_LEVEL_DBG', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Conflict: LOG_MINIMAL suppresses debug output — cannot coexist with LOG_LEVEL_DBG
    no_minimal_conflict = not (log_minimal_enabled and log_level_dbg_enabled)
    details.append(
        CheckDetail(
            check_name="log_minimal_log_level_dbg_mutual_exclusion",
            passed=no_minimal_conflict,
            expected="LOG_MINIMAL and MCUBOOT_LOG_LEVEL_DBG are incompatible",
            actual=(
                "no conflict"
                if no_minimal_conflict
                else "both LOG_MINIMAL=y and MCUBOOT_LOG_LEVEL_DBG=y set (LOG_MINIMAL suppresses debug)"
            ),
            check_type="constraint",
        )
    )

    # Summary: all required configs present
    required = [
        "CONFIG_BOOTLOADER_MCUBOOT",
        "CONFIG_LOG",
        "CONFIG_BOOT_BANNER",
        "CONFIG_MCUBOOT_LOG_LEVEL_DBG",
    ]
    all_present = all(config.get(k) == "y" for k in required)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="BOOTLOADER_MCUBOOT, LOG, BOOT_BANNER, MCUBOOT_LOG_LEVEL_DBG all =y",
            actual=str({k: config.get(k, "missing") for k in required}),
            check_type="exact_match",
        )
    )

    return details
