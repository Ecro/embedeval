"""Behavioral checks for Zephyr Memory Protection Unit Kconfig fragment."""

from embedeval.models import CheckDetail

_HALLUCINATED_CONFIGS = [
    "CONFIG_SECURE_MODE",
    "CONFIG_WIFI_BLE_COEX",
    "CONFIG_DEBUG_ENABLE",
    "CONFIG_NETWORK_STACK",
    "CONFIG_AUTO_INIT",
]


def _parse_config(generated_code: str) -> dict[str, str]:
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()
    return config


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MPU/USERSPACE Kconfig dependency chains and sizing invariants."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    userspace_enabled = config.get("CONFIG_USERSPACE") == "y"
    mpu_enabled = config.get("CONFIG_MPU") == "y"
    arm_mpu_enabled = config.get("CONFIG_ARM_MPU") == "y"
    arc_mpu_enabled = config.get("CONFIG_ARC_MPU") == "y"

    # Check 1: No hallucinated CONFIG options
    found_hallucinated = [opt for opt in _HALLUCINATED_CONFIGS if opt in generated_code]
    details.append(
        CheckDetail(
            check_name="no_hallucinated_config_options",
            passed=not found_hallucinated,
            expected="No hallucinated Zephyr CONFIG options",
            actual="clean" if not found_hallucinated else f"hallucinated: {found_hallucinated}",
            check_type="hallucination",
        )
    )

    # Check 2: Deprecated option conflict check
    has_newlib = config.get("CONFIG_NEWLIB_LIBC") == "y"
    has_minimal = config.get("CONFIG_MINIMAL_LIBC") == "y"
    no_deprecated_conflict = not (has_newlib and has_minimal)
    details.append(
        CheckDetail(
            check_name="no_newlib_minimal_libc_conflict",
            passed=no_deprecated_conflict,
            expected="CONFIG_NEWLIB_LIBC and CONFIG_MINIMAL_LIBC are mutually exclusive",
            actual=(
                "no conflict"
                if no_deprecated_conflict
                else "both CONFIG_NEWLIB_LIBC=y and CONFIG_MINIMAL_LIBC=y present (conflict)"
            ),
            check_type="constraint",
        )
    )

    # Check 3: USERSPACE requires MPU=y
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

    # Check 4: MPU requires a platform-specific implementation
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

    # Check 5: Mutual exclusion: ARM_MPU and ARC_MPU cannot both be enabled
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

    # Check 6: MAX_DOMAIN_PARTITIONS should be a positive integer when USERSPACE is enabled
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

    # Check 7: HEAP_MEM_POOL_SIZE should be set and adequate for user thread stacks
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

    # Check 8: All required configs present
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

    # Check 9: No duplicate CONFIG_* keys with conflicting values
    # LLM failure: emits the same config option twice with different values (e.g. CONFIG_MPU=y then CONFIG_MPU=n)
    seen_keys: dict[str, list[str]] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            if key.startswith("CONFIG_"):
                seen_keys.setdefault(key, []).append(val)
    duplicates = {k: vals for k, vals in seen_keys.items() if len(set(vals)) > 1}
    no_duplicates = len(duplicates) == 0
    details.append(
        CheckDetail(
            check_name="no_conflicting_duplicate_config_keys",
            passed=no_duplicates,
            expected="Each CONFIG_* key appears at most once (no conflicting duplicate definitions)",
            actual="clean" if no_duplicates else f"conflicting duplicates: {duplicates}",
            check_type="constraint",
        )
    )

    return details
