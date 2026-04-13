# LLM Failure Factors in Embedded Software

Why LLMs systematically fail at embedded firmware compared to general software,
and where the gaps are largest.

**Version:** 1.5 (2026-04-13)
**Factors:** 42 code-observable factors across 6 categories
**Evidence:** EmbedEval benchmark (233 TCs, 97 unique failed checks, 109 failure instances), 15+ research papers (2024-2026)
**Companion documents:**
- [LLM-EMBEDDED-DEVELOPMENT-GUIDE.md](LLM-EMBEDDED-DEVELOPMENT-GUIDE.md) — end-to-end workflow, context templates, environment setup
- [LLM-EMBEDDED-CONSIDERATIONS.md](LLM-EMBEDDED-CONSIDERATIONS.md) — production-scale failure patterns and practical guidance
- [LLM-EMBEDDED-TOKEN-SCALING.md](LLM-EMBEDDED-TOKEN-SCALING.md) — token scaling economics: why infinite tokens aren't enough for embedded

---

## How to Read This Document

Each factor has:

| Field | Meaning |
|-------|---------|
| **Strength** | **High** = core LLM failure, frequent and impactful. **Med** = meaningful but less frequent. **Low** = rare or indirect. |
| **Evidence** | **Empirical** = observed in EmbedEval benchmark data. **Research** = cited in published papers with data. **Theoretical** = strong domain reasoning, no direct measurement yet. |
| **Checks** | EmbedEval check names that test this factor (if any). |

---

## Why Embedded Is Fundamentally Different for LLMs

Before the factor taxonomy, five meta-properties explain why embedded code
generation is harder than general software:

### M1. Training Data Sparsity

Embedded C/C++ is a tiny fraction of LLM training data. The Stack v2 (775B
tokens) is dominated by Python, JavaScript, and Java. Zephyr RTOS, ESP-IDF,
and PSA Crypto APIs are orders of magnitude rarer than React or Django.

**Impact:** LLMs have fewer examples to learn embedded patterns from, leading to
API hallucination, platform confusion, and unfamiliarity with RTOS idioms.

*Source: The Stack v2 (arXiv 2402.19173), GoCodeo analysis*

### M2. Silent Failure

In general software, bugs surface as runtime exceptions, stack traces, or
visible errors. In embedded, bugs often cause **silent data corruption**,
**intermittent timing violations**, or **field failures months later**. A
missing `volatile` compiles and runs in testing but corrupts data under load.
A timer period equal to the WDT timeout works 99% of the time but causes
random resets under jitter.

LLMs cannot distinguish "code that compiles" from "code that operates safely"
because the failure mode is invisible in the code itself.

*Source: EmbedEval benchmark data, IEEE QRS 2024*

### M3. Explicit vs. Implicit Knowledge Gap

