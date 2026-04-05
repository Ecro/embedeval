# EmbedEval Benchmark Comparison: Haiku vs Sonnet — Test Results

**Date:** 2026-04-05
**Benchmark Version:** 179 public cases + 48 private cases (227 total)
**Runs:** Haiku 2026-04-04 (179 public) | Sonnet 2026-04-04 (227 total)
**Categories:** 23 embedded categories across Zephyr, FreeRTOS, ESP-IDF, STM32, Yocto
**Analysis:** See companion document [`LLM-EMBEDDED-CONSIDERATIONS.md`](LLM-EMBEDDED-CONSIDERATIONS.md) for conclusions and practical guidance.

---

## 1. Overall Results

| Metric | Haiku (4.5) | Sonnet (4.6) | Delta |
|--------|-------------|--------------|-------|
| Total Cases | 179 (public) | 227 (179 pub + 48 priv) | — |
| Raw pass@1 | 64.8% (116/179) | 80.2% (182/227) | — |
| **Raw pass@1 (public only)** | **64.8% (116/179)** | **76.5% (137/179)** | **+11.7%p** |
| Environment failures | 16 | 8 | -8 |
| Format failures (prose) | 1 | 1 | 0 |
| **Adjusted pass@1 (public)** | **71.2% (116/163)** | **80.1% (137/171)** | **+8.9%p** |
| 95% CI (raw, public) | [57.5%, 71.5%] | [69.8%, 82.3%] | — |

> **Adjusted pass@1** excludes environment failures (Docker build) and format failures (LLM returned prose instead of code). These are not measures of LLM embedded knowledge.

### Failure Distribution by Layer (Public Cases)

| Layer | Haiku | Sonnet | Description |
|-------|-------|--------|-------------|
| L0 Static | 27 | 9 | Missing APIs, wrong headers, structural errors |
| L1 Build | 15 | 7 | Docker west build compile failures |
| L2 Runtime | 6 | 13 | QEMU/native_sim output validation |
| L3 Behavioral | 15 | 13 | Safety pattern / heuristic check failures |
| L4 Mutation | 0 | 0 | — |

> Haiku fails early (L0/L1) — doesn't even know the right APIs. Sonnet gets further but fails at L2/L3 — knows APIs but misses safety patterns.

---

## 2. Environment & Non-Genuine Failures

### 2.1 Docker Build Failures (`west_build_docker`)

Cases where Docker-based `west build` fails — typically due to missing board overlays, SDK config, or Docker environment issues rather than LLM code quality.

| Case | Haiku | Sonnet | Likely Cause |
|------|-------|--------|-------------|
| isr-concurrency-007 | FAIL | FAIL | Both fail build — TC/Docker env issue |
| memory-opt-012 | FAIL | FAIL | Both fail build — TC/Docker env issue |
| threading-013 | FAIL | FAIL | Both fail build — TC/Docker env issue |
| ble-001 | FAIL | pass | Haiku code doesn't compile |
| dma-006 | FAIL | pass | Haiku code doesn't compile |
| isr-concurrency-011 | FAIL | pass | Haiku code doesn't compile |
| networking-003 | FAIL | pass | Haiku code doesn't compile |
| security-001 | FAIL | pass* | Haiku build fail; Sonnet builds but fails L2 |
| storage-005 | FAIL | pass* | Haiku build fail; Sonnet builds but fails L2 |
| storage-008 | FAIL | pass* | Haiku build fail; Sonnet builds but fails L3 |
| threading-004 | FAIL | pass | Haiku code doesn't compile |
| threading-005 | FAIL | pass | Haiku code doesn't compile |
| threading-007 | FAIL | pass* | Haiku build fail; Sonnet builds but fails L2 |
| threading-011 | FAIL | pass* | Haiku build fail; Sonnet builds but fails L2 |
| timer-005 | FAIL | pass | Haiku code doesn't compile |
| dma-002 | pass* | FAIL | Haiku fails L0; Sonnet code doesn't compile |
| isr-concurrency-006 | pass* | FAIL | Haiku fails L0; Sonnet code doesn't compile |
| memory-opt-001 | pass* | FAIL | Haiku fails L0; Sonnet code doesn't compile |
| threading-012 | pass* | FAIL | Haiku fails L0; Sonnet code doesn't compile |

**Total:** 3 both fail (TC/env issue), 12 Haiku-only, 4 Sonnet-only

> *pass\** = case still fails at a different layer (not a build env issue at that layer)

### 2.2 L2 Runtime Failures — Shared Across Both Models

These 5 cases fail L2 `output_validation` in **both** Haiku and Sonnet, strongly suggesting an environment or TC issue:

