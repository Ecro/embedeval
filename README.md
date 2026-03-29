# EmbedEval

[![CI](https://github.com/Ecro/embedeval/actions/workflows/ci.yml/badge.svg)](https://github.com/Ecro/embedeval/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)]()
[![Cases](https://img.shields.io/badge/cases-227-orange)]()
[![Tests](https://img.shields.io/badge/tests-859-green)]()

**LLM Embedded Domain Knowledge Probe** — Do LLMs actually understand embedded firmware, or do they just pattern-match?

EmbedEval measures whether LLMs possess the **implicit domain knowledge** to write safe embedded C code. It covers Zephyr RTOS, ESP-IDF, STM32 HAL, Linux kernel drivers, and Yocto recipes across 227 test cases (179 public + 48 private held-out).

Unlike [HumanEval](https://github.com/openai/human-eval) or [SWE-bench](https://www.swebench.com/) which test general coding, EmbedEval tests knowledge that only embedded engineers would have: interrupt safety, cache coherency, DMA alignment, power management, and real-time constraints — **without telling the LLM what to check**.

---

## Key Insight: The Implicit Knowledge Gap

Most benchmarks tell the LLM exactly what to do. EmbedEval tells the LLM **what** to build but not **how** to make it safe:

```
Prompt:  "Implement DMA transfer from src to dst buffer.
          Use a callback to signal completion."

What an embedded engineer knows (not in prompt):
  - Buffer must be cache-line aligned (__aligned(32))
  - Cache flush before DMA start
  - Cache invalidate after DMA complete
  - Completion flag must be volatile (shared with ISR)
  - Flag checked AFTER synchronization, not before
```

**Measured impact:** Explicit prompts ("use volatile") pass at ~95%. Implicit prompts (derive from domain knowledge) pass at ~60%. This **35%p gap** means current benchmarks overestimate LLM capability in embedded domains.

---

## Leaderboard

Benchmark run on 179 public cases (2026-03-29):

| Model | pass@1 | 95% CI | Weakest Category | Strongest |
|-------|--------|--------|------------------|-----------|
| **Sonnet 4.6** | **84.9%** (152/179) | [79.1%, 89.6%] | threading (42%), isr-concurrency (44%) | kconfig, boot, gpio-basic (100%) |
| Haiku 4.5 | 70.4% (126/179) | [63.2%, 76.8%] | dma (11%), threading (25%) | kconfig (100%) |

**Model gap:** 14.5%p overall, up to 67%p on DMA. 78% of all failures occur at L3 (behavioral heuristic), 22% at L0 (static analysis).

### Category Heatmap

```
Category          Sonnet   Haiku    Gap      What it tests
────────────────  ───────  ───────  ───────  ──────────────────────────
kconfig           100%     100%       0      Build config generation
boot              100%      88%     12%p     Boot sequence + Kconfig
gpio-basic        100%      80%     20%p     GPIO init/interrupt patterns
timer             100%      78%     22%p     Timer callback safety
networking         90%      80%     10%p     Socket lifecycle, error paths
ble                88%      75%     13%p     BLE stack API, connection mgmt
device-tree        88%      75%     13%p     DT syntax, node references
spi-i2c            83%      67%     16%p     Bus protocol, transfer sequences
watchdog           78%      56%     22%p     WDT feed timing, reset handling
security           75%      63%     12%p     Crypto API, key management
dma                78%      11%     67%p     Cache alignment, DMA lifecycle
isr-concurrency    44%      44%      0       ISR safety, volatile, barriers
threading          42%      25%     17%p     Mutex ordering, thread safety
```

---

## Quick Start

```bash
# Prerequisites: Python 3.12+, uv
pip install uv  # if not installed

# Clone and install
git clone https://github.com/Ecro/embedeval.git
cd embedeval
uv sync

# Run benchmark (L0 + L3 static checks, no Docker needed)
uv run embedeval run --model claude-code://sonnet --cases cases/

# View results
cat results/LEADERBOARD.md
```

### LLM Connection Modes

| Mode | Example | Requirement |
|------|---------|-------------|
| Claude Code (subscription) | `--model claude-code://sonnet` | Claude Code CLI installed |
| LiteLLM (API key) | `--model anthropic/claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` env var |
| Mock (testing) | `--model mock` | None |

### Common Commands

```bash
# Filter by category or difficulty
uv run embedeval run --model claude-code://sonnet --cases cases/ -c isr-concurrency
uv run embedeval run --model claude-code://sonnet --cases cases/ -d hard

# Multiple attempts for pass@k
uv run embedeval run --model claude-code://sonnet --cases cases/ --attempts 5

# With compiler feedback (self-correction measurement)
uv run embedeval run --model claude-code://sonnet --cases cases/ --feedback-rounds 3

# Multi-turn agent mode
uv run embedeval agent claude-code://sonnet --cases cases/ --max-turns 5

# Bug fix scenario (LLM diagnoses + fixes seeded bugs)
uv run embedeval run --model claude-code://sonnet --cases cases/ --scenario bugfix

# Temporal filtering (contamination prevention)
uv run embedeval run --model claude-code://sonnet --cases cases/ --after-date 2026-01-01

# Include private held-out cases (separate repo)
uv run embedeval run --model claude-code://sonnet \
    --cases cases/ --private-cases ../embedeval-private/cases/ --include-private

# Only retest cases changed since last run
uv run embedeval run --model claude-code://sonnet --cases cases/ --retest-only

# Validate all reference solutions pass
uv run embedeval validate --cases cases/

# List cases with metadata
uv run embedeval list --cases cases/

# Prompt sensitivity analysis
uv run embedeval sensitivity claude-code://sonnet --sample 30 --variants 3

# Generate safety guide from results
uv run embedeval guide --results results/
```

---

## 5-Layer Evaluation Architecture

Each case is evaluated through five progressive layers. Failure at any layer halts evaluation.

```
  Generated Code
       │
       ▼
  ┌─────────────┐
  │ L0 Static   │  checks/static.py — includes, CONFIG symbols, ISR signatures
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │ L1 Compile  │  west build / idf.py / arm-gcc (Docker or local, skippable)
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │ L2 Runtime  │  native_sim execution with 10s timeout + output validation
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │ L3 Heuristic│  checks/behavior.py — domain-specific pattern analysis
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │ L4 Mutation │  checks/negatives.py — meta-verification (9 cases, 18 mutations)
  └─────────────┘
```

| Layer | Method | What it catches | Docker needed |
|-------|--------|-----------------|---------------|
| L0 | Static pattern matching | Missing headers, wrong CONFIG, bad ISR signatures | No |
| L1 | SDK compilation | Syntax errors, undefined symbols, type mismatches | Yes (or `ZEPHYR_BASE`) |
| L2 | QEMU/native_sim execution | Segfaults, deadlocks, wrong output | Yes |
| L3 | Domain heuristic checks | Missing volatile, wrong lock order, no error cleanup | No |
| L4 | Mutation testing | Validates that L0/L3 checks themselves are sound | No |

**Default mode (no Docker):** L0 + L3 provide strong discriminative power. L1/L2 auto-skip when `EMBEDEVAL_ENABLE_BUILD` is unset.

See [METHODOLOGY.md](docs/METHODOLOGY.md) for detailed architecture diagrams and implementation details.

---

## 23 Categories, 6 Platforms

### Platform Coverage

| Platform | Cases | Build System | Evaluation |
|----------|-------|-------------|------------|
| Zephyr RTOS (native_sim) | 145 | `west build` | Full (L0-L4) |
| Zephyr RTOS (qemu_arm) | 8 | `west build` | L0-L3 |
| ESP-IDF | 5 | `idf.py build` | L0-L1, L3 |
| STM32 HAL + FreeRTOS | 5 | `arm-none-eabi-gcc` | L0-L1, L3 |
| Linux kernel | 8 | `kbuild` | L0, L3 |
| Yocto/Embedded Linux | 8 | `bitbake` | L0, L3 |

### Categories

**Peripheral & Communication:** gpio-basic, uart, adc, pwm, spi-i2c, dma, ble, networking

**Concurrency & Timing:** isr-concurrency, threading, timer, watchdog

**System Configuration:** kconfig, device-tree, boot, ota, power-mgmt

**Safety & Resources:** security, storage, sensor-driver, memory-opt

**Platform-Specific:** yocto, linux-driver

---

## Scoring

### Metrics

| Metric | Description |
|--------|-------------|
| **pass@1** | First-attempt accuracy (primary metric) |
| **pass@k** | Unbiased estimator from Chen et al. (2021): `1 - C(n-c,k) / C(n,k)` |
| **95% CI** | Wilson score confidence interval on pass@1 |
| **Embed Gap** | EmbedEval pass@1 minus HumanEval pass@1 (negative = harder than general coding) |

### Aggregation Dimensions

Results are sliced by model, category (23), difficulty tier (easy/medium/hard), evaluation tier (sanity/core/challenge), and reasoning type (api_recall, rule_application, cross_domain, system_reasoning).

### Report Outputs

A single benchmark run generates:

| File | Content |
|------|---------|
| `results/LEADERBOARD.md` | Model comparison, category heatmap, layer pass rates |
| `results/<model>-results.json` | Full machine-readable report |
| `results/runs/<date>_<model>/report.md` | Per-case failure analysis with patterns |
| `results/SAFE_GUIDE.md` | Risk-tier guidance for embedded engineers |

---

## Evaluation Modes

| Mode | What it measures | CLI |
|------|-----------------|-----|
| **Single-shot** | Raw first-attempt accuracy | `embedeval run` |
| **Multi-attempt** | pass@k across N samples | `embedeval run --attempts 5` |
| **Feedback** | Self-correction on L0/L1 errors | `embedeval run --feedback-rounds 3` |
| **Agent** | Multi-turn iterative refinement | `embedeval agent --max-turns 5` |
| **Bug fix** | Diagnose + fix seeded mutations | `embedeval run --scenario bugfix` |

---

## Case Structure

```
cases/isr-concurrency-003/
├── metadata.yaml       # id, category, difficulty, platform, reasoning_types, ...
├── prompt.md           # Task prompt (functional requirements, no safety hints)
├── reference/main.c    # Verified correct solution
├── checks/
│   ├── static.py       # L0: required includes, struct layout, ISR signature
│   └── behavior.py     # L3: volatile qualifiers, lock ordering, ISR safety
├── CMakeLists.txt      # Zephyr build config
└── prj.conf            # Zephyr Kconfig
```

**Design principles:**
1. **Self-contained** — each case is a standalone Zephyr/ESP-IDF/STM32 project
2. **Deterministic** — all checks are regex/pattern-based, no LLM-as-judge
3. **Implicit knowledge** — prompts describe *what* to build, not *how* to make it safe
4. **Reference verified** — every case has a reference solution that passes all layers

---

## Contamination Prevention

- **48 private cases** in a [separate repository](https://github.com/Ecro/embedeval-private) — never exposed to LLM training data
- **Temporal cutoff** — `--after-date` filter for training data freshness analysis
- **Content-hash tracking** — `--retest-only` detects modified cases for efficient re-evaluation

---

## Project Structure

```
embedeval/
├── src/embedeval/           # Core library (16 modules)
│   ├── cli.py               # Typer CLI entry point
│   ├── runner.py            # Case discovery, filtering, benchmark orchestration
│   ├── llm_client.py        # LiteLLM + claude-code:// + mock providers
│   ├── evaluator.py         # 5-layer evaluation pipeline
│   ├── scorer.py            # pass@k (unbiased) + Wilson 95% CI
│   ├── reporter.py          # JSON, Markdown, failure analysis, safe guide
│   ├── models.py            # Pydantic models (EvalResult, BenchmarkReport, ...)
│   ├── check_utils.py       # Scope-aware check utilities
│   ├── agent.py             # Multi-turn agent evaluation
│   ├── bugfix.py            # Bug fix scenario (mutation-based)
│   ├── sensitivity.py       # Prompt sensitivity analysis
│   ├── difficulty.py        # IRT difficulty calibration
│   ├── ablation.py          # Layer contribution ablation study
│   ├── failure_taxonomy.py  # Automated failure classification (8 patterns)
│   ├── safety_guide.py      # Risk-tier safety guide generation
│   └── test_tracker.py      # Incremental retest tracking
├── cases/                   # 179 public test cases
├── tests/                   # 859 pytest tests
├── docs/
│   ├── METHODOLOGY.md       # Full benchmark methodology + architecture diagrams
│   ├── CONTRIBUTING.md      # How to add new test cases
│   └── INSIGHTS.md          # 13 accumulated research insights
├── external_benchmarks.yaml # HumanEval/SWE-bench reference scores
├── Dockerfile               # Zephyr SDK build environment
├── Dockerfile.esp           # ESP-IDF build environment
├── Dockerfile.stm32         # STM32 HAL build environment
└── .github/workflows/       # CI + benchmark dispatch + case validation
```

---

## Development

```bash
uv run pytest                        # Run all tests
uv run ruff check src/ tests/        # Lint
uv run ruff format src/ tests/       # Format
uv run mypy src/                     # Type check
uv run embedeval validate --cases cases/  # Validate reference solutions
```

---

## Key Research Findings

Documented in [INSIGHTS.md](docs/INSIGHTS.md):

1. **Implicit vs Explicit Gap** — 35%p pass rate drop when removing safety hints from prompts
2. **4-Level Implicit Knowledge Model** — C language → RTOS patterns → Hardware constraints → System safety
3. **Failure Distribution** — 78% of failures at L3 (behavioral), 22% at L0 (static)
4. **General vs Embedded** — 56% of failures are general SW problems, 44% are embedded-specific
5. **Model Size Sensitivity** — HW categories (DMA, threading) show largest Sonnet-Haiku gap (up to 67%p)
6. **6 LLM Failure Patterns** — happy path bias, semantic mismatch, resource imbalance, order violation, cross-platform hallucination, missing safety guards

---

## Known Limitations

- **Platform bias** — 81% Zephyr, with ESP-IDF and STM32 at 5 cases each
- **L3 precision** — Static heuristic checks are regex-based; true semantic verification needs L1/L2
- **Single-file scope** — Cases test single-file code generation, not multi-file project scaffolding
- **Difficulty calibration** — Assigned labels may not match empirical difficulty (IRT tool available via `embedeval difficulty`)

See [METHODOLOGY.md](docs/METHODOLOGY.md) for our complete self-assessment.

---

## Comparison with Related Work

| Dimension | HumanEval | SWE-bench | EmbedAgent (ICSE'26) | **EmbedEval** |
|-----------|-----------|-----------|----------------------|---------------|
| Domain | General Python | Python SWE | Arduino/ESP32/RPi | **Zephyr/ESP-IDF/STM32/Linux** |
| Cases | 164 | 2,294 | 126 | **227** |
| Platforms | 1 | 1 | 3 | **6** |
| Verification | assert | pytest | Wokwi sim | **5-layer pipeline** |
| Contamination | None | PR-based | HW combos | **Separate private repo + temporal** |
| Scoring | pass@k | % resolved | pass@1 | **pass@k + 95% CI + Embed Gap** |
| Unique | — | — | Circuit design | **Implicit Knowledge Gap** |

---

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for how to add new test cases. In brief:

1. Create `cases/<category>-<NNN>/` with `metadata.yaml`, `prompt.md`, `reference/main.c`
2. Write `checks/static.py` (L0) and `checks/behavior.py` (L3)
3. Verify with `uv run embedeval validate --cases cases/ -c <category>`
4. Run `uv run pytest` to ensure all tests pass

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
