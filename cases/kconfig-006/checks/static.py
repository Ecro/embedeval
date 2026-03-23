"""Static analysis checks for Zephyr Secure Boot Hardening Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate secure boot hardening Kconfig fragment format and required options."""
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

    # Check 2: CONFIG_STACK_CANARIES=y present
    has_canaries = any("CONFIG_STACK_CANARIES=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="stack_canaries_enabled",
            passed=has_canaries,
            expected="CONFIG_STACK_CANARIES=y",
            actual="present" if has_canaries else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_HW_STACK_PROTECTION=y present
    has_hw_stack = any("CONFIG_HW_STACK_PROTECTION=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="hw_stack_protection_enabled",
            passed=has_hw_stack,
            expected="CONFIG_HW_STACK_PROTECTION=y",
            actual="present" if has_hw_stack else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_SECURE_BOOT=y present
    has_secure_boot = any("CONFIG_SECURE_BOOT=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="secure_boot_enabled",
            passed=has_secure_boot,
            expected="CONFIG_SECURE_BOOT=y",
            actual="present" if has_secure_boot else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: CONFIG_DEBUG=y must NOT be present (production hardening)
    no_debug = not any(line == "CONFIG_DEBUG=y" for line in lines)
    details.append(
        CheckDetail(
            check_name="debug_not_enabled",
            passed=no_debug,
            expected="CONFIG_DEBUG=y absent in production config",
            actual="not present" if no_debug else "CONFIG_DEBUG=y found (security risk)",
            check_type="constraint",
        )
    )

    # Check 6: CONFIG_ASSERT=y must NOT be present
    no_assert = not any("CONFIG_ASSERT=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="assert_not_enabled",
            passed=no_assert,
            expected="CONFIG_ASSERT=y absent in production config",
            actual="not present" if no_assert else "CONFIG_ASSERT=y found (exposes internals)",
            check_type="constraint",
        )
    )

    # Check 7: Hallucination trap — CONFIG_SECURE_MODE does not exist in Zephyr
    no_fake_secure_mode = not any("CONFIG_SECURE_MODE=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="no_hallucinated_secure_mode",
            passed=no_fake_secure_mode,
            expected="CONFIG_SECURE_MODE not present (does not exist in Zephyr)",
            actual="not present" if no_fake_secure_mode else "CONFIG_SECURE_MODE=y found (hallucinated config)",
            check_type="constraint",
        )
    )

    return details
