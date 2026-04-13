# Considerations for Embedded Development with LLMs

**Date:** 2026-04-13
**Based on:** EmbedEval benchmark data (Haiku 4.5 vs Sonnet 4.6, **233 cases** = 185 public + 48 private, **n=3 aggregate** pass@1 means). Model 95% CIs do not overlap (Haiku [53.2%, 60.6%] vs Sonnet [64.4%, 71.3%]), so the Sonnet–Haiku gap is statistically distinguishable from run noise.
**Test Results:** See companion document [`BENCHMARK-COMPARISON-2026-04-05.md`](BENCHMARK-COMPARISON-2026-04-05.md) (includes n=3 section)
**Full Factor Taxonomy:** [`LLM-EMBEDDED-FAILURE-FACTORS.md`](./LLM-EMBEDDED-FAILURE-FACTORS.md) (42 code factors + 19 non-code factors)
**Token Scaling Economics:** [`LLM-EMBEDDED-TOKEN-SCALING.md`](./LLM-EMBEDDED-TOKEN-SCALING.md) — why infinite tokens aren't enough for embedded

---

## 1. Why LLMs Fail at Embedded: Structural Root Causes

### 1.1 Six Meta-Properties: Why Embedded Is Fundamentally Different

These aren't weaknesses in specific models — they're structural properties of the LLM architecture + embedded domain combination. For detailed descriptions with source citations, see [LLM-EMBEDDED-FAILURE-FACTORS.md](./LLM-EMBEDDED-FAILURE-FACTORS.md) §"Why Embedded Is Fundamentally Different for LLMs."

| # | Meta-Property | Benchmark Evidence |
|---|--------------|-------------------|
| **M1** | **Training Data Sparsity** | Haiku: **8%** DMA (n=3 category run); Sonnet: **31%** DMA. Still weak on ESP-IDF/STM32 platform-specific cases. Rare APIs = worse performance. |
| **M2** | **Silent Failure** | 4 security cases pass L0+L1 but fail L2 in both models. Code "looks right" but doesn't work. |
| **M3** | **Implicit Knowledge Gap** | Haiku fails `volatile` check; Sonnet passes. Both fail memory barriers. 35%p explicit-vs-implicit gap. |
| **M4** | **Complexity Cliff** | “Easy” config categories (device-tree, PWM) ~100% both; DMA/ISR/threading sit ~8–38% (n=3). Same model family, >50%p spread across categories. |
| **M5** | **Familiarity Bias** | DMA category (n=3): **31%** Sonnet vs **8%** Haiku. GPIO-basic (common patterns): **67–83%**. Same nominal difficulty band, very different outcomes. |
| **M6** | **RLHF Alignment Bias** | Both models omit `volatile`, skip `goto err_cleanup`, generate tutorial-style code. 10% secure code naively vs 100% when explicitly prompted. |

### 1.2 What LLMs Structurally Cannot Access

The deepest insight isn't about specific API failures — it's about **entire categories of knowledge that don't exist in LLM training data or context windows**.

| Missing Context | What It Contains | Why LLM Can't Have It | Impact on Generated Code |
|----------------|-----------------|----------------------|-------------------------|
| **Datasheet** | Register maps, timing diagrams, electrical specs, init sequences | Proprietary PDFs, not in training data. Too large for context (100-500 pages). | Wrong init order, wrong DMA config, wrong clock setup. **Root cause of low DMA pass rates (n=3: 31% / 8%).** |
| **Schematic** | Pin connections, voltage levels, pull-ups, level shifters | Board-specific, never in code repos. Visual format. | Pin mux errors, missing level shifter awareness. |
| **Silicon Errata** | Chip-revision-specific bugs and workarounds | Per-revision vendor docs. Nearly zero training examples. | Works on Rev A, fails on Rev B silicon. |
| **Runtime State** | Memory layout, stack depth, ISR nesting, timing jitter | Only observable with debugger/oscilloscope. | Optimistic stack sizes, no jitter margins, single-shot demos. |
| **System Architecture** | Task dependencies, IPC topology, resource ownership | Team documents / architect's head. Multi-file reasoning. | Module works alone, breaks during integration. |
| **Field History** | Failure modes in production over years | Internal incident databases, customer reports. | No wear-leveling, no drift compensation, no manufacturing tolerance. |

**This is not a model quality problem — it's a context availability problem.** Even a perfect model cannot apply datasheet knowledge it has never seen.

### 1.3 The Four Levels of Implicit Knowledge

