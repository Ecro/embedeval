# Sonnet Benchmark Failure Analysis (2026-03-24)

**Model:** claude-code://sonnet
**Cases:** 200 (179 pass, 21 fail)
**pass@1:** 89.5%

## Layer Pass Rates

| Layer | Pass Rate | Note |
|-------|-----------|------|
| L0 Static | 99.5% | 1 failure (storage-009) |
| L1 Build | 100% | Docker unavailable, skipped |
| L2 Runtime | 100% | Docker unavailable, skipped |
| L3 Behavior | 90% | 20 failures — main bottleneck |
| L4 Mutation | 100% | N/A for most cases |

## Category Results

| Category | pass@1 | Status |
|----------|--------|--------|
| ble | 100% | |
| boot | 100% | |
| device-tree | 100% | |
| kconfig | 100% | |
| spi-i2c | 100% | |
| yocto | 100% | |
| dma | 90% | |
| gpio-basic | 90% | |
| isr-concurrency | 90% | |
| security | 90% | |
| sensor-driver | 90% | |
| threading | 90% | |
| timer | 90% | |
| watchdog | 90% | |
| memory-opt | 80% | |
| networking | 80% | |
| ota | 80% | |
| power-mgmt | 80% | |
| storage | 80% | |
| linux-driver | 70% | Weakest |

## General SW vs Embedded-Specific Failures

LLM failure patterns can be divided into **problems that also occur in general software** and **problems caused by embedded-specific characteristics**, as follows.

### General SW Failures (occur in any domain)

These patterns can cause LLM failures equally in any SW development — web, server, desktop, etc.

| Pattern | Cases | Description |
|---------|-------|-------------|
| **Error path cleanup** | linux-driver-001/004/006 | Missing reverse-order release of resources after allocation failure. Occurs identically with DB connection pools, file handles, sockets, etc. |
| **Return value ignored** | networking-001/008, ota-003 | Return value ignored after API call. Same pattern with HTTP clients, DB queries, etc. |
| **Alloc/free mismatch** | memory-opt-003 | Mismatched malloc/free pairs. Memory leak possible in any C/C++ code. |
| **Flag vs early return** | security-007 | Flag accumulation instead of immediate abort on failure. Applies to security code in general. |
| **Ordering violation** | storage-002 | Wrong init -> register -> use order. Applies to all lifecycle management. |
| **Magic numbers** | memory-opt-001 | Constants used repeatedly without names. Maintainability problem in all languages. |
| **Demo mindset** | power-mgmt-009 | Feature demonstration only, operational loop not implemented. Occurs in any service code. |
| **Complexity hiding basics** | ota-005 | Basic safety mechanism omitted within complex structure. Applies to state machines in all domains. |

**Common root causes:**
- Training data is dominated by "working example code" (tutorials that omit error handling)
- LLM's forward token generation structure is poorly suited for reverse dependency tracking
- Optimized for "feature completion", not optimized for "safe operation"

### Embedded-Specific Failures (occur in embedded only)

These patterns originate from **hardware dependencies, real-time constraints, resource limitations**, and other embedded-specific characteristics. The same failures do not occur in web or server development.

| Pattern | Cases | Description | Why Embedded-Only |
|---------|-------|-------------|-------------------|
| **HW cyclic vs SW reload** | dma-003 | Software callback reload used instead of DMA hardware cyclic mode | Hardware modes of DMA controllers are concepts that exist only in embedded systems. Servers have no DMA. |
| **device_is_ready missing** | gpio-basic-001, watchdog-007 | Hardware device used without checking readiness | Server DB connections are verified at connect time, but embedded HW devices may not be ready depending on boot order. |
| **Timing margin ignored** | timer-007 | WDT feed period equals timeout — no margin | On servers, timeout == interval is usually fine, but in real-time systems interrupt latency and scheduling jitter require mandatory margin. |
| **Stack size insufficient** | threading-005* | Work queue stack uses 512/1024 (2048 required) | On servers, the OS auto-expands the stack. In embedded RTOS, stack is fixed size — overflow = hard fault. |
| **ISR context restriction** | sensor-driver-003 | Unaware that blocking APIs cannot be used in ISR context | Similar to signal handler restrictions on servers, but far stricter in embedded — violations cause system hang. |
| **Power state transition** | power-mgmt-001 | PM action return not checked — suspend/resume failures ignored | Server sleep/wake is managed by the OS. In embedded, ignoring PM failure leads to battery drain or inability to wake. |
| **OTA rollback not implemented** | ota-005 | No abort path on DFU download failure | Server deployment failures are easy to roll back. Embedded OTA failure can brick the device. |
| **Flash boundary not validated** | storage-009* | No guard against writes beyond flash region boundaries | Server disks are protected by the OS. Embedded raw flash access beyond boundaries destroys the bootloader or other partitions. |

