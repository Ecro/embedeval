# EmbedEval Methodology

## Overview

EmbedEval is a benchmark for evaluating LLM capability in embedded firmware code generation. It measures whether LLMs possess the domain-specific knowledge required to produce correct, safe embedded C code across multiple RTOS platforms and hardware targets.

### Benchmark Statistics

| Metric | Value |
|--------|-------|
| **Total cases** | 179 |
| **Categories** | 23 |
| **Platforms** | 6 (docker_only, esp_idf, native_sim, qemu_arm, stm32_hal, yocto_build) |
| **Difficulty** | 24 easy, 76 medium, 79 hard |
| **Private held-out** | 0 cases (0%) for contamination prevention |
| **Evaluation scenarios** | 2 (generation, bugfix) |
| **Negatives (mutation tests)** | 9 cases, 18 must_fail mutations |

### Platform Distribution

| Platform | Cases | Categories |
|----------|-------|------------|
| Zephyr RTOS (native_sim) | 145 | gpio-basic, uart, adc, pwm, spi-i2c, dma, isr-concurrency, threading, timer, sensor-driver, networking, ble, security, storage, kconfig, device-tree, boot, ota, power-mgmt, watchdog, memory-opt |
| Zephyr RTOS (qemu_arm) | 8 | (subset of above, board-specific) |
| ESP-IDF | 5 | esp-adc, esp-ble, esp-gpio, esp-i2c, esp-nvs, esp-ota, esp-sleep, esp-spi, esp-timer, esp-wifi |
| STM32 HAL | 5 | stm32-gpio, stm32-uart, stm32-spi, stm32-i2c, stm32-timer, stm32-adc, stm32-dma, stm32-lowpower, stm32-freertos (x2) |
| Linux kernel (docker_only) | 8 | linux-driver |
| Yocto/Embedded Linux | 8 | yocto |

### Difficulty Distribution by Category

| Category | Easy | Medium | Hard | Total |
|----------|------|--------|------|-------|
| adc | 0 | 1 | 1 | 2 |
| ble | 1 | 3 | 4 | 8 |
| boot | 1 | 5 | 2 | 8 |
| device-tree | 2 | 3 | 3 | 8 |
| dma | 1 | 2 | 6 | 9 |
| gpio-basic | 2 | 2 | 1 | 5 |
| isr-concurrency | 0 | 2 | 7 | 9 |
| kconfig | 2 | 3 | 3 | 8 |
| linux-driver | 0 | 3 | 5 | 8 |
| memory-opt | 1 | 4 | 5 | 10 |
| networking | 1 | 6 | 3 | 10 |
| ota | 1 | 3 | 4 | 8 |
| power-mgmt | 1 | 4 | 3 | 8 |
| pwm | 1 | 0 | 0 | 1 |
| security | 0 | 3 | 5 | 8 |
| sensor-driver | 1 | 4 | 3 | 8 |
| spi-i2c | 1 | 8 | 3 | 12 |
| storage | 1 | 4 | 4 | 9 |
| threading | 1 | 4 | 7 | 12 |
| timer | 2 | 4 | 3 | 9 |
| uart | 1 | 1 | 0 | 2 |
| watchdog | 2 | 3 | 4 | 9 |
| yocto | 1 | 4 | 3 | 8 |

---

## System Architecture

### High-Level Component Diagram

