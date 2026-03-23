"""Static analysis checks for Zephyr Memory Protection Unit Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MPU/USERSPACE Kconfig fragment format and required options."""
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
            expected="All lines start with CONFIG_ and contain =",
            actual=f"{len(lines)} lines, format valid: {valid_format}",
            check_type="exact_match",
        )
    )

    # Check 2: CONFIG_USERSPACE=y present
    has_userspace = any("CONFIG_USERSPACE=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="userspace_enabled",
            passed=has_userspace,
            expected="CONFIG_USERSPACE=y",
            actual="present" if has_userspace else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_MPU=y present
    has_mpu = any("CONFIG_MPU=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="mpu_enabled",
            passed=has_mpu,
            expected="CONFIG_MPU=y",
            actual="present" if has_mpu else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_ARM_MPU=y present (ARM platform implementation)
    has_arm_mpu = any("CONFIG_ARM_MPU=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="arm_mpu_enabled",
            passed=has_arm_mpu,
            expected="CONFIG_ARM_MPU=y",
            actual="present" if has_arm_mpu else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: CONFIG_ARC_MPU=y must NOT appear alongside CONFIG_ARM_MPU=y
    has_arc_mpu = any("CONFIG_ARC_MPU=y" in line for line in lines)
    no_mpu_conflict = not (has_arm_mpu and has_arc_mpu)
    details.append(
        CheckDetail(
            check_name="no_mpu_platform_conflict",
            passed=no_mpu_conflict,
            expected="CONFIG_ARM_MPU and CONFIG_ARC_MPU not both enabled",
            actual="no conflict" if no_mpu_conflict else "CONFIG_ARM_MPU and CONFIG_ARC_MPU both set (conflict)",
            check_type="constraint",
        )
    )

    # Check 6: HEAP_MEM_POOL_SIZE or MAX_DOMAIN_PARTITIONS should be set
    has_heap_or_partitions = any(
        "CONFIG_HEAP_MEM_POOL_SIZE=" in line or "CONFIG_MAX_DOMAIN_PARTITIONS=" in line
        for line in lines
    )
    details.append(
        CheckDetail(
            check_name="memory_sizing_configured",
            passed=has_heap_or_partitions,
            expected="CONFIG_HEAP_MEM_POOL_SIZE or CONFIG_MAX_DOMAIN_PARTITIONS configured",
            actual="present" if has_heap_or_partitions else "missing (userspace needs memory sizing)",
            check_type="exact_match",
        )
    )

    return details
