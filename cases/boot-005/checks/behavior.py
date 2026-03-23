"""Behavioral checks for Multi-image Boot Configuration Kconfig."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-image boot Kconfig behavioral properties."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    # Check 1: BOOT_IMAGE_NUMBER and UPDATEABLE_IMAGE_NUMBER are consistent
    image_num = config.get("CONFIG_BOOT_IMAGE_NUMBER", "")
    updateable_num = config.get("CONFIG_UPDATEABLE_IMAGE_NUMBER", "")
    both_present = bool(image_num) and bool(updateable_num)
    consistent = image_num == updateable_num and both_present
    details.append(
        CheckDetail(
            check_name="image_numbers_consistent",
            passed=consistent,
            expected="BOOT_IMAGE_NUMBER == UPDATEABLE_IMAGE_NUMBER (both 2)",
            actual=f"BOOT_IMAGE_NUMBER={image_num}, UPDATEABLE_IMAGE_NUMBER={updateable_num}",
            check_type="constraint",
        )
    )

    # Check 2: BOOT_IMAGE_NUMBER=2 (dual-core)
    image_num_ok = image_num == "2"
    details.append(
        CheckDetail(
            check_name="boot_image_number_2",
            passed=image_num_ok,
            expected="CONFIG_BOOT_IMAGE_NUMBER=2",
            actual=f"CONFIG_BOOT_IMAGE_NUMBER={image_num!r}",
            check_type="constraint",
        )
    )

    # Check 3: PCD_APP enabled for network core
    pcd_ok = config.get("CONFIG_PCD_APP") == "y"
    details.append(
        CheckDetail(
            check_name="pcd_app_enabled",
            passed=pcd_ok,
            expected="CONFIG_PCD_APP=y for network core update support",
            actual="present" if pcd_ok else "missing (network core updates won't work)",
            check_type="constraint",
        )
    )

    # Check 4: SINGLE_APPLICATION_SLOT absent
    no_single = config.get("CONFIG_SINGLE_APPLICATION_SLOT") != "y"
    details.append(
        CheckDetail(
            check_name="no_single_application_slot",
            passed=no_single,
            expected="CONFIG_SINGLE_APPLICATION_SLOT not set (incompatible with multi-image)",
            actual="not set" if no_single else "set (conflicts with multi-image!)",
            check_type="constraint",
        )
    )

    # Check 5: MCUboot enabled
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

    return details