```
                         EmbedEval System Architecture
 ┌──────────────────────────────────────────────────────────────────────┐
 │                           CLI (cli.py)                              │
 │  run | validate | list | categories | agent | sensitivity | guide   │
 └─────────┬────────────────────────────────────────────────────┬──────┘
           │                                                    │
           ▼                                                    ▼
 ┌─────────────────────┐                          ┌────────────────────┐
 │   Runner (runner.py) │                          │ Sensitivity        │
 │  - discover_cases()  │                          │ Analysis           │
 │  - filter_cases()    │                          │ (sensitivity.py)   │
 │  - run_benchmark()   │                          └────────────────────┘
 └──────┬───────┬───────┘
        │       │
        ▼       ▼
 ┌────────────┐ ┌──────────────────────────────────────────────────────┐
 │ LLM Client │ │            Evaluator (evaluator.py)                  │
 │ (llm_      │ │                                                      │
 │  client.py)│ │  L0 Static ──► L1 Compile ──► L2 Runtime            │
 │            │ │      │             │              │                   │
 │ 3 modes:   │ │      ▼             ▼              ▼                   │
 │ - mock     │ │  checks/       west build     west build -t run      │
 │ - claude-  │ │  static.py     (Docker/       (native_sim/QEMU)      │
 │   code://  │ │                 local/skip)         │                 │
 │ - litellm  │ │      │             │              ▼                   │
 │            │ │      ▼             ▼         L3 Heuristic            │
 └────────────┘ │  ┌─────────────────────┐         │                   │
                │  │ Failure at any layer │    checks/behavior.py      │
                │  │ halts evaluation     │         │                   │
                │  └─────────────────────┘         ▼                   │
                │                              L4 Mutation             │
                │                              checks/negatives.py     │
                └──────────────────────────────────────────────────────┘
        │
        ▼
 ┌─────────────────────┐    ┌──────────────────────┐
 │  Scorer (scorer.py)  │───►│ Reporter (reporter.py)│
 │  - pass@k (unbiased) │    │ - JSON results        │
 │  - Wilson 95% CI     │    │ - Markdown leaderboard │
 │  - per-category      │    │ - Failure report       │
 │  - per-tier          │    │ - Safe guide           │
 │  - per-reasoning     │    │ - Run archive          │
 │  - layer pass rates  │    │ - Cross-benchmark      │
 └─────────────────────┘    └──────────────────────┘
```

### End-to-End Benchmark Execution Flow

```
 ┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
 │ User invokes │     │ Discover     │     │ Filter cases    │
 │ `embedeval   │────►│ cases from   │────►│ by category,    │
 │  run ...`    │     │ cases/ dir   │     │ difficulty, tier,│
 └─────────────┘     └──────────────┘     │ visibility, date│
                                          └────────┬────────┘
                                                   │
                      ┌────────────────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ For each case  │◄─────────────────────────────┐
              │ x N attempts   │                              │
              └───────┬───────┘                               │
                      │                                       │
                      ▼                                       │
              ┌───────────────┐                               │
              │ Load prompt   │                               │
              │ + context     │                               │
              └───────┬───────┘                               │
                      │                                       │
                      ▼                                       │
              ┌───────────────┐    ┌──────────────────┐      │
              │ Call LLM      │    │ Extract code from │      │
              │ (model)       │───►│ markdown blocks   │      │
              └───────────────┘    └────────┬─────────┘      │
                                            │                 │
                                            ▼                 │
              ┌─────────────────────────────────────┐        │
              │       5-Layer Evaluation             │        │
              │                                      │        │
              │  L0 Static    → pass/fail            │        │
              │  L1 Compile   → pass/fail/skip       │        │
              │  L2 Runtime   → pass/fail/skip       │        │
              │  L3 Heuristic → pass/fail            │        │
              │  L4 Mutation  → pass/fail             │        │
              │                                      │        │
              │  (failure halts remaining layers)     │        │
              └──────────────┬──────────────────────┘        │
                             │                                │
                             ▼                                │
                    ┌────────────────┐    YES                 │
                    │ Failed at L0/L1│────────┐               │
                    │ & feedback > 0?│        ▼               │
                    └───────┬────────┘ ┌─────────────┐       │
                         NO │          │ Build error  │       │
                            │          │ feedback to  │       │
                            │          │ LLM → retry  │───────┘
                            ▼          └─────────────┘
              ┌───────────────────┐    (up to N feedback rounds)
              │ Append EvalResult │
              │ to results[]     │
              └───────┬──────────┘
                      │
                      ▼
              ┌───────────────┐
              │ Next case/    │───────────────────────┐
              │ attempt       │                       │ All done
              └───────────────┘                       │
                                                      ▼
                                          ┌───────────────────┐
                                          │ Score results      │
                                          │ (pass@k, CI, etc.) │
                                          └─────────┬─────────┘
                                                    │
                                                    ▼
                                          ┌───────────────────┐
                                          │ Generate reports   │
                                          │ - JSON             │
                                          │ - Leaderboard.md   │
                                          │ - Failure report   │
                                          │ - Safe guide       │
                                          │ - Test tracker     │
                                          └───────────────────┘
```

