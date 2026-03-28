# EmbedEval

[![CI](https://img.shields.io/badge/CI-passing-brightgreen)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)]()
[![Cases](https://img.shields.io/badge/cases-220-orange)]()
[![Tests](https://img.shields.io/badge/tests-818-green)]()

**LLM Embedded Domain Knowledge Probe.**

EmbedEval measures how well LLMs understand embedded firmware development — not just whether code compiles, but whether the LLM possesses the domain knowledge to write **safe** embedded code. It covers Zephyr RTOS, ESP-IDF, STM32 HAL + FreeRTOS, Linux kernel drivers, and Yocto recipes across 220 test cases.

Unlike [HumanEval](https://github.com/openai/human-eval) or [SWE-bench](https://www.swebench.com/) which test general coding, EmbedEval tests **implicit domain knowledge**: interrupt safety, cache coherency, DMA alignment, power management, and real-time constraints that only embedded experts would know — without telling the LLM what to do.

## Leaderboard

| Model | pass@1 | HumanEval | Embed Gap | Cases |
|-------|--------|-----------|-----------|-------|
| **Sonnet 4.6** | **89.5%** | 93.7% | **-4.2%p** | 220 |
| Haiku 4.5 | 78.1% | 84.0% | -5.9%p | 220 |

*Embed Gap = EmbedEval pass@1 − HumanEval pass@1. Negative = embedded is harder than general coding.*

### Category Breakdown (Sonnet vs Haiku)

```
Category          Sonnet   Haiku    Delta    Interpretation
────────────────  ───────  ───────  ───────  ──────────────────────
kconfig           100%     100%     0        Config generation — easy
boot              100%     100%     0        Kconfig fragments — easy
ble               100%      73%    -27%p     BLE stack API complexity
spi-i2c            92%      58%    -34%p     HW protocol knowledge
device-tree        90%      60%    -30%p     DT syntax confusion
isr-concurrency    80%      60%    -20%p     ISR safety rules
linux-driver       80%      80%     0        Error cleanup — universal
dma                90%      70%    -20%p     Cache/alignment patterns
ESP-IDF            80%      70%    -10%p     Cross-platform knowledge
STM32 HAL          TBD      TBD     —        FreeRTOS + HAL (new)
```

**Key finding:** HW-related categories (spi-i2c, device-tree, ble) show the largest model-size sensitivity. SW-pattern categories (boot, kconfig) show zero difference.

## Quick Start

```bash
# Install
uv sync

# Run benchmark (single-shot)
uv run embedeval run --model claude-code://sonnet --cases cases/

# With compiler feedback (3 rounds of error correction)
uv run embedeval run --model claude-code://sonnet --cases cases/ --feedback-rounds 3

# Multi-turn agent mode (5 attempts with accumulated context)
uv run embedeval agent claude-code://sonnet --max-turns 5

# Temporal filtering (contamination prevention)
uv run embedeval run --model claude-code://sonnet --cases cases/ --after-date 2026-01-01

# View results
cat results/LEADERBOARD.md
```

## What Makes EmbedEval Different

### 1. Tests Implicit Domain Knowledge

Most coding benchmarks tell the LLM exactly what to do. EmbedEval tells the LLM **what** to build but not **how** to make it safe:

```
Prompt:  "Implement DMA transfer from src to dst buffer.
          Use a callback to signal completion."

Hidden requirements (not in prompt):
  - Buffer must be cache-line aligned (__aligned(32))
  - Cache flush before DMA start
  - Cache invalidate after DMA complete
  - Error flag must be volatile (shared with ISR)
  - Error flag checked AFTER synchronization, not before
```

**Measured impact:** Explicit prompts → ~95% pass. Implicit prompts → ~60% pass. **35%p gap.**

### 2. Multi-Platform (5 platforms)

| Platform | Cases | Build System | Docker |
|----------|-------|-------------|--------|
| Zephyr RTOS | 150 | `west build` | Dockerfile |
| ESP-IDF | 10 | `idf.py build` | Dockerfile.esp |
| STM32 HAL + FreeRTOS | 10 | `arm-none-eabi-gcc` | Dockerfile.stm32 |
| Linux kernel | 10 | `kbuild` | — |
| Yocto | 10 | `bitbake` | — |
| Kconfig/DT/Boot | 30 | N/A (config files) | — |

### 3. Self-Validated Check Precision

We don't just test LLMs — we test our own checks with **subtle negative tests** (intentionally broken code that tries to evade detection):

```
Check Precision Progression:
  Round 1:  6/15 caught (40%)  — checks were too naive
  Round 2:  9/15 caught (60%)  — fixed substring matching, deny lists
  Round 3: 12/15 caught (80%)  — added return verification, comment stripping

  Remaining 3/15 (20%) are regex-unsolvable → need L1/L2 execution
```

### 4. Cross-Platform Hallucination Detection

```c
// ESP-IDF code with Zephyr API hallucination
#include "driver/gpio.h"
#include <zephyr/kernel.h>    // HALLUCINATION — Zephyr in ESP-IDF code
k_sleep(K_SECONDS(1));        // HALLUCINATION — Zephyr API
```

### 5. Evaluation Modes (inspired by leading benchmarks)

| Mode | Inspired By | CLI |
|------|-------------|-----|
| Single-shot | HumanEval | `embedeval run` |
| Compiler feedback | EmbedBench (ICSE'26) | `--feedback-rounds 3` |
| Multi-turn agent | SWE-bench | `embedeval agent --max-turns 5` |
| Temporal filtering | LiveCodeBench (ICLR'25) | `--after-date 2026-01-01` |

## 220 Test Cases, 22 Categories

| Category | Cases | Platform | L1 Build |
|----------|-------|----------|----------|
| gpio-basic | 10 | Zephyr | native_sim |
| spi-i2c | 10 | Zephyr | nrf52840dk |
| dma | 10 | Zephyr | native_sim |
| isr-concurrency | 10 | Zephyr | native_sim |
| threading | 10 | Zephyr | native_sim |
| timer | 10 | Zephyr | native_sim |
| sensor-driver | 10 | Zephyr | nrf52840dk |
| networking | 10 | Zephyr | native_sim |
| ble | 10 | Zephyr | native_sim |
| security | 10 | Zephyr | native_sim |
| storage | 10 | Zephyr | native_sim |
| kconfig | 10 | Zephyr | N/A |
| device-tree | 10 | Zephyr | N/A |
| boot | 10 | Zephyr | N/A |
| ota | 10 | Zephyr | nrf52840dk |
| power-mgmt | 10 | Zephyr | nrf52840dk |
| watchdog | 10 | Zephyr | nrf52840dk |
| memory-opt | 10 | Zephyr | native_sim |
| yocto | 10 | Yocto | N/A |
| linux-driver | 10 | Linux | N/A |
| esp-* | 10 | ESP-IDF | idf.py |
| stm32-* | 10 | STM32 HAL | arm-gcc |

## Evaluation Layers

| Layer | Name | Method | Status |
|-------|------|--------|--------|
| L0 | Static Analysis | Regex pattern matching | Active |
| L1 | Compilation | Docker builds (west/idf.py/arm-gcc) | Active (15/15 verified) |
| L2 | Runtime | `native_sim` + expected output | Ready |
| L3 | Static Heuristic | Domain-specific pattern checks (precision: 80%) | Active |
| L4 | Mutation Testing | Robustness via code mutation | Planned |

**Honest naming:** We call L3 "Static Heuristic" not "Behavioral" — our checks are regex-based pattern matching with 80% precision, not execution-based testing.

## Scoring

- **pass@1, pass@3, pass@5**: First/any-of-k attempt pass rates
- **Weighted scoring**: Partial credit — 9/10 checks = 0.9, not binary FAIL
- **Embed Gap**: EmbedEval pass@1 − HumanEval pass@1 (cross-benchmark)
- **Check Precision**: 80% (12/15 subtle mutations caught by checks)

## 12 Key Insights

Documented in [docs/INSIGHTS.md](docs/INSIGHTS.md):

1. **Implicit vs Explicit Gap** — 35%p difference when removing API hints
2. **General SW vs Embedded failures** — 56% general, 44% embedded-specific
3. **6 LLM failure patterns** — Happy path bias, semantic ignorance, resource imbalance, ordering, magic numbers, demo mindset
4. **4-Level implicit knowledge model** — C → RTOS → Hardware → System safety
5. **Syntactic vs Behavioral gap** — L0-L2 perfect, L3 where models diverge
6. **Implicit prompt validation** — Modified categories show pass rate decrease
7. **Critical self-analysis** — Honest assessment of benchmark limitations
8. **Cross-benchmark comparison** — Embed Gap metric
9. **Re-benchmark results** — 91% → 89.5% with harder checks
10. **Sonnet vs Haiku** — 11.4%p gap, HW categories most discriminating
11. **Check Precision** — 40% → 60% → 80% through iterative blind spot fixing
12. **Cross-benchmark competitive analysis** — vs EmbedBench, LiveCodeBench, SWE-bench

## CLI Reference

```bash
# Benchmark modes
embedeval run --model sonnet --cases cases/              # Single-shot
embedeval run --model sonnet --feedback-rounds 3         # With compiler feedback
embedeval agent sonnet --max-turns 5                     # Multi-turn agent
embedeval run --model sonnet --attempts 3                # pass@3

# Filtering
embedeval run --model sonnet -c isr-concurrency -c dma   # By category
embedeval run --model sonnet --visibility public          # Exclude private set
embedeval run --model sonnet --after-date 2026-01-01      # Temporal filter

# Utilities
embedeval validate --cases cases/                         # Validate references
embedeval list --cases cases/                             # List cases
```

## Docker (L1 Build Verification)

```bash
# Zephyr (15/15 categories verified)
docker build -t embedeval-zephyr .
docker run --rm --entrypoint bash embedeval-zephyr -c 'west build -b native_sim cases/ble-001'

# ESP-IDF
docker build -f Dockerfile.esp -t embedeval-esp .

# STM32 HAL
docker build -f Dockerfile.stm32 -t embedeval-stm32 .
```

## Project Structure

```
embedeval/
├── src/embedeval/           # Core library (14 modules)
│   ├── evaluator.py         # 5-layer evaluation pipeline (Docker/local/skip)
│   ├── runner.py            # Benchmark orchestration + feedback loop
│   ├── scorer.py            # Unbiased pass@k + Wilson 95% CI
│   ├── reporter.py          # Leaderboard + cross-benchmark + scenario comparison
│   ├── bugfix.py            # Bug fix scenario (mutation-based)
│   ├── sensitivity.py       # Prompt sensitivity analysis
│   ├── difficulty.py        # IRT difficulty calibration
│   ├── ablation.py          # Layer contribution ablation study
│   ├── failure_taxonomy.py  # Automated failure classification (8 patterns)
│   ├── check_utils.py       # Scope-aware check utilities (word boundary, AST-like)
│   ├── agent.py             # Multi-turn agent evaluation
│   ├── llm_client.py        # LiteLLM + claude-code:// provider
│   └── cli.py               # Typer CLI (run, agent, validate, sensitivity, list)
├── cases/                   # 220 test cases (170 public + 50 private)
│   ├── {category}-{NNN}/    # Zephyr cases (20 categories × 10+)
│   ├── esp-*/               # ESP-IDF cases (10)
│   └── stm32-*/             # STM32 HAL + FreeRTOS cases (10)
├── tests/                   # 945 tests
│   ├── test_e2e.py          # E2E: 220 reference solutions + pipeline
│   ├── test_negatives.py    # 20 must_fail + 15 subtle mutations
│   ├── test_bugfix.py       # Bug fix scenario tests
│   ├── test_check_utils.py  # Scope-aware check utility tests
│   ├── test_sensitivity.py  # Prompt sensitivity tests
│   ├── test_difficulty.py   # IRT difficulty tests
│   ├── test_ablation.py     # Ablation study tests
│   └── test_failure_taxonomy.py # Failure classification tests
├── docs/
│   ├── METHODOLOGY.md       # Full benchmark methodology
│   └── INSIGHTS.md          # 13 accumulated insights
├── external_benchmarks.yaml # HumanEval/SWE-bench reference scores
├── Dockerfile               # Zephyr SDK (west build)
├── Dockerfile.esp           # ESP-IDF (idf.py build)
├── Dockerfile.stm32         # STM32 HAL (arm-none-eabi-gcc)
└── .github/workflows/       # CI: validate + L1 Docker build
```

## Known Limitations

- **Static heuristic precision: ~80%** — Scope-aware checks catch most bugs, but true semantic verification requires L1/L2 compilation
- **Platform bias** — 77% Zephyr, 5% ESP-IDF, 5% STM32 (expanding)
- **Difficulty calibration** — Assigned labels may not match empirical difficulty (IRT tool available)
- **50 private cases** — 23% held-out set; periodic rotation planned

See [Insight #7](docs/INSIGHTS.md) and [Insight #12](docs/INSIGHTS.md) for our full self-critical analysis, and [METHODOLOGY.md](docs/METHODOLOGY.md) for complete benchmark design.

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