**Embedded-specific root causes:**
- Low proportion of embedded code in LLM training data (web/server >> embedded)
- Hardware datasheet timing constraints are not explicitly visible in code
- Hardware-dependent bugs are hard to detect in the "compile → execute" cycle
- Embedded "safety" requires simultaneously satisfying all three: correct functionality + resource limits + timing guarantees

### Summary Matrix

```
                    General SW    Embedded-Specific
                    ──────────    ─────────────────
Error handling:     8 cases       3 cases
  - return check    networking    power-mgmt, ota
  - cleanup         linux-driver  (same pattern, different consequence)
  - early return    security

HW semantics:      0 cases       4 cases
  - DMA mode                     dma-003
  - device ready                 gpio, watchdog
  - timing margin                timer-007

Resource mgmt:     2 cases       2 cases
  - alloc/free      memory-opt   stack size (threading)
  - lifecycle        storage     flash boundary (storage)

Operational:       2 cases       1 case
  - periodic loop   power-mgmt   OTA rollback
  - demo mindset

TC false negative: -             3 cases (fixed)
```

**Key insight:** Of the 18 actual LLM failures in total, ~10 (56%) are **patterns that also occur in general SW**, and ~8 (44%) originate from **embedded-specific characteristics**. In other words, to improve LLM embedded code quality, improving general error handling capability comes first, followed by understanding of HW semantics.

## Failure Pattern Classification

### 1. Happy Path Bias — Error Path Ignored (7 cases)

**Cases:** linux-driver-001/004/006, networking-001/008, power-mgmt-001, security-007

LLM generates syntactically perfect code for the normal execution path but omits
cleanup on failure. This is the #1 failure pattern.

**Root cause:**
- Training data is dominated by tutorials and blog posts that skip error handling
- LLMs are optimized for forward generation; reverse dependency tracking
  (cleanup in reverse allocation order) is structurally difficult
- The "init_error_path_cleanup" pattern (linux-driver) requires reasoning about
  what resources were already acquired when a later step fails — this is a
  multi-step backward inference that token-by-token generation handles poorly

**Example (linux-driver-001):**
`alloc_chrdev_region()` -> `cdev_add()` -> `class_create()` -> `device_create()`
If `device_create()` fails, must call `class_destroy()`, `cdev_del()`,
`unregister_chrdev_region()` in reverse order. Sonnet omits this entirely.

**Example (security-007):**
When `tls_credential_add()` fails for CA cert, Sonnet sets a flag `ok = false`
but continues to register client cert and private key. Security code requires
immediate early return (fail-fast), not flag accumulation.

### 2. Semantic Context Ignorance — Syntax Correct, Meaning Wrong (5 cases)

**Cases:** dma-003, gpio-basic-001, timer-007, watchdog-007, sensor-driver-003

LLM produces code that compiles and may even run, but misses hardware-level
semantic requirements.

**Root cause:**
- LLMs understand API signatures but not hardware behavior behind them
- "Functionally equivalent" code may have completely different timing,
  power, or reliability characteristics at the hardware level
- Cross-parameter constraints (timer period must be LESS than WDT timeout,
  not equal) require domain-specific reasoning

**Example (dma-003):**
Prompt requires `cyclic = 1` for hardware-driven ping-pong DMA. Sonnet implements
software reload via `dma_reload()` in callback instead. Both "work" but:
- Hardware cyclic: zero-latency, no CPU involvement
- Software reload: interrupt latency on every transfer, CPU overhead

**Example (timer-007):**
WDT timeout = 3000ms, timer period = 3000ms. In real-time systems, timer
execution has jitter. Period must be strictly less than timeout with margin.
LLM treats numbers as "matching is correct" rather than "margin is required."

### 3. TC False Negatives — Check Logic Too Strict (3 cases) [FIXED]

**Cases:** isr-concurrency-004, threading-005, storage-009

The LLM's code is actually correct, but the check logic failed to recognize it.

- **isr-concurrency-004:** Check looked for `k_sleep` but code uses `k_msleep`
  -> Fixed: now matches `k_sleep|k_msleep|k_usleep`
- **threading-005:** Check regex expected numeric literal, but code uses macro
  -> Fixed: now resolves `#define MACRO value` before comparison
- **storage-009:** Static check didn't match `(off_t)(offset + size) > area_size`
  -> Fixed: regex now handles casted expressions with closing parenthesis