### Per-Case Evaluation Pipeline (Detail)

```
                    Generated Code (string)
                            │
                            ▼
    ┌───────────────────────────────────────────────────┐
    │ LAYER 0: Static Analysis                          │
    │                                                   │
    │  checks/static.py::run_checks(code) → CheckDetail[] │
    │                                                   │
    │  Examples:                                        │
    │  - Required #include headers present?             │
    │  - CONFIG_* symbols correct?                      │
    │  - DT node structure valid?                       │
    │  - ISR function signatures correct?               │
    └──────────────────┬────────────────────────────────┘
                       │ PASS
                       ▼
    ┌───────────────────────────────────────────────────┐
    │ LAYER 1: Compilation Gate                         │
    │                                                   │
    │  Platform dispatch:                               │
    │  ┌─────────────┬──────────────┬──────────────┐   │
    │  │ Zephyr      │ ESP-IDF      │ STM32 HAL    │   │
    │  │ west build  │ idf.py build │ arm-none-    │   │
    │  │ (Docker/    │ (IDF_PATH)   │ eabi-gcc     │   │
    │  │  local)     │              │ (STM32_HAL_  │   │
    │  │             │              │  PATH)       │   │
    │  └─────────────┴──────────────┴──────────────┘   │
    │                                                   │
    │  EMBEDEVAL_ENABLE_BUILD:                          │
    │    docker → Docker container build                │
    │    1/local → Local west build (ZEPHYR_BASE)       │
    │    unset → Skip (auto-pass)                       │
    └──────────────────┬────────────────────────────────┘
                       │ PASS
                       ▼
    ┌───────────────────────────────────────────────────┐
    │ LAYER 2: Runtime Execution                        │
    │                                                   │
    │  west build -t run (native_sim or QEMU)           │
    │  - Timeout: 10s (firmware runs forever)            │
    │  - Timeout is normal: kill + capture stdout        │
    │  - Validate output vs checks/expected_output.txt  │
    │  - HW targets (nrf52840dk etc.) → auto-skip       │
    │  - ESP-IDF / STM32 → auto-skip (no QEMU config)  │
    └──────────────────┬────────────────────────────────┘
                       │ PASS
                       ▼
    ┌───────────────────────────────────────────────────┐
    │ LAYER 3: Static Heuristic                         │
    │                                                   │
    │  checks/behavior.py::run_checks(code) → CheckDetail[] │
    │                                                   │
    │  Check utilities (check_utils):                   │
    │  - Word-boundary matching (has_word, has_api_call) │
    │  - Scope-aware (check_api_in_function,            │
    │    check_qualifier_on_variable)                    │
    │  - Flow analysis (check_return_after_error)        │
    │  - Order checking (check_cleanup_reverse_order)    │
    │  - Cross-platform (check_no_cross_platform_apis)   │
    │  - ISR safety (check_no_isr_forbidden)             │
    └──────────────────┬────────────────────────────────┘
                       │ PASS
                       ▼
    ┌───────────────────────────────────────────────────┐
    │ LAYER 4: Mutation Testing (Meta-Verification)     │
    │                                                   │
    │  checks/negatives.py (9 cases, 18 mutations)      │
    │  - Seeds known bugs into reference code            │
    │  - Verifies L0/L3 checks detect the bug           │
    │  - Proves the benchmark's own checks are sound     │
    └──────────────────┬────────────────────────────────┘
                       │ PASS
                       ▼
                  ┌──────────┐
                  │ ALL PASS │
                  └──────────┘
```

### LLM Client Modes

```
             call_model(model, prompt, context_files)
                            │
              ┌─────────────┼──────────────┐
              │             │              │
              ▼             ▼              ▼
        ┌──────────┐ ┌───────────┐ ┌────────────┐
        │  "mock"  │ │ "claude-  │ │ Any other  │
        │          │ │  code://" │ │ string     │
        │ Returns  │ │           │ │            │
        │ fixed    │ │ claude -p │ │ litellm.   │
        │ test     │ │ --output- │ │ completion │
        │ response │ │ format    │ │ ()         │
        │          │ │ json      │ │            │
        │          │ │           │ │ API keys   │
        │ No API   │ │ Subscrip- │ │ required   │
        │ needed   │ │ tion only │ │ (env vars) │
        └──────────┘ └───────────┘ └────────────┘
              │             │              │
              └─────────────┼──────────────┘
                            ▼
                   ┌─────────────────┐
                   │ LLMResponse     │
                   │ - generated_code│ ← _extract_code() strips ```blocks
                   │ - token_usage   │
                   │ - cost_usd      │
                   │ - duration_s    │
                   └─────────────────┘
