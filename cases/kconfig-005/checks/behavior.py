"""Behavioral checks for Zephyr TLS networking Kconfig fragment (metamorphic properties)."""

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
    """Validate TLS Kconfig deep dependency chains and backend conflict invariants."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    networking_enabled = config.get("CONFIG_NETWORKING") == "y"
    sockets_enabled = config.get("CONFIG_NET_SOCKETS") == "y"
    tls_sockopt_enabled = config.get("CONFIG_NET_SOCKETS_SOCKOPT_TLS") == "y"
    tls_creds_enabled = config.get("CONFIG_TLS_CREDENTIALS") == "y"
    mbedtls_enabled = config.get("CONFIG_MBEDTLS") == "y"
    mbedtls_builtin_enabled = config.get("CONFIG_MBEDTLS_BUILTIN") == "y"
    mbedtls_external_enabled = config.get("CONFIG_MBEDTLS_EXTERNAL") == "y"

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

    # Check 3: Strict dependency chain: NET_SOCKETS -> NETWORKING -> NET_SOCKETS_SOCKOPT_TLS
    sockets_requires_networking = not (sockets_enabled and not networking_enabled)
    details.append(
        CheckDetail(
            check_name="sockets_requires_networking",
            passed=sockets_requires_networking,
            expected="NET_SOCKETS requires NETWORKING=y",
            actual=(
                f"NETWORKING={config.get('CONFIG_NETWORKING', 'n')}, "
                f"NET_SOCKETS={config.get('CONFIG_NET_SOCKETS', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 4: NET_SOCKETS_SOCKOPT_TLS requires NET_SOCKETS=y
    tls_sockopt_requires_sockets = not (tls_sockopt_enabled and not sockets_enabled)
    details.append(
        CheckDetail(
            check_name="tls_sockopt_requires_net_sockets",
            passed=tls_sockopt_requires_sockets,
            expected="NET_SOCKETS_SOCKOPT_TLS requires NET_SOCKETS=y",
            actual=(
                f"NET_SOCKETS={config.get('CONFIG_NET_SOCKETS', 'n')}, "
                f"NET_SOCKETS_SOCKOPT_TLS={config.get('CONFIG_NET_SOCKETS_SOCKOPT_TLS', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 5: MBEDTLS_BUILTIN requires MBEDTLS=y
    builtin_requires_mbedtls = not (mbedtls_builtin_enabled and not mbedtls_enabled)
    details.append(
        CheckDetail(
            check_name="mbedtls_builtin_requires_mbedtls",
            passed=builtin_requires_mbedtls,
            expected="MBEDTLS_BUILTIN requires MBEDTLS=y",
            actual=(
                f"MBEDTLS={config.get('CONFIG_MBEDTLS', 'n')}, "
                f"MBEDTLS_BUILTIN={config.get('CONFIG_MBEDTLS_BUILTIN', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 6: Mutual exclusion: MBEDTLS_BUILTIN and MBEDTLS_EXTERNAL cannot both be enabled
    no_backend_conflict = not (mbedtls_builtin_enabled and mbedtls_external_enabled)
    details.append(
        CheckDetail(
            check_name="mbedtls_backend_mutual_exclusion",
            passed=no_backend_conflict,
            expected="MBEDTLS_BUILTIN and MBEDTLS_EXTERNAL are mutually exclusive",
            actual=(
                f"MBEDTLS_BUILTIN={config.get('CONFIG_MBEDTLS_BUILTIN', 'n')}, "
                f"MBEDTLS_EXTERNAL={config.get('CONFIG_MBEDTLS_EXTERNAL', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 7: TLS_CREDENTIALS requires MBEDTLS=y
    tls_creds_has_backend = not (tls_creds_enabled and not mbedtls_enabled)
    details.append(
        CheckDetail(
            check_name="tls_credentials_requires_crypto_backend",
            passed=tls_creds_has_backend,
            expected="TLS_CREDENTIALS requires MBEDTLS=y (or equivalent backend)",
            actual=(
                f"TLS_CREDENTIALS={config.get('CONFIG_TLS_CREDENTIALS', 'n')}, "
                f"MBEDTLS={config.get('CONFIG_MBEDTLS', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 8: All required configs present AND enabled
    required_configs = [
        "CONFIG_NETWORKING",
        "CONFIG_NET_SOCKETS",
        "CONFIG_NET_SOCKETS_SOCKOPT_TLS",
        "CONFIG_TLS_CREDENTIALS",
        "CONFIG_MBEDTLS",
        "CONFIG_MBEDTLS_BUILTIN",
    ]
    all_present = all(config.get(k) == "y" for k in required_configs)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="NETWORKING, NET_SOCKETS, NET_SOCKETS_SOCKOPT_TLS, TLS_CREDENTIALS, MBEDTLS, MBEDTLS_BUILTIN all =y",
            actual=str({k: config.get(k, "missing") for k in required_configs}),
            check_type="exact_match",
        )
    )

    return details
