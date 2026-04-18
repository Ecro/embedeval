# EmbedEval

[![CI](https://github.com/Ecro/embedeval/actions/workflows/ci.yml/badge.svg)](https://github.com/Ecro/embedeval/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)]()
[![Cases](https://img.shields.io/badge/cases-233-orange)]()
[![Tests](https://img.shields.io/badge/tests-1277-green)]()

**LLM Embedded Domain Knowledge Probe** — Do LLMs actually understand embedded firmware, or do they just pattern-match?

EmbedEval measures whether LLMs possess the **implicit domain knowledge** to write safe embedded C code. It covers Zephyr RTOS, ESP-IDF, STM32 HAL, FreeRTOS, Linux kernel drivers, and Yocto recipes across 233 test cases (185 public + 48 private held-out).

![pass@1 heatmap by category](assets/launch/heatmap.png)

Unlike [HumanEval](https://github.com/openai/human-eval) or [SWE-bench](https://www.swebench.com/) which test general coding, EmbedEval tests knowledge that only embedded engineers would have: interrupt safety, cache coherency, DMA alignment, power management, and real-time constraints — **without telling the LLM what to check**.

[Live leaderboard](https://huggingface.co/spaces/ecro/embedeval) · [Methodology](https://github.com/Ecro/embedeval/blob/main/docs/METHODOLOGY.md) · [Roadmap](https://github.com/Ecro/embedeval/blob/main/ROADMAP.md) · [Contribute](https://github.com/Ecro/embedeval/blob/main/docs/CONTRIBUTING.md)

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

![Implicit knowledge gap](assets/launch/implicit-gap.png)

---

## Leaderboard

n=3 aggregate across 233 cases (185 public + 48 private, 2026-04-12):

| Model | pass@1 (n=3 mean) | 95% CI | Stability | Weakest Category | Strongest |
|-------|-------------------|--------|-----------|------------------|-----------|
| **Sonnet 4.6** | **68.0%** | [64.4%, 71.3%] | 87.1% | isr-concurrency (23%), dma (31%), threading (33%) | adc, device-tree, pwm (100%) |
| Haiku 4.5 | 56.9% | [53.2%, 60.6%] | 73.0% | dma (8%), isr-concurrency (38%), memory-opt (33%) | boot, device-tree, pwm (100%) |

**Model gap:** 11.1%p overall (CIs don't overlap — statistically significant). Sonnet stability: 87.1% vs Haiku 73.0%.

See detailed comparison: [`docs/BENCHMARK-COMPARISON-2026-04-05.md`](docs/BENCHMARK-COMPARISON-2026-04-05.md)
See analysis & conclusions: [`docs/LLM-EMBEDDED-CONSIDERATIONS.md`](docs/LLM-EMBEDDED-CONSIDERATIONS.md)

### Category Heatmap

All 23 categories (233 cases, n=3 run, 2026-04-12):

```
Category          Sonnet   Haiku    Gap      What it tests
----------------  -------  -------  -------  --------------------------
adc               100%      50%    +50%p     ADC read, sampling patterns
ble                82%      45%    +37%p     BLE stack API, connection mgmt
boot               90%     100%    -10%p     Boot sequence + Kconfig
device-tree       100%     100%       0      DT syntax, node references
dma                31%       8%    +23%p     Cache alignment, DMA lifecycle
gpio-basic         67%      83%    -16%p     GPIO config, device_ready() checks
isr-concurrency    23%      38%    -15%p     ISR safety, volatile, barriers
kconfig            90%      60%    +30%p     Build config generation
linux-driver       70%      70%       0      Kernel module, syscall interfaces
memory-opt         67%      33%    +34%p     Memory domains, slab allocators
networking         75%      75%       0      Socket lifecycle, error paths
ota                67%      58%     +9%p     OTA update lifecycle
power-mgmt         75%      67%     +8%p     Sleep modes, power domains
pwm               100%     100%       0      PWM duty cycle, device binding (n=1)
security           50%      70%    -20%p     Crypto API, key management
sensor-driver      75%      67%     +8%p     Sensor API patterns
spi-i2c            79%      64%    +15%p     Bus protocol, transfer sequences
storage            54%      31%    +23%p     Flash lifecycle, NVS patterns
threading          33%      33%       0      Mutex ordering, thread safety
timer              83%      50%    +33%p     Timer callback safety
uart               33%      67%    -34%p     UART config, async TX/RX
watchdog           90%      60%    +30%p     WDT feed timing, reset handling
yocto              80%      70%    +10%p     Yocto recipe authoring
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
  │ L4 Mutation │  checks/negatives.py — meta-verification (30 cases)
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
| `results/<model>-results.json` | Full machine-readable report (model name is slug-sanitized) |
| `results/runs/<date>_<model>/report.md` | Per-case failure analysis with patterns |
| `results/SAFE_GUIDE.md` | Risk-tier guidance for embedded engineers (auto-generated by `run`) |
| `results/TEST_RESULTS.md` | Per-case test status tracker (incremental run history) |

---

## Evaluation Modes

| Mode | What it measures | CLI |
|------|-----------------|-----|
| **Single-shot** | Raw first-attempt accuracy | `embedeval run` |
| **Multi-attempt** | pass@k across N samples | `embedeval run --attempts 5` |
| **Feedback** | Self-correction on L0/L1 errors | `embedeval run --feedback-rounds 3` |
| **Agent** | Multi-turn iterative refinement | `embedeval agent --max-turns 5` |
| **Bug fix** | Diagnose + fix seeded mutations | `embedeval run --scenario bugfix` |
| **Context Quality** | Effect of team's CLAUDE.md / system prompt | `embedeval run --context-pack ./CLAUDE.md` + `embedeval context-compare` |

Context Quality Mode quantifies how much your team's implicit-context
files actually help the LLM and how much room is left to improve them.
See [docs/CONTEXT-QUALITY-MODE.md](docs/CONTEXT-QUALITY-MODE.md) for the
workflow and metric interpretation.

---

## Case Structure

```
cases/isr-concurrency-003/
├── metadata.yaml           # id, category, difficulty, platform, reasoning_types, ...
├── prompt.md               # Task prompt (functional requirements, no safety hints)
├── reference/main.c        # Verified correct solution
├── src/main.c              # LLM-generated code goes here during evaluation
├── context/                # Additional context files (optional)
├── checks/
│   ├── static.py           # L0: required includes, struct layout, ISR signature
│   ├── behavior.py         # L3: volatile qualifiers, lock ordering, ISR safety
│   ├── expected_output.txt # L2: expected program output pattern (optional, 119/185)
│   └── negatives.py        # L4: mutation tests to validate checks (optional, 30/185)
├── CMakeLists.txt          # Zephyr build config
└── prj.conf                # Zephyr Kconfig
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
├── src/embedeval/           # Core library (18 modules)
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
├── cases/                   # 185 public test cases
├── tests/                   # 1277 pytest tests
├── docs/
│   ├── METHODOLOGY.md                    # Full benchmark methodology + architecture diagrams
│   ├── CONTRIBUTING.md                   # How to add new test cases
│   ├── LLM-EMBEDDED-CONSIDERATIONS.md    # Research insights + practical guidance
│   ├── LLM-EMBEDDED-FAILURE-FACTORS.md   # 42-factor failure taxonomy (6 categories)
│   ├── LLM-EMBEDDED-DEVELOPMENT-GUIDE.md # End-to-end workflow + knowledge base
│   └── BENCHMARK-COMPARISON-2026-04-05.md # Haiku vs Sonnet detailed comparison
├── scripts/
│   ├── sync_docs.py              # Auto-sync README/METHODOLOGY counts (mandatory at wrapup)
│   └── ...                       # Other analysis and verification scripts
├── external_benchmarks.yaml # HumanEval/SWE-bench reference scores
├── Dockerfile               # Zephyr SDK build environment
├── Dockerfile.esp           # ESP-IDF build environment
├── Dockerfile.stm32         # STM32 HAL build environment
└── .github/workflows/       # CI + benchmark dispatch + case validation
```

---

## Development

```bash
uv run pytest                               # Run all tests
uv run ruff check src/ tests/              # Lint
uv run ruff format src/ tests/             # Format
uv run mypy src/                           # Type check
uv run embedeval validate --cases cases/        # Validate reference solutions
uv run embedeval validate-metadata --cases cases/  # Validate metadata consistency
uv run embedeval categories --cases cases/     # Show case counts per category
uv run python scripts/sync_docs.py         # Sync README/docs counts (run before commit)
```

---

## Key Research Findings

Documented in [LLM-EMBEDDED-CONSIDERATIONS.md](docs/LLM-EMBEDDED-CONSIDERATIONS.md):

1. **Implicit vs Explicit Gap** — 35%p pass rate drop when removing safety hints from prompts
2. **4-Level Implicit Knowledge Model** — C language → RTOS patterns → Hardware constraints → System safety
3. **Failure Distribution** — Sonnet: 31% L2 + 31% L3. Haiku: 43% L0 + 24% L1. Bigger models fail later (safety, not syntax).
4. **General vs Embedded** — 56% of failures are general SW problems (error paths), 44% are embedded-specific (HW constraints)
5. **Model Size Sensitivity** — Category-level gaps reach up to 50%p (e.g., adc); overall n=3 Sonnet–Haiku gap is 11.1%p (CIs non-overlapping)
6. **6 LLM Failure Patterns** — happy path bias, semantic mismatch, resource imbalance, order violation, cross-platform hallucination, missing safety guards
7. **"3AM Paranoia" Layer** — 8 categories of field knowledge (timer overflow, flash wear, sensor plausibility, radio corruption) that LLMs structurally cannot learn

---

## Known Limitations

- **Platform bias** — 81% Zephyr, with ESP-IDF and STM32 at 5 cases each
- **L3 precision** — Static heuristic checks are regex-based; true semantic verification needs L1/L2
- **Single-file scope** — Cases test single-file code generation, not multi-file project scaffolding
- **Difficulty calibration** — Assigned labels may not match empirical difficulty (IRT calibration module in `src/embedeval/difficulty.py`)

See [METHODOLOGY.md](docs/METHODOLOGY.md) for our complete self-assessment.

---

## Comparison with Related Work

| Dimension | HumanEval | SWE-bench | EmbedAgent (ICSE'26) | **EmbedEval** |
|-----------|-----------|-----------|----------------------|---------------|
| Domain | General Python | Python SWE | Arduino/ESP32/RPi | **Embedded (Zephyr/ESP-IDF/STM32/FreeRTOS/Linux/Yocto)** |
| Cases | 164 | 2,294 | 126 | **233** |
| Platforms | 1 | 1 | 3 | **6** |
| Verification | assert | pytest | Wokwi sim | **5-layer pipeline** |
| Contamination | None | PR-based | HW combos | **Separate private repo + temporal** |
| Scoring | pass@k | % resolved | pass@1 | **pass@k + 95% CI + Embed Gap** |
| Unique | — | — | Circuit design | **Implicit Knowledge Gap** |

**vs EmbedAgent (ICSE'26).** Both target embedded LLM evaluation, but the focus is different. EmbedAgent measures cross-platform programming on hobbyist boards (Arduino / ESP32 / Raspberry Pi Pico) with Wokwi circuit simulation and bundles Programmer / Architect / Integrator role tasks. EmbedEval measures production embedded firmware on Zephyr RTOS, ESP-IDF, STM32 HAL, FreeRTOS, Linux kernel drivers, and Yocto, deliberately withholds safety hints from prompts (the "implicit knowledge gap"), and verifies through five layers including a mutation-testing meta-layer. They are complementary: EmbedAgent for breadth across hobbyist hardware, EmbedEval for depth on production RTOS/driver patterns.

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the v0.2/v0.3 plan. Open an [issue](https://github.com/Ecro/embedeval/issues) to influence direction. Briefly: v0.2 broadens model coverage and adds FreeRTOS / Linux driver cases; v0.3 adds multi-file scaffolding and cross-platform migration; v1.0 freezes the schema.

---

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for case authoring. In brief:

- **New case:** create `cases/<category>-<NNN>/` with `metadata.yaml`, `prompt.md`, `reference/main.c`, plus `checks/static.py` and `checks/behavior.py`. Verify with `uv run embedeval validate --cases cases/ -c <category>`.
- **New model:** run `uv run embedeval run --model <litellm-id> --cases cases/` for n=3, then PR `results/runs/<date>_<model>/` along with an updated `LEADERBOARD.md`.
- **Methodology critique:** open an issue using the methodology-question template.

Issue templates: model evaluation request, case contribution, methodology discussion (under `.github/ISSUE_TEMPLATE/`).

---

## Citation

If EmbedEval is useful for your work, please cite:

```bibtex
@misc{embedeval2026,
  title  = {EmbedEval: A Benchmark for LLM-Generated Embedded Firmware},
  author = {{EmbedEval Contributors}},
  year   = {2026},
  url    = {https://github.com/Ecro/embedeval},
  note   = {Open benchmark with 233 cases across Zephyr, ESP-IDF, STM32 HAL,
            FreeRTOS, Linux kernel drivers, and Yocto. Measures the implicit
            knowledge gap in LLM-generated embedded code.}
}
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