```

---

## 5-Layer Evaluation Architecture

EmbedEval evaluates LLM-generated code through five progressively deeper verification layers. Failure at any layer halts evaluation — subsequent layers are marked as skipped.

### Layer 0: Static Analysis

**Purpose:** Catch structural and syntactic issues without compilation.

**Implementation:** Each case provides `checks/static.py` with a `run_checks(generated_code: str) -> list[CheckDetail]` function. Checks include required includes, CONFIG symbol validation, device tree structure, and ISR signature verification.

### Layer 1: Compilation

**Purpose:** Verify that generated code compiles against the target SDK.

**Implementation:** Platform-specific compilation dispatched by metadata:

| Platform | Build Command | Environment Variable |
|----------|---------------|---------------------|
| Zephyr (Docker) | `docker run ... west build` | `EMBEDEVAL_ENABLE_BUILD=docker` |
| Zephyr (local) | `west build` | `EMBEDEVAL_ENABLE_BUILD=1` or `local` |
| ESP-IDF | `idf.py build` | `IDF_PATH` |
| STM32 HAL | `arm-none-eabi-gcc -c` | `STM32_HAL_PATH` |
| Skip | Auto-pass | `EMBEDEVAL_ENABLE_BUILD` unset |

All Zephyr compilation uses temporary directories (copied from case files + generated `src/main.c`) to avoid mutating case files. The build directory is shared between L1 and L2.

### Layer 2: Runtime Execution

**Purpose:** Execute compiled firmware and detect runtime failures (segfaults, deadlocks, hangs).

**Implementation:** `west build -t run` under native_sim with a 10-second timeout. Embedded firmware runs forever (`while(1)` + `k_sleep`), so timeout is the expected exit — the process is killed and captured stdout is validated against `checks/expected_output.txt` keyword lines. Hardware-only boards (nrf52840dk, etc.) and ESP-IDF/STM32 cases auto-skip runtime.

### Layer 3: Static Heuristic

**Purpose:** Verify domain-specific behavioral correctness via pattern analysis.

**Implementation:** Each case provides `checks/behavior.py` with domain-specific checks. Available check utilities include:
- **Word-boundary matching** (`has_word`, `has_api_call`) — prevents substring aliasing
- **Scope-aware checks** (`check_api_in_function`, `check_qualifier_on_variable`) — verifies patterns in correct function scope
- **Flow analysis** (`check_return_after_error`) — verifies error handling has return/goto
- **Order checking** (`check_cleanup_reverse_order`) — verifies cleanup in reverse init order
- **Cross-platform detection** (`check_no_cross_platform_apis`) — catches API contamination
- **ISR safety** (`check_no_isr_forbidden`) — verifies no blocking calls in ISR context

### Layer 4: Mutation Testing

**Purpose:** Meta-verification — ensures the benchmark's own checks catch known bugs in the LLM-generated code's structure.

**Implementation:** 9 cases have `checks/negatives.py` with 18 `must_fail` mutations. The evaluator loads the NEGATIVES data, applies each mutation to the generated code, runs L0+L3 checks on the mutated result, and verifies that the targeted checks detect the seeded bug.

**Scoring:** L4 is meta-verification only — L4 failures do not affect the overall case pass/fail determination or pass@1 scores. They indicate gaps in the benchmark's check coverage rather than LLM quality issues.

**Skip conditions:** If the mutation doesn't change the generated code (different structure from reference), that mutation is skipped. If no `negatives.py` file exists, L4 auto-passes with no details.

---

## Evaluation Scenarios

### Generation (default)

LLM receives a task prompt and must produce complete C source code from scratch. Evaluated through all 5 layers.

```bash
uv run embedeval run --model claude-code://sonnet --cases cases/
```

### Bug Fix

LLM receives buggy code (reference + seeded mutation) and must diagnose and fix the bug. Evaluated through the same checks — fixed code must pass all layers.

```bash
uv run embedeval run --model claude-code://sonnet --cases cases/ --scenario bugfix
```

Bugfix cases are auto-generated from existing `must_fail` mutations. No additional TC authoring required.

### Compiler Feedback Rounds

When `--feedback-rounds N` is set (N > 0), cases that fail at L0 (static) or L1 (compile) trigger a retry loop:

1. Extract error message and failed check details from the failing layer
2. Construct a feedback prompt: original task + error context + "fix the code"
3. Call the LLM again with the feedback prompt
4. Re-evaluate the new code through all layers
5. Repeat up to N rounds or until the case passes

```bash
uv run embedeval run --model claude-code://sonnet --cases cases/ --feedback-rounds 3
```

This measures LLM self-correction capability on compilation/structural errors.

### Multi-Turn Agent Mode

The `agent` command runs cases in a multi-turn conversation loop where the LLM receives evaluation feedback and can iteratively refine its code:

```bash
uv run embedeval agent claude-code://sonnet --cases cases/ --max-turns 5
```

---

## Scoring: pass@k

EmbedEval uses the **unbiased pass@k estimator** from Chen et al. (2021):

```
pass@k = 1 - C(n-c, k) / C(n, k)
```

Where `n` = total samples per case, `c` = correct samples, `C(a,b)` = binomial coefficient.

When `n < k`, falls back to empirical estimate (any correct → 1.0).

### Confidence Intervals

All pass@1 scores include **95% Wilson score confidence intervals**:

```
CI = (center ± spread) / (1 + z²/n)
```

Reports display: `pass@1 = 89.5% [84.7%, 93.1%]`

### Score Aggregation

Results are aggregated across multiple dimensions:

| Dimension | Implementation |
|-----------|---------------|
| **Per-model** | pass@1, pass@3, pass@5, layer pass rates |
| **Per-category** | pass@1 per category (23 categories) |
| **Per-tier** | pass@1 by evaluation tier (sanity, core, challenge) |
| **Per-reasoning** | pass@1 by reasoning type (api_recall, rule_application, cross_domain, system_reasoning) |
| **Overall** | Best model, total cases, best pass@1 |

### Reporting Outputs

| Output | Description |
|--------|-------------|
| `results/<model>-results.json` | Full benchmark report (JSON) |
| `results/LEADERBOARD.md` | Model comparison, heatmaps, failure distribution |
| `results/runs/<date>_<model>/` | Per-case detailed results archive |
| `results/runs/<date>_<model>/report.md` | Failure analysis with patterns |
| `results/SAFE_GUIDE.md` | Risk-tier guidance for embedded engineers |
| `results/test_tracker.json` | Incremental test state for `--retest-only` |
| `results/TEST_RESULTS.md` | Human-readable test results summary |
| `results/history.json` | Run history for trend tracking |

### Key Metrics

- **pass@1** — first-attempt accuracy (primary metric)
- **pass@5** — multi-attempt capability
- **95% CI** — statistical confidence on pass@1
- **Embed Gap** — EmbedEval pass@1 minus HumanEval pass@1 (cross-benchmark positioning)

---

## Contamination Prevention

### Private Held-Out Set

48 private cases are maintained in a **separate repository** (`embedeval-private`) to prevent contamination through LLM training data exposure:

```bash
# Include private cases in benchmark run
uv run embedeval run --model claude-code://sonnet \
    --cases cases/ \
    --private-cases ../embedeval-private/cases/ \
    --include-private