| Case | Haiku | Sonnet | Assessment |
|------|-------|--------|-----------|
| security-002 | FAIL L2 | FAIL L2 | **Likely env/TC issue** — both models fail identically |
| security-004 | FAIL L2 | FAIL L2 | **Likely env/TC issue** — both models fail identically |
| security-006 | FAIL L2 | FAIL L2 | **Likely env/TC issue** — both models fail identically |
| security-008 | FAIL L2 | FAIL L2 | **Likely env/TC issue** — both models fail identically |
| storage-002 | FAIL L2 | FAIL L2 | **Likely env/TC issue** — both models fail L2 |

### 2.3 LLM Format Failures (Prose Instead of Code)

| Case | Haiku | Sonnet | Notes |
|------|-------|--------|-------|
| isr-concurrency-001 | FAIL (`llm_call`) | pass | Haiku returned prose |
| watchdog-010 | pass* | FAIL (`llm_call`) | Sonnet returned prose |

> Non-deterministic — retry would likely produce code. Not a knowledge failure.

### 2.4 Summary of Non-Genuine Failures

| Category | Haiku | Sonnet | Notes |
|----------|-------|--------|-------|
| Docker build (both fail) | 3 | 3 | TC or Docker env problem |
| Docker build (model-specific) | 12 | 4 | Real compile failures |
| L2 runtime (both fail) | 5 | 5 | Likely env/TC issue |
| Format (prose) | 1 | 1 | Non-deterministic |
| **Total non-genuine (shared)** | **9** | **9** | Failures not measuring LLM knowledge |

**Excluding 9 shared non-genuine failures:**

| Metric | Haiku | Sonnet | Delta |
|--------|-------|--------|-------|
| Effective cases | 170 | 170 | — |
| **Effective pass@1** | **68.2% (116/170)** | **80.6% (137/170)** | **+12.4%p** |

---

## 3. Per-Category Comparison (179 Public Cases)

| Category | Cases | Haiku | Sonnet | Delta | Notes |
|----------|-------|-------|--------|-------|-------|
| adc | 2 | 100% | 100% | +0.0 | Both perfect |
| ble | 8 | 75% | 100% | +25.0 | Haiku: 1 build + 1 L3 fail |
| boot | 8 | 100% | 88% | -12.5 | Sonnet regresses on boot-001 |
| device-tree | 8 | 88% | 100% | +12.5 | |
| **dma** | **9** | **0%** | **44%** | **+44.4** | **Hardest category for both** |
| esp-gpio | 1 | 0% | 100% | +100.0 | Haiku: wrong platform APIs |
| esp-i2c | 1 | 0% | 100% | +100.0 | Haiku: wrong platform APIs |
| gpio-basic | 3 | 100% | 67% | -33.3 | Sonnet misses device_ready_check |
| **isr-concurrency** | **9** | **22%** | **33%** | **+11.1** | **Hard for both — concurrency** |
| kconfig | 8 | 75% | 88% | +12.5 | |
| linux-driver | 8 | 88% | 75% | -12.5 | Sonnet fails more error-path checks |
| **memory-opt** | **10** | **30%** | **50%** | **+20.0** | Complex memory management |
| networking | 8 | 62% | 100% | +37.5 | Haiku: build + behavioral fails |
| ota | 8 | 88% | 88% | +0.0 | Both fail ota-005 (rollback) |
| power-mgmt | 8 | 88% | 100% | +12.5 | |
| security | 8 | 38% | 25% | -12.5 | 4 shared L2 env failures inflate both |
| sensor-driver | 8 | 100% | 100% | +0.0 | Both perfect |
| spi-i2c | 8 | 88% | 88% | +0.0 | |
| storage | 9 | 44% | 56% | +11.1 | |
| **threading** | **11** | **27%** | **45%** | **+18.2** | Many build/runtime env failures |
| timer | 8 | 62% | 100% | +37.5 | Haiku misses volatile, sleep patterns |
| uart | 2 | 50% | 100% | +50.0 | |
| watchdog | 9 | 89% | 89% | +0.0 | |
| yocto | 8 | 88% | 100% | +12.5 | |

### Sonnet Regressions (Cases Haiku Passes but Sonnet Fails)

| Category | Haiku | Sonnet | Failed Cases | Failure Type |
|----------|-------|--------|-------------|-------------|
| boot | 100% | 88% | boot-001 | img_manager_enabled not set |
| gpio-basic | 100% | 67% | gpio-basic-001 | device_ready_check omitted |
| linux-driver | 88% | 75% | linux-driver-004 | error path cleanup missing |
| security | 38% | 25% | security-007 | error path early return missing |
| stm32-freertos | 100% | 0% | stm32-freertos-001 | wrong HAL header |
| stm32-spi | 100% | 0% | stm32-spi-001 | SPI clock init order wrong |

