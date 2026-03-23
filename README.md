# EmbedEval

[![CI](https://img.shields.io/badge/CI-passing-brightgreen)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)]()

**Professional embedded firmware LLM code generation benchmark.**

While [SWE-bench](https://www.swebench.com/) evaluates LLMs on general software engineering tasks, EmbedEval focuses exclusively on **embedded firmware** — Zephyr RTOS Kconfig, device trees, ISR concurrency, BLE stacks, and more. Embedded firmware demands domain expertise that general-purpose benchmarks cannot measure: hardware register manipulation, real-time constraints, interrupt safety, and build-system configuration correctness.

EmbedEval uses a rigorous **5-layer verification methodology** that goes far beyond "does it compile?" — catching the subtle bugs that matter in safety-critical embedded systems.

## Quick Start

```bash
# 1. Install
uv sync

# 2. Run benchmark (mock model for demo)
uv run embedeval run --model mock --cases cases/

# 3. View results
cat results/LEADERBOARD.md
```

## Leaderboard

| Rank | Model | pass@1 | pass@5 | Cases |
|------|-------|--------|--------|-------|
| 1 | — | — | — | — |
| 2 | — | — | — | — |
| 3 | — | — | — | — |

*Run `uv run embedeval run --model <your-model>` to add entries.*

## Supported Categories

EmbedEval covers **13 categories** of embedded firmware challenges:

| Category | Description |
|----------|-------------|
| `zephyr-kconfig` | Zephyr RTOS Kconfig fragment generation |
| `device-tree` | Device tree overlay and binding authoring |
| `dma` | DMA controller configuration and buffer management |
| `isr-concurrency` | Interrupt service routines and concurrency safety |
| `ble` | Bluetooth Low Energy stack configuration |
| `spi-i2c` | SPI/I2C peripheral driver implementation |
| `power-mgmt` | Power management and sleep mode configuration |
| `watchdog` | Watchdog timer setup and feeding patterns |
| `ota` | Over-the-air update mechanisms |
| `boot` | Bootloader and secure boot configuration |
| `yocto` | Yocto/BitBake recipe and layer authoring |
| `networking` | Network stack configuration (TCP/UDP/CoAP) |
| `memory-opt` | Memory optimization and linker script tuning |

## 5-Layer Evaluation Methodology

EmbedEval verifies generated code through five progressively deeper layers:

| Layer | Name | What It Catches |
|-------|------|-----------------|
| L0 | **Static Analysis** | Syntax errors, ISR safety violations, DT structure issues |
| L1 | **Compilation** | Build failures via `west build` |
| L2 | **Runtime** | Crashes and hangs under `native_sim` / QEMU |
| L3 | **Behavioral** | Domain-specific assertion failures and metamorphic property violations |
| L4 | **Mutation** | Weak test suites that pass broken code *(planned for v1.1)* |

Code must pass each layer sequentially. A failure at any layer stops evaluation — no credit for code that compiles but behaves incorrectly.

For full details, see [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## CLI Commands

```bash
embedeval run       # Run benchmark against an LLM
embedeval validate  # Validate reference solutions
embedeval report    # Generate leaderboard from results
embedeval list      # List available benchmark cases
```

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for how to add new evaluation cases.

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.