```

Default benchmark runs evaluate only the 179 public cases. The `--include-private` flag enables the full 227-case evaluation. Visibility filtering is enforced at the runner level: without `--include-private`, cases with `visibility: private` in metadata are excluded.

### Temporal Cutoff

Each case has `created_date` in metadata. The `--after-date` filter enables temporal analysis against model training cutoffs.

### Incremental Retesting

The `--retest-only` flag uses content-hash-based change detection to only re-run cases that have been modified since the last benchmark run, enabling efficient iteration after TC updates.

---

## Analysis Tools

### Prompt Sensitivity Analysis

Measures benchmark robustness to prompt phrasing variations.

```bash
uv run embedeval sensitivity claude-code://sonnet --sample 30 --variants 3
```

Three deterministic variant strategies:
1. **Reorder** — reverse requirement bullet order
2. **Rephrase** — swap imperative verbs (Write->Implement)
3. **Remove** — strip "Output ONLY" instructions

Robustness score: 1.0 (all variants agree) to 0.0 (all disagree).

### IRT Difficulty Calibration

Estimates empirical difficulty from multi-model results.

- **Difficulty (b):** `1 - empirical_pass_rate` (higher = harder)
- **Discrimination (a):** Std dev of per-model pass rates (higher = better differentiator)
- **Label validation:** Compares assigned easy/medium/hard vs empirical thresholds (>80% / 40-80% / <40%)
- **Floor/ceiling detection:** Cases all models pass (too easy) or all fail (broken)

### Ablation Study

Measures contribution of each evaluation layer to discriminative power.

| Configuration | Layers |
|---------------|--------|
| L0 only | Static analysis |
| L0 + L3 | Static + heuristic (current default without Docker) |
| L0 + L1 | Static + compile |
| L0 + L1 + L3 | Static + compile + heuristic |
| Full (L0-L4) | All layers |

Layer contribution = delta between configurations (e.g., `L0_rate - L0+L3_rate`).

### Failure Taxonomy

Automated classification of LLM failures into 8 patterns:

| Pattern | Description |
|---------|-------------|
| `happy_path_bias` | Error path cleanup missing |
| `semantic_mismatch` | Compiles but wrong HW semantics |
| `resource_imbalance` | Alloc without free |
| `order_violation` | Init/register/use order wrong |
| `cross_platform` | Wrong platform API used |
| `api_hallucination` | Non-existent API called |
| `missing_safety` | Forbidden API in ISR, missing guards |
| `unknown` | Unmapped check failure |

Classification uses majority voting across failed checks with confidence scoring.

### Safety Guide Generation

Aggregates benchmark results across all models and runs to produce risk-tier guidance:

| Risk Tier | Pass Rate | Recommendation |
|-----------|-----------|----------------|
| Critical | <50% | Do not trust — write manually or review every line |
| Caution | 50-79% | Use as starting point only, expert review mandatory |
| Moderate | 80-89% | Spot check safety-critical patterns |
| Reliable | 90%+ | Standard code review sufficient |

```bash
uv run embedeval guide --results results/
```

---

## Case Structure

Each case directory contains:

```
cases/<category>-<number>/
  metadata.yaml       # Pydantic-validated metadata (id, category, difficulty, platform, etc.)
  prompt.md            # LLM task prompt
  reference/main.c     # Verified correct solution
  checks/static.py     # L0 static analysis checks
  checks/behavior.py   # L3 behavioral heuristic checks
  checks/negatives.py  # (9 cases) Mutation tests for meta-verification
  context/             # Additional context files (optional)
  CMakeLists.txt       # Zephyr build file (Zephyr cases)
  prj.conf             # Zephyr Kconfig (Zephyr cases)
