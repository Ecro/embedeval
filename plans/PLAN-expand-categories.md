# PLAN: EmbedEval Category Expansion (13 -> 20)

**Project:** embedeval
**Task:** Expand CaseCategory from 13 to 20 categories with multi-platform support
**Priority:** High
**Created:** 2026-03-23

---

## Executive Summary

> **TL;DR:** Rename `zephyr-kconfig` to `kconfig`, add 7 new categories (gpio-basic, threading, sensor-driver, security, storage, timer, linux-driver), and update all affected files to support Zephyr + FreeRTOS + Yocto/Embedded Linux multi-platform scope.

### What We're Doing
Expanding EmbedEval from a Zephyr-only benchmark to a multi-platform embedded firmware benchmark covering Zephyr RTOS, FreeRTOS, and Yocto/Embedded Linux. This requires adding 7 missing domain categories and renaming 1 existing category.

### Why It Matters
Current 13 categories miss fundamental embedded domains (GPIO, threading, timers, sensors, storage, security, Linux kernel drivers). Research against EmbedAgent (ICSE 2026) and Zephyr/FreeRTOS subsystem maps confirmed these gaps. The user needs coverage across all three platforms for real-world embedded development evaluation.

### Key Decisions
- **Rename `zephyr-kconfig` to `kconfig`:** Covers both Zephyr prj.conf and Linux .config
- **Keep `yocto`:** User explicitly requires Yocto/Linux coverage
- **Add `linux-driver` (not `linux-kernel`):** More precise name for kernel module/driver dev
- **No `freertos-config` category:** FreeRTOS tasks naturally fit into `threading`, `gpio-basic`, etc.

### Estimated Impact
- **Complexity:** Medium
- **Risk Level:** Low (additive change, no logic rewrite)
- **Files Changed:** ~10 files
- **Tests Updated:** ~5 test files

---

## REVIEW CHECKLIST

### Critical Decisions to Verify
- [ ] **Category names:** Are these 20 names right? (see full list below)
- [ ] **`kconfig` rename:** OK to change `zephyr-kconfig` to `kconfig`? (breaks existing case metadata)
- [ ] **`EvalPlatform` expansion:** Add FreeRTOS/Linux platforms now or defer?
- [ ] **`CaseMetadata.zephyr_version` field:** Rename to `sdk_version` for multi-platform?
- [ ] **Existing case `zephyr-kconfig-001`:** Rename directory + update metadata.yaml?

### Testing Coverage
- [ ] All 94 existing tests must still pass after changes
- [ ] Test files referencing `CaseCategory.KCONFIG` and `"zephyr-kconfig"` updated
- [ ] E2E test `PILOT_CASE_IDS` updated if case directory renamed

---

## Problem Analysis

### What
Add 7 new `CaseCategory` enum values, rename 1 existing value, and update all references across the codebase (models, tests, docs, existing case metadata).

### Why
Research identified these gaps:
1. **gpio-basic** — Most fundamental embedded task, completely missing
2. **threading** — RTOS threading is distinct from ISR concurrency
3. **sensor-driver** — Zephyr sensor API / Linux IIO / HAL wrappers
4. **security** — TF-M, PSA Crypto, OP-TEE (distinct from boot)
5. **storage** — NVS, settings, flash, file systems
6. **timer** — HW/SW timers (distinct from watchdog)
7. **linux-driver** — Linux kernel modules, char/platform/IIO drivers

### Success Criteria
- [ ] `CaseCategory` enum has exactly 20 values
- [ ] `KCONFIG` value is `"kconfig"` (not `"zephyr-kconfig"`)
- [ ] All tests pass (`uv run pytest`)
- [ ] Linting passes (`uv run ruff check src/ tests/`)
- [ ] Type checking passes (`uv run mypy src/`)
- [ ] Existing case `zephyr-kconfig-001` metadata updated
- [ ] Documentation (README, CONTRIBUTING, METHODOLOGY) updated

---

## Full Category List (20)

### Tier 1: Platform-Agnostic C Code (11)

| # | Enum Name | Value | Description |
|---|-----------|-------|-------------|
| 1 | `GPIO_BASIC` | `gpio-basic` | **NEW** GPIO, UART, ADC, PWM basic I/O |
| 2 | `SPI_I2C` | `spi-i2c` | SPI/I2C bus protocol communication |
| 3 | `DMA` | `dma` | DMA controller programming |
| 4 | `ISR_CONCURRENCY` | `isr-concurrency` | ISR safety, atomic, lock-free |
| 5 | `THREADING` | `threading` | **NEW** RTOS/OS threads, mutex, queue |
| 6 | `TIMER` | `timer` | **NEW** HW/SW timers, RTC |
| 7 | `SENSOR_DRIVER` | `sensor-driver` | **NEW** Sensor/device driver development |
| 8 | `NETWORKING` | `networking` | TCP/IP, MQTT, CoAP, sockets |
| 9 | `BLE` | `ble` | Bluetooth Low Energy |
| 10 | `SECURITY` | `security` | **NEW** Crypto, TF-M, OP-TEE, PSA |
| 11 | `STORAGE` | `storage` | **NEW** NVS, settings, flash, FS |

