# PLAN: Factor Gap Closure & Benchmark Hardening

**Project:** embedeval
**Created:** 2026-03-28
**Scope:** Close all remaining factor gaps, harden check quality

---

## TL;DR

4 untested factors에 대한 신규 TC 추가, 12 category-only factors에 specific checks 추가, 7 weak factors 강화, check_utils 마이그레이션, 구조적 문제 해결.

---

## Current State

```
44 Factors Total
 ├── 2 Incapable (D9 MISRA, D10 Static Analysis) — SKIP
 ├── 4 Untested (C4, F1, F10, F12) — NEW TCs NEEDED
 ├── 12 Category-only (no specific checks) — ADD CHECKS
 ├── 7 Weak (1 check only) — STRENGTHEN
 └── 19 Well-tested — MAINTAIN
```

```
Check Quality:
 ├── 48 uses of check_utils helpers
 ├── 1070 raw "x" in generated_code substring matches
 └── Target: migrate high-risk substrings to check_utils
```

---

## Phase 1: New TCs for Untested Factors (4 TCs)

### 1.1 C4 Flash Size — `memory-opt-012`

**Factor:** C4 Flash size [Med] — "Code size constraint; LLMs generate verbose code"
**Concept:** LLM must implement a feature within a flash budget. Check whether the generated code avoids bloat patterns (no STL, no large lookup tables, no string-heavy error messages).

```
Prompt: "Implement a CRC-16 calculator for a Cortex-M0 target with 16KB flash.
Minimize code size — avoid lookup tables, floating point, and string formatting."

Checks:
- No float/double usage
- No large array literals (>64 elements)
- No printf/sprintf (use printk with minimal formatting)
- No unnecessary #include (e.g., <stdio.h>, <stdlib.h>)
- CRC algorithm uses bitwise operations (not table-driven)
- Total function count <= 3 (compact implementation)
```

**Category:** memory-opt | **Difficulty:** hard | **Tier:** challenge
**Factors:** C4 (primary), C1 (secondary)

### 1.2 F1 System Architecture — `threading-012`

**Factor:** F1 System architecture [High] — "Bare-metal vs RTOS, polling vs interrupt, task partition"
**Concept:** Give a system-level requirement, let LLM decide task decomposition. Check if the architecture is reasonable.

```
Prompt: "Design a Zephyr application that reads a sensor every 100ms, filters the
data with a moving average, and sends the result over UART every 1 second. The
sensor read must not be delayed by UART transmission. Structure the code with
appropriate task decomposition."

Checks:
- At least 2 threads (sensor + UART, or sensor + processing)
- Sensor thread has higher priority than UART thread
- Uses message queue or FIFO for inter-thread data (not globals)
- Sensor read is in a periodic loop (not one-shot)
- No blocking UART call in sensor thread
- Moving average uses a circular buffer (not recompute from scratch)
```

**Category:** threading | **Difficulty:** hard | **Tier:** challenge
**Factors:** F1 (primary), D1 (secondary)

### 1.3 F10 Long-term Operation — `storage-012`

**Factor:** F10 Long-term operation [Med] — "10yr+ field operation; memory leaks, flash wear"
**Concept:** Test if LLM considers flash wear leveling and avoids memory leaks in a long-running data logger.

```
Prompt: "Implement a persistent data logger on Zephyr that writes sensor readings
to NVS every 10 seconds. The system must operate reliably for years without
manual intervention. Design for flash endurance."

Checks:
- NVS used (not raw flash_write)
- Write rate limited or batch-buffered (not write-per-sample)
- No k_malloc in the main loop (leak prevention)
- Uses static/stack allocation for buffers
- Counter or timestamp uses wrapping-safe comparison
- Error handling on NVS write failure (space full recovery)
```

**Category:** storage | **Difficulty:** hard | **Tier:** challenge
**Factors:** F10 (primary), C3 (secondary), D11 (tertiary)

### 1.4 F12 Multicore/IPC — `threading-013`

