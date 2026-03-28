"""Behavioral checks for Zephyr Kconfig fragments (metamorphic properties)."""

from embedeval.models import CheckDetail

# CONFIG options that LLMs commonly hallucinate (do not exist in Zephyr)
_HALLUCINATED_CONFIGS = [
    "CONFIG_SECURE_MODE",
    "CONFIG_WIFI_BLE_COEX",
    "CONFIG_DEBUG_ENABLE",
    "CONFIG_NETWORK_STACK",
    "CONFIG_AUTO_INIT",
]

# Deprecated option pair: CONFIG_NEWLIB_LIBC should not coexist with CONFIG_MINIMAL_LIBC
_DEPRECATED_CONFLICT = ("CONFIG_NEWLIB_LIBC", "CONFIG_MINIMAL_LIBC")


def _parse_config(generated_code: str) -> dict[str, str]:
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()
    return config


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Kconfig dependency chains and config consistency."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

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

    # Check 2: Deprecated option conflict — CONFIG_NEWLIB_LIBC with CONFIG_MINIMAL_LIBC
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

    # Check 3: Metamorphic: If SPI is disabled, SPI_DMA must also be disabled
    spi_enabled = config.get("CONFIG_SPI") == "y"
    spi_dma_enabled = config.get("CONFIG_SPI_DMA") == "y"
    dep_consistent = not (spi_dma_enabled and not spi_enabled)
    details.append(
        CheckDetail(
            check_name="dependency_chain_consistent",
            passed=dep_consistent,
            expected="SPI_DMA requires SPI=y",
            actual=(
                f"SPI={config.get('CONFIG_SPI', 'n')}, "
                f"SPI_DMA={config.get('CONFIG_SPI_DMA', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 4: DMA dependency
    dma_enabled = config.get("CONFIG_DMA") == "y"
    dma_dep_ok = not (spi_dma_enabled and not dma_enabled)
    details.append(
        CheckDetail(
            check_name="dma_dependency_chain",
            passed=dma_dep_ok,
            expected="SPI_DMA requires DMA=y",
            actual=(
                f"DMA={config.get('CONFIG_DMA', 'n')}, "
                f"SPI_DMA={config.get('CONFIG_SPI_DMA', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 5: All required configs present AND enabled
    required_configs = ["CONFIG_SPI", "CONFIG_DMA", "CONFIG_SPI_DMA"]
    all_present = all(config.get(k) == "y" for k in required_configs)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="SPI, DMA, SPI_DMA all =y",
            actual=str({k: config.get(k, "missing") for k in required_configs}),
            check_type="exact_match",
        )
    )

    # Check 6: No conflicting configs enabled simultaneously — Factor E3 Build system
    # CONFIG_SPI_SLAVE conflicts with SPI master mode
    has_conflict = config.get("CONFIG_SPI_SLAVE") == "y" and config.get("CONFIG_SPI") == "y"
    details.append(CheckDetail(
        check_name="no_conflicting_configs",
        passed=not has_conflict,
        expected="No mutually exclusive CONFIG options both enabled",
        actual="clean" if not has_conflict else "CONFIG_SPI_SLAVE conflicts with SPI master mode",
        check_type="constraint",
    ))

    # Check 7: Dependency chain complete (SPI with DMA requires CONFIG_DMA) — Factor E3 Build system
    has_spi_dma = config.get("CONFIG_SPI_DMA") == "y"
    dma_present = config.get("CONFIG_DMA") == "y"
    dep_complete = not has_spi_dma or dma_present
    details.append(CheckDetail(
        check_name="dependency_chain_complete",
        passed=dep_complete,
        expected="SPI with DMA requires CONFIG_DMA dependency",
        actual="dependencies satisfied" if dep_complete else "CONFIG_DMA missing for SPI DMA mode",
        check_type="constraint",
    ))

    return details