When safety requirements are stated in the prompt ("use volatile", "add cache
flush"), LLMs comply ~95% of the time. When requirements must be inferred from
domain knowledge ("ISR shares a variable with main" → volatile needed), pass
rate drops to ~60%. This **35 percentage-point gap** means benchmarks that spell
out requirements overestimate LLM capability.

*Source: EmbedEval benchmark data, 16-case controlled experiment. arXiv:2507.06980
catalogues "incomprehension of implicit requirements" as an internal LLM
factor but does not quantify the gap. The 35%p measurement appears to be
novel in the embedded LLM literature.*

### M4. Complexity Cliff

LLM performance degrades sharply as embedded tasks grow in complexity:

| Task Complexity | Success Rate | Source |
|-----------------|-------------|--------|
| Simple (single peripheral) | 70-85% | MDPI 2026 (27 LLMs) |
| Medium (multi-peripheral) | 40-60% | CHI 2024, EmbedAgent |
| Complex (system integration) | 11-20% | MDPI 2026, CHI 2024 |
| Cross-platform migration (ESP-IDF) | 29.4% | EmbedAgent ICSE 2026 |

This is steeper than the complexity curve for general software.

*Source: MDPI Future Internet 18(2):94, Englhardt CHI 2024, EmbedAgent ICSE 2026*

### M5. Familiarity Bias

LLMs perform well on code patterns they have seen during training but collapse
on equivalent but unfamiliar patterns. The OBFUSEVAL benchmark showed a **62.5%
pass rate drop** when familiar APIs were replaced with equivalent but renamed
alternatives. For embedded, this means performance on common APIs (GPIO, UART)
overstates capability on less common APIs (DMA scatter-gather, MPU regions,
PSA Crypto).

*Source: Unseen Horizons, ICSE 2025 (arXiv 2412.08109)*

### M6. Post-Training Alignment Bias (RLHF/RLAIF)

RLHF and RLAIF optimize LLMs for "clean, helpful, readable" outputs. This
creates a systematic bias toward simple patterns and away from defensive code:

- **Omits `volatile`** — "unnecessary" qualifier makes code look less clean
- **Skips error handling** — error paths are "noise" that obscures the main logic
- **Avoids `goto cleanup`** — `goto` is a "bad practice" in general programming education
- **Prefers simple types** — `int flag` over `volatile atomic_t flag`
- **Generates tutorial-style code** — optimized for readability, not production safety

This bias is compounded by training data dominated by blog posts and tutorials
that prioritize teaching over robustness.

*Source: Nathan Lambert "RLHF Book" (2025), Backslash Security (explicit
security prompts achieve 100% vs 10% naive — proving the model CAN generate
safe code but is biased away from it by default)*

---

## A. Hardware Awareness Gap

LLMs lack the hardware mental model that embedded engineers build from
datasheets, schematics, and oscilloscope debugging. This manifests as incorrect
register usage, wrong initialization sequences, and confusion about peripheral
behavior.

| # | Factor | Str | Evidence | Description |
|---|--------|-----|----------|-------------|
| A1 | Register / MMIO access | Med | Research | Memory-mapped register addresses, bitfields, and read/write attributes. LLMs hallucinate nonexistent registers or use wrong bit positions. Less relevant when using HAL/RTOS APIs that abstract registers away. |
| A2 | Peripheral init ordering | High | Empirical | Hardware peripherals require specific initialization sequences (enable clock → configure → start). Order constraints exist only in datasheets, not in API type signatures. Both Haiku and Sonnet fail on this. |
| A3 | Clock & PLL configuration | Med | Theoretical | Clock tree setup, PLL divider ratios, and bus clock relationships. Errors cause peripherals to run at wrong speeds or not at all. LLMs rarely asked to configure clocks from scratch (usually handled by BSP), but get it wrong when asked. |
| A4 | Pin multiplexing | Med | Theoretical | Same physical pin serves multiple functions (UART TX / SPI MOSI / GPIO). Alternate Function (AF) selection and Device Tree pinctrl bindings require board-specific knowledge. |
| A5 | DMA channel & configuration | High | Empirical | DMA channel-to-peripheral mapping, priority, burst size, circular vs. one-shot mode, and direction. Haiku fails 89% of DMA checks. Sonnet confuses HW cyclic mode with SW reload. |
| A6 | Interrupt vector & priority | High | Empirical | NVIC priority grouping, preemption vs. sub-priority, and vector table offset. LLMs generate code with identical priorities for producer/consumer tasks, defeating the scheduling model. |
| A7 | Device Tree / HW description | Med | Empirical | DT node bindings, overlays, `compatible` strings, and property syntax. LLMs omit required properties (PWM polarity, interrupt GPIO) or generate insufficient node structure. |
| A8 | Communication protocol details | High | Empirical | I2C clock stretching, SPI CPOL/CPHA, UART baud tolerance, burst read buffer sizing. LLMs pick wrong buffer sizes or omit protocol-required commands (SPI write-enable before write). IoT-SkillsBench Level 2 (protocol tasks) shows significant pass rate drop vs Level 1. |

**EmbedEval checks mapped:** `dma_header_included`, `dma_config_called`, `dma_reload_called`, `dma_config_and_start`, `cyclic_flag_set`, `cyclic_enabled`, `multiple_block_descriptors`, `channel_priority_field_used`, `peripheral_to_memory_direction`, `cache_header_included`, `config_before_start`, `i2c_clock_before_init`, `interrupt_gpio_present`, `pwm_polarity_specified`, `sufficient_node_count`, `different_task_priorities`, `six_byte_buffer`, `write_enable_before_write`, `rx_buffer_nonzero`, `will_configured_before_connect`, `bt_enable_before_scan`, `block_count_set`, `dma_start_called_twice`, `two_dma_config_calls`, `priority_differentiation`, `interrupt_receive_used`, `hal_i2c_mem_read_used`

---

## B. Temporal & Real-Time Constraints

Embedded systems operate under timing constraints that have no equivalent in
web or server software. LLMs treat time as an abstract concept rather than a
hard physical constraint.

| # | Factor | Str | Evidence | Description |
|---|--------|-----|----------|-------------|
| B1 | Deadline miss & period calculation | High | Empirical | Hard real-time tasks must complete within a deadline every period. LLMs fail to detect deadline overruns, omit corrective actions, and use magic numbers instead of named constants for periods. |
| B2 | Timing margins & safety guards | Med | Empirical | Timer feed intervals must be strictly less than WDT timeout. Polling intervals need margin for ISR jitter. LLMs set equal values (period == timeout) without safety margin. |
| B3 | Bounded polling & finite timeouts | High | Empirical | Polling loops must have an upper iteration bound or timeout. DNS queries need finite timeouts. LLMs generate `while(1)` busy-waits and `K_FOREVER` timeouts that can hang the system. Both models fail. |
| B4 | Periodic operation patterns | High | Empirical | Sensor sampling, watchdog feeding, and battery monitoring require periodic execution (loop + sleep). LLMs implement single-shot demos instead of continuous operational loops. Both Sonnet (`periodic_loop`, `periodic_battery_check`) and Haiku fail — same severity as B3. |
| B5 | Timer / counter accuracy | Med | Empirical | Prescaler values, autoreload registers, capture/compare setup, and counter lifecycle (start → use → stop). LLMs forget to stop counters after measurement, wasting hardware resources. |

**EmbedEval checks mapped:** `deadline_constant_not_magic`, `deadline_miss_detected`, `deadline_miss_action`, `timer_period_less_than_wdt_timeout`, `poll_loop_bounded`, `timeout_not_infinite`, `periodic_loop`, `periodic_feed_in_loop`, `periodic_battery_check`, `counter_is_volatile`, `counter_stopped_after_use`, `duty_cycle_varies`, `k_sleep_for_drain`, `k_sleep_present`, `main_waits_for_work`, `vtaskdelay_used`, `periodic_read_loop`, `uart_output_1s_interval`

---

## C. Memory & Resource Constraints

Embedded targets have KB-scale RAM, fixed stack sizes, and limited Flash. LLMs
are trained on server/desktop code where memory is abundant and the OS manages
allocation failures gracefully.

| # | Factor | Str | Evidence | Description |
|---|--------|-----|----------|-------------|
| C1 | RAM budget | High | Research | Kilobyte-scale RAM. LLMs naturally generate large buffers, lookup tables, and string literals. A single `char buf[4096]` can exhaust an entire MCU's RAM. |
| C2 | Stack overflow | High | Empirical | Each RTOS task has a fixed stack size. Recursion or deep call chains overflow the stack silently (no OS to extend it). LLMs omit stack overflow protection configuration. |
| C3 | Heap fragmentation | High | Research | Long-running `malloc`/`free` cycles create unusable memory fragments. LLMs use dynamic allocation in loops without considering 10-year continuous operation. |
| C4 | Flash / ROM size | Med | Empirical | Code size constraints. LLMs generate verbose code with `printf` formatting (large), `stdio.h` (pulls in libc), and string-heavy error messages. Nano printf and minimal libc exist for a reason. |
| C5 | Dynamic allocation prohibition | High | Research | Safety standards (MISRA, DO-178C, IEC 62304) ban runtime `malloc`. RTOS alternatives exist (`k_mem_slab`, `k_heap`) but LLMs reach for `malloc` by default. |
| C6 | Memory alignment | Med | Empirical | DMA buffers must be cache-line aligned (32B or 64B). Structures may need packing or alignment attributes. Cortex-M0 faults on unaligned access. LLMs omit alignment. |
| C7 | MPU / memory protection | Med | Theoretical | MPU region setup, access permissions, and partition definitions. Zephyr's `K_APPMEM_PARTITION_DEFINE` and memory domain APIs are specialized and rarely seen in training data. |
| C8 | Linker script & memory layout | Med | Theoretical | Section placement (`.text`, `.bss`, `.data`), Flash/RAM boundaries, bootloader/app partitions. LLMs cannot generate or modify linker scripts reliably. |

**EmbedEval checks mapped:** `stack_overflow_protection_configured`, `cbprintf_nano_enabled`, `dynamic_thread_disabled`, `no_stdio_h`, `alloc_error_check`, `balanced_alloc_free`, `block_size_defined`, `heap_defined`, `heap_alloc_called`, `heap_free_called`, `app_memdomain_header`, `cache_header_included`, `minimal_libc_enabled_value`, `thread_analyzer_header`, `thread_analyzer_config`, `thread_analyzer_print_called`, `main_stack_size_defined`, `minimal_libc_enabled`, `no_large_string_literals`, `mem_slab_defined`, `slab_alloc_called`, `mem_domain_declared`, `mem_domain_init_called`, `partition_added_to_domain`, `thread_added_to_domain`

---

## D. Memory Model & Concurrency

Embedded concurrency involves ISRs, multiple priority levels, shared hardware
registers, and weak memory ordering — a fundamentally different model from
server-side threading with OS-managed mutexes.

| # | Factor | Str | Evidence | Description |
|---|--------|-----|----------|-------------|
| D1 | `volatile` misuse | High | Empirical | Variables shared between ISR and thread context must be `volatile` or `atomic_t`. LLMs declare plain variables — the compiler optimizes away the read, causing stale data. Both models fail on this. |
| D2 | Memory barriers & fences | High | Empirical | Compiler barriers (`__asm volatile("":::"memory")`) prevent reordering; hardware fences (`__DSB`, `__DMB`) enforce ordering across cores/bus. LLMs omit both. Both Haiku and Sonnet fail on `memory_barrier_present`. |
| D3 | Cache coherency | Med | Empirical | DMA transfers bypass the CPU cache. Buffers must be flushed before DMA write and invalidated after DMA read. `volatile` does NOT imply uncached. LLMs conflate volatile with cache management. |
| D4 | Race conditions | High | Empirical | ISR-task and task-task shared state requires synchronization. LLMs declare shared variables but omit the protection mechanism. Failures are intermittent and rarely surface in testing. |
| D5 | ISR context restrictions | High | Empirical | ISRs cannot call blocking/allocating functions: `k_malloc`, `printk`, `k_mutex_lock`, `k_sleep`, `k_sem_take(K_FOREVER)`. LLMs put these in ISR bodies naturally. This is the most-tested factor in EmbedEval (12 checks). |
| D6 | Critical section scope | Med | Empirical | Spinlock regions must be minimal and must not contain blocking calls. LLMs either protect too much (latency) or too little (race), and put sleep calls inside locked regions. |
| D7 | Atomic operations | Med | Theoretical | Read-Modify-Write on shared registers must be atomic. Non-atomic `flag |= BIT(n)` causes register corruption when interrupted between read and write. LLMs use plain assignment on shared flags. |
| D8 | Priority inversion & deadlock | Med | Empirical | Multiple locks must be acquired in consistent order. Priority inheritance must be enabled on mutexes protecting shared resources across priorities. Haiku fails `lock_order_a_before_b` and `unlock_order_b_before_a` on threading-006 — demonstrating lock ordering failures in single-file scope. |

**EmbedEval checks mapped:** `volatile_error_flag`, `volatile_on_initialized_flag`, `counter_is_volatile`, `alarm_value_is_volatile`, `error_flag_is_volatile`, `memory_barrier_present`, `barrier_between_data_and_index_update`, `cache_flush_present`, `cache_invalidate_present`, `shared_variable_declared`, `no_forbidden_apis_in_isr`, `spinlock_used_in_both_contexts`, `fifo_reserved_field`, `k_sleep_in_main`, `msgq_adequate_depth`, `isrs_have_observable_work`, `work_between_lock_and_unlock`, `lock_order_a_before_b`, `unlock_order_b_before_a`, `error_flag_checked_after_wait`, `error_flag_read_after_sync`, `inter_thread_communication`, `shared_memory_struct`, `no_printk_in_isr`, `work_handler_does_processing`

---

## E. Error Handling & Safety Patterns

The **#1 failure mode for capable models** (Sonnet: 12/25 failure instances,
9 unique checks in this category). For weaker models, hardware awareness (A) and concurrency (D)
failures are comparable. Across all model sizes, LLMs generate
happy-path code that works in demos but fails catastrophically in production.
This is not unique to embedded, but the consequences are uniquely severe:
bricked devices, safety hazards, and unrecoverable states.