**Factor:** F12 Multicore/heterogeneous [Med] — "Cortex-M+A, PRU, DSP IPC/shared memory"
**Concept:** Test IPC between two subsystems via shared memory with proper synchronization.

```
Prompt: "Implement shared-memory IPC between two Zephyr subsystems using a shared
memory region. One producer writes sensor data, one consumer reads and processes
it. Ensure data consistency without using kernel synchronization primitives
across the shared boundary (use memory-mapped flags or mailbox)."

Checks:
- Shared memory region defined (linker section or __attribute__((section)))
- Memory barrier or volatile on shared data
- Producer-consumer handshake (flag/mailbox pattern)
- No k_mutex across shared boundary (different address spaces)
- Data structure has alignment (cache line or 4-byte)
- Both sides check for data validity before processing
```

**Category:** threading | **Difficulty:** hard | **Tier:** challenge
**Factors:** F12 (primary), C10 (secondary), C6 (tertiary)

---

## Phase 2: Add Specific Checks to Category-Only Factors (12 factors)

These factors currently rely only on category pass rate. Add at least 1 specific `check_name` to each.

### 2.1 A4 Pin muxing → device-tree TCs

**Target TCs:** device-tree-006 (pinctrl), device-tree-005 (multi-peripheral)
```
New check: "pinctrl_node_present" — verify pinctrl-0 = <&xxx_default> binding
New check: "pinctrl_names_default" — verify pinctrl-names = "default"
```

### 2.2 A11 Device Tree → device-tree TCs

**Target TCs:** device-tree-001~010
```
New check: "compatible_string_valid" — verify compatible = "vendor,device" format
New check: "status_okay" — verify status = "okay" on active nodes
```

### 2.3 C3 Heap fragmentation → memory-opt TCs

**Target TCs:** memory-opt-001, memory-opt-003
```
New check: "no_malloc_free_in_loop" — detect malloc/free pattern inside while/for
New check: "slab_preferred_over_heap" — for fixed-size, slab used not heap
```

### 2.4 C12 Power budget → power-mgmt TCs

**Target TCs:** power-mgmt-009 (battery-aware)
```
New check: "multiple_sleep_depths" — at least 2 different PM states used
New check: "peripheral_disabled_in_sleep" — device PM or clock gating present
```

### 2.5 D2 Priority inversion → threading-004

Already has `same_mutex_shared` check from Phase 1. Add:
```
New check: "three_distinct_priorities" — verify 3 different priority values in K_THREAD_DEFINE
```

### 2.6 D3 Deadlock → threading-006

```
New check: "consistent_lock_order" — all threads acquire mutexes in same order
(Already partially exists but uses hardcoded names. Generalize.)
```

### 2.7 E3 Build system → kconfig TCs

```
New check: "no_conflicting_configs" — detect mutually exclusive CONFIG pairs both enabled
New check: "dependency_chain_complete" — required parent configs present
```

### 2.8 E7 OTA pipeline → ota TCs

```
New check: "rollback_on_error" — rollback API called in error paths
New check: "self_test_before_confirm" — validation before boot_write_img_confirmed
```

### 2.9 E8 Bootloader sequence → boot TCs

```
New check: "signature_type_present" — at least one signing method configured
New check: "swap_mode_not_conflicting" — UPGRADE_ONLY and SWAP not both enabled
```

### 2.10 F2 Power state machine → power-mgmt TCs

**Target TCs:** power-mgmt-001, power-mgmt-003
```
New check: "suspend_resume_both_handled" — both PM actions have code paths
New check: "state_transition_guarded" — duplicate transition rejected
```

### 2.11 F3 Protocol timing → spi-i2c TCs

**Target TCs:** spi-i2c-006 (clock stretching), spi-i2c-007 (full-duplex)
```
New check: "spi_frequency_configured" — SPI_WORD_SET or frequency field present
New check: "i2c_speed_configured" — I2C_SPEED_SET or i2c_configure present
```

### 2.12 F6 ADC/DAC conversion → sensor-driver TCs, adc TCs