Confirmed by both Haiku and Sonnet benchmark data:

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
| DMA (31% / 8%) | A. Hardware Awareness + D. Cache Coherency + C. Alignment | M1 (training sparsity), M2 (silent failure) |
| ISR/Concurrency (23% / 38%) | D. Memory Model + B. Timing | M3 (implicit gap), M6 (RLHF suppresses volatile) |
| Error Path (fails on complex) | E. Error Handling | M6 (RLHF prefers clean code), autoregressive bias |
| Memory Optimization (67% / 33%) | C. Memory Constraints | M1 (rare APIs), M5 (familiarity bias) |
| HW Timing/Protocols (varies) | A. Hardware Awareness + B. Temporal | M1 (datasheet absent), M4 (complexity cliff) |

### 1.5 LLM-Embedded Knowledge Boundaries

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LLM Knowledge Boundary                           │
│                                                                     │
│  ┌───────────────────────────────────────┐                          │
│  │  INSIDE: Training Data                │                          │
│  │  API signatures, header names,        │  Haiku: ~57% pass@1     │
│  │  basic RTOS patterns, tutorials       │  Sonnet: ~68% pass@1    │
│  └───────────────────────────────────────┘                          │
│                                                                     │
│  ┌───────────────────────────────────────┐                          │
│  │  BOUNDARY: Implicit Domain Knowledge  │                          │
│  │  volatile for ISR, spinlock vs        │  Sonnet: ~58% pass      │
│  │  mutex, error cleanup ordering        │  Haiku: ~47% pass       │
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

## 2. Production-Scale Failure Patterns: Implicit Knowledge Beyond Training Data

Beyond the 42 code-observable factors ([LLM-EMBEDDED-FAILURE-FACTORS.md](./LLM-EMBEDDED-FAILURE-FACTORS.md)), there are failure patterns that only surface in mass-deployed products running for months or years. These patterns are learned from field incidents — not from documentation or tutorials. **LLMs cannot learn them because they live in internal postmortems, vendor errata, and engineers' hard-won experience, not in public code repositories.**

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

### 2.9 Heap Fragmentation Over Long Runtime

