# Considerations for Embedded Development with LLMs

**Date:** 2026-04-05
**Based on:** EmbedEval benchmark data (Haiku 4.5 vs Sonnet 4.6, 179 public + 48 private cases)
**Test Results:** See companion document [`BENCHMARK-COMPARISON-2026-04-05.md`](BENCHMARK-COMPARISON-2026-04-05.md)
**Full Factor Taxonomy:** [`docs/LLM-EMBEDDED-FAILURE-FACTORS.md`](./LLM-EMBEDDED-FAILURE-FACTORS.md) (42 code factors + 19 non-code factors)

---

## 1. Why LLMs Fail at Embedded: Structural Root Causes

### 1.1 Six Meta-Properties: Why Embedded Is Fundamentally Different

These aren't weaknesses in specific models — they're structural properties of the LLM architecture + embedded domain combination.

| # | Meta-Property | Description | Evidence from Benchmark |
|---|--------------|-------------|------------------------|
| **M1** | **Training Data Sparsity** | Embedded C is a tiny fraction of LLM training corpora. The Stack v2 (775B tokens) is dominated by Python/JS/Java. Zephyr DMA APIs are orders of magnitude rarer than React hooks. | Haiku: 0% DMA, 0% on ESP-IDF/STM32 platform-specific cases. Sonnet: 44% DMA. Rare APIs = worse performance. |
| **M2** | **Silent Failure** | In web/server code, bugs crash visibly. In embedded, a missing `volatile` compiles, runs in QEMU, passes CI — then corrupts data under load on real hardware months later. | 4 security cases pass L0+L1 but fail L2 in both models. Code "looks right" but doesn't work. |
| **M3** | **Implicit Knowledge Gap** | When told "use volatile", LLM complies (~95%). When it must infer volatile is needed from "ISR shares variable with main" — ~60%. **35%p gap.** | Haiku fails `volatile` check; Sonnet passes. Both fail memory barriers. |
| **M4** | **Complexity Cliff** | LLM performance drops sharply: simple peripheral 70-85% → multi-peripheral 40-60% → system integration 11-20%. | Tier 1 categories ~90%. Tier 3 (DMA, ISR, threading) ~30%. Same model, 60%p gap. |
| **M5** | **Familiarity Bias** | LLMs perform well on common patterns, collapse on rarer equivalents. OBFUSEVAL showed 62.5% pass rate drop on renamed APIs. | DMA scatter-gather (rare): 0% both. Basic GPIO (common): 67-100%. Same difficulty, vastly different pass rates. |
| **M6** | **RLHF Alignment Bias** | RLHF optimizes for "clean, readable" output — systematically suppresses embedded safety patterns: `volatile` looks "unnecessary", `goto cleanup` is "bad practice", error handling is "noise". | Both models omit `volatile`, skip `goto err_cleanup`, generate tutorial-style code. Backslash Security: 10% secure code naively vs 100% when explicitly prompted. |

### 1.2 What LLMs Structurally Cannot Access

The deepest insight isn't about specific API failures — it's about **entire categories of knowledge that don't exist in LLM training data or context windows**.

| Missing Context | What It Contains | Why LLM Can't Have It | Impact on Generated Code |
|----------------|-----------------|----------------------|-------------------------|
| **Datasheet** | Register maps, timing diagrams, electrical specs, init sequences | Proprietary PDFs, not in training data. Too large for context (100-500 pages). | Wrong init order, wrong DMA config, wrong clock setup. **Root cause of DMA 0-44%.** |
| **Schematic** | Pin connections, voltage levels, pull-ups, level shifters | Board-specific, never in code repos. Visual format. | Pin mux errors, missing level shifter awareness. |
| **Silicon Errata** | Chip-revision-specific bugs and workarounds | Per-revision vendor docs. Nearly zero training examples. | Works on Rev A, fails on Rev B silicon. |
| **Runtime State** | Memory layout, stack depth, ISR nesting, timing jitter | Only observable with debugger/oscilloscope. | Optimistic stack sizes, no jitter margins, single-shot demos. |
| **System Architecture** | Task dependencies, IPC topology, resource ownership | Team documents / architect's head. Multi-file reasoning. | Module works alone, breaks during integration. |
| **Field History** | Failure modes in production over years | Internal incident databases, customer reports. | No wear-leveling, no drift compensation, no manufacturing tolerance. |