**Target TCs:** sensor-driver-001, gpio-basic-003 (now adc)
```
New check: "raw_to_physical_conversion" — sensor_value.val1/val2 used, or adc_raw_to_millivolts
New check: "unit_conversion_present" — division or multiplication for unit conversion
```

---

## Phase 3: Strengthen Weak Factors (7 factors, 1 check each)

| Factor | Current Check | Add Check |
|--------|--------------|-----------|
| A1 Register/MMIO | register_unregister_balanced | `copy_to_user_not_raw_deref` — no __user pointer dereference |
| A6 Interrupt priority | spinlock_used_in_both_contexts | `irq_priority_configured` — IRQ_CONNECT or irq_enable with priority |
| B5 Timer accuracy | feed_interval_less_than_timeout | `prescaler_calculation_present` — arithmetic for timer period |
| C5 No dynamic alloc | no_forbidden_apis_in_isr | `no_malloc_in_callbacks` — extend to timer/work callbacks |
| C6 Memory alignment | cache_aligned | `aligned_attribute_present` — __aligned() or __attribute__((aligned)) |
| D4 Critical section | spinlock_used_in_both_contexts | `irq_lock_duration_minimal` — no sleep/printk inside locked region |
| D5 Atomic operations | atomic_indices | `atomic_type_for_shared` — atomic_t on shared counters/flags |

---

## Phase 4: check_utils Migration (High-Risk Substring Patterns)

**Current state:** 1070 raw substring matches vs 48 check_utils calls.
**Target:** Migrate the ~50 highest-risk patterns to check_utils helpers.

### Priority patterns to migrate:

| Pattern | Risk | Migration Target | Est. TCs |
|---------|------|-----------------|----------|
| `"printk" in generated_code` | Matches `snprintk` | `has_api_call(code, "printk")` | ~30 |
| `"volatile" in generated_code` | Matches comments | `check_qualifier_on_variable()` | ~15 |
| `"return" in generated_code` | Matches any return | `check_return_after_error()` | ~20 |
| `"if (" in generated_code` | Matches ANY if | Scoped window checks | ~10 |
| `"= 0" in generated_code` | Matches any assignment | Regex with context | ~15 |
| FreeRTOS/Arduino checks | Inconsistent lists | `check_no_cross_platform_apis()` | ~40 |

### Categories with ZERO cross-platform checks:
- **power-mgmt** (0 checks across 12 TCs) — add to all

---

## Phase 5: Structural Fixes

### 5.1 gpio-basic Directory Rename (W3 from review)

6 TCs have directory name `gpio-basic-0xx` but category `uart`/`adc`/`pwm`. Options:
- **Option A:** Rename directories → `uart-001`, `adc-001`, `pwm-001` (breaking: changes case IDs)
- **Option B:** Keep directory names, accept mismatch (current state)
- **Recommendation:** Option A — cleaner long-term, do it now before more references accumulate

### 5.2 Duplicate Check Consolidation

Several TCs have overlapping checks testing the same property (e.g., watchdog-005 checks 2 and 7 both test volatile on health flag). Consolidate to single authoritative check.

---

## Execution Strategy

| Phase | Parallelism | TCs/Files | Est. Effort |
|-------|-------------|-----------|------------|
| Phase 1 | 4 agents (1 per new TC) | 4 new TCs | Medium |
| Phase 2 | 6 agents (2 factors each) | ~20 files | Medium |
| Phase 3 | 1 agent (all 7 quick) | ~10 files | Low |
| Phase 4 | 4 agents (by pattern type) | ~50 files | High |
| Phase 5 | 2 agents | ~10 files + renames | Low |

**Total estimated: ~90 file changes**

---

## Success Criteria

- [ ] 0 untested factors (excluding D9/D10 incapable)
- [ ] All 42 testable factors have at least 1 specific check_name
- [ ] All categories have cross-platform contamination checks
- [ ] High-risk substring patterns migrated to check_utils
- [ ] 992+ tests passing
- [ ] sync_docs.py passes