**The knowledge:** Not a memory leak — free heap stays constant, but the [largest contiguous block shrinks over weeks](https://hubble.com/community/guides/esp32-memory-fragmentation-why-your-device-crashes-after-running-for-days/). "The free memory is there. It's just been shredded into pieces too small to use." Allocation eventually fails even with plenty of total free RAM.

**What LLM generates:** `malloc()`/`free()` in event loops — textbook correct, but variable-size allocations create [Swiss cheese memory over weeks of continuous operation](https://patternsinthemachine.net/2024/11/the-perils-of-dynamic-memory-in-embedded-systems/).

**What engineer does:**
- Fixed-size memory pools (`k_mem_slab`) — any free block fits any request
- Heap-at-startup-only pattern: allocate during init, never `malloc` at runtime
- Boot-order discipline: permanent allocations first, transient last
- [Stack painting](https://barrgroup.com/blog/top-5-causes-nasty-embedded-software-bugs): fill stack with known pattern at boot, periodically check high-water mark

**Why this is different from "memory optimization":** Memory-opt (Section 3.1, high-risk tier — **67% / 33%** n=3) tests static allocation APIs. This pattern is about runtime behavior over weeks — a temporal dimension LLMs cannot simulate.

### 2.10 Endianness Bugs at Protocol Boundaries

**The knowledge:** Most MCUs (ARM Cortex-M, RISC-V) are little-endian. Network protocols (TCP/IP, Modbus) are big-endian. Sensor registers (I2C/SPI) are often big-endian MSB-first. [Casting pointers across endianness boundaries is "almost always a ticking timebomb."](https://www.embedded.com/introduction-to-endianness/)

**What LLM generates:**
```c
// Read 16-bit temperature from I2C sensor register
uint8_t buf[2];
i2c_read(dev, buf, 2);
int16_t temp = *(int16_t*)buf;  // WRONG on little-endian MCU
                                 // Bytes are swapped, value is garbage
```

**What engineer writes:**
```c
int16_t temp = (buf[0] << 8) | buf[1];  // Explicit MSB-first conversion
// Or: int16_t temp = ntohs(*(uint16_t*)buf);
```

**Where this bites:**
- Sensor registers: I2C/SPI devices transmit MSB-first, MCU stores LSB-first
- Network payloads: `htonl()`/`ntohl()` missing at every serialization boundary
- Modbus TCP: field devices in big-endian, host in little-endian
- Multi-byte struct fields sent over the wire without explicit byte-order conversion
- Cross-platform data sharing: file written on ARM, read on PowerPC

### 2.11 Floating-Point NaN Silently Bypassing Safety Checks

**The knowledge:** [Any comparison involving NaN fails](https://betterembsw.blogspot.com/2012/02/floating-point-comparison-problems.html). If a speed calculation produces NaN (division by zero, numeric underflow), a safety check like `if (speed > MAX_SPEED)` silently passes — the speed limit doesn't trigger. The vehicle keeps accelerating.

**What LLM generates:**
```c
float speed = distance / elapsed_time;  // elapsed_time could be 0.0 → NaN
if (speed > MAX_SPEED) {
    emergency_stop();  // NEVER TRIGGERS when speed is NaN
}
```

**What engineer writes:**
```c
float speed = distance / elapsed_time;
if (isnan(speed) || isinf(speed)) {
    emergency_stop();  // NaN/Inf = fault condition
    report_fault(FAULT_INVALID_COMPUTATION);
    return;
}
if (speed > MAX_SPEED) {
    emergency_stop();
}
```

**Additional considerations:**
- Cortex-M4 FPU has [flush-to-zero and default-NaN modes](https://deepbluembedded.com/stm32-fpu-floating-point-unit-enable-disable/) that change behavior silently
- FPU must be [initialized via CPACR register](https://embeddedprep.com/fpu-warning-fix-fpu-errors/) before any float operation — missing init = UsageFault
- Single-precision FPU silently promotes float→double in expressions without `f` suffix — 100x slower
- Fixed-point arithmetic eliminates NaN entirely — preferred for safety-critical paths

### 2.12 Debug vs Release Build Divergence

**The knowledge:** Code that works in debug (`-O0`) breaks in release (`-O2`). [Memfault calls separate debug/release builds "considered harmful."](https://interrupt.memfault.com/blog/debug-vs-release-builds)

**How this manifests:**
- **printf changes timing:** Serial output at 9600 baud takes thousands of cycles — enough to hide race conditions. Remove printf → race appears. Classic [Heisenbug](https://hubble.com/community/guides/why-debug-and-release-firmware-behave-differently/).
- **Optimizer removes "unnecessary" reads:** Without `volatile`, compiler may cache a value that ISR updates. Works at `-O0` (no optimization), breaks at `-O2`.
- **Different memory layout:** Debug builds have larger stack frames (saved registers, canary gaps). Stack overflow that happens in release never appears in debug.
- **Dead code elimination:** Error handling paths that are "unreachable" in compiler analysis get removed at `-O2`, even if they're reachable via hardware fault.

**What LLM doesn't consider:**
- All testing should be on optimized builds — debug-only testing gives false confidence
- Use runtime log levels, not `#ifdef DEBUG` — keep the same binary
- Compiler sanitizers (`-fsanitize=undefined,address`) catch UB that only surfaces under optimization

### 2.13 C Undefined Behavior: Strict Aliasing and Type Punning

**The knowledge:** LLMs generate `*(struct_t*)byte_buffer` to parse network or sensor data — a [strict aliasing violation](https://blog.regehr.org/archives/959). At `-O0` it works. At `-O2`, TBAA (Type-Based Alias Analysis) lets the compiler assume `float*` and `int*` never point to the same memory, and it [optimizes away the load entirely](https://gist.github.com/shafik/848ae25ee209f698763cffee272a58f8).

**What LLM generates:**
```c
void parse_sensor_data(uint8_t *buf) {
    struct sensor_reading *reading = (struct sensor_reading *)buf;
    // STRICT ALIASING VIOLATION — UB at -O2
    process(reading->temperature, reading->humidity);
}
```

**What engineer writes:**
```c
void parse_sensor_data(uint8_t *buf) {
    struct sensor_reading reading;
    memcpy(&reading, buf, sizeof(reading));  // Safe — compiler optimizes to register move
    process(reading.temperature, reading.humidity);
}
```

**Why this is critical for embedded:**
- ARM Cortex-M0 hard-faults on unaligned access from type punning — not just UB, but crash
- [Safety-critical domains (DO-178C, IEC 62304) cannot certify code with UB](https://accu.org/journals/overload/28/160/anonymous/) — provable correctness requires defined semantics
- Code "works for years" then a compiler update enables a new optimization and it breaks
- MISRA C Rule 11.3 forbids pointer type casts between incompatible types for exactly this reason
- Detection: `-Wstrict-aliasing=2` (GCC), `-fsanitize=undefined` (runtime)

### 2.14 Secure Boot Chain and OTA Integrity

**The knowledge:** LLMs generate OTA update code that downloads and flashes firmware — without the entire [chain of trust](https://promwad.com/news/secure-ota-boot-chains-firmware-verification) that prevents unauthorized or corrupted code from running. Each boot stage must cryptographically verify the next: ROM → bootloader → kernel → application.

**What LLM generates:**
```c
// Download firmware update
http_get(url, firmware_buf, firmware_size);
flash_write(SLOT_1_ADDR, firmware_buf, firmware_size);
sys_reboot();  // Boot into unverified code
```

**What engineer implements:**
```c
// Download with TLS
http_get_tls(url, firmware_buf, firmware_size);

// Verify signature (public key from secure element, not flash)
if (!ecdsa_verify(firmware_buf, firmware_size, public_key, signature)) {
    log_security_event(EVENT_INVALID_SIGNATURE);
    return -EAUTH;
}
// Check version (anti-rollback)
if (get_fw_version(firmware_buf) <= get_current_version()) {
    return -EROLLBACK;
}
// Write to inactive slot (A/B partitioning)
flash_write(inactive_slot, firmware_buf, firmware_size);
// Mark pending, reboot, verify on first boot
mark_pending(inactive_slot);
sys_reboot();
// If first boot fails → automatic revert to active slot
```

**What's missing from LLM output:**
- [Firmware signing](https://promwad.com/news/building-secure-ota-update-pipelines-firmware-integrity-factory-to-field) with RSA/ECDSA (private key in HSM, never on device)
- Anti-rollback version counter (prevents downgrade attacks)
- A/B partitioning with automatic revert on boot failure
- [Hardware root of trust](https://www.analog.com/en/resources/technical-articles/the-fundamentals-of-secure-boot-and-secure-download.html) (secure element for key storage, not flash)
- MCUs have [no ASLR, no DEP](https://runsafesecurity.com/blog/6-risks-ai-code-embedded-systems/) — a buffer overflow = direct code execution with zero mitigation

---

### Summary: Production-Scale Failure Pattern Taxonomy

| # | Category | Example | Time to Manifest | LLM Chance |
|---|----------|---------|-------------------|------------|
| 1 | **Counter overflow** | 49.7-day timer wrap | Days to months | ~0% |
| 2 | **Storage wear** | eMMC death from logging | Months to years | ~0% |
| 3 | **Sensor plausibility** | -40°C in Mexico City as real data | Immediate but rare | ~5% |
| 4 | **Power at scale** | 50ms wake overhead x 500K devices | Cumulative | ~0% |
| 5 | **Radio state corruption** | BLE lockup after 87 days | Weeks to months | ~0% |
| 6 | **Watchdog theater** | WDT fed from ISR, main dead | Random | ~10% |
| 7 | **Crystal aging** | Protocol desync after 2yr in cold | Years | ~0% |
| 8 | **Brownout + flash** | Bricked from write during Tx | Random | ~0% |
| 9 | **Heap fragmentation** | ESP32 crash after weeks of malloc/free | Weeks to months | ~0% |
| 10 | **Endianness** | Sensor data inverted across byte-order boundary | Immediate but subtle | ~5% |
| 11 | **Float NaN bypass** | Safety check silently passes on NaN | Immediate but rare | ~0% |
| 12 | **Debug/Release divergence** | Race condition hidden by printf timing | After optimization | ~5% |
| 13 | **C undefined behavior** | Strict aliasing violation breaks at -O2 | After compiler update | ~0% |
| 14 | **Secure boot / OTA integrity** | Unsigned firmware accepted and executed | Immediate (security) | ~5% |

**These are not edge cases. They are the primary failure modes of mass-deployed embedded products.** Every experienced embedded engineer has war stories for each. LLMs have approximately zero chance of handling them because:

1. **Training data gap:** These patterns live in internal postmortems, not public repositories
2. **No physical context:** LLMs can't know your battery chemistry, crystal spec, flash endurance, or byte order
3. **Time horizon:** LLMs optimize for "demo works today," not "production works for 10 years"
4. **Scale blindness:** A 50ms timing bug is invisible on 1 device but catastrophic on 500,000
5. **Compiler blindness:** LLMs generate code for `-O0` behavior; production runs at `-O2` where UB manifests
6. **Security blindness:** LLMs generate functional code, not hardened code — no chain of trust, no input validation at boundaries

---

## 3. Practical Guidance for Embedded Teams

### 3.1 Risk Zones (Derived from n=3 Benchmark Data)

Rates are **Sonnet / Haiku** pass@1 on the category (n=3 reference run, 233 cases total).

**Critical — both models &lt;50%**

| Category | Sonnet | Haiku | Root cause | Action |
|----------|--------|-------|------------|--------|
| isr-concurrency | 23% | 38% | Implicit gap (M3) + RLHF (M6) | Verify: no blocking, correct sync, barriers |
| threading | 33% | 33% | Complexity + timing | Treat as expert-only |
| dma | 31% | 8% | Datasheet (M1) + silent failure (M2) | Never trust LLM DMA without HW validation |

**High risk — at least one model &lt;50%**

| Category | Sonnet | Haiku | Notes |
|----------|--------|-------|--------|
| memory-opt | 67% | 33% | Large Sonnet–Haiku split |
| storage | 54% | 31% | Both weak; Haiku especially |
| uart | 33% | 67% | Sonnet collapses on UART cases |
| security | 50% | 70% | Sonnet below 50% |

**Moderate — both &gt;50%, at least one &lt;80%**

gpio-basic (67% / 83%), ble (82% / 45%), ota (67% / 58%), kconfig (90% / 60%), power-mgmt (75% / 67%), sensor-driver (75% / 67%), spi-i2c (79% / 64%), linux-driver (70% / 70%), yocto (80% / 70%), timer (83% / 50%)

**Low risk — both &gt;80%**

device-tree (100% / 100%), pwm (100% / 100%), boot (90% / 100%)

**Still review:** Error paths on complex init (qualitative), and any category where **stability** is low (Haiku 73.0% vs Sonnet 87.1% case-level consistency across the 3 runs).

### 3.2 What LLMs ARE Good At

Sonnet / Haiku pass@1 by category (n=3 reference run). Strong does not mean “ship without review.”

| Task | Sonnet | Haiku | Why it works |
|------|--------|-------|--------------|
| Kconfig fragments | 90% | 60% | Pattern-matching, abundant training data |
| Device tree overlays | 100% | 100% | Structured syntax, well-represented |
| Sensor driver boilerplate | 75% | 67% | Formulaic driver patterns |
| BLE service scaffolding | 82% | 45% | Common tutorial topic — Haiku still unreliable |
| Yocto recipes | 80% | 70% | Structured build metadata |
| Watchdog basic config | 90% | 60% | Simple recurring pattern |
| MCU boot flow | 90% | 100% | Often board-init / image layout boilerplate |
| OTA patterns | 67% | 58% | Functional drafts common; rollback / signing still human-owned |

### 3.3 Three-Tier Trust Model (n=3)

**Trust (≥90% both)** — light syntax/config review; still run your pipeline.

- device-tree **100% / 100%**, pwm **100% / 100%**

**Verify (mandatory review; Sonnet-usable band)** — run the full static → build → sim path. *Strict “&gt;60% both” is not met for kconfig (Haiku 60%) and BLE (Haiku 45%); they remain here because Sonnet is strong and both need the same review gates.*

- networking **75% / 75%**, linux-driver **70% / 70%**, boot **90% / 100%**, kconfig **90% / 60%**, ble **82% / 45%**, yocto **80% / 70%**, power-mgmt **75% / 67%**, sensor-driver **75% / 67%**, spi-i2c **79% / 64%**, ota **67% / 58%**, gpio-basic **67% / 83%**

**Never trust (&lt;60% for either model)** — treat as draft only; expert ownership.

- threading **33% / 33%**, isr-concurrency **23% / 38%**, dma **31% / 8%**, memory-opt **67% / 33%**, storage **54% / 31%**, security **50% / 70%**, timer **83% / 50%**, uart **33% / 67%**, adc **100% / 50%**

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

- Sonnet > Haiku by **11.1%p** overall pass@1 (n=3 mean: **68.0%** vs **56.9%**); 95% CIs do not overlap
- **Stability** (same outcome 3/3 runs): Sonnet **87.1%** of cases vs Haiku **73.0%** — smaller model is flakier even when mean score is acceptable
- Gains are mostly Level 1–2 style API exposure; Level 3–4 (barriers, cache, cleanup) still collapses for both
- Sonnet still **regresses vs Haiku on individual cases** — bigger is not uniformly better
- Bottleneck is missing context and structural generation bias, not raw model size

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
│     Catches L0 failures (~26% of pooled failures, n=3)          │
│                                                                  │
│  4. BUILD (Toolchain: -Wall -Werror)                             │
│     Catches L1 failures (~22%)                                   │
│                                                                  │
│  5. RUNTIME (QEMU/simulator)                                     │
│     Catches L2 failures (~18%). Misses real HW issues.           │
│                                                                  │
│  6. EXPERT REVIEW (Human)                                        │
│     Focus: Verify + Never-trust tiers. Catches L3 (~34%).        │
│     The layer where LLMs fail silently.                          │
│                                                                  │
│  7. HARDWARE TEST (Board)                                        │
│     DMA cache, timing, peripherals. Stress 24hr+.               │
│     No simulator replaces this for production code.              │
└──────────────────────────────────────────────────────────────────┘
```

### 3.7 The Bottom Line

**n=3 aggregate (233 cases):** Haiku 4.5 pass@1 **56.9%** (95% CI [53.2%, 60.6%]; per-case stability **73.0%**). Sonnet 4.6 **68.0%** ([64.4%, 71.3%]; stability **87.1%**). **Gap: 11.1%p** — confidence intervals do not overlap, so the lift is not explained by a single lucky run.

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

## 4. Meta-Evaluation: Benchmark Limitations and Self-Critique

### 4.1 Critical Self-Analysis

An honest assessment of EmbedEval's limitations, evaluated from both embedded expert and LLM benchmark expert perspectives.

**Show-stoppers:**
- **S1. No compilation.** L1/L2 are disabled. Calling regex pattern matching "behavioral check" is overclaiming. True behavioral evaluation requires QEMU execution + ThreadSanitizer + timing measurement.
- **S2. Residual stochasticity.** Headline Haiku/Sonnet scores now use **n=3** means with Wilson CIs, but **small categories** (e.g., 2–3 cases) still swing ~10%p per flip — always read category tables with *n* in mind.

**Major limitations:**
- **M1. Construct validity:** "Embedded capability" ≠ "API recall." When explicit prompts yield 95% and implicit 60%, we're measuring prompt-following, not domain knowledge.
- **M2. Platform bias:** Zephyr dominates (>90%). Calling this an "Embedded benchmark" is generous — "Zephyr RTOS benchmark" is more accurate.
- **M3. No human baseline:** Is ~68% good or bad? Without a junior engineer comparison, absolute scores are uninterpretable.
- **M4. Prompt sensitivity:** Rephrasing prompts changes scores — a robust benchmark should tolerate reasonable variation.
- **M5. Toy complexity:** Single-file, ~50-line problems. Real projects are multi-module, multi-thousand-line systems.

**Moderate limitations:**
- **D1. Binary scoring:** 9/10 checks passed = FAIL. No partial credit.
- **D2. Check precision unvalidated:** Intentional wrong answers were not systematically tested (negative testing).
- **D3. Contamination risk:** Public repo with reference solutions.
- **D4. Single evaluator bias:** All TCs/checks from one perspective.

**Honest positioning:**

| Overclaim | Honest Alternative |
|-----------|-------------------|
| "Embedded Last Exam" | "Zephyr RTOS Code Generation Benchmark" |
| "Behavioral evaluation" | "Static pattern heuristics" |
| "pass@1 = 91%" | "pass@1 = 68% (Sonnet n=3 mean); single-shot runs overstate precision" |
| "LLM embedded capability" | "API recall + safety pattern awareness" |

### 4.2 Check Precision: 40% on Subtle Mutations

Static heuristic checks catch trivial mutations (code removal: 100%) but miss subtle, bypass-style bugs:

```
Trivial mutations (code removal):     20/20 caught (100%)
Subtle mutations (check bypass):       6/15 caught  (40%)
Blind spots:                           9/15          (60%)
```

**Categories of blind spots:**
| Type | Example | Risk | Root Cause |
|------|---------|------|------------|
| **Location-agnostic keyword** | `volatile` on wrong variable → PASS | High | `"volatile" in code` matches anywhere |
| **Substring bypass** | `__copy_to_user` passes `copy_to_user` check | Critical | Substring matching |
| **Behavior unchecked** | Error detected but no return → continues | High | Presence check, not action check |
| **Missing deny-list entry** | `irq_lock` used — not in mutex deny list | High | Deny lists are always incomplete |
| **Partial satisfaction** | 2/3 cleanup steps done → PASS | High | OR logic instead of AND |

**Structural limitation:** Presence checks (does `volatile` exist?) are fundamentally different from semantic checks (is `volatile` on the correct variable?). Behavioral verification requires execution.

### 4.3 Competitive Positioning

| | HumanEval | SWE-bench | LiveCodeBench | EmbedBench (ICSE'26) | **EmbedEval** |
|---|---|---|---|---|---|
| Evaluation | assert exec | pytest exec | exec+predict | Wokwi simulator | **regex patterns** |
| Code execution | Yes | Yes | Yes | Yes | **No** |
| Contamination prevention | None | Large-scale | Temporal cutoff | HW combinations | **48 private TCs** |
| TC count | 164 | 2,294 | 1,055 | 126 | **233** |
| Top pass@1 | ~97% | ~75% | ~65% | 55.6% | **68.0%** (Sonnet 4.6, n=3 mean) |

**Additional related benchmarks (2026)**

| Benchmark | Focus | Reference |
|-----------|-------|-----------|
| InCoder-32B + EmbedCGen | Embedded C code generation evaluation | [arXiv:2603.16790](https://arxiv.org/abs/2603.16790) |
| MobileKernelBench | Mobile / embedded kernel benchmarks | [arXiv:2603.09292](https://arxiv.org/abs/2603.09292) |

**EmbedEval's unique contributions:**
1. **Implicit Knowledge Gap (35%p)** — no other benchmark measures this
2. **Embed Gap metric** — cross-benchmark comparison vs HumanEval
3. **Check precision self-evaluation (40%)** — quantified benchmark limitations
4. **4-Level Implicit Knowledge Model** (C → RTOS → HW → Safety)
5. **Cross-platform hallucination detection** — systematic API confusion tracking

**Where EmbedEval trails:**
1. No code execution (all competitors execute)
2. Inflated pass@1 vs execution-heavy benches (68% vs EmbedBench 55.6% with simulator) — still not apples-to-apples
3. Weaker contamination prevention than LiveCodeBench temporal cutoff
4. Single-shot only — no compiler feedback or agent iteration

**Honest framing:** EmbedEval is a "LLM Embedded Domain Knowledge Probe" — it measures whether LLMs possess embedded domain knowledge, not whether code actually works. This is meaningful because domain knowledge probing does not require execution.

---

## Sources

### Field Incidents & Production Failures
- [Zephyr OpenThread 49-day overflow](https://github.com/zephyrproject-rtos/zephyr/issues/41509)
- [ESPHome 49-day sensor freeze](https://github.com/esphome/issues/issues/826)
- [LoRaWAN timer overflow](https://github.com/Lora-net/LoRaMac-node/issues/1016)
- [STM32 HAL uwTick overflow](https://community.st.com/t5/stm32-mcus-embedded-software/what-happens-when-the-32bit-hal-uwtick-timer-variable-overflows/td-p/120367)
- [Tesla eMMC wear failure](https://www.cnx-software.com/2019/08/16/wear-estimation-emmc-flash-memory/)
- [TI CC2642R BLE stack crash](https://e2e.ti.com/support/wireless-connectivity/bluetooth-group/bluetooth/f/bluetooth-forum/771568/)
- [Nordic nRF52840 SPI-BLE interference](https://devzone.nordicsemi.com/f/nordic-q-a/106208/)
- [STM32WB55 BLE connection blocking](https://community.st.com/t5/stm32-mcus-wireless/ble-central-connection-timeout-with-sleeping-peer-device-is-not/td-p/702755)
- [ESP32 heap fragmentation crash](https://hubble.com/community/guides/esp32-memory-fragmentation-why-your-device-crashes-after-running-for-days/)

### Best Practices & Engineering References
- [Jack Ganssle — Watchdog Timers](https://www.ganssle.com/watchdogs.htm)
- [Memfault — Watchdog Best Practices](https://interrupt.memfault.com/blog/firmware-watchdog-best-practices)
- [Memfault — Debug vs Release Builds Considered Harmful](https://interrupt.memfault.com/blog/debug-vs-release-builds)
- [Memfault — Defensive Programming](https://interrupt.memfault.com/blog/defensive-and-offensive-programming)
- [Watchdog Anti-Patterns](https://www.embeddedrelated.com/showarticle/1276.php)
- [Barr Group — Top 5 Nasty Embedded Bugs](https://barrgroup.com/blog/top-5-causes-nasty-embedded-software-bugs)
- [Perils of Dynamic Memory in Embedded Systems](https://patternsinthemachine.net/2024/11/the-perils-of-dynamic-memory-in-embedded-systems/)
- [Why Not Use Dynamic Memory in Embedded](https://electrical.codidact.com/posts/286121)
- [LittleFS — Flash-safe filesystem](https://github.com/littlefs-project/littlefs)
- [Kingston eMMC lifecycle](https://www.kingston.com/en/blog/embedded-and-industrial/emmc-lifecycle)

### Hardware-Specific Knowledge
- [Crystal Oscillator Aging](https://www.fujicrystal.com/news_details/crystal-oscillator-aging.html)
- [Crystal Temperature Drift](https://blog.mbedded.ninja/electronics/components/crystals-and-oscillators/)
- [Brownout Reset Analysis](https://www.embedded.com/brown-out-reset/)
- [Endianness Introduction](https://www.embedded.com/introduction-to-endianness/)
- [Float Comparison Problems](https://betterembsw.blogspot.com/2012/02/floating-point-comparison-problems.html)
- [STM32 FPU Enable/Disable](https://deepbluembedded.com/stm32-fpu-floating-point-unit-enable-disable/)
- [FPU Warning Fix Guide](https://embeddedprep.com/fpu-warning-fix-fpu-errors/)
- [GPIO Leakage & Power Optimization](https://dojofive.com/blog/power-optimization-techniques-for-firmware/)
- [Battery Power Efficiency](https://www.analog.com/en/resources/technical-articles/greatly-improve-battery-power-efficiency-for-iot-devices.html)
- [Low-Power RTOS Techniques](https://www.embeddedrelated.com/showarticle/1667.php)

### C Language & Compiler Behavior
- [John Regehr — Type Punning, Strict Aliasing, and Optimization](https://blog.regehr.org/archives/959)
- [ACCU — Strict Aliasing Rule](https://accu.org/journals/overload/28/160/anonymous/)
- [Strict Aliasing Reference (GitHub)](https://gist.github.com/shafik/848ae25ee209f698763cffee272a58f8)
- [Debug vs Release Build Divergence](https://hubble.com/community/guides/why-debug-and-release-firmware-behave-differently/)

### Security & OTA
- [Secure OTA Update Pipelines](https://promwad.com/news/building-secure-ota-update-pipelines-firmware-integrity-factory-to-field)
- [Secure Boot Chain & Firmware Verification](https://promwad.com/news/secure-ota-boot-chains-firmware-verification)
- [Secure Boot Fundamentals (Analog Devices)](https://www.analog.com/en/resources/technical-articles/the-fundamentals-of-secure-boot-and-secure-download.html)
- [6 Risks of AI Code in Embedded Systems (RunSafe)](https://runsafesecurity.com/blog/6-risks-ai-code-embedded-systems/)

### Safety Standards
- [IEC 61508 Fault Detection](https://risknowlogy.com/articles/detail/17305/)
- [ISO 26262 Software Architectural Design](http://embeddedinembedded.blogspot.com/)

### Academic Papers
- [arXiv:2603.11139 — H2LooP](https://arxiv.org/abs/2603.11139) — 7B continual pretraining for hardware-aware code generation
- [arXiv:2603.16790 — InCoder-32B + EmbedCGen](https://arxiv.org/abs/2603.16790) — embedded code generation benchmark suite
- [arXiv:2603.09292 — MobileKernelBench](https://arxiv.org/abs/2603.09292) — mobile / embedded kernel evaluation
- [arXiv:2503.09061 — LLM-FSM](https://arxiv.org/abs/2503.09061) — bridging LLM code to formal verification (FSM extraction)
- [arXiv:2503.11901 — SpecMap](https://arxiv.org/abs/2503.11901) — datasheet-to-code traceability / spec alignment
- [arXiv:2404.07732 — VulInstruct](https://arxiv.org/abs/2404.07732) — implicit security specifications mined from CVEs
- [arXiv:2509.09970 — Securing LLM-Generated Embedded Firmware](https://arxiv.org/abs/2509.09970) (92.4% vulnerability remediation)
- [arXiv:2601.13864 — HardSecBench: Security Awareness of LLMs for HW Code](https://arxiv.org/abs/2601.13864)
- [arXiv:2603.19583 — IoT-SkillsBench: Skilled AI Agents for Embedded/IoT](https://arxiv.org/abs/2603.19583)
- [arXiv:2503.15554 — Rethinking Evaluation of Secure Code Generation (ICSE'26)](https://arxiv.org/abs/2503.15554)

### EmbedEval Project
- [LLM-EMBEDDED-FAILURE-FACTORS.md](./LLM-EMBEDDED-FAILURE-FACTORS.md) (42-factor taxonomy + 19 non-code factors)
- [BENCHMARK-COMPARISON-2026-04-05.md](./BENCHMARK-COMPARISON-2026-04-05.md) (test data)
