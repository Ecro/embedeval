"""Behavioral checks for Zephyr Secure Boot Hardening Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate secure boot Kconfig dependency chains and security invariants."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    secure_boot_enabled = config.get("CONFIG_SECURE_BOOT") == "y"
    fw_info_enabled = config.get("CONFIG_FW_INFO") == "y"
    stack_canaries_enabled = config.get("CONFIG_STACK_CANARIES") == "y"
    hw_stack_enabled = config.get("CONFIG_HW_STACK_PROTECTION") == "y"
    debug_enabled = config.get("CONFIG_DEBUG") == "y"
    assert_enabled = config.get("CONFIG_ASSERT") == "y"
    fake_secure_mode = config.get("CONFIG_SECURE_MODE") == "y"
    debug_opts_enabled = config.get("CONFIG_DEBUG_OPTIMIZATIONS") == "y"

    # Metamorphic: SECURE_BOOT requires FW_INFO=y
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

    # Security invariant: debug options absent in production hardened config
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

    # Security invariant: assert absent in production
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

    # Hallucination invariant: CONFIG_SECURE_MODE does not exist
    no_hallucinated_config = not fake_secure_mode
    details.append(
        CheckDetail(
            check_name="no_hallucinated_secure_mode",
            passed=no_hallucinated_config,
            expected="CONFIG_SECURE_MODE not used (non-existent Zephyr option)",
            actual=(
                "not present"
                if no_hallucinated_config
                else "CONFIG_SECURE_MODE=y present (hallucinated — not a real Zephyr option)"
            ),
            check_type="constraint",
        )
    )

    # Behavioral: both stack protections enabled together for defense-in-depth
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

    # Security invariant: debug build flags absent
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

    # Summary: all required security configs present
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
