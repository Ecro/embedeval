"""Behavioral checks for MCUboot Kconfig."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MCUboot Kconfig behavioral properties."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    # Check 1: MCUboot IMG_MANAGER requires IMG_MANAGER
    mcuboot_img = config.get("CONFIG_MCUBOOT_IMG_MANAGER") == "y"
    img_mgr = config.get("CONFIG_IMG_MANAGER") == "y"
    dep_ok = not mcuboot_img or img_mgr
    details.append(
        CheckDetail(
            check_name="img_manager_dependency",
            passed=dep_ok,
            expected="MCUBOOT_IMG_MANAGER requires IMG_MANAGER=y",
            actual=f"MCUBOOT_IMG_MANAGER={mcuboot_img}, IMG_MANAGER={img_mgr}",
            check_type="constraint",
        )
    )

    # Check 2: No UPGRADE_ONLY (preserves rollback capability)
    no_upgrade_only = config.get("CONFIG_BOOT_UPGRADE_ONLY") != "y"
    details.append(
        CheckDetail(
            check_name="no_upgrade_only",
            passed=no_upgrade_only,
            expected="CONFIG_BOOT_UPGRADE_ONLY not set (swap mode)",
            actual="not set" if no_upgrade_only else "set (no rollback!)",
            check_type="constraint",
        )
    )

    # Check 3: No SINGLE_APPLICATION_SLOT
    no_single = config.get("CONFIG_SINGLE_APPLICATION_SLOT") != "y"
    details.append(
        CheckDetail(
            check_name="no_single_slot",
            passed=no_single,
            expected="CONFIG_SINGLE_APPLICATION_SLOT not set",
            actual="not set" if no_single else "set (breaks swap)",
            check_type="constraint",
        )
    )

    # Check 4: FLASH enabled (required for image storage)
    flash_ok = config.get("CONFIG_FLASH") == "y"
    details.append(
        CheckDetail(
            check_name="flash_dependency",
            passed=flash_ok,
            expected="CONFIG_FLASH=y for image storage",
            actual="present" if flash_ok else "missing",
            check_type="constraint",
        )
    )

    return details
