# EmbedEval

[![CI](https://img.shields.io/badge/CI-passing-brightgreen)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)]()

**Professional embedded firmware LLM code generation benchmark.**

While [SWE-bench](https://www.swebench.com/) evaluates LLMs on general software engineering tasks, EmbedEval focuses exclusively on **embedded firmware** — spanning Zephyr RTOS, FreeRTOS, and Yocto/Embedded Linux. It covers Kconfig, device trees, ISR concurrency, BLE stacks, kernel drivers, and more. Embedded firmware demands domain expertise that general-purpose benchmarks cannot measure: hardware register manipulation, real-time constraints, interrupt safety, and build-system configuration correctness.

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

EmbedEval covers **20 categories** across Zephyr RTOS, FreeRTOS, and Yocto/Embedded Linux:

**Platform-Agnostic Domains:**

| Category | Description | Platforms |
|----------|-------------|-----------|
| `gpio-basic` | GPIO, UART, ADC, PWM basic peripheral I/O | All |
| `spi-i2c` | SPI/I2C bus protocol communication | All |
| `dma` | DMA controller configuration and buffer management | All |
| `isr-concurrency` | Interrupt service routines and concurrency safety | All |
| `threading` | RTOS/OS threading, mutex, semaphore, message queue | All |
| `timer` | Hardware/software timers, RTC, periodic scheduling | All |
| `sensor-driver` | Sensor and device driver development | All |
| `networking` | Network stack configuration (TCP/UDP/MQTT/CoAP) | All |
| `ble` | Bluetooth Low Energy stack configuration | Zephyr/FreeRTOS |
| `security` | Crypto, TF-M, OP-TEE, PSA API | All |
| `storage` | NVS, settings, flash management, file systems | All |

**System-Level:**

| Category | Description | Platforms |
|----------|-------------|-----------|
| `kconfig` | Kconfig fragment generation | Zephyr/Linux |
| `device-tree` | Device tree overlay and binding authoring | Zephyr/Linux |
| `boot` | Bootloader configuration (MCUboot, U-Boot) | Zephyr/Linux |
| `ota` | Firmware update mechanisms (DFU, SWUpdate) | All |
| `power-mgmt` | Power management and sleep mode configuration | All |
| `watchdog` | Watchdog timer setup and feeding patterns | All |

**Platform-Specific:**

| Category | Description | Platforms |
|----------|-------------|-----------|
| `yocto` | Yocto/BitBake recipe and layer authoring | Embedded Linux |
| `linux-driver` | Linux kernel modules, char/platform/IIO drivers | Embedded Linux |
| `memory-opt` | Memory optimization and linker script tuning | All |

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