**This is not a model quality problem — it's a context availability problem.** Even a perfect model cannot apply datasheet knowledge it has never seen.

### 1.3 The Four Levels of Implicit Knowledge

From [INSIGHTS.md #4](./INSIGHTS.md), confirmed by both Haiku and Sonnet data:

```
Level 1: C Language Knowledge        ← Sonnet ~95%, Haiku ~80%
  volatile, const, named constants, goto cleanup
  
Level 2: RTOS Knowledge              ← Sonnet ~85%, Haiku ~65%
  ISR blocking forbidden, spinlock vs mutex, K_NO_WAIT
  
Level 3: Hardware Knowledge          ← Sonnet ~60%, Haiku ~30%
  Cache alignment >=32, flush/invalidate, timing margins
  
Level 4: System Safety Knowledge     ← Sonnet ~50%, Haiku ~30%
  OTA rollback, reverse cleanup, fail-fast, conditional WDT feed
```

**Level 1-2** exist abundantly in training data (C textbooks, RTOS tutorials).
**Level 3-4** exist primarily in datasheets, internal docs, and experienced engineers' heads — **outside the LLM's knowledge boundary**.

### 1.4 From Observation to Root Cause

| Risk Zone (Test Data) | Root Factor Categories | Key Meta-Properties |
|----------------------|----------------------|-------------------|
| DMA (0-44%) | A. Hardware Awareness + D. Cache Coherency + C. Alignment | M1 (training sparsity), M2 (silent failure) |
| ISR/Concurrency (22-33%) | D. Memory Model + B. Timing | M3 (implicit gap), M6 (RLHF suppresses volatile) |
| Error Path (fails on complex) | E. Error Handling | M6 (RLHF prefers clean code), autoregressive bias |
| Memory Optimization (30-50%) | C. Memory Constraints | M1 (rare APIs), M5 (familiarity bias) |
| HW Timing/Protocols (varies) | A. Hardware Awareness + B. Temporal | M1 (datasheet absent), M4 (complexity cliff) |

### 1.5 LLM-Embedded Knowledge Boundaries

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LLM Knowledge Boundary                           │
│                                                                     │
│  ┌───────────────────────────────────────┐                          │
│  │  INSIDE: Training Data                │                          │
│  │  API signatures, header names,        │  Haiku: ~65% pass       │
│  │  basic RTOS patterns, tutorials       │  Sonnet: ~80% pass      │
│  └───────────────────────────────────────┘                          │
│                                                                     │
│  ┌───────────────────────────────────────┐                          │
│  │  BOUNDARY: Implicit Domain Knowledge  │                          │
│  │  volatile for ISR, spinlock vs        │  Sonnet: ~60% pass      │
│  │  mutex, error cleanup ordering        │  Haiku: ~40% pass       │
│  └───────────────────────────────────────┘  (35%p gap vs explicit) │
│                                                                     │
│  ┌───────────────────────────────────────┐                          │
│  │  OUTSIDE: Context LLM Never Has      │                          │
│  │  Datasheets, schematics, errata,      │  Both: ~30% pass        │
│  │  runtime state, field history,        │  (when these matter)    │
│  │  system architecture decisions        │                          │
│  └───────────────────────────────────────┘                          │
│                                                                     │
│  ┌───────────────────────────────────────┐                          │
│  │  NEVER POSSIBLE: Non-Code Factors     │                          │
│  │  Board bring-up, EMC testing,         │  N/A — requires         │
│  │  safety certification, silicon        │  physical interaction   │
│  │  validation, manufacturing test       │                          │
│  └───────────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. The "3AM Paranoia" Layer: Field Knowledge LLMs Cannot Learn

Beyond the 42 code-observable factors, there's knowledge that only exists in engineers who have debugged production failures at scale. These patterns come from 10,000 devices going silent simultaneously — not from reading documentation. **LLMs cannot learn them because they live in incident reports and postmortems, not public code repos.**

### 2.1 Long-Running Timer & Counter Overflows

**The knowledge:** A 32-bit millisecond counter overflows after 49.7 days. Code using `millis()` or `HAL_GetTick()` works for weeks, then the device locks up, reboots, or produces wrong timing.

**Real incidents:**
- [Zephyr/OpenThread nRF52840](https://github.com/zephyrproject-rtos/zephyr/issues/41509): All devices hang at exactly 49 days — "showstopper for commercial products"
- [ESPHome ESP32](https://github.com/esphome/issues/issues/826): Sensors stop updating after 49 days
- [LoRaWAN LoRaMac-node](https://github.com/Lora-net/LoRaMac-node/issues/1016): Timers silently stop — "IOT devices are designed to run for years"
- [STM32 HAL `uwTick`](https://community.st.com/t5/stm32-mcus-embedded-software/what-happens-when-the-32bit-hal-uwtick-timer-variable-overflows/td-p/120367): 32-bit overflow, subtle race in 64-bit extension

**What LLM generates:** `if (millis() - start > timeout)` — correct for short durations, breaks after 49 days.
**What engineer writes:** 64-bit counters, or unsigned modular arithmetic with wrap handling, and boundary tests at 49.7 days.

**Variant — the 87-day radio lockup:** Protocol stacks with 32-bit tick counters at different resolutions overflow at different magic numbers. An 87-day lockup is consistent with a ~2ms-resolution counter overflowing 2^32. LLMs have zero chance of anticipating this.

### 2.2 Flash/eMMC Wear and Write Amplification

**The knowledge:** NAND flash has finite write endurance (1,000-100,000 erase cycles per SLC/MLC/TLC). Write amplification means a 4-byte log write triggers a full 128KB block erase-rewrite. A device logging every 10 seconds kills its flash in months.

**Real incident:** [Tesla eMMC failure](https://www.cnx-software.com/2019/08/16/wear-estimation-emmc-flash-memory/) — excessive logging wore out eMMC on thousands of vehicles.

**What LLM generates:**
```c
f = fopen("/data/sensor.log", "a");
fprintf(f, "%d,%d\n", timestamp, value);
fclose(f);  // Every 10 seconds — kills flash in months
```

**What engineer writes:**
```c
// Buffer in RAM, flush to flash every N minutes
// Use tmpfs for /var/log
// Use LittleFS/UBIFS (wear-leveling aware)
// Monitor eMMC health registers (EXT_CSD DEVICE_LIFE_TIME_EST)
// Calculate: 500MB/day x 365 x 10yr = 1.8TB TBW required
// Account for write amplification factor (WAF 3-10x)
```

**Key numbers LLMs don't know:**
- TLC: ~1,000 P/E cycles. SLC: ~100,000. [pSLC mode](https://www.kingston.com/en/blog/embedded-and-industrial/emmc-lifecycle): 10x endurance, half capacity.
- WAF: 3-10x for random small writes. The fuller the disk, the worse.
- A 4GB eMMC with WAF=8 and endurance=3000 = only 1.5TB total lifetime writes.

### 2.3 Sensor Plausibility and Fault Detection

**The knowledge:** -40°C in Mexico City is a hardware fault, not real data. An experienced engineer implements plausibility checks: range limits, rate-of-change limits, stuck-at detection, and cross-sensor correlation.

**What LLM generates:**
```c
int16_t temp = read_sensor();
transmit_data(temp);  // Blindly sends -40°C
```

**What engineer writes (from [IEC 61508](https://risknowlogy.com/articles/detail/17305/) / [ISO 26262](http://embeddedinembedded.blogspot.com/)):**
```c
int16_t temp = read_sensor();

// Range check: physically impossible values
if (temp < TEMP_MIN_PLAUSIBLE || temp > TEMP_MAX_PLAUSIBLE) {
    fault_counter++;
    report_sensor_fault(FAULT_OUT_OF_RANGE);
    return last_known_good;
}
// Rate-of-change: can't jump 50 degrees in 1 second
if (abs(temp - last_temp) > MAX_RATE_OF_CHANGE) {
    report_sensor_fault(FAULT_IMPLAUSIBLE_CHANGE);
    return last_known_good;
}
// Stuck-at: sensor frozen too long
if (temp == last_temp && ++stuck_count > STUCK_LIMIT) {
    report_sensor_fault(FAULT_STUCK_AT);
}
// Freshness: data too old
if (now - last_read_time > FRESHNESS_TIMEOUT_MS) {
    report_sensor_fault(FAULT_STALE_DATA);
}
```

**Why LLM misses this:** Training data assumes sensors work. Plausibility checking is an engineering discipline (IEC 61508, ISO 26262) that rarely appears in code repos.

### 2.4 Power Management at Scale

**The knowledge:** Waking 50ms too early is invisible on 1 prototype. On 500,000 devices, it's thousands of dollars in wasted battery life per year.

**What LLM misses:**
- [GPIO leakage](https://dojofive.com/blog/power-optimization-techniques-for-firmware/): Unconfigured pins leak hundreds of uA in sleep — more than the MCU itself
- [Regulator quiescent current](https://www.analog.com/en/resources/technical-articles/greatly-improve-battery-power-efficiency-for-iot-devices.html): An "idle" LDO at 10uA cuts months off battery life
- Wake-up penalty: Deep sleep saves power but takes 10-100us to wake; peripheral re-init = milliseconds
- [Tickless RTOS](https://www.embeddedrelated.com/showarticle/1667.php): Without it, the periodic tick wakes the MCU for nothing
- Temperature derating: Battery resistance increases in cold → voltage sag → [brownout during flash write bricks the device](https://www.embedded.com/brown-out-reset/)
- Always 20% safety margin for unpredictable network retransmissions

**What LLM generates:** `k_sleep(K_SECONDS(60));` — correct for functionality, ignoring wake/sleep power cost, peripheral power-down, and energy budget calculation.

### 2.5 Radio Stack State Corruption

**The knowledge:** BLE/WiFi/LoRa stacks maintain complex state machines. After weeks of connection cycles, resource leaks accumulate until the radio silently locks up. No crash, no hard fault, no watchdog trigger — but the radio never recovers.

**Real incidents:**
- [TI CC2642R](https://e2e.ti.com/support/wireless-connectivity/bluetooth-group/bluetooth/f/bluetooth-forum/771568/rtos-cc2642r-stack-crash-in-simple-peripheral-when-connecting-multiple-devices): "Ghost connections" leak memory; "Our startup will not survive" — 8 months debugging
- [Nordic nRF52840](https://devzone.nordicsemi.com/f/nordic-q-a/106208/spi-transfers-cause-ble-connection-timeout-but-only-on-some-units-and-especially-when-cold): SPI interference causes BLE timeout — only 5% of units, only when cold
- [STM32WB55](https://community.st.com/t5/stm32-mcus-wireless/ble-central-connection-timeout-with-sleeping-peer-device-is-not/td-p/702755): Timeout with sleeping peer blocks ALL future connections

**What LLM generates:** Happy-path connect/disconnect/reconnect.
**What engineer adds:** Periodic stack health check, connection table GC, radio watchdog (full stack re-init after N minutes silence), resource watermark logging.

### 2.6 Watchdog Anti-Patterns

**The knowledge:** A watchdog fed unconditionally is security theater. `wdt_feed()` in a timer ISR means the watchdog never triggers even if main is deadlocked.

**[Key anti-patterns](https://www.embeddedrelated.com/showarticle/1276.php) LLMs reproduce:**
- Feeding from timer ISR (main dead but WDT happy)
- Suspending WDT during long operations
- Feeding without verifying system health
- No escalation (soft → hard → factory default)

**What an engineer paged at 3AM builds:**
- Task-level watchdog: WDT fed only when ALL critical tasks report healthy
- [Warm boot detection](https://www.ganssle.com/watchdogs.htm): "One outfit found their product crashing thousands of times per second — warm-boot recovery was so fast users only noticed degraded response"
- Reset reason logging: read MCU reset registers before clearing, store to persistent memory
- Graceful degradation: WDT 3x in 1 hour → disable non-essential features, send alert

### 2.7 Crystal Oscillator Drift and Aging

**The knowledge:** A crystal at +/-20ppm at 25°C drifts +/-100ppm across temperature. Over years, aging adds +/-3-5ppm/year. For BLE/LoRa with tight timing, this causes sync failures — only in winter, only on 2+ year old devices.

**What LLM doesn't know:**
- [Aging accelerates with overdrive](https://www.fujicrystal.com/news_details/crystal-oscillator-aging.html) — months of aging compressed into weeks
- [Temperature vs drift](https://blog.mbedded.ninja/electronics/components/crystals-and-oscillators/) — parabolic curve, accuracy at 25°C says nothing about -20°C
- Spec pre-aged/burn-in crystals for production; hermetic packages for 10+ year life

### 2.8 Brownout During Flash Write = Bricked Device

**The knowledge:** [A power dip during flash write corrupts the sector](https://www.embedded.com/brown-out-reset/). If it's the boot vector or FS metadata, the device is permanently bricked. Battery voltage sag during RF transmit (100mA draw) can cause exactly this.

**What LLM generates:** `flash_write(addr, data, len);` — no voltage check, no double-buffer, no post-write CRC.
**What engineer writes:** Check Vdd before write. Double-buffered write (backup first, then swap). CRC verify after write. BOR fires during write → mark sector suspect on next boot.

---

### Summary: The "3AM Knowledge" Taxonomy

| Category | Example | Time to Manifest | LLM Chance |
|----------|---------|-------------------|------------|
| **Counter overflow** | 49.7-day timer wrap | Days to months | ~0% |
| **Storage wear** | eMMC death from logging | Months to years | ~0% |
| **Sensor plausibility** | -40°C in Mexico City as real data | Immediate but rare | ~5% |
| **Power at scale** | 50ms wake overhead x 500K devices | Cumulative | ~0% |
| **Radio state corruption** | BLE lockup after 87 days | Weeks to months | ~0% |
| **Watchdog theater** | WDT fed from ISR, main dead | Random | ~10% |
| **Crystal aging** | Protocol desync after 2yr in cold | Years | ~0% |
| **Brownout + flash** | Bricked from write during Tx | Random | ~0% |

**These are not edge cases. They are the primary failure modes of mass-deployed embedded products.** Every experienced embedded engineer has war stories for each. LLMs have ~0% chance of handling them because:

1. **Training data gap:** Patterns live in internal postmortems, not public repos
2. **No physical context:** LLMs can't know your battery chemistry, crystal spec, or flash endurance
3. **Time horizon:** LLMs optimize for "demo works today," not "production works for 10 years"
4. **Scale blindness:** 50ms timing bug invisible on 1 device, catastrophic on 500,000

---

## 3. Practical Guidance for Embedded Teams

### 3.1 Risk Zones (Derived from Benchmark Data)

| Zone | Category | Pass Rate | Root Cause | Action |
|------|----------|-----------|------------|--------|
| 1 | DMA | 0-44% | Datasheet (M1) + silent failure (M2) | Never trust LLM DMA code |
| 2 | ISR/Concurrency | 22-33% | Implicit gap (M3) + RLHF (M6) | Verify: no blocking, correct sync, barriers |
| 3 | Error paths | Fails complex | RLHF (M6) + autoregressive bias | Every multi-resource init needs review |
| 4 | Memory opt | 30-50% | Rare APIs (M1) + familiarity (M5) | Expert review all memory config |
| 5 | HW timing | Varies | Datasheet (M1) + complexity (M4) | Datasheet-level init/timing review |

### 3.2 What LLMs ARE Good At

| Task | Pass Rate | Why It Works |
|------|-----------|-------------|
| Kconfig fragments | 75-88% | Pattern-matching, abundant training data |
| Device tree overlays | 88-100% | Structured syntax, well-represented |
| Sensor driver boilerplate | 100% | Standard formulaic patterns |
| BLE service scaffolding | 75-100% | Common tutorial topic |
| Yocto recipes | 88-100% | Structured syntax |
| Watchdog basic config | 89% | Simple pattern |

### 3.3 Three-Tier Trust Model

**Tier 1: Trust but Verify (>85%)**
Kconfig, device-tree, sensor-driver, BLE (Sonnet), networking (Sonnet), timer (Sonnet), watchdog, yocto
- Inside LLM boundary. Light review.

**Tier 2: Starting Point (50-85%)**
boot, gpio-basic, linux-driver, ota, power-mgmt, spi-i2c, storage, uart
- At the boundary. Mandatory review for error paths and HW interaction.

**Tier 3: Expert Review Required (<50%)**
DMA, ISR-concurrency, memory-opt, threading, security
- Outside LLM boundary. Code "works" in simulator, fails on hardware.

### 3.4 The Implicit Knowledge Paradox

```
Explicit prompt ("use volatile for the ISR flag")  → ~95% pass
Implicit requirement (LLM derives from context)     → ~60% pass
                                                      ────────
                                                      35%p gap
```

**The paradox:** If your prompt says "add cache flush before DMA" — you already know the answer. LLM value is autonomous domain knowledge, and that's where it fails.

**For teams without embedded expertise:** LLM output in Tier 3 is actively dangerous — it looks correct but isn't.

### 3.5 Model Size: Bigger Helps, But Not Enough

- Sonnet > Haiku by 12%p, mostly from Level 1-2 knowledge (more API exposure)
- Level 3-4 barely improves — both fail on memory barriers, cache coherence, reverse cleanup
- Sonnet **regresses on 8 cases** Haiku passes — bigger is not always better
- Bottleneck is missing context and structural generation bias, not model size

### 3.6 Recommended Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│  1. ARCHITECT (Human)                                            │
│     System decomposition, HW assignments, safety analysis        │
│     Generate CONTEXT DOCUMENT per module                         │
│                                                                  │
│  2. GENERATE (LLM)                                               │
│     Feed context doc + explicit safety requirements              │
│     Specify SDK version, forbidden APIs, resource budget         │
│                                                                  │
│  3. STATIC CHECK (Automated)                                     │
│     volatile on ISR vars? No blocking in ISR? Error cleanup?     │
│     Catches L0 failures (~26% of total errors)                   │
│                                                                  │
│  4. BUILD (Toolchain: -Wall -Werror)                             │
│     Catches L1 failures (~9%)                                    │
│                                                                  │
│  5. RUNTIME (QEMU/simulator)                                     │
│     Catches L2 failures (~19%). Misses real HW issues.           │
│                                                                  │
│  6. EXPERT REVIEW (Human)                                        │
│     Focus: Tier 2-3 code. Catches L3 failures (~40%).            │
│     The layer where LLMs fail silently.                          │
│                                                                  │
│  7. HARDWARE TEST (Board)                                        │
│     DMA cache, timing, peripherals. Stress 24hr+.               │
│     No simulator replaces this for production code.              │
└──────────────────────────────────────────────────────────────────┘
```

### 3.7 The Bottom Line

| LLM Output | Trust Level | Why |
|------------|------------|-----|
| "Compiles successfully" | Low | Syntax, not safety (M2) |
| "Works in simulator" | Medium | Simulator lacks DMA cache, timing |
| "Uses correct API" | Medium-High | Inside boundary; parameters may be wrong |
| "Handles errors properly" | Low | #1 failure — RLHF suppresses defensive code (M6) |
| "Is ISR-safe" | Very Low | Level 3-4 implicit knowledge (M3) |
| "DMA transfers work" | Very Low | Datasheet knowledge, outside boundary (M1) |
| "Memory is optimized" | Low | Niche APIs, familiarity bias (M5) |

**LLMs accelerate embedded dev ~2-3x for boilerplate and config (inside the knowledge boundary). For safety-critical paths — DMA, ISR, error handling, memory — they produce code that compiles, runs in simulation, and fails in production.**

**The gap is not model quality. It's knowledge that doesn't exist in training data, context that can't fit in a prompt, and field experience that lives in engineers' heads — not public repos.**

AI is great for boilerplate. But embedded code that runs unattended for 10 years needs the paranoia that only comes from debugging at 3AM because 10,000 devices went silent simultaneously.

---

## Sources

- [Zephyr OpenThread 49-day overflow](https://github.com/zephyrproject-rtos/zephyr/issues/41509)
- [ESPHome 49-day sensor freeze](https://github.com/esphome/issues/issues/826)
- [LoRaWAN timer overflow](https://github.com/Lora-net/LoRaMac-node/issues/1016)
- [STM32 HAL uwTick overflow](https://community.st.com/t5/stm32-mcus-embedded-software/what-happens-when-the-32bit-hal-uwtick-timer-variable-overflows/td-p/120367)
- [Tesla eMMC wear failure](https://www.cnx-software.com/2019/08/16/wear-estimation-emmc-flash-memory/)
- [Kingston eMMC lifecycle](https://www.kingston.com/en/blog/embedded-and-industrial/emmc-lifecycle)
- [TI CC2642R BLE stack crash](https://e2e.ti.com/support/wireless-connectivity/bluetooth-group/bluetooth/f/bluetooth-forum/771568/)
- [Nordic nRF52840 SPI-BLE interference](https://devzone.nordicsemi.com/f/nordic-q-a/106208/)
- [STM32WB55 BLE connection blocking](https://community.st.com/t5/stm32-mcus-wireless/ble-central-connection-timeout-with-sleeping-peer-device-is-not/td-p/702755)
- [Jack Ganssle — Watchdog Timers](https://www.ganssle.com/watchdogs.htm)
- [Memfault — Watchdog Best Practices](https://interrupt.memfault.com/blog/firmware-watchdog-best-practices)
- [Watchdog Anti-Patterns](https://www.embeddedrelated.com/showarticle/1276.php)
- [Crystal Oscillator Aging](https://www.fujicrystal.com/news_details/crystal-oscillator-aging.html)
- [Crystal Temperature Drift](https://blog.mbedded.ninja/electronics/components/crystals-and-oscillators/)
- [Brownout Reset Analysis](https://www.embedded.com/brown-out-reset/)
- [IEC 61508 Fault Detection](https://risknowlogy.com/articles/detail/17305/)
- [GPIO Leakage & Power Optimization](https://dojofive.com/blog/power-optimization-techniques-for-firmware/)
- [Battery Power Efficiency](https://www.analog.com/en/resources/technical-articles/greatly-improve-battery-power-efficiency-for-iot-devices.html)
- [Low-Power RTOS Techniques](https://www.embeddedrelated.com/showarticle/1667.php)
- [Memfault — Defensive Programming](https://interrupt.memfault.com/blog/defensive-and-offensive-programming)
- [LittleFS — Flash-safe filesystem](https://github.com/littlefs-project/littlefs)
- [LLM-EMBEDDED-FAILURE-FACTORS.md](./LLM-EMBEDDED-FAILURE-FACTORS.md) (42-factor taxonomy)
