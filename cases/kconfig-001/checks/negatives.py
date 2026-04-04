"""Negative tests for Zephyr Kconfig fragment with SPI+DMA.

Reference: cases/kconfig-001/reference/main.c (Kconfig fragment)
Checks:    cases/kconfig-001/checks/static.py

The reference fragment:
    CONFIG_SPI=y
    CONFIG_DMA=y
    CONFIG_SPI_DMA=y

The static checks verify each CONFIG_ line is present individually:
  spi_enabled      → CONFIG_SPI=y
  dma_enabled      → CONFIG_DMA=y
  spi_dma_enabled  → CONFIG_SPI_DMA=y

Mutation strategy
-----------------
* missing_spi_config     : remove CONFIG_SPI=y → spi_enabled fails
* missing_spi_dma_config : remove CONFIG_SPI_DMA=y → spi_dma_enabled fails
"""


def _remove_lines(code: str, pattern: str) -> str:
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_spi_config",
        "description": (
            "CONFIG_SPI=y omitted — SPI subsystem disabled, "
            "SPI transfers will fail at runtime"
        ),
        "mutation": lambda code: _remove_lines(code, "CONFIG_SPI=y"),
        "must_fail": ["spi_enabled"],
    },
    {
        "name": "missing_spi_dma_config",
        "description": (
            "CONFIG_SPI_DMA=y omitted — SPI DMA transfers disabled, "
            "driver falls back to PIO mode or fails"
        ),
        "mutation": lambda code: _remove_lines(code, "CONFIG_SPI_DMA=y"),
        "must_fail": ["spi_dma_enabled"],
    },
]