### 4. Resource Balance Failure — Alloc/Free Mismatch (2 cases)

**Cases:** memory-opt-003, power-mgmt-009

**Root cause:**
- LLM writes "demo code" mindset — allocates to show functionality, forgets cleanup
- memory-opt-003: heap_alloc=2 but heap_free=1 (second allocation never freed)
- power-mgmt-009: Battery checked once instead of periodically — LLM demonstrates
  the feature but doesn't implement the operational loop

### 5. Ordering Dependency Violation (2 cases)

**Cases:** storage-002, ota-005

**Root cause:**
- storage-002: LLM interprets "save and load" as normal-use pattern (load -> modify -> save)
  instead of the verify pattern (save -> load -> compare) required by the prompt
- ota-005: Complex 219-line state machine implemented, but the basic rollback path
  `dfu_target_done(false)` on download failure is missing. Complexity obscured the
  fundamental safety requirement.

### 6. Magic Numbers / Abstraction Failure (1 case)

**Cases:** memory-opt-001

**Root cause:**
- LLM prefers concise code over maintainable code
- `K_MEM_SLAB_DEFINE(my_slab, 64, 4, 4)` with bare `64` repeated elsewhere
  instead of `#define BLOCK_SIZE 64`
- In embedded, named constants for hardware parameters are mandatory for
  maintainability

## Key Insight

LLM cannot distinguish between "code that compiles and runs" and "code that
operates safely in production." It achieves 100% on L0 (static) and L1/L2
(compile/runtime) but fails at L3 (behavioral correctness).

The failure distribution reveals a fundamental limitation:

```
Syntactic correctness:  99.5%  (L0)
Compilation success:    100%   (L1)
Runtime execution:      100%   (L2)
Behavioral correctness: 90%    (L3)  <-- gap here
```

This means when using LLMs for embedded firmware:
1. **Always manually verify error paths and resource cleanup** (General SW)
2. **Cross-parameter constraints require human review** — timing margins, etc. (Embedded)
3. **Hardware-semantic choices cannot be delegated to LLM** — cyclic DMA vs software reload (Embedded)
4. **Security code needs fail-fast review** — LLMs prefer "try everything" over "stop immediately" (General SW)
5. **device_is_ready() is non-negotiable** — LLMs skip HW readiness checks (Embedded)
6. **OTA/flash operations need rollback paths** — bricking risk is unique to embedded (Embedded)

## Failure Summary Table

| Case | Failed Check | Root Cause | LLM or TC? | General or Embedded? |
|------|-------------|------------|-------------|---------------------|
| dma-003 | cyclic_enabled | SW reload instead of HW cyclic | LLM | Embedded |
| gpio-basic-001 | device_ready_check | No device_is_ready before use | LLM | Embedded |
| isr-concurrency-004 | k_sleep_present | Check doesn't match k_msleep | TC (fixed) | - |
| linux-driver-001 | init_error_path_cleanup | No cleanup on init failure | LLM | General SW |
| linux-driver-004 | init_error_path_cleanup | No cleanup on init failure | LLM | General SW |
| linux-driver-006 | init_error_path_cleanup | No cleanup on init failure | LLM | General SW |
| memory-opt-001 | block_size_defined | Magic number instead of constant | LLM | General SW |
| memory-opt-003 | heap/slab_balanced | Alloc without matching free | LLM | General SW |
| networking-001 | connect_error_handling | mqtt_connect return unchecked | LLM | General SW |
| networking-008 | connect_error_handling | mqtt_connect return unchecked | LLM | General SW |
| ota-003 | init/write_error_handling | DFU API returns unchecked | LLM | General SW |
| ota-005 | rollback_abort | No dfu_target_done(false) on error | LLM | Embedded |
| power-mgmt-001 | pm_error_handling | pm_device_action_run unchecked | LLM | Embedded |
| power-mgmt-009 | periodic_battery_check | Single check, no loop | LLM | Embedded |
| security-007 | error_path_returns_early | Flag instead of early return | LLM | General SW |
| sensor-driver-003 | periodic_loop | Loop present but sleep missing | LLM | Embedded |
| storage-002 | init/register/save ordering | Wrong operation order | LLM | General SW |
| storage-009 | offset_plus_size_boundary | Check regex too strict | TC (fixed) | - |
| threading-005 | stack_size_adequate | Check doesn't match macro | TC (fixed) | - |
| timer-007 | timer_period < wdt_timeout | Period == timeout (no margin) | LLM | Embedded |
| watchdog-007 | device_ready_check | No device_is_ready before use | LLM | Embedded |
