"""Static analysis checks for Zephyr Hardware Crypto Acceleration Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate hardware crypto Kconfig fragment format and required options."""
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

    # Check 2: CONFIG_MBEDTLS=y present
    has_mbedtls = any("CONFIG_MBEDTLS=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="mbedtls_enabled",
            passed=has_mbedtls,
            expected="CONFIG_MBEDTLS=y",
            actual="present" if has_mbedtls else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_MBEDTLS_BUILTIN=y present
    has_mbedtls_builtin = any("CONFIG_MBEDTLS_BUILTIN=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="mbedtls_builtin_enabled",
            passed=has_mbedtls_builtin,
            expected="CONFIG_MBEDTLS_BUILTIN=y",
            actual="present" if has_mbedtls_builtin else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_MBEDTLS_PSA_CRYPTO_C=y present
    has_psa = any("CONFIG_MBEDTLS_PSA_CRYPTO_C=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="mbedtls_psa_crypto_enabled",
            passed=has_psa,
            expected="CONFIG_MBEDTLS_PSA_CRYPTO_C=y",
            actual="present" if has_psa else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: CONFIG_HW_CC3XX=y present (hardware acceleration)
    has_hw_cc3xx = any("CONFIG_HW_CC3XX=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="hw_cc3xx_enabled",
            passed=has_hw_cc3xx,
            expected="CONFIG_HW_CC3XX=y",
            actual="present" if has_hw_cc3xx else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: CONFIG_TINYCRYPT must NOT be present (conflicts with MbedTLS)
    no_tinycrypt = not any(
        line.startswith("CONFIG_TINYCRYPT") and line.endswith("=y")
        for line in lines
    )
    details.append(
        CheckDetail(
            check_name="no_tinycrypt_conflict",
            passed=no_tinycrypt,
            expected="CONFIG_TINYCRYPT* not enabled (conflicts with MbedTLS backend)",
            actual="not present" if no_tinycrypt else "CONFIG_TINYCRYPT* found (conflicts with MbedTLS)",
            check_type="constraint",
        )
    )

    # Check 7: CONFIG_MBEDTLS_EXTERNAL must NOT appear alongside CONFIG_MBEDTLS_BUILTIN
    has_mbedtls_external = any("CONFIG_MBEDTLS_EXTERNAL=y" in line for line in lines)
    no_backend_conflict = not (has_mbedtls_builtin and has_mbedtls_external)
    details.append(
        CheckDetail(
            check_name="no_mbedtls_backend_conflict",
            passed=no_backend_conflict,
            expected="CONFIG_MBEDTLS_EXTERNAL and CONFIG_MBEDTLS_BUILTIN are mutually exclusive",
            actual="no conflict" if no_backend_conflict else "both MBEDTLS_BUILTIN and MBEDTLS_EXTERNAL set",
            check_type="constraint",
        )
    )

    return details
