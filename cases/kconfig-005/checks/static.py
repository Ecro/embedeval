"""Static analysis checks for Zephyr TLS networking Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate TLS networking Kconfig fragment format and required options."""
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

    # Check 2: CONFIG_NETWORKING=y present
    has_networking = any("CONFIG_NETWORKING=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="networking_enabled",
            passed=has_networking,
            expected="CONFIG_NETWORKING=y",
            actual="present" if has_networking else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_NET_SOCKETS=y present
    has_sockets = any("CONFIG_NET_SOCKETS=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="net_sockets_enabled",
            passed=has_sockets,
            expected="CONFIG_NET_SOCKETS=y",
            actual="present" if has_sockets else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_NET_SOCKETS_SOCKOPT_TLS=y present
    has_tls_sockopt = any("CONFIG_NET_SOCKETS_SOCKOPT_TLS=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="net_sockets_sockopt_tls_enabled",
            passed=has_tls_sockopt,
            expected="CONFIG_NET_SOCKETS_SOCKOPT_TLS=y",
            actual="present" if has_tls_sockopt else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: CONFIG_TLS_CREDENTIALS=y present
    has_tls_creds = any("CONFIG_TLS_CREDENTIALS=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="tls_credentials_enabled",
            passed=has_tls_creds,
            expected="CONFIG_TLS_CREDENTIALS=y",
            actual="present" if has_tls_creds else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: CONFIG_MBEDTLS=y present
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

    # Check 7: CONFIG_MBEDTLS_BUILTIN=y present
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

    # Check 8: No conflicting TLS backend (MBEDTLS_EXTERNAL conflicts with BUILTIN)
    no_external_backend = not any(
        "CONFIG_MBEDTLS_EXTERNAL=y" in line for line in lines
    )
    details.append(
        CheckDetail(
            check_name="no_conflicting_tls_backend",
            passed=no_external_backend,
            expected="CONFIG_MBEDTLS_EXTERNAL not enabled alongside MBEDTLS_BUILTIN",
            actual=(
                "not present" if no_external_backend else "CONFIG_MBEDTLS_EXTERNAL=y found"
            ),
            check_type="constraint",
        )
    )

    return details
