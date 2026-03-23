"""Behavioral checks for Zephyr Hardware Crypto Acceleration Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate hardware crypto Kconfig PSA dependency chain and backend exclusion invariants."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    mbedtls_enabled = config.get("CONFIG_MBEDTLS") == "y"
    mbedtls_builtin_enabled = config.get("CONFIG_MBEDTLS_BUILTIN") == "y"
    mbedtls_external_enabled = config.get("CONFIG_MBEDTLS_EXTERNAL") == "y"
    psa_enabled = config.get("CONFIG_MBEDTLS_PSA_CRYPTO_C") == "y"
    psa_driver_cc3xx = config.get("CONFIG_PSA_CRYPTO_DRIVER_CC3XX") == "y"
    hw_cc3xx_enabled = config.get("CONFIG_HW_CC3XX") == "y"
    tinycrypt_keys = [k for k in config if k.startswith("CONFIG_TINYCRYPT") and config[k] == "y"]

    # Metamorphic: MBEDTLS_BUILTIN requires MBEDTLS=y
    builtin_needs_mbedtls = not (mbedtls_builtin_enabled and not mbedtls_enabled)
    details.append(
        CheckDetail(
            check_name="mbedtls_builtin_requires_mbedtls",
            passed=builtin_needs_mbedtls,
            expected="MBEDTLS_BUILTIN requires MBEDTLS=y",
            actual=(
                f"MBEDTLS={config.get('CONFIG_MBEDTLS', 'n')}, "
                f"MBEDTLS_BUILTIN={config.get('CONFIG_MBEDTLS_BUILTIN', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Metamorphic: PSA_CRYPTO_C requires MBEDTLS=y
    psa_needs_mbedtls = not (psa_enabled and not mbedtls_enabled)
    details.append(
        CheckDetail(
            check_name="psa_crypto_requires_mbedtls",
            passed=psa_needs_mbedtls,
            expected="MBEDTLS_PSA_CRYPTO_C requires MBEDTLS=y",
            actual=(
                f"MBEDTLS={config.get('CONFIG_MBEDTLS', 'n')}, "
                f"MBEDTLS_PSA_CRYPTO_C={config.get('CONFIG_MBEDTLS_PSA_CRYPTO_C', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Metamorphic: HW_CC3XX requires PSA_CRYPTO_DRIVER_CC3XX=y
    hw_cc3xx_needs_driver = not (hw_cc3xx_enabled and not psa_driver_cc3xx)
    details.append(
        CheckDetail(
            check_name="hw_cc3xx_requires_psa_driver",
            passed=hw_cc3xx_needs_driver,
            expected="HW_CC3XX requires PSA_CRYPTO_DRIVER_CC3XX=y",
            actual=(
                f"PSA_CRYPTO_DRIVER_CC3XX={config.get('CONFIG_PSA_CRYPTO_DRIVER_CC3XX', 'n')}, "
                f"HW_CC3XX={config.get('CONFIG_HW_CC3XX', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Mutual exclusion: MBEDTLS_BUILTIN and MBEDTLS_EXTERNAL cannot coexist
    no_backend_conflict = not (mbedtls_builtin_enabled and mbedtls_external_enabled)
    details.append(
        CheckDetail(
            check_name="mbedtls_backend_mutual_exclusion",
            passed=no_backend_conflict,
            expected="MBEDTLS_BUILTIN and MBEDTLS_EXTERNAL are mutually exclusive",
            actual=(
                "no conflict"
                if no_backend_conflict
                else "both MBEDTLS_BUILTIN and MBEDTLS_EXTERNAL set"
            ),
            check_type="constraint",
        )
    )

    # Mutual exclusion: TinyCrypt conflicts with MbedTLS backend
    no_tinycrypt_conflict = len(tinycrypt_keys) == 0
    details.append(
        CheckDetail(
            check_name="no_tinycrypt_mbedtls_conflict",
            passed=no_tinycrypt_conflict,
            expected="CONFIG_TINYCRYPT* not enabled (conflicts with MbedTLS backend)",
            actual=(
                "no TinyCrypt configs"
                if no_tinycrypt_conflict
                else f"TinyCrypt configs found: {tinycrypt_keys}"
            ),
            check_type="constraint",
        )
    )

    # Summary: PSA hardware crypto chain all present
    required = [
        "CONFIG_MBEDTLS",
        "CONFIG_MBEDTLS_BUILTIN",
        "CONFIG_MBEDTLS_PSA_CRYPTO_C",
        "CONFIG_HW_CC3XX",
    ]
    all_present = all(config.get(k) == "y" for k in required)
    details.append(
        CheckDetail(
            check_name="all_required_crypto_configs_enabled",
            passed=all_present,
            expected="MBEDTLS, MBEDTLS_BUILTIN, MBEDTLS_PSA_CRYPTO_C, HW_CC3XX all =y",
            actual=str({k: config.get(k, "missing") for k in required}),
            check_type="exact_match",
        )
    )

    return details
