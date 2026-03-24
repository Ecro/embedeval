"""Behavioral checks for Zephyr Secure Boot Hardening Kconfig fragment."""

from embedeval.models import CheckDetail

_HALLUCINATED_CONFIGS = [
    "CONFIG_SECURE_MODE",       # Does not exist in Zephyr
    "CONFIG_WIFI_BLE_COEX",    # Wrong name
    "CONFIG_DEBUG_ENABLE",     # Does not exist, use CONFIG_DEBUG
    "CONFIG_NETWORK_STACK",    # Does not exist
    "CONFIG_AUTO_INIT",        # Does not exist
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
    """Validate secure boot Kconfig dependency chains and security invariants."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    secure_boot_enabled = config.get("CONFIG_SECURE_BOOT") == "y"
    fw_info_enabled = config.get("CONFIG_FW_INFO") == "y"
    stack_canaries_enabled = config.get("CONFIG_STACK_CANARIES") == "y"
    hw_stack_enabled = config.get("CONFIG_HW_STACK_PROTECTION") == "y"
    debug_enabled = config.get("CONFIG_DEBUG") == "y"
    assert_enabled = config.get("CONFIG_ASSERT") == "y"
    debug_opts_enabled = config.get("CONFIG_DEBUG_OPTIMIZATIONS") == "y"

    # Check 1: No hallucinated CONFIG options (enhanced: checks all known fakes)
    found_hallucinated = [opt for opt in _HALLUCINATED_CONFIGS if opt in generated_code]
    details.append(
        CheckDetail(
            check_name="no_hallucinated_config_options",
            passed=not found_hallucinated,
            expected="No hallucinated Zephyr CONFIG options (e.g. CONFIG_SECURE_MODE does not exist)",
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

    # Check 3: SECURE_BOOT requires FW_INFO=y
    secure_boot_needs_fw_info = not (secure_boot_enabled and not fw_info_enabled)
    details.append(
        CheckDetail(
            check_name="secure_boot_requires_fw_info",
            passed=secure_boot_needs_fw_info,
            expected="SECURE_BOOT requires FW_INFO=y",
            actual=(
                f"SECURE_BOOT={config.get('CONFIG_SECURE_BOOT', 'n')}, "
                f"FW_INFO={config.get('CONFIG_FW_INFO', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 4: Security invariant: debug options absent in production hardened config
    no_debug_in_production = not debug_enabled
    details.append(
        CheckDetail(
            check_name="no_debug_in_production",
            passed=no_debug_in_production,
            expected="CONFIG_DEBUG=y absent (production security hardening)",
            actual=(
                "CONFIG_DEBUG not set"
                if no_debug_in_production
                else "CONFIG_DEBUG=y present (security risk in production)"
            ),
            check_type="constraint",
        )
    )

    # Check 5: Security invariant: assert absent in production
    no_assert_in_production = not assert_enabled
    details.append(
        CheckDetail(
            check_name="no_assert_in_production",
            passed=no_assert_in_production,
            expected="CONFIG_ASSERT=y absent (exposes internal state in production)",
            actual=(
                "CONFIG_ASSERT not set"
                if no_assert_in_production
                else "CONFIG_ASSERT=y present (may expose internal state)"
            ),
            check_type="constraint",
        )
    )

    # Check 6: Both stack protections enabled together for defense-in-depth
    both_stack_protections = stack_canaries_enabled and hw_stack_enabled
    details.append(
        CheckDetail(
            check_name="defense_in_depth_stack_protection",
            passed=both_stack_protections,
            expected="Both STACK_CANARIES=y and HW_STACK_PROTECTION=y for defense-in-depth",
            actual=(
                f"STACK_CANARIES={config.get('CONFIG_STACK_CANARIES', 'n')}, "
                f"HW_STACK_PROTECTION={config.get('CONFIG_HW_STACK_PROTECTION', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 7: Security invariant: debug build flags absent
    no_debug_opts = not debug_opts_enabled
    details.append(
        CheckDetail(
            check_name="no_debug_optimizations_in_production",
            passed=no_debug_opts,
            expected="CONFIG_DEBUG_OPTIMIZATIONS=y absent in hardened production config",
            actual=(
                "not present"
                if no_debug_opts
                else "CONFIG_DEBUG_OPTIMIZATIONS=y found (disables compiler optimizations)"
            ),
            check_type="constraint",
        )
    )

    # Check 8: All required security configs present
    required = ["CONFIG_STACK_CANARIES", "CONFIG_HW_STACK_PROTECTION", "CONFIG_SECURE_BOOT"]
    all_present = all(config.get(k) == "y" for k in required)
    details.append(
        CheckDetail(
            check_name="all_required_security_configs_enabled",
            passed=all_present,
            expected="STACK_CANARIES, HW_STACK_PROTECTION, SECURE_BOOT all =y",
            actual=str({k: config.get(k, "missing") for k in required}),
            check_type="exact_match",
        )
    )

    return details
