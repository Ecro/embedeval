"""Behavioral checks for Zephyr Memory Protection Unit Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MPU/USERSPACE Kconfig dependency chains and sizing invariants."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    userspace_enabled = config.get("CONFIG_USERSPACE") == "y"
    mpu_enabled = config.get("CONFIG_MPU") == "y"
    arm_mpu_enabled = config.get("CONFIG_ARM_MPU") == "y"
    arc_mpu_enabled = config.get("CONFIG_ARC_MPU") == "y"

    # Metamorphic: USERSPACE requires MPU=y
    userspace_needs_mpu = not (userspace_enabled and not mpu_enabled)
    details.append(
        CheckDetail(
            check_name="userspace_requires_mpu",
            passed=userspace_needs_mpu,
            expected="USERSPACE requires MPU=y",
            actual=(
                f"MPU={config.get('CONFIG_MPU', 'n')}, "
                f"USERSPACE={config.get('CONFIG_USERSPACE', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Metamorphic: MPU requires a platform-specific implementation
    mpu_has_impl = not (mpu_enabled and not (arm_mpu_enabled or arc_mpu_enabled))
    details.append(
        CheckDetail(
            check_name="mpu_has_platform_implementation",
            passed=mpu_has_impl,
            expected="MPU=y requires CONFIG_ARM_MPU=y or CONFIG_ARC_MPU=y",
            actual=(
                f"MPU={config.get('CONFIG_MPU', 'n')}, "
                f"ARM_MPU={config.get('CONFIG_ARM_MPU', 'n')}, "
                f"ARC_MPU={config.get('CONFIG_ARC_MPU', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Mutual exclusion: ARM_MPU and ARC_MPU cannot both be enabled
    no_mpu_conflict = not (arm_mpu_enabled and arc_mpu_enabled)
    details.append(
        CheckDetail(
            check_name="mpu_platform_mutual_exclusion",
            passed=no_mpu_conflict,
            expected="CONFIG_ARM_MPU and CONFIG_ARC_MPU are mutually exclusive",
            actual=(
                "no conflict"
                if no_mpu_conflict
                else "both ARM_MPU and ARC_MPU enabled (platform conflict)"
            ),
            check_type="constraint",
        )
    )

    # Behavioral: MAX_DOMAIN_PARTITIONS should be a positive integer when USERSPACE is enabled
    max_partitions_val = config.get("CONFIG_MAX_DOMAIN_PARTITIONS", "")
    partitions_ok = True
    if userspace_enabled and max_partitions_val:
        try:
            partitions_ok = int(max_partitions_val) >= 1
        except ValueError:
            partitions_ok = False
    details.append(
        CheckDetail(
            check_name="max_domain_partitions_positive",
            passed=partitions_ok,
            expected="CONFIG_MAX_DOMAIN_PARTITIONS >= 1 when USERSPACE enabled",
            actual=f"MAX_DOMAIN_PARTITIONS={max_partitions_val!r}",
            check_type="constraint",
        )
    )

    # Behavioral: HEAP_MEM_POOL_SIZE should be set and positive for user thread stacks
    heap_val = config.get("CONFIG_HEAP_MEM_POOL_SIZE", "")
    heap_ok = True
    if userspace_enabled and heap_val:
        try:
            heap_ok = int(heap_val) >= 1024
        except ValueError:
            heap_ok = False
    details.append(
        CheckDetail(
            check_name="heap_mem_pool_adequate",
            passed=heap_ok,
            expected="CONFIG_HEAP_MEM_POOL_SIZE >= 1024 for user thread stacks",
            actual=f"HEAP_MEM_POOL_SIZE={heap_val!r}",
            check_type="constraint",
        )
    )

    # Summary: all required configs present
    required = ["CONFIG_MPU", "CONFIG_ARM_MPU", "CONFIG_USERSPACE"]
    all_present = all(config.get(k) == "y" for k in required)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="MPU, ARM_MPU, USERSPACE all =y",
            actual=str({k: config.get(k, "missing") for k in required}),
            check_type="exact_match",
        )
    )

    return details
