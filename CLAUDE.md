# EmbedEval

Professional-grade LLM benchmark for embedded firmware development (Zephyr RTOS, FreeRTOS, Yocto/Embedded Linux).

## Project Context

- **Vault Project:** embedeval
- **Repository:** /home/noel/embedeval
- **TODO Sync:** Enabled
- **GitHub:** https://github.com/Ecro/embedeval

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.12+ |
| Package Manager | uv | latest |
| LLM Client | litellm | latest |
| CLI | typer | latest |
| Models | pydantic | v2 |
| Container | Docker | latest |
| Target SDKs | Zephyr RTOS, FreeRTOS, Yocto | various |
| CI | GitHub Actions | - |

## Project Structure

```
embedeval/
├── src/embedeval/       # Core library
│   ├── models.py        # Pydantic models (EvalResult, BenchmarkReport, etc.)
│   ├── evaluator.py     # 5-layer evaluation pipeline (L0-L4)
│   ├── runner.py        # Benchmark runner orchestration
│   ├── scorer.py        # Score aggregation (pass@1, pass@5, layer rates)
│   ├── reporter.py      # JSON + Markdown report generation
│   ├── llm_client.py    # LiteLLM wrapper with retry logic
│   └── cli.py           # Typer CLI (run, list, validate, report)
├── cases/               # Test cases (each case is a directory)
│   ├── kconfig-001/
│   ├── device-tree-001/
│   └── isr-concurrency-001/
├── tests/               # pytest test suite
├── docs/                # METHODOLOGY.md, CONTRIBUTING.md
└── .github/workflows/   # CI, case validation, benchmark dispatch
```

## Commands

| Command | Purpose |
|---------|---------|
| `uv run pytest` | Run all tests |
| `uv run ruff check src/ tests/` | Lint |
| `uv run ruff format src/ tests/` | Format |
| `uv run mypy src/` | Type check |
| `uv run embedeval --help` | CLI help |
| `uv run embedeval list --cases cases/` | List cases |
| `uv run embedeval validate --cases cases/` | Validate cases |

## Available Workflow Commands

- `/research` - Gather best practices, explore options
- `/myplan [task]` - Analyze, design, and plan implementation
- `/execute [task]` - Implement and test
- `/review [task]` - Code review and quality check
- `/wrapup [task]` - Finalize, commit, PR, and complete

## 20 Evaluation Categories

Platform-agnostic: `gpio-basic`, `spi-i2c`, `dma`, `isr-concurrency`, `threading`, `timer`, `sensor-driver`, `networking`, `ble`, `security`, `storage`

System-level: `kconfig`, `device-tree`, `boot`, `ota`, `power-mgmt`, `watchdog`

Platform-specific: `yocto`, `linux-driver`, `memory-opt`

## 5-Layer Evaluation Architecture

- **L0 Static**: Pattern matching, required includes, structure checks
- **L1 Compile**: Docker-based SDK compilation (west build, idf.py, make)
- **L2 Runtime**: QEMU/native_sim execution with timeout
- **L3 Behavioral**: Output validation against expected patterns
- **L4 Mutation**: Robustness testing with code mutations

## Boundaries

- NO placeholder code or TODO comments
- NO skipping tests
- NO adding dependencies without justification
- All new test cases must include reference solutions that pass all layers
