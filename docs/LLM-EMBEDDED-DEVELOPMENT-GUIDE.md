# LLM-Assisted Embedded Development Guide

A complete system for using LLMs to develop embedded firmware — from
requirements through deployment — without shipping demos as products.

**Companion documents:**
- [LLM-EMBEDDED-FAILURE-FACTORS.md](LLM-EMBEDDED-FAILURE-FACTORS.md) — 42 code factors + 19 non-code factors describing WHERE LLMs fail
- [LLM-EMBEDDED-CONSIDERATIONS.md](LLM-EMBEDDED-CONSIDERATIONS.md) — 14 production-scale failure patterns and practical guidance for teams
- [LLM-EMBEDDED-TOKEN-SCALING.md](LLM-EMBEDDED-TOKEN-SCALING.md) — token scaling economics: why infinite tokens aren't enough for embedded

---

## Quick Start

**New to LLM-assisted embedded development?** Follow this path:

1. **Read** [The Core Problem](#the-core-problem) (2 min)
2. **Create** a [Board Profile](#11-board-profile) and [SDK Profile](#13-sdk-profile) for your project (1-2 days first time)
3. **Copy** the [CLAUDE.md template](#42-claudemd-for-embedded-projects) into your repo
4. **Pick** a module to implement. Select the matching [context template](#32-module-type-templates)
5. **Follow** the [context assembly checklist](#33-context-assembly-checklist)
6. **Generate** code with the LLM, then **review** using the [manual checklist](#phase-4-review--static-analysis)
7. **Test** on hardware — [6 test levels](#phase-5-testing-6-levels)

**Already using LLMs for embedded?** Jump to:
- [Model selection](#5-model-selection-for-embedded-tasks) — which model for which task
- [Prompt engineering techniques](#6-prompt-engineering-for-embedded--how-to-ask) — 16 specific techniques
- [Anti-patterns](#7-anti-patterns--common-mistakes) — 20 common mistakes ranked by impact
- [Maturity model](#8-maturity-model--growing-your-llm-practice) — assess your current level

---

## Table of Contents

1. [Knowledge Base](#1-knowledge-base--what-to-prepare-before-writing-code)
   - [Board Profile](#11-board-profile) · [Pin Map](#12-pin-map) · [SDK Profile](#13-sdk-profile) · [Requirements](#14-requirements-specification)
2. [Development Workflow](#2-development-workflow--7-phases) — Phase 0-6
3. [Context Templates & Assembly](#3-context-templates--assembly)
   - [Universal Context](#31-universal-context-always-include) · [Template Library](#32-module-type-templates) (9 templates) · [Checklist](#33-context-assembly-checklist)
4. [Environment Setup](#4-environment-setup) — Tooling + CLAUDE.md
5. [Model Selection](#5-model-selection-for-embedded-tasks) — Benchmark-based guidance
6. [Prompt Engineering](#6-prompt-engineering-for-embedded--how-to-ask)
   - [Structural](#61-structural-techniques) · [Knowledge Injection](#62-knowledge-injection-techniques) · [Reasoning](#63-reasoning-techniques) · [Iteration](#64-iteration-techniques) · [Future Work](#65-techniques-to-explore-future-work)
7. [Anti-Patterns](#7-anti-patterns--common-mistakes) — 28 mistakes ranked by impact
8. [Maturity Model](#8-maturity-model--growing-your-llm-practice) — 4 levels
9. [Project Safety Checklist](#9-project-safety-checklist--copy-and-fill-per-project)
   - [How It Works](#91-how-this-checklist-works) · [Project Context](#92-project-context-documents) · [Per-Module Checklist](#93-per-module-safety-checklist) · [Traceability Matrix](#94-requirements-traceability-matrix)

---

## The Core Problem

An embedded project's knowledge is scattered across datasheets (500+ pages),
schematics, board pinmaps, SDK docs, coding standards, safety requirements,
and existing code. An LLM needs the **right subset** of this knowledge at the
**right time** for each task.

Dumping everything into context doesn't work — it exceeds token limits and
dilutes focus (Chroma 2025: performance degrades at every length increment).
Feeding nothing doesn't work — the LLM hallucinates APIs and misses hardware
constraints. The solution is **context engineering** — the practice of curating
exactly the right information for each task. This guide implements context
engineering through a **structured knowledge base** with **selective context
assembly** per task.

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  Datasheet ──┐                                                 │
│  Schematic ──┤                    ┌──────────────┐             │
│  Pinmap ─────┤──► Knowledge ──►  │ Context      │──► LLM      │
│  SDK docs ───┤      Base         │ Package      │   (focused  │
│  Standards ──┤    (curated,      │ (per-task,   │    prompt)   │
│  Req docs ───┘     structured)   │  2-5 pages)  │             │
│                                   └──────────────┘             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 1. Knowledge Base — What to Prepare Before Writing Code

Create these files **once per project** (or once per board/SDK). They are the
foundation that makes every subsequent LLM interaction effective.

### 1.1 Board Profile

One file per target board. Extract from datasheet and schematic — the LLM
cannot read PDF datasheets or KiCad schematics directly.

> **Platform note:** Fields marked `[Universal]` apply to all MCUs.
> Fields marked `[MCU-specific]` may not apply to your platform — adapt or omit.
> This example uses STM32. For ESP32: no CCM, no SWD (use JTAG/USB), different memory map.
> For nRF: different power domains, no FPU on some variants.

```markdown
# Board Profile: [Board Name]

## MCU [Universal]
- Part: STM32F407VGT6 (or nRF52840, ESP32-S3, etc.)
- Core: ARM Cortex-M4F @ 168 MHz
- Flash: 1 MB
- RAM: 192 KB (128 KB main + 64 KB CCM)
- FPU: Yes (single precision)

## Memory Map [Universal — addresses are MCU-specific]
| Region | Start | Size | Usage |
|--------|-------|------|-------|
| Flash | 0x0800_0000 | 1 MB | Application (0-768K), OTA slot (768K-1M) |
| SRAM1 | 0x2000_0000 | 128 KB | Heap, stacks, .bss, .data |
| CCM | 0x1000_0000 | 64 KB | DMA-inaccessible; use for stack/compute [STM32-specific — omit for ESP32/nRF] |

## Power Domains
| Domain | Voltage | Peripherals | Sleep Behavior |
|--------|---------|-------------|----------------|
| VDD | 3.3V | Core, GPIO, ADC | Off in standby |
| VBAT | 3.0V (coin cell) | RTC, backup regs | Always on |

## Oscillators
- HSE: 8 MHz crystal → PLL → 168 MHz SYSCLK
- LSE: 32.768 kHz crystal → RTC
- HSI: 16 MHz RC (backup, ±1%)

## Debug Interface
- SWD on PA13 (SWDIO), PA14 (SWCLK)
- UART debug on PB6 (TX), PB7 (RX) @ 115200

## Known Errata (silicon rev Z)
- [ES0182 2.1.8] I2C BUSY flag stuck after reset → software clear sequence
- [ES0182 2.5.1] DMA2 Stream 7 may lose last byte → read NDTR workaround
```

### 1.2 Pin Map

Every pin used in the project. This is what the LLM needs to generate correct
GPIO init, DT bindings, or HAL configuration.

```markdown
# Pin Map: [Board Name]

## Pin Assignments

| Pin | Function | AF | Direction | Pull | Speed | Notes |
|-----|----------|----|-----------|------|-------|-------|
| PA0 | ADC1_CH0 | Analog | Input | None | - | Temperature sensor, 0-3.3V |
| PA5 | SPI1_SCK | AF5 | Output | None | High | Flash memory, 42 MHz max |
| PA6 | SPI1_MISO | AF5 | Input | None | High | |
| PA7 | SPI1_MOSI | AF5 | Output | None | High | |
| PB0 | GPIO_OUT | - | Output | None | Low | LED (active low) |
| PB1 | GPIO_IN | - | Input | Pull-up | - | Button (active low, 10ms debounce) |
| PB6 | USART1_TX | AF7 | Output | None | Med | Debug console 115200 8N1 |
| PB7 | USART1_RX | AF7 | Input | Pull-up | Med | |
| PC4 | INT_ACCEL | EXTI | Input | Pull-up | - | Accelerometer DRDY, falling edge |

## Peripheral-DMA-IRQ Map

| Peripheral | DMA Controller | Stream | Channel | IRQ | Priority |
|-----------|---------------|--------|---------|-----|----------|
| SPI1 RX | DMA2 | Stream 0 | Ch 3 | DMA2_Stream0_IRQn | High (2) |
| SPI1 TX | DMA2 | Stream 3 | Ch 3 | DMA2_Stream3_IRQn | High (2) |
| USART1 RX | DMA2 | Stream 5 | Ch 4 | DMA2_Stream5_IRQn | Med (5) |
| ADC1 | DMA2 | Stream 4 | Ch 0 | DMA2_Stream4_IRQn | Low (8) |
| I2C1 (accel) | DMA1 | Stream 0 | Ch 1 | - | Polled |

## Interrupt Priority Plan

| Priority | Assignment | Rationale |
|----------|-----------|-----------|
| 0 (highest) | (reserved) | Fault handlers |
| 1 | SysTick | RTOS tick, must not be preempted |
| 2 | DMA SPI | High-throughput data path |
| 3 | EXTI (accel DRDY) | Time-sensitive sensor event |
| 5 | UART DMA | Debug output, can tolerate delay |
| 8 | ADC DMA | Slow periodic sampling |
| 15 (lowest) | Software timer | Non-critical housekeeping |
```

### 1.3 SDK Profile

One file per SDK. Prevents cross-platform confusion and API hallucination.

```markdown
# SDK Profile: Zephyr RTOS 3.6

## Build System
- Tool: west (Zephyr meta-tool)
- Build: cmake + ninja
- Config: Kconfig (prj.conf)
- Device Tree: .dts / .overlay files

## Project Structure

    app/
    ├── CMakeLists.txt      # cmake_minimum_required + find_package(Zephyr)
    ├── prj.conf            # CONFIG_* options
    ├── boards/             # Board-specific overlays
    │   └── nrf52840dk_nrf52840.overlay
    └── src/
        └── main.c

## API Quick Reference

### Threading
| Function | Usage | Notes |
|----------|-------|-------|
| K_THREAD_DEFINE() | Static thread creation | Preferred over k_thread_create |
| k_sleep(K_MSEC(n)) | Sleep current thread | Use K_MSEC/K_SECONDS macros |
| k_msleep(n) | Sleep n milliseconds | Shorthand, takes raw int |

### Synchronization
| Mechanism | ISR-safe? | Use When |
|-----------|-----------|----------|
| k_mutex | NO | Thread-thread shared data |
| k_sem | give: YES, take(K_NO_WAIT): YES | ISR-to-thread signaling |
| k_spin_lock | YES | ISR-thread shared data (short critical section) |
| k_msgq | put(K_NO_WAIT): YES | ISR-to-thread data transfer |
| atomic_* | YES | Simple counters, flags |

### ISR Rules
NEVER call in ISR body:
- k_malloc, k_free
- k_mutex_lock, k_mutex_unlock
- k_sleep, k_msleep, k_usleep
- printk (allowed in Zephyr but causes jitter — avoid in tight ISRs)
- k_sem_take with timeout != K_NO_WAIT

ALLOWED in ISR body:
- k_sem_give
- k_msgq_put(K_NO_WAIT)
- k_work_submit
- atomic_set, atomic_get, atomic_inc
- k_spin_lock / k_spin_unlock

## Forbidden APIs (NOT Zephyr)
| API | Platform | Zephyr Equivalent |
|-----|----------|-------------------|
| xTaskCreate | FreeRTOS | K_THREAD_DEFINE |
| vTaskDelay | FreeRTOS | k_sleep |
| pthread_create | POSIX/Linux | k_thread_create |
| malloc/free | stdlib | k_mem_slab_alloc/free or k_heap_alloc/free |
| printf | stdio | printk or LOG_INF |
| analogRead | Arduino | adc_read (with adc_sequence) |
| gpio_set_level | ESP-IDF | gpio_pin_set_dt |
| HAL_GPIO_WritePin | STM32 HAL | gpio_pin_set_dt |

## Required Kconfig (common)
| Feature | Required Options |
|---------|-----------------|
| GPIO | CONFIG_GPIO=y |
| SPI + DMA | CONFIG_SPI=y, CONFIG_SPI_DMA=y, CONFIG_DMA=y |
| I2C | CONFIG_I2C=y |
| Sensor | CONFIG_SENSOR=y |
| BLE | CONFIG_BT=y, CONFIG_BT_PERIPHERAL=y |
| TLS | CONFIG_NET_SOCKETS_SOCKOPT_TLS=y, CONFIG_TLS_CREDENTIALS=y, CONFIG_MBEDTLS=y |
```

### 1.4 Requirements Specification

Each requirement must be **testable** — with clear acceptance criteria that
can be checked automatically or on hardware.

```markdown
# Requirement: REQ-SENSOR-001

## Description
Read accelerometer (LIS2DH12) at 100 Hz via I2C, buffer 10 samples,
and send batch to processing task via message queue.

## Functional Criteria
- sensor_fetch() called in a while(true) loop
- k_sleep(K_MSEC(10)) between reads (100 Hz)
- sensor_channel_get(SENSOR_CHAN_ACCEL_XYZ) after each fetch
- 10-sample batch pushed to k_msgq as a single struct
- Return value of sensor_fetch checked (< 0 → log error, skip sample)

## Timing Criteria
- Sampling period: 10ms ± 0.5ms (5% tolerance)
- I2C transaction must complete within 2ms
- Message queue push must not block > 1ms (use K_MSEC(1) timeout)

## Resource Criteria
- Thread stack: 1024 bytes maximum
- Message queue depth: 4 batches (prevents data loss if consumer is slow)
- No dynamic allocation (use static queue)

## Safety Criteria
- sensor_fetch error → log + continue (do not halt)
- Queue full → drop oldest batch + log warning (do not block producer)
- Sensor not ready at boot → retry 3 times with 100ms delay, then log error and disable

## Test Plan
| Level | Test | Pass Criteria |
|-------|------|---------------|
| L0 Static | Check sensor_fetch return value handled | < 0 branch exists |
| L0 Static | Check k_sleep in loop | K_MSEC(10) present |
| L0 Static | Check no forbidden APIs | No malloc, no printf |
| L3 Emulation | Run on native_sim, verify 100 batches produced | 100 batches in log output |
| L4 Hardware | Logic analyzer on I2C bus | Period = 10ms ± 0.5ms over 1000 samples |
| L5 Stress | Run 24 hours continuously | No memory growth, no error log entries |
```

---

## 2. Development Workflow — 7 Phases

```
  Phase 0        Phase 1         Phase 2          Phase 3
  KNOWLEDGE  ──► REQUIREMENTS ──► ARCHITECTURE ──► IMPLEMENTATION
  BASE SETUP     ENGINEERING      & DESIGN         (per module)
  [Human]        [Human+LLM]     [Human+LLM]      [LLM+Human]
      │               │               │                │
      │               │               │                ▼
      │               │               │          Phase 4
      │               │               │          REVIEW &
      │               │               │          STATIC ANALYSIS
      │               │               │          [Tools+Human]
      │               │               │                │
      │               │               │                ▼
      │               │               │          Phase 5
      │               │               │          TESTING
      │               │               │          (6 levels)
      │               │               │          [Human+Tools+Board]
      │               │               │                │
      │               │               │                ▼
      │               │               │          Phase 6
      │               │               │          INTEGRATION
      │               │               │          & RELEASE
      │               │               │          [Human]
      │               │               │                │
      └───────────────┴───────────────┴────────────────┘
                    feedback loops (update knowledge base)
```

### Phase 0: Knowledge Base Setup

| Aspect | Detail |
|--------|--------|
| **Who** | Lead embedded engineer |
| **Input** | Datasheets, schematics, SDK docs, coding standards |
| **LLM Role** | Can help extract/summarize datasheet sections if given PDF text |
| **Output** | Board Profile, Pin Map, SDK Profile, Coding Standard |
| **Time** | 1-2 days for new MCU family; 2-4 hours for known MCU on new board; 30 min for new project on known board |
| **Amortized** | Done once per board+SDK combination, reused across projects |

**LLM can help with:**
- Converting datasheet tables to markdown (paste text, ask to format)
- Generating SDK API cheatsheets from header files (feed `.h` files)
- Creating Kconfig dependency lists from SDK documentation

**Human must do:**
- Verify every pin assignment against actual schematic
- Verify memory map against linker script
- Verify errata against actual silicon revision
- Decide interrupt priority scheme (architectural decision)

### Phase 1: Requirements Engineering

| Aspect | Detail |
|--------|--------|
| **Who** | Product owner + embedded engineer |
| **Input** | Product spec, safety requirements, regulatory constraints |
| **LLM Role** | Decompose high-level requirements into testable specs |
| **Context** | Board Profile (for resource constraints), Safety standards |
| **Output** | Structured requirements with test criteria |

**Prompt pattern:**
```
Given this product requirement:
"The device must read temperature every second and transmit via BLE"

And these constraints:
- MCU: nRF52840 (256KB RAM, 1MB Flash)
- RTOS: Zephyr 3.6
- BLE: Peripheral role, GATT notifications
- Battery: CR2032 (target 1 year life)

Decompose into testable requirements with:
1. Functional criteria (what the code must do)
2. Timing criteria (periods, deadlines, margins)
3. Resource criteria (RAM, stack, buffers)
4. Safety criteria (error handling, fallback behavior)
5. Test plan (which level tests which criteria)
```

### Phase 2: Architecture & Design

| Aspect | Detail |
|--------|--------|
| **Who** | Embedded engineer (primary), LLM (advisor) |
| **Input** | Requirements, Board Profile, SDK Profile |
| **LLM Role** | Suggest task decomposition, IPC patterns, review decisions |
| **Output** | Architecture document: tasks, priorities, IPC, memory map |

**Human decides:**
- Number of RTOS tasks and their responsibilities
- IPC mechanism between tasks (queue, semaphore, shared memory)
- Interrupt assignments and priorities
- Memory partitioning (stack sizes, heap budgets, DMA buffers)
- Error handling strategy (fail-fast, retry, degrade)
- Power management strategy (sleep modes, wake sources)

**LLM can help with:**
- Drafting the architecture document from decisions
- Suggesting IPC patterns for specific communication needs
- Calculating stack size estimates from call depth analysis
- Reviewing architecture for obvious issues (blocking in ISR, etc.)

**Architecture document template:**
```markdown
# Architecture: [Project Name]

## Task Decomposition
| Task | Priority | Stack | Period | Responsibility |
|------|----------|-------|--------|---------------|
| sensor_task | 5 | 1024 | 10ms | Read accelerometer, buffer, send to processing |
| process_task | 7 | 2048 | - | Receive batches, compute FFT, detect anomaly |
| ble_task | 10 | 2048 | - | BLE GATT server, send notifications on event |
| watchdog_task | 3 | 512 | 500ms | Feed WDT, monitor task health |

## IPC
| From | To | Mechanism | Depth | Data |
|------|-----|-----------|-------|------|
| sensor_task | process_task | k_msgq | 4 | struct accel_batch (120 bytes) |
| process_task | ble_task | k_sem + shared struct | 1 | struct anomaly_event |
| ISR (DRDY) | sensor_task | k_sem_give | 1 | (signal only) |

## Memory Budget
| Allocation | Size | Notes |
|-----------|------|-------|
| sensor_task stack | 1024 | No deep calls, no printf |
| process_task stack | 2048 | FFT needs scratch space |
| ble_task stack | 2048 | BLE stack requires this minimum |
| watchdog_task stack | 512 | Minimal: feed + health check |
| Message queue buffers | 480 | 4 × 120 bytes |
| BLE buffers | 2048 | CONFIG_BT_BUF_ACL_TX_SIZE |
| **Total static** | **~8 KB** | of 256 KB available |

## Error Strategy
| Error | Response | Recovery |
|-------|----------|----------|
| Sensor I2C timeout | Log, skip sample, continue | Auto-recovers next cycle |
| Queue full | Drop oldest, log warning | Continues without data loss |
| BLE disconnect | Stop notifications, advertise | Auto-reconnect |
| Process task crash | WDT triggers reset | Clean reboot |
| OTA download fail | Abort DFU, keep current image | Manual retry |
```

### Phase 3: Implementation (Per Module)

| Aspect | Detail |
|--------|--------|
| **Who** | LLM (generator), Human (reviewer) |
| **Input** | Architecture doc + module requirement + context package |
| **LLM Role** | Generate code for ONE module at a time |
| **Output** | Draft source files for review |

**Critical rules:**
1. **One module per prompt** — multi-module generation fails (complexity cliff)
2. **Always include the context package** — see Section 3
3. **Demand error handling explicitly** — "Check return value of every API call. On error, goto cleanup."
4. **Specify what NOT to do** — "Do NOT use FreeRTOS APIs. Do NOT use malloc."
5. **Provide the interface** — paste header files and types the module must use

### Phase 4: Review & Static Analysis

| Aspect | Detail |
|--------|--------|
| **Who** | Tools (automated) + Human (manual) |
| **Input** | Generated code |
| **Output** | Issue list → feed back to LLM or fix manually |

**Automated pipeline (CI/pre-commit):**

> **Note:** Steps 1-3 use standard tools. Steps 4-6 require project-specific
> scripts — minimal implementations shown below. Adapt for your project.

```bash
# 1. Cross-compile (standard)
west build -b $BOARD app/

# 2. MISRA check (standard — requires cppcheck ≥ 2.7)
cppcheck --addon=misra --enable=all src/

# 3. Cross-platform API scan (grep — works today)
grep -rn -E 'xTaskCreate|vTaskDelay|analogRead|HAL_GPIO|gpio_set_level' src/
# Must return empty

# 4. ISR body forbidden API scan (minimal: grep-based)
# Full version would extract ISR function bodies and scan only those
grep -n 'k_malloc\|k_mutex_lock\|k_sleep\|k_msleep' src/*.c | \
  grep -i 'isr\|irq\|handler\|callback'
# Any output = potential ISR violation → manual review needed

# 5. Kconfig consistency (minimal: compare CONFIG usage vs prj.conf)
for cfg in $(grep -ohP 'CONFIG_\w+' src/*.c src/*.h | sort -u); do
  grep -q "$cfg" prj.conf || echo "WARNING: $cfg used in code but not in prj.conf"
done

# 6. Resource balance (minimal: count alloc vs free)
echo "alloc: $(grep -c 'k_mem_slab_alloc\|k_heap_alloc\|k_malloc' src/*.c)"
echo "free:  $(grep -c 'k_mem_slab_free\|k_heap_free\|k_free' src/*.c)"
# Counts should be roughly equal — investigate if not

# 7. Strict aliasing violations (type punning via pointer cast)
grep -rn '(\(struct\|uint32_t\|uint16_t\|int32_t\|int16_t\) \*)' src/*.c
# Any output = potential strict aliasing violation → use memcpy instead

# 8. Runtime malloc (heap fragmentation risk in long-running systems)
grep -rn 'malloc\|k_malloc\|k_heap_alloc\|pvPortMalloc' src/*.c | \
  grep -v 'init\|setup\|start\|main'
# malloc outside init = fragmentation risk over weeks/months

# 9. Missing endianness conversion at protocol boundaries
grep -rn 'i2c_read\|i2c_burst_read\|spi_transceive\|net_buf_pull' src/*.c | \
  grep -v 'ntohs\|ntohl\|htons\|htonl\|bswap\|__builtin_bswap'
# Sensor/network reads without byte-order conversion → investigate
```

**Manual review checklist** (see [Failure Factors](LLM-EMBEDDED-FAILURE-FACTORS.md) and [Considerations](LLM-EMBEDDED-CONSIDERATIONS.md)):
- [ ] Error paths: every init/alloc has cleanup on failure (reverse order)?
- [ ] Shared variables: all have volatile or atomic?
- [ ] Init ordering: matches datasheet sequence?
- [ ] Timing margins: all timeouts < relevant deadline?
- [ ] ISR body: no blocking/allocating calls?
- [ ] DMA buffers: cache-line aligned? flush/invalidate present?
- [ ] Resource lifecycle: every alloc has matching free?
- [ ] Rollback paths: OTA/flash operations have abort path?
- [ ] Endianness: byte-order conversion at every protocol boundary (sensor registers, network)?
- [ ] Float safety: NaN/Inf checks before safety-critical comparisons?
- [ ] Type punning: `memcpy()` used instead of `*(struct*)buf` pointer casts?
- [ ] Counter overflow: 32-bit ms counters wrap at 49.7 days — use 64-bit or wrap-safe arithmetic?
- [ ] Heap usage: no `malloc()`/`free()` in runtime loops (fragmentation over weeks)?
- [ ] Secure OTA: signature verification, anti-rollback, A/B partitioning?

### Phase 5: Testing (6 Levels)

| Level | What | Where | Catches | Automated? |
|-------|------|-------|---------|-----------|
| **L0 Static** | Pattern checks on source | CI | API hallucination, missing volatile, forbidden APIs, Kconfig gaps | Yes |
| **L1 Compile** | Cross-compile + link | CI + Docker | Wrong APIs, missing symbols, section overflow, size budget | Yes |
| **L2 Emulation** | Run on QEMU / native_sim | CI | Logic errors, state machine bugs, IPC correctness | Yes |
| **L3 Hardware** | Run on target board | Lab bench | Peripheral behavior, DMA correctness, real timing, power modes | Manual |
| **L4 Stress** | Extended run (24hr+, target 50 days for counter overflow) | Test rack | Memory leaks, heap fragmentation, counter overflow (49.7d), flash wear, radio state corruption, timing drift | Semi-auto |
| **L5 Formal & Safety** | MC/DC coverage, fault injection, model checking | CI + review | Structural coverage, safety case, spec2code verification (arXiv:2411.13269) | Semi-auto |
| **L6 Regulatory** | EMC pre-scan, RF compliance, environmental testing | Certified lab | FCC/CE/UL compliance — hardware activity, not software testing | Manual |

**Requirements traceability:**
```
REQ-SENSOR-001
  ├── L0: check_sensor_fetch_error_handled      → PASS
  ├── L0: check_k_sleep_in_loop                 → PASS
  ├── L0: check_no_forbidden_apis               → PASS
  ├── L2: test_100_batches_native_sim            → PASS
  ├── L3: test_i2c_timing_logic_analyzer         → PASS (9.98ms avg)
  └── L4: test_24hr_soak                         → PASS (0 errors)
```

**What each level catches that others miss:**

| Bug Type | L0 | L1 | L2 | L3 | L4 | L5 |
|----------|----|----|----|----|----|----|
| Hallucinated API | Sometimes | **Yes** | - | - | - | - |
| Missing volatile | Sometimes | No | Rarely | **Sometimes** | **Yes** | - |
| ISR forbidden call | **Yes** | No | No | **Crash** | - | - |
| Wrong DMA mode | No | No | No | **Yes** | - | - |
| Cache coherency | No | No | No | **Yes** | - | - |
| Timing margin | No | No | No | **Yes** | **Yes** | - |
| Memory leak | No | No | No | No | **Yes** | - |
| Error path bug | Sometimes | No | Sometimes | **Yes** | **Yes** | - |
| MISRA violation | **Yes** | No | No | No | No | **Yes** |

### Phase 6: Integration & Release

| Aspect | Detail |
|--------|--------|
| **Who** | Human (lead engineer) |
| **LLM Role** | Generate release notes, CI scripts, documentation |
| **Activities** | Final integration test, sign firmware image, tag release, update knowledge base |

**Post-release feedback loop:**
- Field issues → update Board Profile (errata, power behavior)
- API changes → update SDK Profile
- New failure patterns → update review checklist
- Test gaps → add requirements + test criteria

---

## 3. Context Templates & Assembly

The **Context Package** is the curated set of information you feed the LLM for
a specific code generation task. It is assembled from the knowledge base.

### 3.1 Universal Context (Always Include)

These go into every prompt, regardless of module type:

```markdown
## Project Context
- Board: [Board name] ([MCU part number])
- SDK: [Zephyr 3.6 / ESP-IDF 5.2 / STM32 HAL 1.28]
- RTOS: [Zephyr / FreeRTOS / bare-metal]

## Coding Rules
- Check return value of EVERY API call. On error: log + cleanup + return error code.
- Use named constants (#define) for all numeric values. No magic numbers.
- No dynamic allocation (malloc/free). Use k_mem_slab or static allocation.
- No stdio.h. Use printk (Zephyr) or ESP_LOG (ESP-IDF).
- All shared variables between ISR and thread must be volatile or atomic_t.

## Forbidden APIs
[paste from SDK Profile FORBIDDEN_APIS section]
```

### 3.2 Module-Type Templates

**9 templates available.** Select the one matching your task, fill in
board-specific values, and combine with Universal Context (3.1).

| Module Type | Template | Key Rules |
|-------------|----------|-----------|
| ISR Handler | [ISR](#isr-handler-template) | No blocking, volatile, spinlock |
| DMA Driver | [DMA](#dma-driver-template) | Alignment, cache, cyclic mode |
| Sensor | [Sensor](#sensor-driver-template) | Periodic loop, device_is_ready |
| Power Mgmt | [Power](#power-management-template) | State machine, error check |
| OTA Update | [OTA](#ota--firmware-update-template) | Rollback, validation, power loss |
| BLE Stack | [BLE](#ble-stack-template) | Service ordering, disconnect handling |
| Kernel Module | [Linux](#linux-kernel-module-template) | goto cleanup, copy_to_user |
| Watchdog | [WDT](#watchdog-template) | Feed margin, conditional feed |
| GPIO/Button | [GPIO](#gpio--button-debounce-template) | device_is_ready, debounce via work |

> **Missing your module type?** Use Universal Context (3.1) with relevant
> ISR/DMA rules. Templates for UART, Timer, Networking/MQTT, and NVS/Flash
> are planned.

#### ISR Handler Template

```markdown
## Task: Implement ISR handler for [peripheral]

## Context
[Universal context]

## Hardware
- Interrupt source: [e.g., EXTI line 4, GPIO PC4, falling edge]
- IRQ name: [e.g., EXTI4_IRQn]
- Priority: [e.g., 3 (preempts priority 5+)]
- Shared data with thread: [e.g., struct sensor_event written in ISR, read in sensor_task]

## ISR Rules (CRITICAL)
- NO blocking calls: no k_mutex_lock, no k_sleep, no k_sem_take with timeout
- NO allocation: no k_malloc, no k_heap_alloc
- NO heavy logging: no printk in tight ISRs (causes jitter)
- ALLOWED: k_sem_give, k_msgq_put(K_NO_WAIT), k_work_submit, atomic_*
- Shared variables MUST be volatile or atomic_t
- Use k_spin_lock (not k_mutex) for ISR-thread shared data
- Spinlock must be used in BOTH ISR body AND thread body

## Synchronization
- Mechanism: [k_sem_give in ISR, k_sem_take in thread]
- Shared data protection: [k_spin_lock with key capture]

## Expected Output
- ISR function body
- Thread-side code that consumes the ISR event
- Shared data declaration with correct qualifiers
```

#### DMA Driver Template

```markdown
## Task: Implement DMA transfer for [peripheral]

## Context
[Universal context]

## Hardware
- DMA controller: [e.g., DMA2]
- Stream/Channel: [e.g., Stream 0, Channel 3 for SPI1 RX]
- Direction: [MEMORY_TO_PERIPHERAL / PERIPHERAL_TO_MEMORY / MEMORY_TO_MEMORY]
- Mode: [CIRCULAR for continuous / NORMAL for one-shot]
- Source/Dest addresses: [peripheral register addr, buffer addr]

## DMA Rules (CRITICAL)
- Buffer MUST be cache-line aligned (32-byte or 64-byte on this MCU)
- For CIRCULAR mode: set .cyclic = 1 in dma_block_config
- Call dma_config() BEFORE dma_start() (strict ordering)
- For continuous: call dma_reload() in DMA callback
- Call dma_stop() on error or when transfer complete
- Cache management:
  - Before TX (memory→peripheral): sys_cache_data_flush_range(buf, size)
  - After RX (peripheral→memory): sys_cache_data_invd_range(buf, size)
- Error flag variable MUST be volatile (written in DMA callback, read in main)

## Buffer Specification
- Size: [e.g., 256 bytes]
- Count: [e.g., 2 for ping-pong, 1 for single]
- Alignment: __aligned(32)

## Expected Output
- DMA configuration and start function
- DMA callback handler
- Buffer declarations with alignment
- Proper cache flush/invalidate calls
```

#### Sensor Driver Template

```markdown
## Task: Implement sensor reading for [sensor part number]

## Context
[Universal context]

## Hardware
- Sensor: [e.g., LIS2DH12 accelerometer]
- Interface: [I2C @ 0x19 / SPI @ CS=PA4]
- Data ready signal: [GPIO PC4, falling edge / polling]
- Register map: [key registers only]
  - WHO_AM_I: 0x0F (expected value: 0x33)
  - CTRL_REG1: 0x20 (ODR[7:4], LP[3], Zen[2], Yen[1], Xen[0])
  - OUT_X_L: 0x28 (6-byte burst read for XYZ, auto-increment)

## Timing
- Sampling period: [e.g., 10ms (100 Hz)]
- I2C bus speed: [100 kHz standard / 400 kHz fast]
- Settling time after power-on: [e.g., 10ms boot + 1/ODR for first sample]

## Requirements
- Read in periodic loop with k_sleep (not one-shot)
- Check device_is_ready() before first use
- Check return value of sensor_fetch() / i2c_burst_read()
- Buffer size: [6 bytes for XYZ burst read]
- Batch N samples before sending to processing task

## Expected Output
- Init function (with device ready check)
- Periodic read function (loop + sleep + error handling)
- Data structure for batch transfer
```

#### Power Management Template

```markdown
## Task: Implement power management for [sleep scenario]

## Context
[Universal context]

## Hardware
- Available sleep modes:
  | Mode | Power | Wake Sources | RAM Retention | Wake Latency |
  |------|-------|-------------|---------------|-------------|
  | Idle | 5 mA | Any IRQ | Full | <1 us |
  | Sleep | 500 uA | GPIO, RTC, UART | Full | ~10 us |
  | Deep Sleep | 5 uA | GPIO, RTC | Partial (16KB) | ~1 ms |
  | Shutdown | 0.5 uA | Reset pin only | None | Full reboot |

## Requirements
- Transition: [e.g., enter Deep Sleep when idle > 30 seconds]
- Wake source: [e.g., GPIO button press (PB1) + RTC alarm (every 60s)]
- Before sleep: [e.g., disable SPI, flush UART, save state to retention RAM]
- After wake: [e.g., re-init SPI, check wake reason, resume or reboot]
- Error handling: pm_device_action_run return value MUST be checked
- Both suspend AND resume transitions must be handled

## Expected Output
- Sleep entry function (with pre-sleep cleanup)
- Wake handler (with post-wake re-init)
- pm_device_action_run calls with error checking
```

#### OTA / Firmware Update Template

```markdown
## Task: Implement OTA firmware update for [transport]

## Context
[Universal context]

## Hardware
- Flash layout: [e.g., Slot 0: 0x0000-0x3FFFF (active), Slot 1: 0x40000-0x7FFFF (staging)]
- Transport: [e.g., BLE DFU / HTTP download / UART XMODEM]
- Bootloader: [e.g., MCUboot with swap-scratch]

## OTA Rules (CRITICAL)
- ALWAYS implement rollback: if download fails → dfu_target_done(false) or equivalent abort
- Verify image integrity BEFORE marking as confirmed (CRC/SHA/signature)
- Self-test after first boot from new image → confirm only if test passes
- Handle power loss at ANY point: download, flash write, reboot, validation
- Never erase active slot before new image is fully validated
- Return value of EVERY DFU API call must be checked

## Secure Boot Chain (CRITICAL)
- Firmware image MUST be signed (RSA/ECDSA) — private key in HSM, NEVER on device
- Device verifies signature with public key from secure element before flashing
- Anti-rollback: version counter prevents downgrade attacks
- A/B partitioning: atomic update with automatic revert on boot failure
- Download over TLS — no plaintext firmware transfer
- MCUs have no ASLR/DEP — buffer overflow in OTA = arbitrary code execution

## State Machine
Download → Validate → Reboot → Self-test → Confirm
    ↓ error    ↓ error              ↓ fail
  Abort      Abort              Rollback (auto via MCUboot)

## Expected Output
- Download function with per-chunk error checking and abort path
- Validation function (CRC/signature check before apply)
- Self-test function (called on first boot from new image)
- Confirm/rollback logic
```

#### BLE Stack Template

```markdown
## Task: Implement BLE [GATT server / peripheral / central] for [use case]

## Context
[Universal context]

## BLE Configuration
- Role: [Peripheral / Central / Both]
- Services: [e.g., Custom sensor service UUID: 0x1234]
- Characteristics:
  | Name | UUID | Properties | Size | Description |
  |------|------|-----------|------|-------------|
  | sensor_data | 0x1235 | Read, Notify | 12 bytes | XYZ accel, 3x int32 |
  | config | 0x1236 | Read, Write | 4 bytes | Sampling rate (Hz) |
- Advertising: [e.g., connectable, 100ms interval, device name "SENSOR-01"]
- Connection: [e.g., min interval 7.5ms, max interval 30ms, timeout 4s]

## BLE Rules
- Register services BEFORE starting advertising
- Handle disconnect event: stop notifications, restart advertising
- Connection parameter update: negotiate after connection established
- MTU exchange: request larger MTU if data > 20 bytes
- Error handling: bt_enable() can fail → check and handle

## Expected Output
- Service and characteristic definitions (BT_GATT_SERVICE_DEFINE)
- Advertising setup and start
- Connection callbacks (connected, disconnected, parameter updated)
- Notification sending function with connection state check
- prj.conf BLE Kconfig options (CONFIG_BT=y, CONFIG_BT_PERIPHERAL=y, etc.)
```

#### Linux Kernel Module Template

```markdown
## Task: Implement Linux kernel module for [device/function]

## Context
- Kernel version: [e.g., 5.15 / 6.1]
- Platform: [e.g., ARM64, Yocto-based]
- Module type: [char device / platform driver / I2C client]

## Kernel Module Rules (CRITICAL)
- __init function: allocate resources in order, cleanup ALL on ANY failure
- __exit function: release resources in REVERSE order of init
- Cleanup must use goto-based unwinding:
  ```
  alloc_chrdev_region → cdev_add → class_create → device_create
  On device_create fail: class_destroy → cdev_del → unregister_chrdev_region
  ```
- Use copy_to_user / copy_from_user for ALL user-space data transfer (NEVER raw __user deref)
- Check IS_ERR() on every pointer-returning function
- kfree every kmalloc on error paths
- Use dev_err/dev_info, not printk with manual prefixes
- MODULE_LICENSE("GPL") required

## Expected Output
- module_init and module_exit functions with full error path cleanup
- File operations struct (read, write, open, release)
- Proper copy_to_user/copy_from_user with size validation
- Device registration with error unwinding
- Makefile for out-of-tree module build
```

#### Watchdog Template

```markdown
## Task: Implement watchdog timer for [reset scenario]

## Context
[Universal context]

## Hardware
- WDT peripheral: [e.g., nRF WDT, STM32 IWDG]
- Channels: [e.g., 2 channels — main loop + communication task]
- Timeout: [e.g., Channel 0: 3000ms, Channel 1: 5000ms]

## WDT Rules (CRITICAL)
- wdt_install_timeout() BEFORE wdt_setup() (strict ordering)
- Feed interval MUST be strictly LESS than timeout (add ≥ 30% margin)
- WDT_FLAG_RESET_SOC on ALL channel configurations
- Periodic feed in a while loop with k_sleep (not one-shot)
- Conditional feed: only feed if monitored task is healthy (not unconditional)
- device_is_ready() before any WDT operation
- Error checking on all WDT API return values

## Expected Output
- WDT init function with channel setup + error handling
- Periodic feed function (loop + health check + sleep)
- Health monitoring (check task heartbeats before feeding)
```

#### GPIO / Button Debounce Template

```markdown
## Task: Implement GPIO [input with debounce / output control]

## Context
[Universal context]

## Hardware
- Pin: [e.g., PB1, active low, external pull-up]
- Function: [e.g., button input with 10ms software debounce]
- Interrupt: [e.g., GPIO_INT_EDGE_TO_ACTIVE on falling edge]

## GPIO Rules
- device_is_ready() BEFORE any GPIO operation (check DT node)
- gpio_pin_configure_dt() — use DT-based API, not raw pin numbers
- For input: configure interrupt, register callback
- Debounce: use k_work_delayable (NOT busy-wait or k_sleep in ISR callback)
- ISR callback body: only submit k_work or give semaphore (no blocking)
- For output: check return value of gpio_pin_set_dt()

## Expected Output
- GPIO init with device_is_ready check
- Button callback (ISR-safe: only schedules work)
- Debounce work handler (processes button event after debounce delay)
```

> **Templates for UART, Timer, Networking/MQTT, and NVS/Flash are planned.**
> Until available, use the [Universal Context](#31-universal-context-always-include)
> with relevant ISR/DMA rules from existing templates.

### 3.3 Context Assembly Checklist

Before sending a prompt to the LLM, verify:

- [ ] **Board identified** — MCU part number, board name
- [ ] **SDK pinned** — exact version number
- [ ] **Forbidden APIs listed** — platform-specific exclusion list
- [ ] **Relevant pins/peripherals** — only what this module uses
- [ ] **DMA/IRQ assignments** — from the Peripheral-DMA-IRQ Map
- [ ] **Timing constraints** — with numeric values and margins
- [ ] **Resource budget** — stack size, buffer sizes, memory limits
- [ ] **Error handling policy** — explicit instructions for every error path
- [ ] **Shared state identified** — which variables, which qualifier (volatile/atomic)
- [ ] **Interface code provided** — header files, struct definitions this module uses
- [ ] **Test criteria included** — so the LLM knows what "correct" means

---

## 4. Environment Setup

### 4.1 Required Tooling

```
Development Machine
│
├── LLM Access
│   ├── Claude Code (CLI) — primary interface
│   │   └── CLAUDE.md per project (universal context + coding rules)
│   ├── MCP Servers
│   │   ├── context7 — SDK documentation lookup (RAG: 2x pass rate on unfamiliar APIs)
│   │   ├── esp-idf-mcp-server — ESP-IDF specific API docs and examples
│   │   └── (future) board-profile-server — auto-inject board context
│   └── Custom hooks (pre-commit checks)
│
├── Knowledge Base (in repo)
│   ├── docs/board/BOARD_PROFILE.md
│   ├── docs/board/PINMAP.md
│   ├── docs/sdk/SDK_PROFILE.md
│   ├── docs/sdk/FORBIDDEN_APIS.md
│   ├── docs/requirements/*.md
│   ├── docs/architecture/ARCHITECTURE.md
│   └── docs/templates/     # Context templates
│
├── Build Environment
│   ├── Docker container with cross-compiler + SDK
│   │   └── Reproducible: Dockerfile in repo
│   ├── west (Zephyr) / idf.py (ESP-IDF) / make (bare-metal)
│   └── CI/CD: GitHub Actions
│       ├── build.yml — cross-compile on every push
│       ├── lint.yml — MISRA + custom linters
│       └── test.yml — QEMU / native_sim tests
│
├── Static Analysis
│   ├── cppcheck + MISRA addon
│   ├── tools/isr_checker.py — scan ISR bodies for forbidden APIs
│   ├── tools/kconfig_checker.py — CONFIG_* usage vs prj.conf
│   ├── tools/alloc_checker.py — alloc/free balance
│   └── tools/api_allowlist.py — cross-platform API detection
│
├── Test Infrastructure
│   ├── QEMU targets (native_sim, qemu_cortex_m3)
│   ├── pytest + twister (Zephyr test framework)
│   ├── Target board + J-Link / ST-Link
│   ├── Logic analyzer (Saleae / DSLogic)
│   └── Serial console monitor (minicom / pyserial)
│
└── Review Tooling
    ├── Pre-commit hooks (format, lint, API scan)
    ├── PR template with embedded review checklist
    └── EmbedEval-style behavioral checks (per module)
```

### 4.2 CLAUDE.md / AGENTS.md for Embedded Projects

> **AGENTS.md** is an emerging cross-tool standard (Linux Foundation / AAIF,
> 2025) supported by Claude Code, Cursor, Copilot, Gemini CLI, and others.
> If you use multiple tools, consider `AGENTS.md` in addition to `CLAUDE.md`.
> The content is the same — the filename determines which tool reads it.

Place this at your project root. It is automatically loaded into every Claude
Code session.

```markdown
# CLAUDE.md — [Project Name]

## Project
- Board: [Board name] ([MCU])
- SDK: [Zephyr 3.6 / ESP-IDF 5.2]
- Platform: [Zephyr RTOS / FreeRTOS / bare-metal]

## Build
- `west build -b [board] app/` — Build
- `west flash` — Flash to target
- `west build -t run` — Run on QEMU (if supported)

## Coding Rules (MANDATORY)
1. Check return value of every API call. On error: cleanup in reverse order.
2. Named constants for all numeric values. No magic numbers.
3. No malloc/free. Use k_mem_slab or static allocation.
4. No stdio.h. Use printk or LOG_INF/LOG_ERR.
5. Shared ISR/thread variables: volatile or atomic_t.
6. ISR body: no blocking (mutex, sleep, sem_take with timeout).
7. DMA buffers: __aligned(32), cache flush/invalidate around transfers.

## Forbidden APIs
Do NOT use: xTaskCreate, vTaskDelay, analogRead, digitalWrite,
HAL_GPIO_WritePin, gpio_set_level, pthread_*, printf, malloc, free,
open, close, read, write (POSIX file I/O).

## Key Files
- docs/board/BOARD_PROFILE.md — MCU specs, memory map, errata
- docs/board/PINMAP.md — Pin assignments, DMA map, IRQ priorities
- docs/sdk/SDK_PROFILE.md — API reference, Kconfig requirements
- docs/requirements/ — Structured requirements with test criteria

## Before Generating Code
Read the relevant requirement spec and the corresponding context template.
Always include error handling for every API call.
```

#### ESP-IDF Variant

```markdown
# CLAUDE.md — [Project Name] (ESP-IDF)

## Project
- Board: [e.g., ESP32-S3-DevKitC-1]
- SDK: ESP-IDF v5.2
- Platform: FreeRTOS (ESP-IDF native)

## Build
- `idf.py build` — Build
- `idf.py flash -p /dev/ttyUSB0` — Flash
- `idf.py monitor -p /dev/ttyUSB0` — Serial monitor
- `idf.py menuconfig` — Configure (sdkconfig)

## Coding Rules (MANDATORY)
1. Check return value of every API call (ESP_OK / ESP_ERR_*).
2. Named constants for all numeric values. No magic numbers.
3. No malloc/free. Use heap_caps_malloc(size, MALLOC_CAP_DMA) for DMA buffers.
4. Logging: ESP_LOGI/ESP_LOGW/ESP_LOGE with TAG. No printf.
5. ISR functions: IRAM_ATTR attribute. No printf, no malloc, no mutex.
6. ISR-to-task: xQueueSendFromISR (not xQueueSend). Check xHigherPriorityTaskWoken.
7. DMA buffers: heap_caps_malloc with MALLOC_CAP_DMA. Cache flush via esp_cache_msync().

## Forbidden APIs
Do NOT use: k_sleep, K_THREAD_DEFINE, printk, k_sem_give,
gpio_pin_set_dt, analogRead, digitalWrite, delay(),
HAL_GPIO_WritePin, pthread_create.
```

#### STM32 HAL + FreeRTOS Variant

```markdown
# CLAUDE.md — [Project Name] (STM32 HAL)

## Project
- Board: [e.g., NUCLEO-F407ZG]
- SDK: STM32CubeF4 v1.28.0 + FreeRTOS v10.5
- Platform: FreeRTOS on STM32 HAL

## Build
- `make -j$(nproc)` — Build (Makefile project)
- Or: STM32CubeIDE Build (GUI)
- `st-flash write build/*.bin 0x08000000` — Flash via ST-Link
- `minicom -D /dev/ttyACM0 -b 115200` — Serial debug

## Coding Rules (MANDATORY)
1. Check HAL return: HAL_OK / HAL_ERROR / HAL_BUSY / HAL_TIMEOUT.
2. Named constants for all numeric values. No magic numbers.
3. No malloc/free in MISRA projects. Use pvPortMalloc/vPortFree or static alloc.
4. Logging: printf via SWO/UART retarget, or custom LOG macro. No ESP_LOG.
5. ISR: No osDelay, no osMutexAcquire. Use osMessageQueuePut with timeout=0.
6. Enable clock before peripheral init: __HAL_RCC_GPIOx_CLK_ENABLE() before HAL_GPIO_Init().
7. DMA buffers: __ALIGNED(32) attribute. SCB_CleanDCache_by_Addr before TX, SCB_InvalidateDCache_by_Addr after RX.

## Forbidden APIs
Do NOT use: k_sleep, K_THREAD_DEFINE, printk, gpio_pin_set_dt,
gpio_set_level, esp_log_write, analogRead, digitalWrite, delay().
```

---

## 5. Model Selection for Embedded Tasks

Not all LLMs perform equally on embedded code. EmbedEval benchmark data
(n=3 run aggregate mean, **233 cases** — 185 public + 48 private — across 23 categories, post-check-fix) shows
significant performance gaps between model tiers.

### 5.1 Overall Performance

| Model | pass@1 | 95% CI | Failed | Strongest | Weakest |
|-------|--------|--------|--------|-----------|---------|
| Sonnet 4.6 | 68.0% (n=3 mean) | [64.4%, 71.3%] | ~75/233 | adc, device-tree, pwm (100%) | isr-concurrency (23%), dma (31%), threading (33%) |
| Haiku 4.5 | 56.9% (n=3 mean) | [53.2%, 60.6%] | ~100/233 | boot, device-tree, pwm (100%) | dma (8%), storage (31%), memory-opt (33%) |

**Gap: 11.1 percentage points overall; largest category split on DMA (31% vs 8% pass@1).**

See [BENCHMARK-COMPARISON-2026-04-05.md](BENCHMARK-COMPARISON-2026-04-05.md) for detailed per-case analysis.

### 5.2 Category Risk Tiers

Based on n=3 aggregate pass@1, embedded tasks fall into four risk tiers (rates are Sonnet / Haiku unless noted):

| Risk Tier | Categories | Pass@1 (illustrative) | Recommendation |
|-----------|------------|----------------------|----------------|
| **Critical risk** (best model under 40%) | threading (33%/33%), isr-concurrency (23%/38%), dma (31%/8%) | — | Sonnet minimum; expert review mandatory. Haiku especially weak on DMA. |
| **High risk** (40–65% or mixed quality) | memory-opt (67%/33%), storage (54%/31%), security (50%/70%), uart (33%/67%), adc (100%/50%) | — | Sonnet strongly preferred where it leads (e.g. adc, uart); full review of concurrency and error paths. |
| **Moderate** (65–85%) | gpio-basic, ble, ota, kconfig, power-mgmt, sensor-driver, spi-i2c, linux-driver, yocto, timer | e.g. ble 82%/45%, timer 83%/50%, networking 75%/75% | Sonnet default; mandatory review for HW interaction and timing. |
| **Low risk** (best model over 85%) | device-tree, pwm, boot (90%/100%), watchdog (90%/60%) | 90–100% / 60–100% | Sonnet or Haiku often sufficient; still run CI and spot-check. |

### 5.3 When to Use Which Model

**Use a larger model (Sonnet/Opus) when:**
- Task involves ISR handlers, DMA configuration, or threading synchronization (Critical risk tier — pass@1 often below 40% even for Sonnet)
- Code has shared state between ISR and thread (volatile, spinlock, atomic)
- Linux kernel module with error path cleanup (goto unwinding)
- Memory optimization using Zephyr-specific APIs (mem_slab, mem_domain)
- Any task in the **Critical** or **High** risk tiers above, or mixed Sonnet/Haiku results (e.g. adc, uart)

**Haiku is acceptable when:**
- Categories in the **Low** or lighter **Moderate** band (e.g. device-tree, pwm, boot scaffolding) with templates and clear interfaces
- Kconfig generation from clear requirements (watch transitive `CONFIG_*` deps)
- Boilerplate where the template provides most of the logic and you will still compile on hardware

Avoid relying on Haiku alone for **DMA**, **ISR/concurrency**, and **threading** (Haiku pass@1 down to **8%** on DMA in this aggregate).

### 5.4 What No Model Gets Right

Even the best models fail on these patterns — always verify manually.

**EmbedEval category pass@1 (n=3, 233 cases)** — systemic weak spots that mirror the pattern failures below:

| Category | Sonnet | Haiku |
|----------|--------|-------|
| dma | 31% | 8% |
| isr-concurrency | 23% | 38% |
| threading | 33% | 33% |

| Pattern | Sonnet Fail Rate | Why LLMs Struggle |
|---------|-----------------|-------------------|
| Memory barriers (ISR↔thread) | ~80% miss | Requires CPU architecture + compiler model reasoning |
| DMA cache coherence | ~60% miss | Requires understanding CPU cache vs DMA engine interaction |
| Strict aliasing / type punning | ~90% miss | LLM training data is full of `*(struct*)buf` patterns |
| Error path cleanup (goto unwinding) | ~50% miss | Requires tracking all allocated resources across branches |
| `volatile` on shared flags | ~40% miss | Implicit knowledge: compiler optimization is invisible |
| ISR-safe signaling (k_sem_give, not mutex) | ~40% miss | Requires knowing which APIs are ISR-safe |
| Endianness conversion at boundaries | ~80% miss | Requires knowing sensor register byte order vs MCU |
| NaN guard on safety comparisons | ~95% miss | Almost never in training data — NaN comparison is invisible |
| Counter overflow handling (49.7 day) | ~95% miss | Requires thinking about multi-week continuous operation |
| Secure OTA (signature, anti-rollback) | ~90% miss | Generates functional OTA, not secure OTA |

These are the patterns where the **implicit/explicit gap** (Section 6.3.5)
is largest. Even with the best model, include these requirements explicitly
in your prompt or context template. See [LLM-EMBEDDED-CONSIDERATIONS.md](LLM-EMBEDDED-CONSIDERATIONS.md)
Section 2 for detailed analysis with real-world incidents.

---

## 6. Prompt Engineering for Embedded — How to Ask

How you structure the prompt matters as much as what context you include.
This section catalogs techniques that measurably improve LLM output quality
for embedded code generation.

### 6.1 Structural Techniques — How to Organize the Prompt

#### 6.1.1 Constraint-First Ordering

State constraints and restrictions BEFORE the task description. LLMs weight
earlier tokens more heavily during generation.

```
❌ Bad:  "Write a DMA driver. Oh, and don't use malloc."
✅ Good: "Constraints: No malloc. DMA buffers must be __aligned(32).
         Cache flush before TX, invalidate after RX.
         Task: Write a DMA driver for SPI1 RX on DMA2 Stream 0."
```

**Why it works:** When constraints come last, the LLM has already planned
its approach. Constraints first shape the generation from the start.

#### 6.1.2 Negative Constraints (Deny List)

Explicitly state what NOT to do. LLMs are better at avoiding named patterns
than inferring what's forbidden.

```
## Do NOT:
- Use FreeRTOS or Arduino APIs
- Call k_malloc, printk, or k_sleep inside ISR bodies
- Use magic numbers — define every constant with #define
- Use printf or stdio.h — use printk only
- Generate placeholder/TODO comments — implement fully
```

**Why it works:** The 35%p explicit/implicit gap. Naming the forbidden pattern
makes the LLM avoid it; leaving it implicit means ~40% chance it appears.

#### 6.1.3 Output Format Specification

Tell the LLM exactly what files and structure to produce.

```
## Expected Output
1. src/dma_driver.h — public API (init, start, stop, get_buffer)
2. src/dma_driver.c — implementation
3. prj.conf additions — required CONFIG_* options
4. Kconfig fragment — if new config options needed
5. boards/nrf52840dk.overlay — DT overlay if needed

Each function must have:
- Doxygen-style brief comment (1 line)
- Return value: 0 on success, negative errno on error
- Error handling on every API call
```

#### 6.1.4 Structured Prompt Sections

Use clear section headers. The LLM treats markdown headers as semantic
boundaries.

```
## Constraints      ← what NOT to do (read first)
## Hardware Context ← board-specific facts
## Task             ← what to implement
## Interface        ← existing types/headers to use
## Error Handling   ← explicit error policy
## Expected Output  ← file list and format
```

**Why it works:** LLMs parse markdown headers as semantic boundaries —
context under `## Constraints` is weighted differently than context under
`## Task`. Structured sections also prevent the LLM from treating hardware
constraints as part of the task description, which causes constraint violations.

### 6.2 Knowledge Injection Techniques — How to Feed Context

#### 6.2.1 Reference Implementation Pattern

Provide a working example of a SIMILAR (not identical) module. LLMs excel at
pattern adaptation.

```
## Reference: Here is our existing UART driver (src/uart_driver.c).
   Note the error handling pattern, the init/deinit lifecycle,
   and the device_is_ready check. Follow this same pattern for SPI.

[paste uart_driver.c]

## Task: Implement SPI driver following the same patterns.
```

**Why it works:** The reference provides implicit knowledge (coding style,
error handling patterns, project conventions) without having to spell each
one out. IoT-SkillsBench (2026) found that "human-expert skills" (structured
examples) achieve near-perfect success rates.

#### 6.2.2 Register Map Injection

For low-level drivers, paste the relevant register subset (not entire
datasheet).

```
## LIS2DH12 Registers (relevant subset)
| Addr | Name | R/W | Reset | Description |
|------|------|-----|-------|-------------|
| 0x0F | WHO_AM_I | R | 0x33 | Device identification |
| 0x20 | CTRL_REG1 | RW | 0x07 | ODR[7:4]=0101 for 100Hz, LPen[3], Zen[2]Yen[1]Xen[0] |
| 0x28 | OUT_X_L | R | - | X-axis LSB (auto-increment: read 6 bytes for XYZ) |

## Timing
- Power-on to data ready: 10ms + 1/ODR
- I2C address: 0x19 (SDO/SA0 = HIGH)
```

#### 6.2.3 Existing Header Injection

Paste the header files that define types and interfaces this module must use.

```
## Existing interfaces (do not modify, implement against these):

```c
// From include/app/sensor_types.h
struct accel_sample {
    int16_t x, y, z;
    uint32_t timestamp_ms;
};

struct accel_batch {
    struct accel_sample samples[10];
    uint8_t count;
};

// From include/app/sensor_driver.h
int sensor_driver_init(void);
int sensor_driver_read_batch(struct accel_batch *batch);
void sensor_driver_deinit(void);
```

#### 6.2.4 Error Context from Previous Attempt

When iterating, feed the specific error — not just "it didn't work."

```
## Previous attempt failed. Here is the code and the error:

[paste generated code]

## Error:
Compilation error: undefined reference to `gpio_pin_set`
The correct Zephyr API is `gpio_pin_set_dt` which takes a gpio_dt_spec.
Fix this and check for any other deprecated API usage.
```

**Why it works:** Specific error feedback is dramatically more effective than
"try again." Abtahi (2025) showed 92.4% vulnerability remediation with
targeted feedback loops.

### 6.3 Reasoning Techniques — How to Make the LLM Think Harder

#### 6.3.1 Chain-of-Thought for Hardware Reasoning

Ask the LLM to reason through hardware constraints before writing code.

```
Before writing code, reason through:
1. What is the DMA transfer direction? (peripheral→memory or memory→peripheral?)
2. Does this MCU have data cache? If yes, what cache ops are needed?
3. What alignment does the DMA controller require?
4. What happens if the DMA transfer is interrupted mid-way?
5. Now write the code.
```

**Why it works:** This is a form of **Structured Chain-of-Thought (SCoT)**
which uses pseudocode/algorithm steps instead of natural language reasoning.
SCoT improves pass@1 by **+13-14%** vs standard CoT's +2-7% (arXiv:2305.06599).
Note: standard CoT's value is decreasing with newer models that do internal
reasoning by default (arXiv:2506.07142).

#### 6.3.2 Failure Mode Enumeration

Ask the LLM to enumerate failure modes before implementing error handling.

```
Before implementing, list every way this function can fail:
1. What if i2c_transfer returns an error?
2. What if the sensor WHO_AM_I doesn't match?
3. What if the sensor is powered off?
4. What if the I2C bus is stuck (SDA held low)?
5. What if this function is called before i2c_init?

Now implement with error handling for each case.
```

**Why it works:** Directly addresses the #1 LLM failure (happy-path bias).
Enumerating failures before coding forces error paths into the generation plan.

#### 6.3.3 Adversarial Self-Review

Ask the LLM to review its own output for embedded-specific issues.

```
Now review the code you just generated for:
1. Any variables shared between ISR and thread missing volatile?
2. Any blocking calls inside ISR bodies?
3. Any API return values not checked?
4. Any resources allocated but not freed on error paths?
5. Any magic numbers that should be named constants?
List every issue found, then output the corrected code.
```

#### 6.3.4 Two-Pass Generation

First pass: architecture/pseudocode. Second pass: implementation.

```
Pass 1: Write pseudocode for this DMA driver showing:
- Init sequence (what order, what depends on what)
- Runtime flow (how data moves, who triggers what)
- Error handling (what can fail, what cleanup is needed)
- Shutdown sequence (reverse of init)

[LLM outputs pseudocode]

Pass 2: Now implement in C following exactly this pseudocode.
Use Zephyr APIs. Include all error handling from the pseudocode.
```

**Why it works:** Separates "thinking" from "coding." The pseudocode pass
catches architectural issues before they're baked into implementation details.

#### 6.3.5 Specification-First Generation

Provide the acceptance criteria BEFORE asking for code. The LLM then generates
code that targets specific test criteria rather than "whatever seems right."

```
## Acceptance Criteria (code must satisfy ALL):
1. sensor_fetch() return value checked — on < 0, log and skip
2. Sampling loop with k_sleep(K_MSEC(10)) — must be periodic, not one-shot
3. device_is_ready() called before first sensor access
4. No malloc, no printf, no FreeRTOS APIs
5. Stack usage must fit within 1024 bytes (no large local arrays)
6. Message queue push uses K_MSEC(1) timeout, not K_FOREVER

## Task: Implement sensor_task() that satisfies all criteria above.
```

**Why it works:** Criteria-first primes the LLM with specific constraints that
it would otherwise miss. This is the most direct way to close the implicit→
explicit gap. Especially effective for safety and timing requirements.


#### 6.3.6 Context Budgeting & Placement

LLMs attend most strongly to the **beginning and end** of the context window,
and poorly to the middle ("Lost-in-the-Middle" effect — confirmed on 18
frontier models by Chroma 2025). Even with perfect retrieval, adding more
context **degrades** performance (arXiv:2510.05381).

**Rules:**
- **Constraints at the START** — ISR restrictions, forbidden APIs, error handling policy
- **Task description in the MIDDLE** — what to implement
- **Expected output format at the END** — file list, function signatures
- **Budget: 2,000-8,000 tokens** of context per task. Beyond 8K, split into two prompts.
- If context exceeds budget: **remove** verbose examples, history, and redundant docs. Keep constraints and interfaces.

```
[START — high attention]
## Constraints (ISR rules, forbidden APIs, error handling)
## Hardware Context (pin assignments, DMA channels)

[MIDDLE — lower attention]
## Task Description
## Interface (existing headers, types)

[END — high attention]
## Expected Output (file list, format)
## Test Criteria (what "correct" means)
```

### 6.4 Iteration Techniques — How to Refine Output

#### 6.4.1 Compile-Fix Loop

```
Generate → Cross-compile → Feed errors back → Fix → Repeat (max 3 rounds)
```

Most compilation errors (60%) are from missing context/dependencies (Abtahi
2025). Feeding the exact error message usually fixes it in one round. After
3 rounds without resolution, the root cause is almost always missing context
(wrong SDK version, undeclared type, missing header) — not something more
iterations will solve. Stop iterating and update the context package instead.

> **WARNING: Security degrades with iteration.** arXiv:2506.11022 found a
> **37.6% increase in critical vulnerabilities** after 5 iterations of
> LLM self-repair. Each "fix" can introduce new security issues while
> resolving the original error. Re-run static analysis after EVERY iteration,
> not just the final one.

#### 6.4.2 Checklist-Driven Review

After generation, ask the LLM to audit against a specific checklist:

```
Check this code against the following embedded safety checklist:
[ ] Every API return value is checked
[ ] Error paths free all allocated resources in reverse order
[ ] Shared variables are volatile or atomic_t
[ ] No blocking calls in ISR bodies
[ ] DMA buffers are cache-line aligned
[ ] Timer periods have safety margin below WDT timeout
[ ] No magic numbers — all constants are #defined
Mark each as PASS or FAIL with line numbers.
```

#### 6.4.3 Differential Review

When modifying existing code, provide the full file and ask for minimal diff:

```
Here is the current src/sensor_driver.c. I need to:
1. Add error retry logic (3 retries with 10ms delay)
2. Add device_is_ready check in init

Show ONLY the changes needed. Do not rewrite unchanged code.
Use the existing error handling patterns in the file.
```

#### 6.4.4 Minimum Viable Context Discovery

Start with minimal context. Generate. Check result. Add context ONLY where
the LLM failed. This finds the **minimum context** needed per task type.

```
Round 1: [SDK Profile + Task description only]
  → LLM output: uses wrong DMA mode
  → Learning: DMA mode requires explicit context

Round 2: [+ DMA channel map + cyclic mode requirement]
  → LLM output: missing cache flush
  → Learning: cache management requires explicit context

Round 3: [+ cache alignment and flush/invalidate rules]
  → LLM output: correct
  → Conclusion: this task needs SDK + DMA map + cache rules (3 context docs)
```

**Why it works:** Avoids over-stuffing context (which causes attention
dilution — Chroma 2025) and reveals exactly which knowledge the LLM lacks
per task type. Over time, you build a minimal context recipe for each module
type. This is more efficient than always including the maximum context.

### 6.5 Techniques to Explore (Future Work)

The following techniques have theoretical or preliminary evidence but need
systematic measurement against EmbedEval-style benchmarks.

| Technique | Hypothesis | Status |
|-----------|-----------|--------|
| **Few-shot with failure examples** | Show LLM a buggy ISR + the fix → better ISR generation | Untested |
| ~~**Persona prompting**~~ | ~~"You are a senior embedded engineer"~~ | **DISPROVEN** — EMNLP 2025 found expert personas are harmful for code (-3 to -5% accuracy). Use specific constraints instead. Moved to Anti-Patterns. |
| **Datasheet-to-code pipeline** | OCR datasheet → extract tables → structured context → generate | Tooling exists (marker, nougat) but integration untested |
| **Test-driven generation** | Provide test cases first, ask LLM to write code that passes | Works for general SW (TDD), untested for embedded-specific checks |
| **Retrieval-augmented generation** | MCP server retrieves relevant SDK docs per task | **HIGH VALUE**: RAG doubles pass rate for unfamiliar APIs (0.21→0.43, arXiv:2503.15231). context7 + ESP-IDF MCP Server exist. |
| **Multi-model consensus** | Generate with 3 models, take majority approach | Expensive, but Homogenization Trap (arXiv 2507.06920) suggests LLM errors cluster — may not help |
| **Formal spec → code** | TLA+ or Z spec → LLM generates implementation | Would catch state machine bugs, very high effort |
| **MISRA-guided generation** | Feed top-20 MISRA rules in prompt → measure violation reduction | Umer 2025 showed 83% reduction with instructions, but only 20 rules tested |
| **Implicit-to-explicit converter** | Tool that reads a prompt and adds safety requirements that domain experts would infer | Highest potential impact — see concept below |

#### Concept: Implicit-to-Explicit Converter

The 35%p explicit/implicit gap is the single largest source of LLM failure in
embedded code. An **implicit-to-explicit converter** would be a tool (rule
engine, MCP server, or pre-processing hook) that:

1. **Reads** a code generation prompt
2. **Detects** embedded patterns (ISR, DMA, shared variable, timer, init sequence)
3. **Injects** safety requirements that a domain expert would infer:
   - Sees "ISR" → adds "no blocking calls, use volatile on shared vars"
   - Sees "DMA" → adds "cache-line alignment, flush/invalidate"
   - Sees "init" → adds "cleanup in reverse order on failure"
   - Sees "timer" + "watchdog" → adds "timer period < WDT timeout"
   - Sees "shared variable" → adds "volatile or atomic_t"

This is essentially **automated context template selection + injection**. The
simpler version (manual template selection from Section 3.2) already works —
this would automate it.

**Implementation options:**
- Rule-based: keyword detection → template injection (simple, brittle)
- LLM-based: "meta-prompt" that rewrites the user's prompt with safety additions (flexible, recursive)
- Hybrid: rules detect patterns, LLM generates the specific safety clauses

---

## 7. Anti-Patterns — Common Mistakes

| Anti-Pattern | Impact | Why It Fails | Do This Instead |
|-------------|--------|-------------|-----------------|
| "Write a complete firmware" | Fatal | Complexity cliff: <20% success on system-level tasks | Decompose into single-module tasks. Human designs architecture. |
| Trusting ISR code without review | Fatal | #1 concurrency failure. LLMs put blocking calls in ISRs. | Always run ISR body scanner. Always manually verify. |
| "It compiles, ship it" | Fatal | L1 pass 100%, L3 safety pass 88% (Sonnet) / 70% (Haiku). Compile proves nothing. | Compilation is necessary but not sufficient. Run all 6 test levels. |
| No error handling instructions | High | LLMs generate happy-path code 100% of the time | ALWAYS include: "Check return value. On error: cleanup + return." |
| Trusting LLM stack size estimates | High | LLMs underestimate by 30-50% (miss deep call chains, RTOS overhead) | Add 256-512 bytes to LLM's estimate. Verify with CONFIG_THREAD_ANALYZER. |
| Accepting LLM interrupt priorities | High | LLMs assign identical or wrong NVIC priorities; may break RTOS scheduler | Human decides priority scheme in Architecture doc. LLM follows it. |
| Letting LLM write the test plan | High | LLM creates tests that pass its own code, not tests that catch its bugs | Human writes acceptance criteria. LLM can generate test boilerplate. |
| Using LLM without SDK version | High | LLM mixes APIs from different SDK versions | Pin exact version: "Zephyr 3.6" not "Zephyr" |
| No forbidden API list | High | LLM mixes FreeRTOS into Zephyr code, Arduino into ESP-IDF | Always include platform-specific forbidden API list. |
| "Make it safe" | High | Too vague. LLM doesn't know what "safe" means in your context. | Specify: "volatile on shared vars, no malloc in ISR, bounded loops" |
| Feeding raw datasheet PDF | Med | LLMs can't read PDFs (or extract poorly). Too much irrelevant data. | Create curated Board Profile markdown from datasheet. |
| One giant prompt for entire project | Med | Context overflow + complexity cliff | One module per prompt. Feed focused context. |
| Skipping Kconfig | Med | LLM writes code but forgets prj.conf entries | Include required Kconfig in every prompt. Verify with checker. |
| Incomplete Kconfig deps | Med | LLM produces CONFIG_* that miss transitive dependencies | Verify dependency chains: `west build` will catch most, but test on target. |
| Testing only on QEMU | Med | DMA, cache, timing, power bugs are invisible in emulation | Test on real hardware for every peripheral-touching module. |
| Not providing existing code | Med | LLM reinvents patterns instead of following project conventions | Always paste relevant existing modules as reference implementations. |
| Re-iterating without changing context | Med | Same prompt × 5 rounds = same mistake. LLM won't self-correct systematic weakness. | After 3 rounds, stop. Update context package with missing information. |
| Relying on LLM for cross-platform migration | Med | 29.4% pass@1 for ESP-IDF migration (EmbedAgent). Almost guaranteed to fail. | Human maps APIs manually, LLM assists per-function only. |
| "You are an expert embedded engineer" | Med | Persona prompting HURTS code accuracy by -3 to -5% (EMNLP 2025). Activates instruction-following at expense of factual recall. | Use specific constraints, SDK versions, and hardware details. Never generic role prompts. |
| Casting pointers to parse buffers | High | `*(struct*)buf` violates strict aliasing — works at -O0, breaks at -O2. Cortex-M0 hard-faults on unaligned access. | Use `memcpy()` for type punning. Compiler optimizes it to register move. |
| Ignoring byte order at boundaries | High | Sensor registers (big-endian) read directly into little-endian MCU = garbage data. | Explicit `ntohs()`/`ntohl()` or manual MSB-first conversion at every protocol boundary. |
| No NaN guard on safety comparisons | High | `if (speed > MAX)` silently passes when speed is NaN (div by zero). Safety limit bypassed. | Add `isnan()`/`isinf()` check before every safety-critical float comparison. Or use fixed-point. |
| malloc/free in runtime loops | High | Heap fragmentation over weeks. Total free RAM unchanged but largest block shrinks until allocation fails. | Fixed-size pools (`k_mem_slab`), or heap-at-startup-only pattern. No runtime malloc. |
| OTA without signature verification | High | Unsigned firmware accepted = arbitrary code execution. No chain of trust. | Sign with ECDSA, verify on device, implement anti-rollback, use A/B partitioning. |
| Testing only in debug builds | Med | printf hides race conditions. Optimizer at -O2 removes "unnecessary" volatile reads. Different stack layout. | Always test on optimized builds. Use runtime log levels, not `#ifdef DEBUG`. |
| 32-bit ms counter without wrap handling | Med | System hangs at exactly 49.7 days of uptime. | Use 64-bit counters, or unsigned wrap-safe arithmetic. Test at the 49.7-day boundary. |
| Not updating knowledge base | Low | Board profile gets stale, new errata missed | Update after every field issue. Schedule quarterly review. |
| "The LLM said it's correct" | Low | 68.0% pass rate (Sonnet, n=3 on 233 cases) ≈ 1 in 3 may still miss benchmark checks. Haiku 56.9% ≈ more than 2 in 5. | Review EVERY module. Trust but verify. |

---

## 8. Maturity Model — Growing Your LLM Practice

### Level 1: Manual (Starting Out)

- Copy-paste context into LLM prompts manually
- Review all output manually
- No automated checks
- **Suitable for:** Individual developer, first embedded LLM project

### Level 2: Templated (Established)

- Knowledge base exists in repo (Board Profile, SDK Profile, etc.)
- Context templates for common module types
- CLAUDE.md with coding rules and forbidden APIs
- Pre-commit hooks for basic checks (compile, lint)
- **Suitable for:** Small team, recurring embedded projects

### Level 3: Automated (Mature)

- CI pipeline: compile + MISRA + custom linters + QEMU tests
- Automated context assembly (script reads Board Profile + requirement, generates prompt)
- EmbedEval-style behavioral checks per module
- Automated requirements traceability (req → code → test mapping)
- **Suitable for:** Product team, shipping firmware to customers

### Level 4: Integrated (Advanced)

- MCP server auto-injects board context based on file being edited
- LLM-in-the-loop testing: feed test failures back to LLM for fix suggestions
- Continuous benchmark: run EmbedEval-style checks on every PR
- Knowledge base auto-updated from field issues
- **Suitable for:** Platform team, multiple products on same MCU family

---

## 9. Project Safety Checklist — Copy and Fill Per Project

This is a **complete checklist template** designed for LLM-assisted embedded projects.
Copy this section into your project repository (e.g., `docs/SAFETY_CHECKLIST.md`),
fill in the project-specific values, and use it throughout development.

**How the LLM uses this checklist:**
1. **At project start:** LLM reads the checklist and requests missing documents
2. **During code generation:** LLM verifies its output against filled-in constraints
3. **During review:** LLM runs self-check against all applicable checklist items
4. **At milestone:** Human and LLM jointly verify all boxes are checked

### 9.1 How This Checklist Works

```
┌──────────────────────────────────────────────────────────────────────┐
│  PROJECT START                                                       │
│                                                                      │
│  1. Copy this checklist template to your project                     │
│  2. Fill Part A (Project Context) — architect provides documents     │
│  3. For each module, fill Part B (Per-Module Checklist)              │
│  4. Feed filled checklist to LLM in CLAUDE.md or as context         │
│                                                                      │
│  LLM READS CHECKLIST AND:                                            │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  "I see Board Profile is missing. Please provide:             │  │
│  │   - MCU part number and memory map                            │  │
│  │   - Pin assignments for peripherals this module uses          │  │
│  │   - DMA channel-to-peripheral mapping                        │  │
│  │   - Known silicon errata for this revision"                   │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  DURING DEVELOPMENT                                                  │
│                                                                      │
│  5. Before generating code: LLM checks Part B constraints            │
│  6. After generating code: LLM self-checks against Part B items      │
│  7. Human reviews LLM self-check results                             │
│                                                                      │
│  AT REVIEW / MILESTONE                                               │
│                                                                      │
│  8. Fill Part C (Traceability) — link requirements to test results   │
│  9. Verify all checkboxes in Parts A-C are completed                 │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Requirements ↔ Test Case Linkage:**

Each requirement (REQ-xxx) maps to specific checklist items in Part B,
which map to specific test levels in Part C. This creates bidirectional
traceability required by IEC 61508, DO-178C, and ISO 26262:

```
REQ-SENSOR-001 ("Read accelerometer at 100Hz")
    │
    ├──► Part B Checklist Items:
    │    ├── [x] device_is_ready() before first use
    │    ├── [x] sensor_fetch() return value checked
    │    ├── [x] Periodic loop with k_sleep(K_MSEC(10))
    │    └── [x] No malloc in loop (fragmentation risk)
    │
    └──► Part C Test Levels:
         ├── L0: static check — sensor_fetch error handling present
         ├── L2: QEMU — 100 batches produced in log output
         ├── L3: Hardware — I2C timing 10ms ± 0.5ms (logic analyzer)
         └── L4: Stress — 24hr soak, no memory growth
```

---

### 9.2 Project Context Documents

> **Instructions:** Check each box when the document exists and is verified.
> For each unchecked box, the LLM should request the information from the architect.

#### A. Hardware Context

| # | Document | Status | Provided By | LLM Needs This For |
|---|----------|--------|-------------|-------------------|
| A1 | **Board Profile** | [ ] | HW Engineer | MCU selection, memory constraints, power domains, oscillator specs |
| | - MCU part number + revision | [ ] | | Errata lookup, correct peripheral set |
| | - Flash / RAM / CCM sizes | [ ] | | Memory budget, linker script |
| | - FPU: yes/no, single/double | [ ] | | Float code generation, `-mfpu` flags |
| | - Power domains + sleep modes | [ ] | | Power management code |
| | - Oscillator specs (HSE/LSE freq, ppm) | [ ] | | Clock tree, RTC accuracy |
| | - Debug interface (SWD/JTAG pins) | [ ] | | Avoiding pin conflicts |
| | - Known silicon errata | [ ] | | Workaround code generation |
| A2 | **Pin Map** | [ ] | HW Engineer | GPIO init, peripheral config, DT overlays |
| | - Pin ↔ Function ↔ AF assignments | [ ] | | Correct gpio_pin_configure / pinctrl |
| | - Pull-up/down resistor configuration | [ ] | | Input pin configuration |
| | - Peripheral ↔ DMA ↔ IRQ mapping | [ ] | | DMA channel assignment, IRQ priority |
| | - Interrupt priority plan | [ ] | | NVIC priority, RTOS scheduler interaction |
| A3 | **Schematic (relevant sections)** | [ ] | HW Engineer | Level shifters, external pull-ups, voltage domains |
| | - Power supply topology | [ ] | | Brown-out thresholds, battery sag analysis |
| | - Sensor connections (I2C addr, SPI CS) | [ ] | | Driver configuration |
| | - RF section (antenna, matching) | [ ] | | BLE/WiFi power configuration |

#### B. Software Context

| # | Document | Status | Provided By | LLM Needs This For |
|---|----------|--------|-------------|-------------------|
| B1 | **SDK Profile** | [ ] | SW Lead | Correct API usage, forbidden API list |
| | - SDK name + exact version | [ ] | | Version-specific API calls |
| | - Build system commands | [ ] | | CMake, west, idf.py configuration |
| | - ISR-safe vs unsafe API table | [ ] | | ISR body generation |
| | - Forbidden API list (cross-platform) | [ ] | | Preventing API hallucination |
| | - Required Kconfig for each feature | [ ] | | prj.conf generation |
| B2 | **Coding Standard** | [ ] | SW Lead | Code style, safety patterns |
| | - MISRA C subset (if applicable) | [ ] | | Compliance-aware generation |
| | - Error handling policy | [ ] | | goto cleanup vs early return |
| | - Naming conventions | [ ] | | Consistent identifiers |
| | - Logging policy (printk vs LOG_*) | [ ] | | Appropriate log calls |
| | - Dynamic allocation policy | [ ] | | malloc prohibition, pool usage |
| B3 | **Architecture Document** | [ ] | Architect | Task decomposition, IPC, memory budget |
| | - Task list with priorities + stack sizes | [ ] | | Thread creation, stack allocation |
| | - IPC topology (queue/sem/shared mem) | [ ] | | Inter-task communication |
| | - Memory budget per module | [ ] | | Buffer sizing, allocation |
| | - Error/recovery strategy | [ ] | | Fault handling patterns |
| | - Power state machine | [ ] | | Sleep/wake transitions |

#### C. Requirements & Safety

| # | Document | Status | Provided By | LLM Needs This For |
|---|----------|--------|-------------|-------------------|
| C1 | **Functional Requirements** | [ ] | Product Owner | What to implement |
| | - Structured format (REQ-xxx) | [ ] | | Traceability |
| | - Acceptance criteria per requirement | [ ] | | Test case generation |
| | - Timing constraints (numeric) | [ ] | | Deadline/period code |
| | - Resource constraints (stack, RAM) | [ ] | | Memory-aware generation |
| C2 | **Safety Requirements** | [ ] | Safety Engineer | What must NOT go wrong |
| | - Safety integrity level (SIL/ASIL) | [ ] | | MISRA strictness, coverage level |
| | - Fail-safe states per subsystem | [ ] | | Error handler targets |
| | - Plausibility check ranges | [ ] | | Sensor validation code |
| | - Watchdog strategy | [ ] | | WDT configuration |
| C3 | **Security Requirements** | [ ] | Security Engineer | Hardening code |
| | - Secure boot requirement (yes/no) | [ ] | | Boot chain verification |
| | - OTA signing method (RSA/ECDSA) | [ ] | | Update verification code |
| | - Key storage (secure element/flash) | [ ] | | Key access patterns |
| | - Communication encryption (TLS/DTLS) | [ ] | | Network stack config |

#### D. Test Infrastructure

| # | Document | Status | Provided By | LLM Needs This For |
|---|----------|--------|-------------|-------------------|
| D1 | **Test Environment** | [ ] | Test Engineer | Test code generation |
| | - QEMU/native_sim target available | [ ] | | L2 emulation tests |
| | - Hardware test board available | [ ] | | L3/L4 test planning |
| | - CI pipeline (build + test) | [ ] | | Automated verification |
| | - Static analysis tools configured | [ ] | | MISRA/lint integration |
| D2 | **Test Plan Template** | [ ] | Test Engineer | Requirements traceability |
| | - Test levels mapped to requirements | [ ] | | Coverage analysis |
| | - Pass/fail criteria per test | [ ] | | Automated verdict |

**Completeness Gate:**
```
Documents A1-A3, B1-B3, C1 minimum → ready for code generation
Documents C2-C3 → required for safety/security-critical modules
Documents D1-D2 → required before testing phase
```

---

### 9.3 Per-Module Safety Checklist

> **Instructions:** For each module you implement, copy the applicable category
> checklist below. Fill in project-specific values in `{braces}`. Check each
> box during review. Feed to LLM as part of context for self-checking.

#### 9.3.1 Universal Checks (Apply to ALL Modules)

```markdown
## Safety Checklist: {MODULE_NAME}
## Date: {YYYY-MM-DD}
## Reviewer: {name}
## LLM Model: {model + version}

### Code Quality
- [ ] Every API return value is checked (no ignored returns)
- [ ] Error paths clean up ALL resources in reverse allocation order
- [ ] No magic numbers — all constants use #define with descriptive names
- [ ] No dynamic allocation (malloc/free) at runtime — static or pool only
- [ ] No stdio.h / printf — use platform logging (printk / LOG_* / ESP_LOG*)
- [ ] No cross-platform API contamination (only {SDK_NAME} APIs used)

### Concurrency Safety
- [ ] All ISR-thread shared variables are volatile or atomic_t
- [ ] No blocking calls in ISR bodies (no mutex, sleep, malloc, printf)
- [ ] Correct sync primitive: spinlock for ISR↔thread, mutex for thread↔thread
- [ ] Spinlock used in BOTH ISR and thread (not just one side)
- [ ] Memory barriers present where ISR updates data read by thread

### Type Safety
- [ ] No pointer-cast type punning (*(struct*)buf) — use memcpy()
- [ ] Endianness conversion at every protocol boundary (sensor, network)
- [ ] Float comparisons include NaN/Inf guard for safety-critical paths
- [ ] No unaligned memory access (Cortex-M0 will hard-fault)

### Temporal Safety
- [ ] All timers use 64-bit or wrap-safe 32-bit arithmetic
- [ ] Polling loops have explicit iteration bounds or timeouts
- [ ] Sleep/delay durations have named constants, not magic numbers
- [ ] Timer periods < watchdog timeout (with ≥30% margin)

### Build Safety
- [ ] Code compiles at -O2 without warnings (-Wall -Werror)
- [ ] Behavior verified on optimized build (not just debug -O0)
- [ ] No #ifdef DEBUG code paths that change runtime behavior
- [ ] Kconfig: all CONFIG_* used in code are set in prj.conf
```

#### 9.3.2 DMA Module Checklist

```markdown
### DMA-Specific ({PERIPHERAL} on DMA{N} Stream {M})
- [ ] Buffer alignment: __aligned({CACHE_LINE_SIZE}) — typically 32 or 64
- [ ] Cache flush before TX: sys_cache_data_flush_range(buf, size)
- [ ] Cache invalidate after RX: sys_cache_data_invd_range(buf, size)
- [ ] DMA mode correct: CIRCULAR for continuous / NORMAL for one-shot
- [ ] For circular: dma_reload() in DMA callback, or .cyclic=1
- [ ] dma_config() called BEFORE dma_start() (strict ordering)
- [ ] dma_stop() called on error or transfer complete
- [ ] DMA buffer NOT in CCM/DTCM (DMA-inaccessible on some MCUs)
- [ ] Completion flag is volatile (written in DMA callback)
- [ ] Channel priority matches system interrupt priority plan
```

#### 9.3.3 ISR / Concurrency Module Checklist

```markdown
### ISR-Specific ({IRQ_NAME}, priority {PRIORITY})
- [ ] ISR function has correct attribute (e.g., IRAM_ATTR for ESP32)
- [ ] ISR body contains ONLY: k_sem_give / k_msgq_put(K_NO_WAIT) / k_work_submit / atomic_*
- [ ] No printk/printf in ISR body (causes jitter, may block)
- [ ] Shared data struct declared with volatile qualifier
- [ ] k_spin_lock used with key capture: key = k_spin_lock(&lock)
- [ ] Initialization complete BEFORE interrupt is enabled
- [ ] ISR-to-thread data path: verify ordering (data written → flag set → barrier → thread reads)
- [ ] Thread priority matches architecture document: {EXPECTED_PRIORITY}
- [ ] Lock ordering: if multiple locks, always acquire in same order (A→B, never B→A)
```

#### 9.3.4 Sensor / Peripheral Module Checklist

```markdown
### Sensor-Specific ({SENSOR_PART} on {INTERFACE} @ {ADDRESS})
- [ ] device_is_ready() called before first access
- [ ] WHO_AM_I / device ID verified against expected value: {EXPECTED_ID}
- [ ] Register byte order: sensor is {BIG/LITTLE}-endian, MCU is {BIG/LITTLE}-endian
- [ ] Byte-order conversion applied: {YES: how / NO: same endianness}
- [ ] Sampling in periodic loop (not one-shot): k_sleep(K_MSEC({PERIOD_MS}))
- [ ] sensor_fetch() / i2c_read() return value checked on every call
- [ ] Plausibility checks on raw values:
  - [ ] Range: {MIN_PLAUSIBLE} to {MAX_PLAUSIBLE}
  - [ ] Rate-of-change: max {MAX_DELTA} per {SAMPLE_PERIOD}
  - [ ] Stuck-at detection: {STUCK_LIMIT} identical consecutive readings
  - [ ] Freshness timeout: {FRESHNESS_MS} ms
- [ ] Settling time after power-on respected: {SETTLING_MS} ms
```

#### 9.3.5 Power Management Module Checklist

```markdown
### Power-Specific (target: {TARGET_BATTERY_LIFE})
- [ ] GPIO pins reconfigured before sleep (prevent leakage: {EXPECTED_SLEEP_UA} uA)
- [ ] Peripherals powered down before sleep entry
- [ ] Wake source configured: {WAKE_SOURCES}
- [ ] Wake-up latency accounted for: {WAKE_LATENCY_US} us
- [ ] pm_device_action_run() return value checked for BOTH suspend AND resume
- [ ] Battery voltage checked before flash write (brownout risk)
- [ ] Tickless mode enabled (CONFIG_TICKLESS_KERNEL=y) to avoid unnecessary wakes
- [ ] Energy budget calculated:
  - [ ] Active current: {ACTIVE_MA} mA × {ACTIVE_DUTY_PCT}%
  - [ ] Sleep current: {SLEEP_UA} uA × {SLEEP_DUTY_PCT}%
  - [ ] Average: {AVG_UA} uA → battery life: {CALCULATED_DAYS} days
  - [ ] 20% margin applied for retransmissions
```

#### 9.3.6 OTA / Firmware Update Module Checklist

```markdown
### OTA-Specific (transport: {TRANSPORT})
- [ ] Firmware image signed: {ALGORITHM} (key in {KEY_STORAGE})
- [ ] Signature verified on device before flashing
- [ ] Anti-rollback: version counter checked (current: {CURRENT_VER})
- [ ] A/B partitioning: inactive slot used for download
- [ ] Download over TLS — no plaintext firmware transfer
- [ ] Per-chunk error checking during download
- [ ] Abort path: dfu_target_done(false) on any download error
- [ ] Self-test on first boot from new image
- [ ] Auto-revert to previous image if self-test fails
- [ ] Power-loss safe at every step (download, flash, reboot, validate)
- [ ] Flash write: voltage checked, double-buffered, CRC verified
```

#### 9.3.7 Storage / Flash Module Checklist

```markdown
### Storage-Specific (media: {FLASH_TYPE}, filesystem: {FS_TYPE})
- [ ] Flash endurance calculated:
  - [ ] P/E cycles: {ENDURANCE} (SLC/MLC/TLC)
  - [ ] Daily writes: {DAILY_WRITE_MB} MB/day
  - [ ] WAF estimated: {WAF}x
  - [ ] TBW: {TBW_TB} TB → lifetime: {CALCULATED_YEARS} years
- [ ] Write-aware filesystem used (LittleFS/UBIFS, NOT raw FAT)
- [ ] Logging to tmpfs/RAM, flushed to flash periodically (not every event)
- [ ] eMMC health register monitored (DEVICE_LIFE_TIME_EST)
- [ ] Flash write rate limited: max {MAX_WRITES_PER_HOUR} writes/hour
- [ ] Power-fail-safe write: double-buffer or journaling
- [ ] CRC verified after critical writes (boot vector, FS metadata)
```

#### 9.3.8 BLE / Radio Module Checklist

```markdown
### Radio-Specific ({PROTOCOL} on {CHIP})
- [ ] Services registered BEFORE advertising starts
- [ ] bt_enable() / esp_bt_controller_init() return value checked
- [ ] Disconnect handler: stop notifications, restart advertising
- [ ] Connection table garbage collection (stale handles cleaned after {TIMEOUT_S} s)
- [ ] Radio stack health check: periodic "can I still advertise?" test
- [ ] Radio watchdog: full stack re-init after {SILENCE_MINUTES} min no communication
- [ ] Connection parameter negotiation after connection established
- [ ] MTU exchange if payload > 20 bytes
- [ ] Crystal drift within BLE spec: ±{PPM} ppm at operating temp range
```

#### 9.3.9 Watchdog Module Checklist

```markdown
### Watchdog-Specific (timeout: {WDT_TIMEOUT_MS} ms)
- [ ] wdt_install_timeout() BEFORE wdt_setup() (strict ordering)
- [ ] Feed interval: {FEED_INTERVAL_MS} ms (< {WDT_TIMEOUT_MS} ms with ≥30% margin)
- [ ] WDT_FLAG_RESET_SOC on all channels
- [ ] Conditional feed: WDT fed ONLY when ALL monitored tasks report healthy
- [ ] NOT fed from timer ISR (defeats the purpose)
- [ ] Escalation: 1st timeout → soft recovery, 2nd → hard reset, 3rd → factory default
- [ ] Reset reason logged: read MCU reset registers on boot, store to persistent memory
- [ ] Warm boot detection: application detects and handles repeated resets
```

#### 9.3.10 Linux Kernel Module Checklist

```markdown
### Kernel Module-Specific ({MODULE_NAME}.ko)
- [ ] __init: resources allocated in order, ALL cleaned up on ANY failure
- [ ] __exit: resources released in REVERSE order of init
- [ ] goto-based error unwinding (not early return without cleanup)
- [ ] copy_to_user / copy_from_user for ALL user-space data (never raw deref)
- [ ] IS_ERR() checked on every pointer-returning function
- [ ] kfree() for every kmalloc() on error paths
- [ ] dev_err/dev_info used (not printk with manual prefix)
- [ ] MODULE_LICENSE("GPL") present
- [ ] of_match_table has null sentinel entry
```

---

### 9.4 Requirements Traceability Matrix

> **Instructions:** For each requirement, list the checklist items it maps to
> and the test level that verifies it. Fill the Result column during testing.

```markdown
## Requirements Traceability: {PROJECT_NAME}

| REQ-ID | Description | Checklist Items | Test Level | Result |
|--------|-------------|-----------------|------------|--------|
| REQ-{xxx}-001 | {requirement text} | 9.3.1: {items}, 9.3.{N}: {items} | L0: {check}, L3: {test} | [ ] PASS |
| REQ-{xxx}-002 | {requirement text} | 9.3.1: {items}, 9.3.{N}: {items} | L0: {check}, L2: {test} | [ ] PASS |
| ... | ... | ... | ... | ... |
```

**Example (filled):**

| REQ-ID | Description | Checklist Items | Test Level | Result |
|--------|-------------|-----------------|------------|--------|
| REQ-SENSOR-001 | Read accel at 100Hz, batch 10 samples | 9.3.1: return-value-check, no-malloc. 9.3.4: device_is_ready, periodic-loop, plausibility | L0: sensor_fetch error handled. L2: 100 batches in log. L3: I2C 10ms±0.5ms. L4: 24hr soak | [ ] PASS |
| REQ-DMA-001 | SPI DMA transfer to flash | 9.3.1: volatile-shared, no-ISR-blocking. 9.3.2: aligned-buf, cache-flush, config-before-start | L0: alignment check. L1: compiles. L3: DMA transfer on HW. L4: 1hr continuous | [ ] PASS |
| REQ-OTA-001 | Secure firmware update via BLE | 9.3.1: error-paths. 9.3.6: signature-verify, anti-rollback, A/B, power-loss-safe | L0: dfu_target_done on error. L2: simulate update. L3: real OTA on target. L4: power-cut during update | [ ] PASS |
| REQ-SAFETY-001 | Sensor fault detection | 9.3.4: plausibility-range, rate-of-change, stuck-at, freshness | L0: range check exists. L2: inject -40°C → fault reported. L3: disconnect sensor → fault. L4: 24hr fault-free | [ ] PASS |
| REQ-POWER-001 | 1 year battery on CR2032 | 9.3.5: GPIO-leakage, tickless, wake-latency, energy-budget | L3: current measurement. L4: 48hr power profile. Manual: PPK2 measurement | [ ] PASS |

---

### 9.5 LLM Self-Check Protocol

When the LLM generates code, it should run this self-check before presenting
the result. Include this instruction in your CLAUDE.md or prompt:

```markdown
## LLM Self-Check (run after generating code)

Before presenting the generated code, verify against the project
safety checklist (docs/SAFETY_CHECKLIST.md):

1. Read the applicable per-module checklist (Section 9.3.x)
2. For each checklist item, verify the generated code satisfies it
3. Report results as:

### Self-Check Results
| Checklist Item | Status | Evidence |
|---------------|--------|----------|
| Return values checked | PASS | Lines 45, 62, 78 — all API calls checked |
| No malloc at runtime | PASS | Static allocation only |
| Volatile on shared vars | FAIL | Line 23: `int flag` should be `volatile int flag` |
| Endianness conversion | N/A | No protocol boundary in this module |

**Issues Found:** 1
**Action:** Fixed `flag` to `volatile int flag` on line 23.

4. If any item is FAIL: fix before presenting code
5. If any item is UNKNOWN: flag for human review
```

**How to integrate with CLAUDE.md:**

```markdown
# CLAUDE.md — {Project Name}

## Before Generating Code
Read docs/SAFETY_CHECKLIST.md and verify:
1. All Part A documents are available for this module
2. The applicable Part B (per-module) checklist is loaded

## After Generating Code
Run the LLM Self-Check Protocol (Section 9.5 of Development Guide).
Report results in the self-check table format.
Fix all FAIL items before presenting code.

## Safety Checklist Reference
- Universal checks: always apply
- Module-specific: select based on module type
- Traceability: update after testing
```

---

### 9.6 Document Request Template

When starting a new project, the LLM can use this template to request
missing information from the architect/engineer:

```markdown
## Missing Context for {MODULE_NAME}

I need the following information to generate safe embedded code.
Please provide or point me to the relevant documents.

### Required (cannot generate without these):
- [ ] {A1} Board Profile: MCU part number, RAM/Flash sizes, FPU capability
- [ ] {A2} Pin Map: pins used by this module, DMA/IRQ assignments
- [ ] {B1} SDK Profile: exact SDK version, ISR-safe API list, forbidden APIs
- [ ] {C1} Requirements: acceptance criteria for this module

### Recommended (code will be less safe without these):
- [ ] {A1} Silicon errata for this MCU revision
- [ ] {A3} Schematic section showing this peripheral's connections
- [ ] {B3} Architecture: task priorities, IPC mechanism, memory budget
- [ ] {C2} Safety requirements: fail-safe states, plausibility ranges

### Optional (improves code quality):
- [ ] {B2} Coding standard: MISRA rules, naming conventions
- [ ] {D1} Test infrastructure: QEMU target, CI pipeline
- [ ] Reference implementation of a similar module in this project
```

---

## Summary

```
What makes LLM-assisted embedded development work:

1. CURATED KNOWLEDGE   — Board Profile, Pin Map, SDK Profile (not raw datasheets)
2. STRUCTURED REQUIREMENTS — Testable criteria, not prose descriptions
3. FOCUSED CONTEXT     — 2-5 pages per task, not everything at once
4. EXPLICIT SAFETY     — Spell out error handling, volatile, forbidden APIs
5. ONE MODULE AT A TIME — Complexity cliff is real. Decompose.
6. 7-LEVEL TESTING     — Static → Compile → Emulate → Hardware → Stress → Certify
7. HUMAN ARCHITECTURE  — LLM generates functions. Human designs systems.
8. FEEDBACK LOOPS      — Update knowledge base from every failure.
```

The LLM does not replace the embedded engineer.
The LLM replaces the tedious parts of the embedded engineer's day:
boilerplate, API lookup, pattern application, first drafts.

The engineer's irreplaceable value:
architecture, hardware judgment, safety reasoning, integration, debugging.

**Use both. Trust neither alone.**
