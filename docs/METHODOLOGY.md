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
| Zephyr RTOS (native_sim) | 170 | gpio-basic, uart, adc, pwm, spi-i2c, dma, isr-concurrency, threading, timer, sensor-driver, networking, ble, security, storage, kconfig, device-tree, boot, ota, power-mgmt, watchdog, memory-opt |
| Zephyr RTOS (qemu_arm) | 10 | (subset of above, board-specific) |
| ESP-IDF | 10 | esp-adc, esp-ble, esp-gpio, esp-i2c, esp-nvs, esp-ota, esp-sleep, esp-spi, esp-timer, esp-wifi |
| STM32 HAL | 10 | stm32-gpio, stm32-uart, stm32-spi, stm32-i2c, stm32-timer, stm32-adc, stm32-dma, stm32-lowpower, stm32-freertos (×2) |
| Linux kernel (docker_only) | 10 | linux-driver |
| Yocto/Embedded Linux | 10 | yocto |

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

## 5-Layer Evaluation Architecture

EmbedEval evaluates LLM-generated code through five progressively deeper verification layers. Failure at any layer halts evaluation.

### Layer 0: Static Analysis

**Purpose:** Catch structural and syntactic issues without compilation.

**Implementation:** Each case provides `checks/static.py` with a `run_checks(generated_code: str) -> list[CheckDetail]` function. Checks include required includes, CONFIG symbol validation, device tree structure, and ISR signature verification.

### Layer 1: Compilation

**Purpose:** Verify that generated code compiles against the target SDK.

**Implementation:** Three build modes controlled by `EMBEDEVAL_ENABLE_BUILD`:
- `docker` — Runs `west build` in Docker container (`embedeval-zephyr` image), tmpdir-isolated
- `local` or `1` — Runs `west build` locally (requires `ZEPHYR_BASE`)
- unset — Skips compilation (auto-pass)

ESP-IDF cases use `idf.py build`, STM32 cases use `arm-none-eabi-gcc`. All compilation uses temporary directories to avoid mutating case files.

### Layer 2: Runtime Execution

**Purpose:** Execute compiled firmware and detect runtime failures (segfaults, deadlocks, hangs).

**Implementation:** `west build -t run` under native_sim or QEMU with configurable timeout. Output validated against `checks/expected_output.txt` if present.

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

**Purpose:** Meta-verification — ensures the benchmark's own checks catch known bugs.

**Implementation:** 10 cases have `checks/negatives.py` with 20 `must_fail` mutations. Each mutation seeds a known bug and verifies that at least one check detects it.

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

20 bugfix cases are auto-generated from existing `must_fail` mutations across 10 TCs. No additional TC authoring required.

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

### Reporting

- **pass@1** — first-attempt accuracy (primary metric)
- **pass@5** — multi-attempt capability
- **95% CI** — statistical confidence on pass@1
- **Embed Gap** — EmbedEval pass@1 minus HumanEval pass@1 (cross-benchmark positioning)

---

## Contamination Prevention

### Private Held-Out Set

50 of 220 cases (23%) are marked `visibility: private`:
- 40 cases from main categories (the -009 and -010 of each)
- 5 ESP-IDF cases
- 5 STM32 HAL cases

Default benchmark runs exclude private cases. Use `--include-private` for full evaluation.

### Temporal Cutoff

Each case has `created_date` in metadata. The `--after-date` filter enables temporal analysis against model training cutoffs.

---

## Analysis Tools

### Prompt Sensitivity Analysis

Measures benchmark robustness to prompt phrasing variations.

```bash
uv run embedeval sensitivity claude-code://sonnet --sample 30 --variants 3
```

Three deterministic variant strategies:
1. **Reorder** — reverse requirement bullet order
2. **Rephrase** — swap imperative verbs (Write→Implement)
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
  checks/negatives.py  # (10 cases) Mutation tests for meta-verification
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
| **Cases** | 164 | 2,294 | 126 | 220 |
| **Platforms** | 1 | 1 | 3 | 6 |
| **Scenarios** | 1 | 1 | 3 | 2 |
| **Verification** | assert | pytest | Wokwi sim | 5-layer (static + compile + runtime + heuristic + mutation) |
| **Contamination** | None | PR-based | HW combinations | Private held-out (23%) + temporal |
| **Scoring** | pass@k | % resolved | pass@1 | pass@k (unbiased) + 95% CI |
| **Unique** | — | — | Circuit design | Implicit Knowledge Gap, 4-Level Model, Embed Gap |