**Root cause:** Autoregressive token generation is structurally biased toward
forward progress. Reasoning backward ("if step 3 fails, undo steps 1-2 in
reverse order") requires multi-step backward inference that left-to-right
generation handles poorly. Training data is dominated by tutorials and blog
posts that skip error handling.

| # | Factor | Str | Evidence | Description |
|---|--------|-----|----------|-------------|
| E1 | Error path cleanup | High | Empirical | When a multi-step initialization fails at step N, all resources acquired in steps 1..N-1 must be released in reverse order. LLMs omit the error branch entirely or only clean up partially. **Both models fail on this** — the single most reliable discriminator. |
| E2 | Return value checking | High | Empirical | API functions return error codes that must be checked. LLMs call `mqtt_connect()`, `pm_device_action_run()`, `nvs_set_i32()` etc. and proceed without checking the return value. 8+ benchmark checks detect this. |
| E3 | Resource lifecycle balance | High | Empirical | Every `alloc` needs a `free`, every `register` needs an `unregister`, every `init` needs a `deinit`. LLMs write demo code that allocates to show functionality but never cleans up. |
| E4 | Rollback & recovery | High | Empirical | OTA download failure must call `dfu_target_done(false)` to abort and rollback. Image validation failure must invalidate the slot. LLMs implement 200+ lines of happy-path state machine but omit the 1-line rollback call. Both models fail. |
| E5 | Watchdog management | Med | Empirical | WDT channels need distinct timeouts, reset flags on both channels, and periodic feeding in a loop with sleep. LLMs configure one channel correctly but forget the second, or feed once without a loop. |
| E6 | Defensive checks & bounds | Med | Empirical | `device_is_ready()` before peripheral use, `memcmp()` for data verification, bounds checking before pool free, low-stack warning emission. LLMs skip pre-condition checks that prevent silent corruption. |
| E7 | Coding standards (MISRA) | High | Research | 0 out of 5 tested LLMs produce MISRA-compliant code at baseline (23-29 violations/KLOC). With explicit MISRA instructions, violations reduce by 83% but never reach zero. LLMs are structurally incapable of full compliance without external static analysis. |

**EmbedEval checks mapped:** `init_error_path_cleanup`, `init_cleanup_no_comments`, `connect_error_handling`, `pm_error_handling`, `return_values_checked`, `error_handling`, `error_handling_present`, `adc_read_error_checked`, `nvs_set_error_checked`, `esp_timer_create_error_checked`, `alloc_error_check`, `balanced_alloc_free`, `rollback_abort_on_download_error`, `rollback_on_error`, `distinct_channel_timeouts`, `reset_flag_on_both_channels`, `periodic_feed_in_loop`, `device_ready_check`, `ready_check_before_scan`, `memcmp_verification`, `bounds_check_in_free`, `warning_emitted_on_low_stack`, `error_message_printed`, `printk_present`, `error_flag_causes_return`, `callback_sets_flag_on_error_status`, `proc_create_failure_returns_error`, `sensor_error_handling`, `slab_alloc_error_check`, `sysfs_create_group_error_handled`, `slab_free_called`, `found_count_reported`, `success_printed`

---

## F. Toolchain, SDK & Platform Knowledge

LLMs must generate code for specific SDKs (Zephyr, ESP-IDF, STM32 HAL) with
specific build systems, configuration mechanisms, and API conventions. Errors
here cause compilation failures — the most immediately visible failure mode.

| # | Factor | Str | Evidence | Description |
|---|--------|-----|----------|-------------|
| F1 | API hallucination | High | Research | Generating calls to functions that do not exist in the target SDK, or using wrong function signatures. **#1 cause of compilation failure** across all embedded LLM benchmarks. |
| F2 | Cross-platform API confusion | High | Empirical | Using valid APIs from the wrong platform: `gpio_set_level()` (ESP-IDF) in Zephyr code, `xTaskCreate` (FreeRTOS) in Zephyr, `analogRead()` (Arduino) in ESP-IDF. LLMs blend platforms because training data mixes them. ESP-IDF migration drops to 29.4% pass rate. |
| F3 | Build system & Kconfig | High | Empirical | Writing application code but forgetting to enable required CONFIG options in `prj.conf`. Code calls `CONFIG_SPI_DMA` features but `prj.conf` doesn't set `CONFIG_SPI_DMA=y`. Also: generating nonexistent CONFIG options (hallucination). |
| F4 | SDK / HAL version dependency | High | Research | API changes between SDK versions (ESP-IDF v5.1 vs v5.2, Zephyr 3.x vs 4.x, STM32 HAL updates). LLMs generate code for deprecated or not-yet-available APIs. Version pinning in prompts helps but doesn't solve the problem. |
| F5 | Platform header & include knowledge | Med | Empirical | Missing or wrong `#include` directives: `zephyr/kernel.h`, `zephyr/drivers/dma.h`, `thread_analyzer.h`. Haiku fails on basic header inclusion for 3+ categories. Indicates the model has insufficient exposure to the platform's header structure. |
| F6 | Build system integration | Med | Research | ESP-IDF component structure, Zephyr west manifest, Yocto recipe syntax. LLMs generate standalone `.c` files that don't integrate into the actual build system. Yocto `IMAGE_ROOTFS_SIZE` should use `?=` (weak assignment), not `=` (hard override). |

**EmbedEval checks mapped:** `no_hallucinated_config_options`, `spi_dma_enabled`, `net_sockets_sockopt_tls_enabled`, `tls_credentials_enabled`, `zephyr_headers_included`, `kernel_header_included`, `dma_header_included`, `no_stdio_h`, `rootfs_size_uses_weak_assignment`, `pm_action_run_called`, `k_sleep_with_k_msec`, `tick_conversion_macro`, `i2c_master_new_api`, `no_legacy_i2c_driver`, `i2c_master_header`, `of_match_table_sentinel`

---

## Summary Statistics

| Category | Factors | High | Med | Low |
|----------|---------|------|-----|-----|
| A. Hardware Awareness | 8 | 4 | 4 | 0 |
| B. Temporal Constraints | 5 | 3 | 2 | 0 |
| C. Memory & Resource | 8 | 4 | 4 | 0 |
| D. Memory Model & Concurrency | 8 | 4 | 4 | 0 |
| E. Error Handling & Safety | 7 | 5 | 2 | 0 |
| F. Toolchain & Platform | 6 | 4 | 2 | 0 |
| **Total** | **42** | **24** | **18** | **0** |

### Evidence Distribution

| Evidence Level | Count | Meaning |
|---------------|-------|---------|
| Empirical | 29 | Observed in EmbedEval benchmark (233 TCs, 97 unique failed checks, 109 instances, 2 models) |
| Research | 8 | Cited in published papers with quantitative data |
| Theoretical | 5 | Strong domain reasoning, no direct LLM measurement yet |

### Factors That Fail Both Sonnet and Haiku (Hardest)

These 8 checks defeat both models on the same check name — the strongest
cross-model discriminators:

| Factor | Check | Same TC? | Category |
|--------|-------|----------|----------|
| E1 Error path cleanup | `init_error_path_cleanup` | linux-driver-006 | E |
| E2 Return value checking | `connect_error_handling` | networking-008 | E |
| E2 Return value checking | `error_handling` | (different TCs) | E |
| D2 Memory barriers | `memory_barrier_present` | isr-concurrency-008 | D |
| D2 Memory barriers | `barrier_between_data_and_index_update` | isr-concurrency-008 | D |
| E4 Rollback | `rollback_abort_on_download_error` | ota-005 | E |
| B1 Deadline naming | `deadline_constant_not_magic` | threading-008 | B |
| A7 Device Tree | `pwm_polarity_specified` | device-tree-003 | A |

**6 of 8 are in categories D (Concurrency) and E (Error Handling)** — confirming
these as the primary LLM blind spots across model sizes.

> **Note:** Four checks previously listed here (`pm_error_handling`,
> `periodic_loop`, `poll_loop_bounded`, `counter_stopped_after_use`) are
> Sonnet-specific, not cross-model. For `poll_loop_bounded`, Haiku passes
> the TC entirely. For the other three, Haiku fails the same TC but on a
> different check name.

---

# Part II: How to Use LLMs for Embedded Development

The 42 factors above describe WHERE LLMs fail. This part describes WHAT TO DO
about it — what data to feed the LLM, what to verify in its output, and how
the overall development workflow should look.

---

## Context Data Guide — What to Feed the LLM

The #1 finding from EmbedEval is the **Explicit vs. Implicit gap (35%p)**.
LLMs succeed when you tell them what to do; they fail when they must infer
requirements from domain knowledge. The practical implication: **make implicit
knowledge explicit in your prompts.**

### Per-Category Context

#### A. Hardware Awareness — Feed the Datasheet

| Data to Provide | Why | Example |
|----------------|-----|---------|
| Target board & MCU | Prevents cross-platform confusion | "nRF52840-DK, Zephyr 3.6" |
| Peripheral init sequence | LLMs don't know datasheet ordering | "Enable I2C clock before HAL_I2C_Init" |
| DMA channel map | LLMs hallucinate channel assignments | "DMA channel 0 → SPI RX, channel 1 → SPI TX" |
| Device Tree snippet | LLMs need the existing DT context | Paste the relevant `.dts` node |
| Interrupt priority scheme | LLMs assign identical priorities | "ISR priority 1 (highest), worker thread priority 7" |
| Pin assignments | Prevents AF/pinmux errors | "SPI1_SCK = PA5 (AF5), SPI1_MOSI = PA7 (AF5)" |

#### B. Temporal Constraints — State Numbers Explicitly

| Data to Provide | Why | Example |
|----------------|-----|---------|
| WDT timeout value | LLMs set timer == WDT, no margin | "WDT timeout = 3000ms, feed must be < 2000ms" |
| Polling timeout limit | LLMs generate infinite loops | "Max 1000 iterations, then return -ETIMEDOUT" |
| Sampling period | LLMs write single-shot demos | "Read sensor every 100ms in infinite loop" |
| Deadline requirement | LLMs omit deadline detection | "If cycle takes > 10ms, log warning and skip" |

#### C. Memory & Resource — State Budgets

| Data to Provide | Why | Example |
|----------------|-----|---------|
| RAM/Flash budget | LLMs generate 4KB buffers on 32KB MCU | "Total RAM = 64KB, this module may use ≤ 2KB" |
| Stack size policy | LLMs don't know stack is fixed | "Thread stack = 1024 bytes, no recursion" |
| Allocation strategy | LLMs default to malloc | "Use k_mem_slab, no heap allocation" |
| Alignment constraints | LLMs omit __aligned | "DMA buffers must be 32-byte aligned" |
| printf policy | LLMs pull in full libc | "Use printk, not printf. Enable CONFIG_CBPRINTF_NANO" |

#### D. Memory Model & Concurrency — Name Shared State

| Data to Provide | Why | Example |
|----------------|-----|---------|
| Shared variables | LLMs skip volatile if not told | "counter is written in ISR, read in main → volatile" |
| ISR restrictions | LLMs put sleep/malloc in ISR | "ISR body: no blocking calls, no allocation, no printk" |
| Synchronization mechanism | LLMs pick mutex for ISR (wrong) | "ISR-thread sync: use k_spin_lock, not k_mutex" |
| Memory ordering needs | LLMs never add barriers | "Barrier between data write and index update" |

> **This is the 35%p gap.** If you say "counter is shared between ISR and
> main", the LLM might or might not add `volatile`. If you say "counter must
> be volatile because ISR writes it", the LLM will comply. **Always be
> explicit about safety-critical requirements.**

#### E. Error Handling — Demand It

| Data to Provide | Why | Example |
|----------------|-----|---------|
| Error handling policy | LLMs skip it by default | "Check return value of every API call. On error, goto cleanup." |
| Cleanup sequence | LLMs can't infer reverse order | "On failure after cdev_add: call cdev_del, then unregister_chrdev_region" |
| Rollback requirement | LLMs implement happy path only | "If OTA download fails, call dfu_target_done(false) to abort" |
| Resource lifecycle | LLMs leak resources | "Every k_mem_slab_alloc must have a matching k_mem_slab_free" |

> **Error handling is the single most important thing to demand explicitly.**
> Without it, LLMs generate code that works in demos and bricks devices in
> production.

#### F. Toolchain & Platform — Pin the Version

| Data to Provide | Why | Example |
|----------------|-----|---------|
| SDK name + exact version | Prevents deprecated API usage | "ESP-IDF v5.2.1" or "Zephyr 3.6 + nRF Connect SDK 2.6" |
| Required Kconfig options | LLMs write code, forget prj.conf | "prj.conf must include CONFIG_SPI_DMA=y" |
| Forbidden APIs | Prevents cross-platform confusion | "Do NOT use FreeRTOS, Arduino, or Linux POSIX APIs" |
| Build system structure | LLMs generate standalone files | "This is a Zephyr app: CMakeLists.txt + prj.conf + src/main.c" |

---

## Review Checklist — What to Verify in LLM Output

### Automated Checks (Tool-Assisted)

| Check | Tool | Catches |
|-------|------|---------|
| Cross-platform API contamination | `grep -E 'xTaskCreate\|vTaskDelay\|analogRead\|HAL_GPIO'` | F2 |
| Missing volatile on shared vars | Custom linter or manual review | D1 |
| ISR forbidden API calls | Custom linter: extract ISR bodies, scan for blocklist | D5 |
| Kconfig completeness | Compare `CONFIG_*` in code vs. `prj.conf` | F3 |
| MISRA compliance | PC-lint, Polyspace, cppcheck --addon=misra | E7 |
| Return value checking | `cppcheck --enable=unusedFunction` or custom | E2 |
| Balanced alloc/free | Custom: count alloc vs free calls | E3 |

### Manual Review (Human Required)

| What to Check | Why Automation Fails | Factor |
|--------------|---------------------|--------|
| Error path completeness | Regex can detect presence but not correctness of cleanup | E1 |
| Init ordering | Requires datasheet knowledge | A2 |
| Timing margins | Requires system-level reasoning | B2 |
| DMA mode selection (HW cyclic vs SW) | Semantic choice, not syntax | A5 |
| Power state machine design | Architectural decision | A2 + E2 |
| Rollback path adequacy | Requires understanding failure scenarios | E4 |

### Hardware Verification (Board Required)

| What to Test | Why Simulation Fails | When |
|-------------|---------------------|------|
| Peripheral init sequence | QEMU lacks peripheral state machines | First integration |
| DMA transfer correctness | Cache coherency invisible in emulator | After DMA code changes |
| Timing under load | Jitter and latency vary with real interrupts | Before release |
| Power consumption | Emulators don't model power domains | Power-related changes |
| Watchdog behavior | QEMU WDT doesn't match real silicon | After WDT code changes |

---

## Task Risk Matrix — What to Delegate vs. Not

### Safe to Delegate (LLM + Quick Review)

LLM success rate > 90%. Quick scan for obvious issues is sufficient.

| Task | Why Safe | Review Focus |
|------|---------|-------------|
| Kconfig / prj.conf fragments | Pattern-matching task, well-represented in training data | Check option names exist |
| Basic GPIO / UART / SPI init | Common patterns, abundant examples | Check device_is_ready |
| Thread creation boilerplate | K_THREAD_DEFINE is formulaic | Check stack size |
| Device Tree node addition | Structured syntax | Check compatible string, required properties |
| CMakeLists.txt additions | Formulaic | Check target names |

### Delegate with Thorough Review

LLM success rate 60-85%. LLM produces a useful first draft but expect 1-3
issues to fix.

| Task | Common LLM Mistakes | Review Checklist |
|------|---------------------|-----------------|
| ISR handlers | Missing volatile, forbidden APIs, wrong sync primitive | D1, D5, D6 |
| DMA configuration | Wrong mode (cyclic vs one-shot), missing cache ops, alignment | A5, C6, D3 |
| BLE stack setup | Incomplete lifecycle, missing error checks | A8, E2 |
| Error handling code | Partial cleanup, missing rollback, flag instead of early return | E1-E4 |
| Timer / counter setup | No safety margin, counter not stopped after use | B2, B5 |
| Sensor driver | Single-shot instead of periodic loop, missing error checks | B4, E2 |
| Networking (MQTT, DNS) | Missing connect error check, infinite timeout, no LWT ordering | B3, E2 |

### Human-Primary (LLM Assists with Fragments Only)

LLM success rate < 40% on complete task. Use LLM for individual functions
within a human-designed architecture.

| Task | Why LLM Fails | How LLM Helps |
|------|--------------|---------------|
| Multi-component system architecture | Requires cross-module reasoning, 50+ file context | Generate individual modules after human designs the architecture |
| Power state machine | Sleep/wake transitions require HW + SW co-design | Generate individual state handlers |
| OTA update pipeline | Safety-critical; rollback design requires system thinking | Generate download/verify functions, human designs the state machine |
| Cross-platform migration | 29.4% success rate (EmbedAgent) | Generate API mapping tables, human reviews each mapping |
| Safety-critical control loops | Hard RT + fault tolerance + certification | Generate boilerplate, human designs safety logic |

### Never Delegate (Human Only)

These require physical interaction, certification knowledge, or judgment
calls that have no code representation.

| Task | Why |
|------|-----|
| Board bring-up & clock tree | Requires oscilloscope, datasheet, iterative HW debugging |
| Safety certification (ISO 26262, DO-178C, IEC 62304) | Requires traceability artifacts, formal methods, auditor approval |
| Security threat modeling | Requires system-level attack surface analysis |
| EMC / thermal / signal integrity | Requires RF engineering, thermal simulation, PCB layout |
| Production test design | Requires knowledge of ICT fixtures, boundary scan, yield targets |
| Chip errata workarounds | Requires reading specific silicon revision errata sheets |
| Field failure analysis | Requires physical device forensics and environmental data |

---

## Recommended Development Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   1. ARCHITECT (Human)                                              │
│      ├── System decomposition: modules, tasks, IPC                  │
│      ├── Hardware assignments: pins, DMA, interrupts, clocks        │
│      ├── Safety analysis: which paths are critical                  │
│      └── Generate CONTEXT DOCUMENT for each module                  │
│                                                                     │
│   2. GENERATE (LLM)                                                 │
│      ├── Feed: context doc + prompt for ONE function/module         │
│      ├── Be explicit about: error handling, volatile, ordering      │
│      ├── Specify: SDK version, forbidden APIs, resource budget      │
│      └── Output: first-draft code                                   │
│                                                                     │
│   3. REVIEW (Human + Tools)                                         │
│      ├── Automated: MISRA, cross-platform scan, alloc balance       │
│      ├── Manual: error paths, init ordering, timing margins         │
│      ├── Fix: typically 1-3 issues per function                     │
│      └── Iterate: feed errors back to LLM for correction            │
│                                                                     │
│   4. COMPILE & STATIC ANALYSIS (Toolchain)                          │
│      ├── Cross-compile for target                                   │
│      ├── Static analysis: cppcheck, PC-lint, Coverity               │
│      ├── Fix all warnings (LLMs generate ~25 MISRA violations/KLOC) │
│      └── Verify Kconfig consistency                                 │
│                                                                     │
│   5. TEST ON HARDWARE (Human + Board)                               │
│      ├── Unit tests on QEMU/native_sim where possible               │
│      ├── Integration test on real board (MANDATORY for DMA, ISR,    │
│      │   timing, power, watchdog)                                   │
│      ├── Stress test: 24hr+ soak for memory leaks, timing drift     │
│      └── Failure injection: disconnect power during OTA, corrupt    │
│          flash, trigger WDT                                         │
│                                                                     │
│   6. CERTIFY & RELEASE (Human)                                      │
│      ├── Safety certification evidence (if applicable)              │
│      ├── EMC/regulatory testing                                     │
│      └── Production test validation                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Key principle:** LLM is a **first-draft generator for individual functions**
within a human-designed architecture. The human is the architect, reviewer,
integrator, tester, and certifier. The LLM accelerates the most tedious parts
(boilerplate, API lookup, pattern application) but cannot replace the
engineering judgment that makes embedded systems safe.

---

## Non-Code Factors — Human Verification Required

These factors were excluded from the 42-factor code taxonomy because they
cannot be addressed by code generation. However, they are **critical to
embedded product success** and must be verified by the human developer.
Ignoring them because "the LLM didn't mention it" is a common failure mode
when teams over-rely on AI-generated code.

### Hardware & Physics

| # | Factor | Impact | What the Human Must Do |
|---|--------|--------|----------------------|
| H1 | Voltage & power domain design | Cross-domain communication needs level shifters; brown-out thresholds affect boot reliability | Review schematic for level shifting on I2C/SPI lines crossing voltage domains. Verify brown-out detector (BOD) threshold in code matches hardware capability. |
| H2 | Analog circuit dependencies | ADC accuracy depends on reference voltage, sampling time, and input impedance matching | Verify ADC configuration against actual circuit: VREF source, input filter, sampling capacitor charge time. LLM cannot know your PCB's RC constants. |
| H3 | Chip errata | Specific silicon revisions have known bugs requiring software workarounds | Check errata sheet for your exact chip revision (e.g., STM32F4 errata ES0182). Apply workarounds. LLMs have no knowledge of revision-specific bugs. |
| H4 | Endianness | Mixed-endian systems (network ↔ MCU ↔ sensor) require byte-order conversion | Verify byte ordering at every serialization boundary. LLMs sometimes get `htons`/`ntohs` correct but miss sensor register byte order. |
| H5 | EMC/EMI compliance | GPIO slew rate, filter capacitors, and software toggle frequency affect radiated emissions | Configure GPIO drive strength and slew rate appropriately. Avoid high-frequency software toggling. Run pre-compliance scan before certification. |
| H6 | Signal integrity | High-speed SPI/I2C/UART may need impedance matching and termination | If communication fails intermittently at high clock rates, the issue is likely SI — not code. Reduce clock speed or add termination. |
| H7 | Thermal constraints | Sustained computation causes thermal throttling or shutdown | Profile CPU utilization. If thermal limit is a concern, add sleep windows. LLMs do not consider thermal budget. |

### Verification & Testing

| # | Factor | Impact | What the Human Must Do |
|---|--------|--------|----------------------|
| V1 | Hardware-in-the-loop (HIL) testing | QEMU/emulators miss peripheral timing, power sequencing, and analog behavior | Test on real hardware before any release. DMA, ISR timing, power modes, and watchdog MUST be verified on silicon. |
| V2 | JTAG/SWD debugging | Race conditions, HardFaults, and memory corruption require real-time debugging | When LLM code crashes on hardware, use a debugger to inspect registers, call stack, and fault status. LLMs cannot debug for you. |
| V3 | Emulator/simulator limitations | QEMU has no DMA timing, no cache coherency, limited peripheral models | Emulator pass ≠ hardware pass. Use emulators for logic testing only. Timing and peripheral interaction require real hardware. |
| V4 | LLM output reproducibility | Same prompt → different code each run. Certification requires deterministic build artifacts. | Pin the LLM model version and temperature. Save generated code in version control immediately. Never regenerate for production — iterate on the saved version. |

### Certification & Compliance

| # | Factor | Impact | What the Human Must Do |
|---|--------|--------|----------------------|
| Cert-1 | Safety certification (ISO 26262, DO-178C, IEC 62304) | Requires structural coverage, traceability matrices, formal verification — none of which LLMs produce | Use LLM for code drafts only. All certification artifacts must be human-authored. Traceability from requirement → code → test must be manually established. |
| Cert-2 | Regulatory certification (FCC, CE, UL) | Software choices (clock rates, PWM frequencies, RF parameters) affect RF emissions | Verify that code-configured parameters (transmit power, duty cycle, frequency hopping) comply with regulatory limits. LLMs have no knowledge of regional regulations. |
| Cert-3 | IP & license compliance | LLM-generated code may inadvertently reproduce copyrighted/patented code | Run license scanning tools (FOSSA, Snyk) on generated code. For safety-critical products, obtain legal review of AI-generated components. |

### Manufacturing & Longevity

| # | Factor | Impact | What the Human Must Do |
|---|--------|--------|----------------------|
| Mfg-1 | Manufacturing variation | Same chip model varies between production lots in clock accuracy, ADC offset, and threshold voltages | Add calibration routines at manufacturing time. Do not hard-code calibration values that LLMs might generate. |
| Mfg-2 | Long-term field operation (10yr+) | Flash wear-leveling, capacitor aging, clock drift accumulation, memory fragmentation over years | Review LLM code for: `malloc` in loops (fragmentation), Flash write without wear-leveling, monotonic counters that overflow. Run 24hr+ soak tests. |
| Mfg-3 | BOM cost optimization | Cheaper MCU with less RAM/Flash requires more aggressive code optimization | When porting to cheaper hardware, re-check all buffer sizes, stack allocations, and Flash usage. LLMs generate code for "comfortable" resource budgets. |

---

## The Bottom Line

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   LLM-generated embedded code is a FIRST DRAFT,             │
│   not a finished product.                                    │
│                                                              │
│   It passes static checks.   (Sonnet 99.5% / Haiku 89% L0)  │
│   It will probably run.      (100% L1 compile, L2 runtime)   │
│   It may not be safe.        (Sonnet 90% / Haiku 70% L3)    │
│   It will not be certified.  (0% MISRA compliance)           │
│                                                              │
│   The 10.5% gap between "runs" and "safe" is where          │
│   devices get bricked, batteries drain, data corrupts,       │
│   and field recalls happen.                                  │
│                                                              │
│   LLM = speed on the straightaways.                          │
│   Human = steering through the turns.                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

The 42 code factors tell you WHERE to look.
The non-code factors tell you WHAT ELSE to check.
The context guide tells you HOW to prompt.
The risk matrix tells you WHAT to delegate.
The workflow tells you HOW to integrate it all.

**Use all five together, and LLMs become the most productive tool in your
embedded development kit. Use the LLM alone, and you ship a demo, not a
product.**

---

## Research Sources

| Short Name | Full Citation | Key Finding |
|-----------|--------------|-------------|
| EmbedAgent | Xu et al., "EmbedAgent," ICSE 2026 | Best model 55.6% pass@1; ESP-IDF migration 29.4% |
| IoT-SkillsBench | Li et al., arXiv:2603.19583, 2026 | Raw LLM insufficient; human-expert skills achieve near-perfect |
| MDPI-MCU | Babiuch & Smutny, Future Internet 18(2), 2026 | 27 LLMs: simple 85% → complex <20%; API hallucination #1 failure |
| Unseen Horizons | Zhang et al., ICSE 2025 | 62.5% pass rate drop on obfuscated/unfamiliar code |
| CHI-Embedded | Englhardt et al., CHI EA 2024 | GPT-4: I2C 66%, IMU 16%; iterative approach needed |
| IEEE-QRS | Dunne et al., IEEE QRS 2024 | CWE taxonomy: buffer overflow, race condition, resource mismanagement |
| Abtahi-Firmware | Abtahi et al., arXiv:2509.09970, 2025 | 92.4% vulnerability remediation with agent-driven patching |
| HardSecBench | Chen et al., arXiv:2601.13864, 2026 | 924 tasks, 76 CWEs; functional pass ≠ security pass |
| Backslash | Backslash Security Report, 2025 | GPT-4o: 10% secure (naive); Claude: 60% secure (naive), 100% (prompted) |
| RunSafe | AI in Embedded Systems Report, 2025 | 83.5% deploy AI code to production; security #1 concern |
| MISRA-LLM | Umer et al., 2025 | 23-29 violations/KLOC baseline; 83% reduction with instructions |
| Homogenization | arXiv:2507.06920 | LLM errors cluster tightly; cross-validation needed |
| H2LooP | arXiv:2603.11139, 2026 | Continual pretraining for hardware design — 7B model achieving domain-specific improvements |
| VulInstruct | arXiv:2404.07732, 2024 | Implicit security specifications from CVE patterns for embedded vulnerability detection |
| InCoder-32B + EmbedCGen | arXiv:2603.16790, 2026 | Dedicated embedded code generation model and benchmark |
| Stack-v2 | arXiv:2402.19173 | 775B tokens; embedded C is tiny fraction |
| EmbedEval | This project | 233 TCs, 97 unique failed checks, implicit knowledge gap 35%p |
| CONCUR | arXiv:2603.03683, 2026 | First concurrent code generation benchmark (deadlocks, races, sync) |
| LLM-CSEC | arXiv:2511.18966, 2025 | C/C++ security: CWE-120, -787, -122, -190, -401 found across 10 LLMs |
| Safety-Auto | PMLR v284, Sevenhuijsen 2025 | ISO 26262 C: 540/800 easy, 46/800 hard; Zero-Shot CoT best strategy |
| spec2code | arXiv:2411.13269, 2024 | LLM + ACSL formal specs + Frama-C for automotive embedded C |
| Clover | arXiv:2504.00521, 2025 | Automated atomicity violation detection in ISR/shared-resource contexts |
| SecureDegrades | arXiv:2506.11022, 2025 | 37.6% vuln increase after 5 iterations — self-repair can introduce security flaws |
| CoT-Quality | arXiv:2507.06980, 2025 | "Incomprehension of implicit requirements" catalogued as internal LLM factor |
| Persona-EMNLP | arXiv:2508.19764, EMNLP 2025 | Expert personas harmful for code: -3 to -5% accuracy |
| ContextRot | Chroma Research, 2025 | 18 frontier models: every model degrades at every input length increment |
| PromptSpec | arXiv:2508.03678, 2025 | +30% absolute pass@1 from enhanced prompt specificity on specialized tasks |
| RAG-API | arXiv:2503.15231, 2025 | RAG doubles pass rate (0.21→0.43) for unfamiliar API documentation |

---

## Changelog

### v1.5 (2026-04-13)
- Updated TC count from 210 to 233 (6 new cases: adc, uart, pwm categories)
- Added research sources: H2LooP, VulInstruct, InCoder-32B/EmbedCGen
- All evidence now based on n=3 aggregate results

- **v1.4 (2026-03-29):** Research-backed update. Added 11 new research sources
  (CONCUR, LLM-CSEC, spec2code, Clover, CoT-Quality, Persona-EMNLP,
  ContextRot, PromptSpec, RAG-API, Safety-Auto, SecureDegrades).
  Noted 35%p implicit/explicit gap as novel finding in literature.
- **v1.3 (2026-03-29):** Data-verified review. Fixed "Both Models Fail" table:
  12→8 entries (4 were Sonnet-only). Updated 99→97 unique checks / 109
  instances. Upgraded D8 (deadlock) Theoretical→Empirical (Haiku fails
  lock ordering on threading-006). Fixed G2 orphan ref. Renamed Part II IDs
  (C1→Cert-1, M1→Mfg-1) to avoid collision with Part I. Qualified E category
  "#1 failure" claim as Sonnet-specific. Added model-specific stats to
  Bottom Line box.
- **v1.2 (2026-03-29):** Post-review improvements. Added M6 (RLHF alignment
  bias) meta-factor. Upgraded A8 (protocol details) Med→High based on
  IoT-SkillsBench evidence. Updated summary statistics (23 High, 19 Med).
- **v1.1 (2026-03-29):** Added Part II — practical development guide. Context
  data guide (what to feed per category), review checklist (automated + manual),
  task risk matrix (4-tier delegation model), recommended workflow, and expanded
  non-code factors (19 factors across 4 groups) with prescriptive human actions.
- **v1.0 (2026-03-29):** Initial release. 42 code factors from 58 original
  candidates. Removed 13 non-code factors, merged 3 overlapping pairs,
  corrected 8 strength ratings. Added evidence tags and research citations.
  Mapped all 99 benchmark checks to taxonomy factors.
