# EmbedEval

[![CI](https://img.shields.io/badge/CI-passing-brightgreen)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)]()
[![Cases](https://img.shields.io/badge/cases-210-orange)]()

**LLM benchmark for embedded firmware code generation.**

EmbedEval measures how well LLMs generate embedded firmware code — Zephyr RTOS, ESP-IDF, Linux kernel drivers, and Yocto recipes. While [HumanEval](https://github.com/openai/human-eval) and [SWE-bench](https://www.swebench.com/) test general coding, EmbedEval tests **domain-specific knowledge**: interrupt safety, cache coherency, DMA alignment, power management, and real-time constraints that only embedded experts would know.

## Leaderboard

| Model | pass@1 | HumanEval | Embed Gap | Cases |
|-------|--------|-----------|-----------|-------|
| **Sonnet 4.6** | **89.5%** | 93.7% | **-4.2%p** | 210 |
| Haiku 4.5 | 78.1% | 84.0% | -5.9%p | 210 |

*Embed Gap = EmbedEval pass@1 − HumanEval pass@1. Negative means embedded is harder than general coding.*

### Category Breakdown

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
ESP-IDF (new)      80%      70%    -10%p     Cross-platform knowledge
```

**Key finding:** HW-related categories (spi-i2c, device-tree, ble) show the largest model-size sensitivity. SW-pattern categories (boot, kconfig) show zero difference.

## Quick Start

```bash
# Install
uv sync

# Run benchmark with Claude (subscription, no API key needed)
uv run embedeval run --model claude-code://sonnet --cases cases/

# Run with multiple attempts for statistical validity
uv run embedeval run --model claude-code://sonnet --cases cases/ --attempts 3

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
  ✗ Buffer must be cache-line aligned (__aligned(32))
  ✗ Cache flush before DMA start
  ✗ Cache invalidate after DMA complete
  ✗ Error flag must be volatile (shared with ISR)
  ✗ Error flag checked AFTER synchronization, not before
```

An embedded expert would add these automatically. An LLM that only follows instructions won't.

**Measured impact:** Explicit prompts → ~95% pass. Implicit prompts → ~60% pass. 35%p gap.

### 2. Multi-Platform

| Platform | Cases | Build System |
|----------|-------|-------------|
| Zephyr RTOS | 150 | `west build` |
| ESP-IDF | 10 | `idf.py build` |
| Linux kernel | 10 | `kbuild` |
| Yocto | 10 | `bitbake` |
| Kconfig/DT/Boot | 30 | N/A (config files) |

### 3. Cross-Platform Hallucination Detection

LLMs frequently mix APIs from different platforms:

```c
// ESP-IDF code with Zephyr API hallucination
#include "driver/gpio.h"
#include <zephyr/kernel.h>    // ✗ HALLUCINATION — Zephyr in ESP-IDF code
k_sleep(K_SECONDS(1));        // ✗ HALLUCINATION — Zephyr API
```

EmbedEval catches these with platform-specific hallucination checks.

## 210 Test Cases, 21 Categories

| Category | Cases | Difficulty | Platform |
|----------|-------|-----------|----------|
| gpio-basic | 10 | Easy-Hard | Zephyr |
| spi-i2c | 10 | Easy-Hard | Zephyr |
| dma | 10 | Medium-Hard | Zephyr |
| isr-concurrency | 10 | Hard | Zephyr |
| threading | 10 | Medium-Hard | Zephyr |
| timer | 10 | Easy-Hard | Zephyr |
| sensor-driver | 10 | Medium-Hard | Zephyr |
| networking | 10 | Medium-Hard | Zephyr |
| ble | 10 | Hard | Zephyr |
| security | 10 | Hard | Zephyr |
| storage | 10 | Medium-Hard | Zephyr |
| kconfig | 10 | Easy-Medium | Zephyr |
| device-tree | 10 | Medium-Hard | Zephyr |
| boot | 10 | Medium | Zephyr |
| ota | 10 | Hard | Zephyr |
| power-mgmt | 10 | Medium-Hard | Zephyr |
| watchdog | 10 | Easy-Medium | Zephyr |
| memory-opt | 10 | Medium-Hard | Zephyr |
| yocto | 10 | Medium | Yocto |
| linux-driver | 10 | Hard | Linux |
| esp-* | 10 | Medium-Hard | ESP-IDF |

## Evaluation Layers

| Layer | Name | Method | Status |
|-------|------|--------|--------|
| L0 | Static Analysis | Regex pattern matching | Active |
| L1 | Compilation | `west build` / `idf.py build` in Docker | Ready (Docker required) |
| L2 | Runtime | `native_sim` execution | Ready (Docker required) |
| L3 | Static Heuristic | Domain-specific pattern checks | Active |
| L4 | Mutation Testing | Robustness via code mutation | Planned |

**Note on L3 naming:** We deliberately call L3 "Static Heuristic" rather than "Behavioral" because our checks are regex-based pattern matching, not actual execution-based behavioral testing. See [Insight #7](docs/INSIGHTS.md#7-embedded-last-exam-비판적-자기-분석-2026-03-24) for our self-critical analysis.

## Scoring

- **pass@1**: First attempt pass rate (default)
- **pass@3**: Any of first 3 attempts passes
- **Weighted scoring**: Partial credit — 9/10 checks passing scores 0.9, not binary FAIL
- **Embed Gap**: EmbedEval pass@1 − HumanEval pass@1 (cross-benchmark comparison)

## Key Insights

10 insights documented in [docs/INSIGHTS.md](docs/INSIGHTS.md):

1. **Implicit vs Explicit Gap** — 35%p difference when removing API hints from prompts
2. **General SW vs Embedded failures** — 56% general, 44% embedded-specific
3. **6 LLM failure patterns** — Happy path bias, semantic ignorance, resource imbalance, ordering, magic numbers, demo mindset
4. **4-Level implicit knowledge model** — C language → RTOS → Hardware → System safety
5. **Syntactic vs Behavioral gap** — L0-L2 near-perfect, L3 where models diverge
6. **Implicit prompt validation** — Modified categories show pass rate decrease
7. **Critical self-analysis** — Honest assessment of benchmark limitations
8. **Cross-benchmark comparison** — Embed Gap metric replaces human baseline
9. **Re-benchmark after improvements** — 91% → 89.5% with harder checks
10. **Sonnet vs Haiku** — 11.4%p gap, HW categories most discriminating

## CLI Reference

```bash
# Run benchmark
uv run embedeval run --model claude-code://sonnet --cases cases/ -v
uv run embedeval run --model claude-code://haiku --cases cases/ --attempts 3

# Filter by category
uv run embedeval run --model claude-code://sonnet --cases cases/ -c isr-concurrency -c dma

# Filter by visibility (exclude private test set)
uv run embedeval run --model claude-code://sonnet --cases cases/ --visibility public

# Validate reference solutions
uv run embedeval validate --cases cases/

# List cases
uv run embedeval list --cases cases/
```

## Docker (L1/L2 Build Verification)

```bash
# Build Docker image with Zephyr SDK
docker-compose build

# Run benchmark with compilation enabled
docker-compose run embedeval uv run embedeval run \
  --model claude-code://sonnet --cases cases/ -v

# ESP-IDF builds
docker build -f Dockerfile.esp -t embedeval-esp .
```

## Project Structure

```
embedeval/
├── src/embedeval/           # Core library
│   ├── evaluator.py         # 5-layer evaluation pipeline
│   ├── runner.py            # Benchmark orchestration
│   ├── scorer.py            # pass@k + weighted scoring
│   ├── reporter.py          # Leaderboard + cross-benchmark comparison
│   ├── llm_client.py        # LiteLLM + claude-code:// provider
│   └── cli.py               # Typer CLI
├── cases/                   # 210 test cases
│   ├── {category}-{NNN}/    # Each case directory
│   │   ├── metadata.yaml    # Category, difficulty, platform
│   │   ├── prompt.md        # LLM prompt (implicit requirements)
│   │   ├── reference/main.c # Reference solution
│   │   ├── checks/static.py # L0 checks
│   │   └── checks/behavior.py # L3 heuristic checks
│   └── esp-*/               # ESP-IDF cases
├── docs/
│   ├── INSIGHTS.md          # 10 accumulated insights
│   ├── METHODOLOGY.md       # Evaluation methodology
│   └── BENCHMARK-ANALYSIS-2026-03-24.md
├── external_benchmarks.yaml # HumanEval/SWE-bench reference scores
├── Dockerfile               # Zephyr SDK build environment
├── Dockerfile.esp           # ESP-IDF build environment
└── docker-compose.yml       # Orchestrated build environment
```

## Known Limitations

Documented in [Insight #7](docs/INSIGHTS.md):

- **L1/L2 not yet validated** — Docker infrastructure ready but not tested at scale
- **Static heuristic, not behavioral** — L3 checks are regex, not execution-based
- **Platform bias** — 71% Zephyr, 5% ESP-IDF (aspirational: broader coverage)
- **n=10 per category** — Statistical significance limited; pass@3 recommended
- **Public test set contamination risk** — 20 cases marked private as mitigation

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

## License

Apache 2.0 — see [LICENSE](LICENSE).
