"""Behavioral checks for Zephyr Kconfig fragments (metamorphic properties)."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Kconfig dependency chains and config consistency."""
    details: list[CheckDetail] = []
    lines = [
        line.strip()
        for line in generated_code.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    config: dict[str, str] = {}
    for line in lines:
        if "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    # Metamorphic: If SPI is disabled, SPI_DMA must also be disabled
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

    # Check: DMA dependency
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

    # Check: all required configs present AND enabled
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

    return details