### Tier 2: System-Level (6)

| # | Enum Name | Value | Description |
|---|-----------|-------|-------------|
| 12 | `KCONFIG` | `kconfig` | **RENAMED** Kconfig fragments (Zephyr + Linux) |
| 13 | `DEVICE_TREE` | `device-tree` | Device Tree overlays |
| 14 | `BOOT` | `boot` | MCUboot, U-Boot |
| 15 | `OTA` | `ota` | DFU, SWUpdate, firmware updates |
| 16 | `POWER_MGMT` | `power-mgmt` | Power management, sleep modes |
| 17 | `WATCHDOG` | `watchdog` | Watchdog configuration |

### Tier 3: Platform-Specific (3)

| # | Enum Name | Value | Description |
|---|-----------|-------|-------------|
| 18 | `YOCTO` | `yocto` | BitBake recipes, layers |
| 19 | `LINUX_DRIVER` | `linux-driver` | **NEW** Kernel modules, char/platform drivers |
| 20 | `MEMORY_OPT` | `memory-opt` | Memory optimization |

---

## Implementation Plan

### Phase 1: Core Model Changes

**File: `src/embedeval/models.py`**
- [ ] Rename `KCONFIG = "zephyr-kconfig"` to `KCONFIG = "kconfig"`
- [ ] Add 7 new enum values: `GPIO_BASIC`, `THREADING`, `SENSOR_DRIVER`, `SECURITY`, `STORAGE`, `TIMER`, `LINUX_DRIVER`
- [ ] Reorder enum alphabetically or by tier

### Phase 2: Scorer Fallback Update

**File: `src/embedeval/scorer.py`**
- [ ] Update `_resolve_category()` — default fallback currently returns `CaseCategory.KCONFIG`, verify this still makes sense

### Phase 3: Existing Case Migration

**File: `cases/zephyr-kconfig-001/metadata.yaml`**
- [ ] Change `category: "zephyr-kconfig"` to `category: "kconfig"`

### Phase 4: Test Updates

**File: `tests/test_runner.py`**
- [ ] Update `_create_case()` default `category="zephyr-kconfig"` to `"kconfig"`
- [ ] Update `test_filter_by_category` string `"zephyr-kconfig"` to `"kconfig"`

**File: `tests/test_reporter.py`**
- [ ] Update `_make_report()` — `CaseCategory.KCONFIG` reference (enum name unchanged, just value changes)
- [ ] Update string assertions: `"zephyr-kconfig"` to `"kconfig"`

**File: `tests/test_e2e.py`**
- [ ] Verify `PILOT_CASE_IDS` — directory name `zephyr-kconfig-001` stays the same (case ID != category value)

### Phase 5: Documentation Updates

**File: `README.md`**
- [ ] Update "13 categories" to "20 categories"
- [ ] Update category table (add 7 new, rename kconfig)
- [ ] Update project description for multi-platform scope

**File: `docs/CONTRIBUTING.md`**
- [ ] Update "13 supported categories" list
- [ ] Update metadata.yaml example
- [ ] Note multi-platform support (not just Zephyr)

**File: `docs/METHODOLOGY.md`**
- [ ] Add note about multi-platform scope
- [ ] Keep 5-layer methodology (applies to all platforms)

**File: `CLAUDE.md`**
- [ ] Update category count and list

### Phase 6: Verification

- [ ] `uv run pytest` — all tests pass
- [ ] `uv run ruff check src/ tests/` — no lint errors
- [ ] `uv run ruff format --check src/ tests/` — formatting OK
- [ ] `uv run mypy src/` — type check passes
- [ ] `uv run embedeval list --cases cases/` — shows cases with new category value
- [ ] `uv run embedeval validate --cases cases/` — reference solutions still pass

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Rename breaks existing JSON results | Low | No existing benchmark results in production yet |
| Tests reference old string `"zephyr-kconfig"` | Medium | Grep all test files, update systematically |
| `_resolve_category` fallback logic wrong | Low | Review and test the fallback path |

---

## Files Changed Summary

| File | Change Type | Description |
|------|-------------|-------------|
| `src/embedeval/models.py` | Edit | Add 7 enums, rename 1 |
| `src/embedeval/scorer.py` | Edit | Review fallback logic |
| `cases/zephyr-kconfig-001/metadata.yaml` | Edit | category value update |
| `tests/test_runner.py` | Edit | Update category strings |
| `tests/test_reporter.py` | Edit | Update category strings |
| `tests/test_e2e.py` | Review | Verify no breakage |
| `README.md` | Edit | Update categories table |
| `docs/CONTRIBUTING.md` | Edit | Update categories list |
| `docs/METHODOLOGY.md` | Edit | Multi-platform note |
| `CLAUDE.md` | Edit | Update category count |
