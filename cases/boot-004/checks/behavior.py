"""Behavioral checks for MCUboot Swap with Revert Kconfig."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MCUboot swap-revert Kconfig behavioral properties."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    # Check 1: SWAP_USING_MOVE and UPGRADE_ONLY conflict check
    has_swap = config.get("CONFIG_BOOT_SWAP_USING_MOVE") == "y"
    has_upgrade_only = config.get("CONFIG_BOOT_UPGRADE_ONLY") == "y"
    no_conflict = not (has_swap and has_upgrade_only)
    details.append(
        CheckDetail(
            check_name="no_swap_upgrade_only_conflict",
            passed=no_conflict,
            expected="SWAP_USING_MOVE and UPGRADE_ONLY must not both be set",
            actual="no conflict" if no_conflict else "CONFLICT: both set!",
            check_type="constraint",
        )
    )

    # Check 2: SWAP_USING_MOVE enabled
    details.append(
        CheckDetail(
            check_name="swap_using_move_enabled",
            passed=has_swap,
            expected="CONFIG_BOOT_SWAP_USING_MOVE=y",
            actual="present" if has_swap else "missing",
            check_type="constraint",
        )
    )

    # Check 3: MAX_IMG_SECTORS >= 128
    sectors_val = config.get("CONFIG_BOOT_MAX_IMG_SECTORS", "")
    sectors_ok = sectors_val.isdigit() and int(sectors_val) >= 128
    details.append(
        CheckDetail(
            check_name="max_img_sectors_sufficient",
            passed=sectors_ok,
            expected="CONFIG_BOOT_MAX_IMG_SECTORS >= 128",
            actual=f"CONFIG_BOOT_MAX_IMG_SECTORS={sectors_val!r}",
            check_type="constraint",
        )
    )

    # Check 4: SINGLE_APPLICATION_SLOT absent (requires dual slot)
    no_single = config.get("CONFIG_SINGLE_APPLICATION_SLOT") != "y"
    details.append(
        CheckDetail(
            check_name="no_single_application_slot",
            passed=no_single,
            expected="CONFIG_SINGLE_APPLICATION_SLOT not set (dual-slot required for swap)",
            actual="not set" if no_single else "set (breaks swap!)",
            check_type="constraint",
        )
    )

    # Check 5: FLASH enabled
    flash_ok = config.get("CONFIG_FLASH") == "y"
    details.append(
        CheckDetail(
            check_name="flash_enabled",
            passed=flash_ok,
            expected="CONFIG_FLASH=y for swap operations",
            actual="present" if flash_ok else "missing",
            check_type="constraint",
        )
    )

    return details