```

### Design Principles

1. **Self-contained** — No external dependencies beyond SDK Docker images
2. **Reference required** — Every case has a verified reference solution
3. **Deterministic** — All checks produce deterministic pass/fail (no LLM-as-judge)
4. **Implicit knowledge** — Prompts describe functional requirements without giving away safety patterns

---

## How EmbedEval Differs from Related Work

| Dimension | HumanEval | SWE-bench | EmbedAgent (ICSE'26) | EmbedEval |
|-----------|-----------|-----------|----------------------|-----------|
| **Domain** | General Python | Python SWE | Arduino/ESP32/RPi | Zephyr/ESP-IDF/STM32/Linux |
| **Cases** | 164 | 2,294 | 126 | 227 (179 public + 48 private) |
| **Platforms** | 1 | 1 | 3 | 6 |
| **Scenarios** | 1 | 1 | 3 | 2 + feedback + agent |
| **Verification** | assert | pytest | Wokwi sim | 5-layer (static + compile + runtime + heuristic + mutation) |
| **Contamination** | None | PR-based | HW combinations | Separate private repo + temporal cutoff |
| **Scoring** | pass@k | % resolved | pass@1 | pass@k (unbiased) + 95% CI + Embed Gap |
| **Unique** | — | — | Circuit design | Implicit Knowledge Gap, 4-Level Model, Safety Guide |