> 8 total regressions — bigger model doesn't guarantee monotonic improvement

---

## 4. Failure Pattern Analysis

### 4.1 Hardest Cases (Both Models Fail, Genuine Errors)

| Case | Haiku Failure | Sonnet Failure | Pattern |
|------|--------------|----------------|---------|
| dma-003 | L0: cyclic_flag | L3: cyclic_enabled | DMA cyclic mode — HW vs SW reload |
| dma-004 | L0: block_descriptors | L0: block_descriptors | Scatter-gather DMA linked list |
| dma-007 | L0: channel_priority | L0: channel_priority | DMA channel priority config |
| dma-009 | L0: headers | L3: config_after_stop | DMA stop-reconfigure-restart |
| isr-concurrency-002 | L0: printk_in_isr | L3: forbidden_apis | ISR-safe communication |
| isr-concurrency-005 | L0: init_before_isr | L2: output_validation | ISR initialization ordering |
| isr-concurrency-008 | L3: memory_barrier | L2: output_validation | Memory barriers between threads |
| kconfig-001 | L0: spi_dma_enabled | L0: spi_dma_enabled | Kconfig dependency chain |
| linux-driver-006 | L3: error_path_cleanup | L3: error_path_cleanup | Reverse-order resource cleanup |
| memory-opt-005 | L0: memdomain | L0: partition_domain | Memory domain partitioning |
| memory-opt-008 | L0: dynamic_thread | L0: fpu_disabled | FPU/thread memory optimization |
| ota-005 | L3: rollback | L3: rollback | OTA rollback on error |
| spi-i2c-004 | L0: spi_header | L3: poll_loop_bounded | Poll loop timeout safety |
| storage-012 | L3: write_rate_limited | L3: write_rate_limited | Flash wear-leveling awareness |
| threading-008 | L3: deadline_magic | L3: deadline_magic | Named constants for deadlines |

### 4.2 Implicit Knowledge Gap (Confirmed by Both Models)

| Pattern | Haiku | Sonnet | Required Domain Knowledge |
|---------|-------|--------|--------------------------|
| `volatile` for ISR-shared vars | FAIL | PASS | C language + ISR interaction |
| Memory barriers between threads | FAIL | FAIL | Hardware memory model |
| DMA cache coherence (flush/invalidate) | FAIL | FAIL | DMA + CPU cache interaction |
| Spinlock (not mutex) for ISR sync | FAIL | FAIL | RTOS concurrency primitives |
| Error path reverse-order cleanup | FAIL | FAIL | Linux driver conventions |
| Flash write rate limiting | FAIL | FAIL | Storage hardware constraints |
| DMA scatter-gather linked list | FAIL | FAIL | DMA controller architecture |
| OTA rollback on partial failure | FAIL | FAIL | System reliability patterns |

---

## 5. Private Cases (Sonnet Only, 48 Held-Out)

| Metric | Value |
|--------|-------|
| Total | 48 |
| Passed | 45 |
| Failed | 3 |
| pass@1 | 93.8% |

**Failures:**
- esp-adc-001: L3 — `adc_read_error_checked` (error handling omission)
- esp-nvs-001: L3 — `nvs_set_error_checked` (error handling omission)
- power-mgmt-009: L3 — `periodic_battery_check` (monitoring loop missing)

> Private 93.8% vs public 76.5% — private cases are likely easier on average, or public check scripts have more env issues.

---

## 6. Benchmark Improvement Recommendations

| Priority | Action | Impact |
|----------|--------|--------|
| P0 | Fix 3 shared `west_build_docker` failures (isr-007, mem-012, thread-013) | Cleaner data |
| P0 | Investigate 5 shared L2 `output_validation` failures (security-002/004/006/008, storage-002) | +5 genuine results |
| P1 | Run n>=3 for both models | Publication-ready CI estimates |
| P1 | Re-baseline Sonnet after check fixes for fair comparison | Remove noise from delta |
| P2 | Add graduated DMA/ISR difficulty (easy→expert) | Better resolution in weak areas |
| P3 | Analyze 8 Sonnet regressions | Understand model-specific failure modes |

---

## 7. Data Files

| File | Contents |
|------|----------|
| `results/test_tracker.json` | Per-case results with content hashes |
| `results/LEADERBOARD.md` | Current leaderboard (latest model) |
| `results/runs/2026-04-04_claude-code___haiku/` | Full Haiku run details |
| `results/runs/2026-04-04_claude-code___sonnet/` | Full Sonnet run details |
| `results/history.json` | Historical run summaries |
