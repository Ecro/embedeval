# Token Scaling in Embedded Development: Why Infinite Tokens Aren't Enough

In general software, investing unlimited LLM tokens can almost automatically
achieve quality, features, and market dominance. In embedded, it can't. This
document structurally analyzes why, and presents strategies for embedded
development teams to optimize their token investment.

**Companion documents:**
- [LLM-EMBEDDED-FAILURE-FACTORS.md](LLM-EMBEDDED-FAILURE-FACTORS.md) — WHERE LLMs fail (42 code factors, diagnostic)
- [LLM-EMBEDDED-CONSIDERATIONS.md](LLM-EMBEDDED-CONSIDERATIONS.md) — WHY they fail at production scale (14 patterns, analytical)
- [LLM-EMBEDDED-DEVELOPMENT-GUIDE.md](LLM-EMBEDDED-DEVELOPMENT-GUIDE.md) — HOW to use LLMs (7-phase workflow, tactical)
- **→ This document** — THE ECONOMICS of token investment (strategic/architectural)

**Version:** 1.0 (2026-04-07)
**Evidence:** EmbedEval benchmark data (Haiku 4.5 vs Sonnet 4.6, 227 TCs), 15+ arXiv papers (2024-2026)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Token-Scaling Model for General Software](#2-the-token-scaling-model-for-general-software)
3. [The Physical Ceiling: Why Embedded Is Fundamentally Different](#3-the-physical-ceiling-why-embedded-is-fundamentally-different)
4. [5-Layer Verification Map: Where Tokens Work and Where They Don't](#4-5-layer-verification-map-where-tokens-work-and-where-they-dont)
5. [The Feedback Loop Gap: 5 Broken Links in Embedded](#5-the-feedback-loop-gap-5-broken-links-in-embedded)
6. [Where Token Investment Pays Off (The Digital 70%)](#6-where-token-investment-pays-off-the-digital-70)
7. [Where Tokens Are Powerless (The Physical 30%)](#7-where-tokens-are-powerless-the-physical-30)
8. [The Speed Mismatch Trap](#8-the-speed-mismatch-trap)
9. [Bridge Technologies: Raising the Ceiling](#9-bridge-technologies-raising-the-ceiling)
10. [Optimal Workflow Architecture](#10-optimal-workflow-architecture)
11. [General SW vs Embedded: Full Comparison](#11-general-sw-vs-embedded-full-comparison)
12. [Practical Guide for Development Teams](#12-practical-guide-for-development-teams)
13. [Open Questions and Future Research](#13-open-questions-and-future-research)
14. [Sources](#14-sources)

---

## 1. Executive Summary

### The Core Formula

```
Q(general_sw) ∝ log(tokens)                                 — no ceiling, logarithmic diminishing returns
Q(embedded)   = min(Q_digital(tokens), Q_physical_ceiling)   — hard physical ceiling exists
```

### Three-Sentence Summary

1. In **general software**, investing unlimited tokens enables a **fully automated loop** — generate code → test → fix → deploy → collect user feedback → regenerate — where quality improves proportionally to token investment.

2. In **embedded**, only about **70% of this loop is automatable**. The remaining 30% — real-time timing, EMC, manufacturing variance, environmental testing, safety certification — requires physical-world interaction and **cannot be replaced by tokens**.

3. The winning strategy in embedded is not spending the most tokens, but **building the best bridge between the digital token world and the physical non-tokenizable world** — Digital Twins, HIL-as-a-Service, datasheet RAG, formal verification.

### Summary Table

| Dimension | General SW | Embedded |
|-----------|-----------|----------|
| Automatable testing | ~95% | ~50-60% |
| Token scaling ceiling | None | ~70-80% of total quality |
| Feedback loop speed | Seconds to minutes | Minutes to days (SW), weeks to months (HW) |
| Deployment automation | ~100% | ~30-50% |
| Rollback cost | Near-zero | Moderate to catastrophic |

---

## 2. The Token-Scaling Model for General Software

### 2.1 The Closed Digital Feedback Loop

LLM-driven autonomous development works for general software because **every step of the feedback loop is digital**.

```
Requirements → Code Gen → Test → Fix → Deploy → User Feedback → New Requirements
      ↑                                                               ↓
      └──────────── All digital, all automatable, seconds to minutes ─┘
```

**Six enabling conditions:**

| Condition | General SW Status | Why Tokens Work |
|-----------|------------------|----------------|
| Verification is digital | Unit tests, integration tests, E2E — all software | 1 iteration = milliseconds |
| Deployment is digital | `git push` → CI → container → production | Minutes to deploy |
| Feedback is digital | Error logs, analytics, user reports — machine-readable | Auto-triage possible |
| Environment is reproducible | Docker containers = identical environments | Deterministic testing |
| Rollback is instant | Seconds to roll back on failure | Risk minimized |
| No physical consequences | Bad code = wrong screen, no danger | Cost of experimentation = 0 |

### 2.2 Test-Time Compute Scaling Research

That token investment improves quality is not theory — it's validated research.

| Paper | Key Finding | Implication |
|-------|------------|-------------|
| Scaling LLM Test-Time Compute (arXiv 2408.03314) | "Optimally scaling inference-time compute is more effective than **14x** model parameter scaling" | More inference beats bigger models |
| S*: Test Time Scaling for Code (arXiv 2502.14382) | Non-reasoning models surpass reasoning models via test-time scaling | Token volume = quality |
| Thinking Longer, Not Larger (arXiv 2503.23803) | SWE-SynInfer+: adding a patch verification phase improves performance | Iterative verification is key |
| CodeMonkeys (arXiv 2501.14723) | Test-time compute scaling demonstrated for software engineering tasks | Applies to code generation |

**Scaling curve:**

```
Token Investment      →  General SW Quality
$100 (1 iteration)    →  Working MVP
$1K (10 iterations)   →  Production-ready
$10K (100 iterations) →  Edge cases + polish
$100K (1000 iter.)    →  Enterprise-grade
                          ↑ No ceiling — continues improving at log scale
```

### 2.3 The Autonomous Agent Ecosystem

As of 2025-2026, LLM coding agents autonomously perform multi-file changes, run tests, and iteratively fix code.

- **Anthropic research:** Claude Code users' auto-approve rate increases from 20% → 40% with experience (750 sessions)
- **Self-Organizing Multi-Agent Systems** (arXiv 2603.25928): Multi-agent coordination for continuous SW development
- **ALMAS** (arXiv 2510.03463): Sprint Agent → Code Agent → Peer Agent autonomous pipeline
- **Self-evolving agents** (EvoAgentX): Learning from past experience for continuous improvement

In this ecosystem, the human role shrinks to **defining requirements, specs, and test cases** — everything else is replaced by tokens. In general software, this is already reality.

---

## 3. The Physical Ceiling: Why Embedded Is Fundamentally Different

### 3.1 The Ceiling Function

```
Q(embedded) = min(Q_digital(tokens), Q_physical_ceiling)
```

Q_physical_ceiling is determined by:

1. **Hardware verification fidelity** — What percentage of real behavior can the emulator reproduce?
2. **Timing determinism** — Can the emulator reproduce real-time behavior?
3. **Peripheral coverage** — Are all HW interfaces simulated?
4. **Environmental factors** — Can EMI, temperature, and power supply noise be reproduced digitally?

**No matter how many tokens you invest, you cannot exceed Q_physical_ceiling.** This is the fundamental difference from general software.

### 3.2 Scaling Curve Comparison

```
        Quality
        ↑
   100% ┤                          ┌─── General SW (no ceiling, log diminishing)
        │                       ╱
    90% ┤                    ╱
        │                 ╱
    80% ┤ ─ ─ ─ ─ ─ ─╱─ ─ ─ ─ ─ ─ ─ ── Physical ceiling (embedded)
        │           ╱ ═══════════════════ Embedded (plateaus at ceiling)
    70% ┤        ╱═╱
        │      ╱═╱
    60% ┤   ╱═╱
        │ ╱═╱
    50% ┤╱═╱
        │╱
    40% ┤
        └────────────────────────────────── Token Investment →
          $100    $1K    $10K   $100K   $1M
```

### 3.3 Why the Ceiling Exists: Knowledge LLMs Cannot Access

As detailed in [LLM-EMBEDDED-CONSIDERATIONS.md §1.2](./LLM-EMBEDDED-CONSIDERATIONS.md), information outside the LLM's knowledge boundary determines the ceiling.

| Missing Context | Contents | Why LLM Can't Have It | Impact on Generated Code |
|----------------|---------|----------------------|-------------------------|
| **Datasheet** | Register maps, timing diagrams, init sequences | Proprietary PDFs, 100-500 pages | Root cause of DMA 0-44% |
| **Schematic** | Pin connections, voltage levels, pull-ups | Board-specific, never in code repos | Pin configuration errors |
| **Silicon errata** | Chip-revision bugs and workarounds | Vendor-specific proprietary docs | Works on Rev A, fails on Rev B |
| **Runtime state** | Memory layout, stack depth, ISR nesting | Observable only with debugger/oscilloscope | Optimistic stack sizes, no jitter margin |
| **System architecture** | Task dependencies, IPC topology | Team docs / architect's head | Module works alone, breaks during integration |
| **Field history** | Production failure modes over years | Internal incident DBs, customer reports | No wear compensation, no tolerance handling |

### 3.4 The Four Levels of Implicit Knowledge

LLM performance by knowledge level, confirmed by EmbedEval benchmark data:

```
Level 1: C Language Knowledge          ← Sonnet ~95%, Haiku ~80%
  volatile, const, named constants, goto cleanup

Level 2: RTOS Knowledge               ← Sonnet ~85%, Haiku ~65%
  ISR blocking forbidden, spinlock vs mutex, K_NO_WAIT

Level 3: Hardware Knowledge            ← Sonnet ~60%, Haiku ~30%
  Cache alignment ≥32, flush/invalidate, timing margins

Level 4: System Safety Knowledge       ← Sonnet ~50%, Haiku ~30%
  OTA rollback, reverse cleanup, fail-fast, conditional WDT feed
```

**Levels 1-2** are abundant in training data (C textbooks, RTOS tutorials).
**Levels 3-4** exist primarily in datasheets, internal docs, and experienced engineers' heads — **outside the LLM's knowledge boundary**.

No matter how many tokens you invest, Levels 3-4 knowledge will not improve **unless provided as context**.

---

## 4. 5-Layer Verification Map: Where Tokens Work and Where They Don't

Analyzing EmbedEval's 5-layer evaluation architecture from an automation perspective.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Layer      │ Description                │ Automatable │ Token Effect │ Time │
├─────────────────────────────────────────────────────────────────────────────┤
│ L0 Static  │ Pattern matching, headers   │ 100%       │ ◉◉◉◉◉      │ ms   │
│ L1 Compile │ Docker-based SDK build      │ ~90%       │ ◉◉◉◉○      │ 30-120s │
│ L2 Runtime │ QEMU/native_sim execution   │ ~50%       │ ◉◉◉○○      │ min  │
│ L3 Behav.  │ Output pattern validation   │ ~30%       │ ◉◉○○○      │ min-hr │
│ L4 Phys.   │ Real HW, stress testing     │ ~5%        │ ◉○○○○      │ hr-day │
├─────────────────────────────────────────────────────────────────────────────┤
│ L5 Env*    │ EMC, temperature, vibration │  0%        │ ○○○○○      │ day-wk │
│ L6 Cert*   │ ISO 26262, IEC 61508       │  0%        │ ○○○○○      │ wk-mo │
│ L7 Field*  │ Long-term ops, wear, aging  │  0%        │ ○○○○○      │ mo-yr │
└─────────────────────────────────────────────────────────────────────────────┘
 * L5-L7 are outside EmbedEval scope but essential for real products
```

### Failure Distribution by Layer from EmbedEval Data

| Layer | Haiku Failures | Sonnet Failures | Solvable by Token Scaling? |
|-------|---------------|----------------|--------------------------|
| L0 (Static) | 27 | 9 | **YES** — more iterations + compiler feedback improves this |
| L1 (Build) | 15 | 7 | **YES** — SDK error message feedback enables fixes |
| L2 (Runtime) | 6 | 13 | **PARTIAL** — only within emulator scope |
| L3 (Behavioral) | 15 | 13 | **LIMITED** — safety patterns require context injection |

**Key insight:** Scaling from Haiku to Sonnet dramatically improves L0/L1 (42→16), but L2/L3 barely changes (21→26). **Model size (= more training tokens) does not solve problems above the physical ceiling.**

---

## 5. The Feedback Loop Gap: 5 Broken Links in Embedded

Five points where the general-SW autonomous loop breaks down in embedded:

### 5.1 Code Generation (Degraded but Improvable)

| Comparison | General SW | Embedded |
|------------|-----------|----------|
| Training data | Abundant (Python/JS/Java) | Sparse (embedded C = tiny fraction of GitHub) |
| Best pass@1 | ~97% (HumanEval) | 55.6% (EmbedAgent), 80% (EmbedEval) |
| RAG effectiveness | Moderate | **High** — EmbedAgent: 29.4% → 65.1% (+35.7%p) |
| Compiler feedback effect | Moderate | **High** — error messages are specific and actionable |

**For teams:** To maximize token ROI in embedded code generation, **datasheet RAG + compiler feedback loops** are essential. Prompts alone hit a low ceiling.

### 5.2 Test-Fix Inner Loop (Much Slower + Limited Scope)

| Step | General SW | Embedded |
|------|-----------|----------|
| Unit test execution | Milliseconds | L0/L1: 30-120s (west build) |
| Integration tests | Seconds | L2: Minutes (QEMU boot + run) |
| System tests | Minutes | L3-L4: Hours (real HW required) |
| Coverage | ~95% of code paths | ~50% (emulator can't reproduce all peripherals) |

**EmbedEval experience:**
- `native_sim` has no DMA/WDT/sensor nodes → L2 testing impossible for these categories
- QEMU timing is non-deterministic → real-time tests are meaningless
- west build error messages are useful → compiler feedback loop works well

**One test-fix cycle:** General SW ≈ seconds, Embedded ≈ minutes to hours. Same token budget yields **10-100x fewer iterations**.

### 5.3 Deployment (Fundamentally Different)

| Comparison | General SW | Embedded |
|------------|-----------|----------|
| Deployment mechanism | Container → cloud | Firmware flash (physical devices) |
| OTA possible | Always (web deploy) | Some (bandwidth, battery, brick risk) |
| Canary deploy | Route 5% of traffic | **Impossible** — you can't route electrons through different firmware |
| Rollback | One command, seconds | Dual-bank architecture required (many devices lack it) |
| Risk | User sees wrong screen | **Physical damage**, safety incidents, product recalls |
| Regulation | Low (except medical/financial) | **High** — ISO 26262, IEC 61508, DO-178C |

### 5.4 User Feedback (Slow, Noisy, Physical)

| Comparison | General SW | Embedded |
|------------|-----------|----------|
| Error reporting | Stack traces, crash dumps, auto-collected | "It doesn't work" — no reproducible environment |
| Debugging tools | Logs, APM, remote debuggers | JTAG, oscilloscope, logic analyzer — **physical** |
| Reproducibility | High (identical environments) | Low (intermittent, temperature-dependent, timing-dependent) |
| Environmental factors | None | EMI, voltage fluctuation, manufacturing variance |

**Example:** The 87-day radio lockup from [CONSIDERATIONS.md §2.5](./LLM-EMBEDDED-CONSIDERATIONS.md) — a BLE stack counter overflow that only occurs after 87 days. No digital test can reproduce this.

### 5.5 Feedback → Token Conversion (Very Limited)

| Step | General SW | Embedded |
|------|-----------|----------|
| Bug report → test generation | Fully automatable | Only L0/L1 tests automatable |
| Fix simulation | Fully possible | Partial (QEMU-supported platforms only) |
| Real HW validation | Unnecessary | **Required** — physical access needed |
| Auto-deploy fix | Immediate | **Risky** — certification may be required |

**Conclusion:** The general-SW "autonomous feedback → tokens → improvement" cycle is **10-100x slower and partially manual** in embedded.

---

## 6. Where Token Investment Pays Off (The Digital 70%)

Below the ceiling, tokens deliver high ROI. **Embedded teams should concentrate tokens here.**

### 6.1 Code Generation (ROI: ◉◉◉◉◉)

| Strategy | Effect | Evidence |
|----------|--------|---------|
| Compiler feedback loop | Dramatic L0/L1 failure reduction | EmbedAgent: +35.7%p |
| Datasheet RAG | Closes implicit knowledge gap | EmbedEval: explicit → 95%, implicit → 60% → RAG can reach 80%+ |
| Multi-pass generation | Select highest-quality code | S* (arXiv 2502.14382): increasing k in pass@k = quality increase |
| SDK example injection | Correct API pattern learning | EmbedEval: kconfig 75-88%, yocto 88-100% |

**Practical application:**
```
Prompt: "Implement SPI DMA transfer in Zephyr"
→ Step 1: Extract DMA register map from datasheet, inject as context
→ Step 2: Inject SDK example code (samples/drivers/spi)
→ Step 3: LLM code generation (3-5 generations, select best)
→ Step 4: west build error feedback → auto-fix (3 iterations)
→ Step 5: Static analysis feedback → auto-fix
```

### 6.2 Static Analysis (ROI: ◉◉◉◉◉)

LLMs can perform unlimited passes of static analysis. EmbedEval's L0 checks are this domain.

| Analysis Pattern | Detection Target | EmbedEval Example |
|-----------------|-----------------|-------------------|
| ISR forbidden API scan | Blocking/allocating calls in ISR | isr-concurrency-002: printk_in_isr |
| volatile/atomic missing | Shared variable memory model violation | timer, threading categories |
| Cross-platform API mixing | FreeRTOS/Arduino/STM32 APIs in Zephyr code | esp-gpio-001, stm32-spi-001 |
| Error path cleanup | Reverse-order resource release missing | linux-driver-006: error_path_cleanup |
| Cache coherency | Missing DMA flush/invalidate | dma-003, dma-009 |
| MISRA C rules | Safety coding standard violations | security category |

**Token strategy:** Multi-agent analysis — each agent specializes in a different pattern set.

```
Agent 1: ISR safety checks
Agent 2: Memory model (volatile, barrier, cache) checks
Agent 3: Error path + resource lifetime checks
Agent 4: Cross-platform API + forbidden pattern checks
Agent 5: MISRA / CERT C rule checks
→ Aggregate results → Priority sort → Auto-fix or human review
```

### 6.3 Test Case Generation (ROI: ◉◉◉◉○)

| Strategy | Effect | Limitation |
|----------|--------|-----------|
| Mass unit test generation | Maximize code coverage | Valid only within emulator scope |
| Automated edge case discovery | Boundary values, overflows, NULL inputs | Cannot detect timing-related edge cases |
| Mutation test generation | Check precision verification | EmbedEval L4 mutations: only 40% of subtle variants caught |
| Fuzz scenario generation | Protocol/parser inputs | Physical bus timing not reproducible |

### 6.4 Code Review (ROI: ◉◉◉◉○)

arXiv 2509.09970 demonstrated **92.4% vulnerability remediation through agent-driven iterative validation + patching**.

| Review Type | Detection Target | Token Effect |
|------------|-----------------|-------------|
| Security audit | CWE patterns, buffer overflows, race conditions | High — multi-pass improves detection rate |
| Safety review | ISR violations, WDT theater, error paths | High — CONSIDERATIONS.md 14 patterns as checklist |
| Architecture review | Task structure, IPC correctness, memory budget | Medium — when context provided |

### 6.5 Design Space Exploration (ROI: ◉◉◉○○)

LLMs can explore architectural alternatives faster than humans.

| Exploration Area | Example | Token Strategy |
|-----------------|---------|---------------|
| RTOS primitive selection | k_msgq vs k_fifo vs k_pipe | Generate trade-off analysis for each |
| Memory allocation | Stack vs heap vs static allocation | Explore optimal allocation within constraints |
| Power strategy | Sleep mode selection, wake sources | Battery life calculation + alternative comparison |
| DMA vs PIO | Throughput/latency trade-offs | Generate quantitative comparison table |

### 6.6 Configuration Optimization (ROI: ◉◉◉○○)

EmbedEval data shows Kconfig/DT have the highest pass@1 — rule-based with abundant training data.

| Area | Haiku pass@1 | Sonnet pass@1 | Token Strategy |
|------|-------------|--------------|---------------|
| Kconfig | 75% | 88% | Auto-explore dependency chains, generate minimal configs |
| Device Tree | 88% | 100% | Auto-generate compatible nodes from DT bindings |
| Yocto recipes | 88% | 100% | Learn existing recipe patterns + auto-generate |

### 6.7 Documentation (ROI: ◉◉○○○)

| Artifact | Token Strategy | Value |
|----------|---------------|-------|
| HAL documentation | Code → API docs auto-generation | Accelerate team onboarding |
| Test plans | Requirements → verification matrix | Foundation for certification docs |
| Architecture docs | Code → task/IPC diagrams | Support design reviews |

---

## 7. Where Tokens Are Powerless (The Physical 30%)

This 30% contains the most dangerous bugs. Most of the 14 production-scale failure patterns from [CONSIDERATIONS.md §2](./LLM-EMBEDDED-CONSIDERATIONS.md) fall in this domain.

### 7.1 Real-Time Timing Verification

- QEMU does not reproduce real-time timing behavior
- Jitter, WCET (worst-case execution time), interrupt latency — measurable only on real HW
- Investing $1M in tokens still cannot verify WCET
- **Required equipment:** Oscilloscope, logic analyzer

**Real-world example:** When timer period equals WDT timeout, it works 99% of the time but causes random resets due to jitter — [CONSIDERATIONS.md §2.6 "Watchdog Theater"](./LLM-EMBEDDED-CONSIDERATIONS.md)

### 7.2 Electrical/Analog Characteristics

- Signal integrity: ringing, crosstalk, overshoot
- EMI/EMC compliance: requires anechoic chamber testing
- Power consumption: current measurement at each operating mode
- **Token effect: ZERO.** This is physics, not software.

### 7.3 Manufacturing Variance

- Component tolerance: resistors ±5%, crystals ±50ppm
- PCB manufacturing defects, solder quality
- Creates behavior no simulation can predict
- **Each physical unit is unique**

**Real-world example:** [CONSIDERATIONS.md §2.7](./LLM-EMBEDDED-CONSIDERATIONS.md) — crystal aging causes protocol desynchronization after 2 years in cold conditions. LLM prediction probability ~0%.

### 7.4 Environmental Conditions

- Temperature range: -40°C to +85°C (automotive), thermal cycling stress
- Humidity, vibration, mechanical shock
- Aging effects: electrolytic capacitor lifetime, flash wear
- **Required equipment:** Environmental chambers, vibration testers

### 7.5 Safety Certification

| Standard | Domain | Certification Period | Replaceable by Tokens? |
|----------|--------|---------------------|----------------------|
| ISO 26262 | Automotive | 6-18 months | **NO** — documented evidence required, independent verification required |
| IEC 61508 | Industrial control | 6-12 months | **NO** — Safety Integrity Level (SIL) verification |
| DO-178C | Aviation | 12-36 months | **NO** — object code verification, MC/DC coverage |
| IEC 62443 | Industrial cybersecurity | 3-12 months | **NO** — penetration testing, threat modeling |

**Where tokens CAN help:** Generating **documentation** needed for certification (requirements traceability matrices, test plans, design documents). But the certification process itself requires human-to-certification-body interaction.

### 7.6 Multi-Device Integration

- Device A ↔ Device B physical bus communication
- Signal timing, protocol negotiation, error recovery
- Each physical connection is unique
- **Token effect: ZERO** for physical integration testing

### 7.7 Why This 30% Matters Most

Of the 14 production-scale failure patterns in [CONSIDERATIONS.md §2](./LLM-EMBEDDED-CONSIDERATIONS.md), **12 fall in this domain**:

| # | Pattern | Time to Manifest | LLM Success Rate |
|---|---------|-----------------|-----------------|
| 1 | 49.7-day counter overflow | Days to months | ~0% |
| 2 | eMMC wear from logging | Months to years | ~0% |
| 4 | 500K-device power overhead accumulation | Cumulative | ~0% |
| 5 | 87-day BLE lockup | Weeks to months | ~0% |
| 7 | Crystal aging desync | Years | ~0% |
| 8 | Brownout + flash brick | Random | ~0% |
| 9 | Heap fragmentation (ESP32) | Weeks to months | ~0% |
| 13 | C undefined behavior (manifests at -O2) | After compiler update | ~0% |

**These are the causes of field failures, safety incidents, and product recalls.** "Code compiles and works in QEMU" does not catch them.

---

## 8. The Speed Mismatch Trap

### 8.1 Code Generation Speed >> Verification Speed

```
LLM code generation:     ████████████████████████████████  (seconds, infinitely scalable)
Static analysis:          ████████████████████              (minutes, automated)
Emulator verification:    ████████████                      (min-hours, partially automated)
Real HW verification:     ████                              (hours-days, manual)
Env/certification:        ██                                (weeks-months, fully manual)
```

**Result:** The code an LLM generates in a day takes **weeks to months** to fully verify.

### 8.2 Quality Debt Accumulation Model

```
Time →
Code generated:    ████████████████████████████████████████
Code verified:     ████████████████
                                 ↑
                    Quality debt = unverified code
                    (risk: manifests as field failures)
```

### 8.3 The DORA 2025 Report Warning

> "AI is an amplifier, not a fix. Organizations with strong engineering practices benefit; those without just make existing bottlenecks more visible."

Applied to embedded:
- **Teams WITH HW test infrastructure** → LLM tokens significantly boost SW productivity
- **Teams WITHOUT HW test infrastructure** → LLM tokens mass-produce unverifiable code

### 8.4 Mitigation Strategies

| Strategy | Description | Cost |
|----------|------------|------|
| **Gated deployment** | Block code merge until L0-L2 pass | Low — CI pipeline |
| **HW verification scheduling** | Synchronize HW test sprints with code generation | Medium — process change |
| **Risk tiering** | Tier 3 code (DMA, ISR, security) requires HW verification before merge | Medium — classification system |
| **Digital Twin pre-investment** | Increase HW verification speed to close the gap | High — infrastructure investment |

---

## 9. Bridge Technologies: Raising the Ceiling

The physical ceiling is not fixed — it can be raised with these technologies.

### 9.1 Digital Twins (Ceiling: 50% → 70-80%)

| Technology | Features | Limitations |
|-----------|---------|------------|
| Renode | Open-source HW emulator, peripheral modeling | Cost of adding new board models |
| QEMU + peripheral models | Basic peripheral simulation | Low DMA/timing fidelity |
| Nvidia Omniverse | High-fidelity HW digital twins | Expensive, limited embedded support |
| Vendor virtual platforms | Virtual MCUs from ST, NXP, TI | Vendor lock-in, proprietary |

**Key limitation:** Building a per-board Digital Twin is itself expensive and manual. But once built, the **effective scope** of token scaling expands dramatically.

### 9.2 HIL-as-a-Service (Ceiling: 70% → 85%)

| Approach | Description | Cost |
|----------|------------|------|
| In-house HIL farm | Board farm with remote access + JTAG | Initial $10K-$50K + maintenance |
| Cloud HIL | AWS IoT Device Advisor, etc. | Usage-based pricing |
| CI integration | GitHub Actions → remote JTAG → auto-flash/test | Medium (pipeline setup) |

**Ideal pipeline:**
```
LLM code gen → west build (CI) → QEMU test → HIL flash → HW test → Result report
                                                  ↑
                                        This is the Bridge core
```

### 9.3 Datasheet RAG (Implicit Gap: 35%p → ~10%p)

One of EmbedEval's most important findings: **explicit prompt 95% vs implicit 60% = 35%p gap**. RAG injection of datasheets/errata/SDK docs into context can dramatically reduce this gap.

| Document Type | RAG Pipeline | Expected Effect |
|--------------|-------------|----------------|
| Datasheet register maps | Table extraction → chunking → vector DB | DMA/SPI/I2C pass@1 improvement |
| SDK API reference | Header files → function signature DB | Reduced API hallucination |
| Errata documents | Per-errata workaround mapping | Silicon bug mitigation |
| Coding standards | MISRA/CERT C rules → checklists | Improved safety pattern compliance |

### 9.4 LLM + Formal Verification (Addressing Silent Failures)

arXiv 2411.13269 proposes combining specification-driven LLM code generation with formal verification.

| Approach | Verification Scope | Limitations |
|----------|-------------------|------------|
| Model checking (SPIN, TLA+) | Deadlocks, livelocks, safety properties | State explosion — hard to scale to complex systems |
| Static analysis (Frama-C, CBMC) | Memory safety, bounds violations, UB | Annotation authoring cost |
| LLM + spec co-generation | Generate code + formal specification together | Research stage, not production-ready |

### 9.5 Self-Evolving Agents (Optimizing the Digital Portion)

- ALMAS (arXiv 2510.03463): Sprint Agent → Code Agent → Peer Agent autonomous pipeline
- Iterative Experience Refinement (IER): Learning from past task experience for continuous improvement
- AutoCodeRover: Automating the generate-test-fix loop
- **EmbedEval's role:** Functioning as the **quality gate** for these agent systems

### 9.6 Ceiling Rise Projection Timeline

```
                     ┌─────────────────────── Theoretical maximum (~90%)
                     │  ┌──────────────────── 2-3 years (Digital Twin + HIL + RAG: ~80%)
                     │  │  ┌───────────────── Current (~60%)
                     │  │  │
   100% ┤            │  │  │
        │            │  │  │
    90% ┤ ─ ─ ─ ─ ─ ┤  │  │ ─ ─ ─ ─  Never reachable (physics ≠ tokenizable)
        │            │  │  │
    80% ┤ ─ ─ ─ ─ ─ ┤──┤  │
        │            │     │
    70% ┤            │     │
        │            │     │
    60% ┤ ─ ─ ─ ─ ─ ┤ ─ ─ ┤
        │
    50% ┤
        └──────────────────── Quality achievable without physical verification
         Now     +1yr   +2-3yr   Theoretical max

    Remaining 10-40%: Physical verification + human expertise ALWAYS required
```

---

## 10. Optimal Workflow Architecture

### 10.1 The 3-Zone Model

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                    TOKEN ZONE (Maximize Token Investment)     │    │
│  │                                                              │    │
│  │  • Code generation (multi-pass + compiler feedback)          │    │
│  │  • Static analysis (exhaustive scan, multi-pattern, agents)  │    │
│  │  • Test case generation (thousands, auto edge case discovery)│    │
│  │  • Code review (security, safety, architecture perspectives) │    │
│  │  • Design space exploration (alternatives, trade-off analysis│    │
│  │  • Configuration optimization (Kconfig, Device Tree, Yocto)  │    │
│  │  • Documentation (API docs, test plans, cert doc drafts)     │    │
│  │                                                              │    │
│  │  ROI: High │ Automation: ~100% │ Human involvement: Minimal  │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                              ↕                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                    BRIDGE ZONE (Invest in Infrastructure)    │    │
│  │                                                              │    │
│  │  • Digital Twin development and maintenance                  │    │
│  │  • HIL-as-a-Service setup (remote board farms, CI integration│    │
│  │  • Datasheet RAG pipeline (vector DB, chunking, retrieval)   │    │
│  │  • CI/CD + remote HW access (JTAG, SSH, auto-flash)         │    │
│  │  • Formal verification tool integration (CBMC, SPIN, Frama-C│    │
│  │                                                              │    │
│  │  ROI: High (long-term) │ Initial cost: High │ Maintenance: Med   │
│  └──────────────────────────────────────────────────────────────┘    │
│                              ↕                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                    HUMAN ZONE (Focus Expert Investment)      │    │
│  │                                                              │    │
│  │  • System architecture decisions (tasks, IPC, memory, power) │    │
│  │  • HW bring-up & integration (first boot, JTAG debugging)   │    │
│  │  • Real-time timing verification (oscilloscope, logic analyzer│   │
│  │  • EMC/environmental testing (anechoic chamber, env chamber) │    │
│  │  • Safety certification (ISO 26262, IEC 61508, auditor work) │    │
│  │  • Field failure investigation (physical debugging, RMA)     │    │
│  │  • Domain requirements (customers, regulations, supply chain)│    │
│  │                                                              │    │
│  │  ROI: Essential │ Irreplaceable │ Human expertise = only solution │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 10.2 Mapping to the DEVELOPMENT-GUIDE 7-Phase Workflow

Reinterpreting the 7-phase workflow from [LLM-EMBEDDED-DEVELOPMENT-GUIDE.md](./LLM-EMBEDDED-DEVELOPMENT-GUIDE.md) through the 3-Zone lens.

| Phase | Original Classification | Zone | Token % | Human % | Rationale |
|-------|----------------------|------|---------|---------|-----------|
| **Phase 0: Knowledge Base** | Human | Human + Bridge | 20% | 80% | Datasheet extraction is tokenizable; verification is human |
| **Phase 1: Requirements** | Human+LLM | Human | 30% | 70% | LLM helps decompose; final judgment is human |
| **Phase 2: Architecture** | Human+LLM | Human | 40% | 60% | LLM suggests alternatives; decisions are human |
| **Phase 3: Implementation** | LLM+Human | **Token** | **80%** | 20% | Core token domain for code generation |
| **Phase 4: Review** | Tools+Human | Token + Human | **60%** | 40% | Automated analysis + human review |
| **Phase 5: Testing** | Human+Tools+Board | Bridge + Human | 40% | **60%** | Emulator limits → HW needed |
| **Phase 6: Integration/Release** | Human | **Human** | 10% | **90%** | HW integration, certification, deployment |

**Key insight:** Phases 3-4 are the token-intensive zone; Phases 5-6 are the human-intensive zone. Bridge investment aims to reduce the human percentage in Phase 5.

### 10.3 Optimal Token Allocation by Category

Mapping token strategies to EmbedEval's 3-Tier trust model ([CONSIDERATIONS.md §3.3](./LLM-EMBEDDED-CONSIDERATIONS.md)).

| Tier | Categories | pass@1 | Token Strategy | Human Review Level |
|------|-----------|--------|---------------|-------------------|
| **1: Trust but Verify** | kconfig, device-tree, sensor-driver, yocto, watchdog, timer | >85% | Mass generation + auto-select | Light review |
| **2: Starting Point** | boot, gpio, linux-driver, ota, power-mgmt, spi-i2c, storage, uart, networking | 50-85% | RAG-augmented generation + error path focused analysis | Mandatory review (error paths, HW interaction) |
| **3: Expert Review Required** | DMA, ISR-concurrency, memory-opt, threading, security | <50% | Datasheet RAG required + formal verification considered + multi-generation | **Full expert review mandatory** |

**Warning for Tier 3:** Using LLM output without review in this domain puts **"code that works but isn't safe"** into production. This is **actively dangerous** for teams lacking embedded expertise.

---

## 11. General SW vs Embedded: Full Comparison

### 11.1 12-Dimension Comparison Matrix

| Dimension | General SW | Embedded | Gap |
|-----------|-----------|----------|-----|
| **Feedback loop speed** | Seconds to minutes | Minutes to days (SW), weeks to months (HW) | 10-1000x |
| **Automatable testing** | ~95% | ~50-60% | ~40%p |
| **Token scaling ceiling** | None (log diminishing) | ~70-80% of total quality | Hard limit |
| **Deployment automation** | ~100% (containers) | ~30-50% (OTA-capable devices only) | ~60%p |
| **Feedback digitization** | ~95% (logs, analytics) | ~30% (physical symptoms) | ~65%p |
| **Rollback cost** | Near-zero | Moderate to catastrophic | N/A |
| **Regulatory overhead** | Low (except medical/financial) | High (safety certification required) | Qualitative |
| **User scaling speed** | Instant (web deploy) | Slow (physical devices) | Qualitative |
| **Environment reproducibility** | Docker = identical | Each device is unique | Qualitative |
| **Failure consequences** | Wrong screen, data | **Physical damage, safety incidents** | Qualitative |
| **Training data** | Abundant (Python/JS/Java) | Sparse (embedded C) | ~100x |
| **Debugging tools** | Software (logs, APM) | Physical (JTAG, oscilloscope) | Qualitative |

### 11.2 The "One-Person Startup" Thought Experiment

**General software:**
A solo developer with $1,000/month token budget:
- LLM builds full web app (frontend + backend + DB)
- CI/CD auto-deployment
- User feedback auto-collection → auto bug fixes
- **Feasible:** Near-fully-automatic SaaS product operation

**Embedded:**
A solo developer with $1,000/month token budget:
- LLM generates firmware code → **OK**
- Static analysis + QEMU testing → **OK**
- Real board testing → **HW purchase + measurement equipment needed ($5K+)**
- EMC testing → **Outsource $10K+**
- Safety certification → **6+ months, certification body costs $50K+**
- Mass production → **Tooling, PCB manufacturing, assembly line**

**Conclusion:** LLMs democratize general SW development, but **embedded development has physical infrastructure costs 10-100x greater than token costs, making the same level of democratization impossible.**

### 11.3 Economic Model Comparison

```
General SW:  Cost(quality) ∝ tokens
Embedded:    Cost(quality) = tokens + FIXED_HW_COST + FIXED_CERTIFICATION_COST + FIXED_PRODUCTION_COST
```

Fixed costs persist regardless of token efficiency. This is the structural reason token scaling is not as revolutionary for embedded as it is for general software.

---

## 12. Practical Guide for Development Teams

### 12.1 Token Strategy by Team Size

#### Small Teams (1-5 people, single product)

| Priority | Investment | Expected Effect |
|----------|-----------|----------------|
| 1 | **Code generation + compiler feedback loop** setup | 2-3x development speed |
| 2 | **Static analysis automation** (L0 checks in CI) | 80%+ common mistakes auto-detected |
| 3 | **Datasheet RAG** (target MCU datasheet only) | Tier 2-3 pass@1 improvement |
| 4 | **QEMU test automation** (supported platforms only) | L2 coverage |

**Do NOT invest in:** Digital Twins (low ROI — build cost > benefit at small scale), formal verification (high learning curve)

#### Medium Teams (5-20 people, multiple products)

| Priority | Investment | Expected Effect |
|----------|-----------|----------------|
| 1-4 | Small team strategy + | (foundation) |
| 5 | **In-house HIL farm** (remote board access + CI integration) | HW test automation possible |
| 6 | **Multi-agent review pipeline** | Security + safety + architecture review |
| 7 | **Digital Twin** (1-2 primary boards) | Expanded emulation coverage |

#### Large Teams (20+ people, platforms/SDKs)

| Priority | Investment | Expected Effect |
|----------|-----------|----------------|
| 1-7 | Medium team strategy + | (foundation) |
| 8 | **Enterprise datasheet RAG** (all MCU families) | Platform-wide pass@1 improvement |
| 9 | **Formal verification integration** (safety-critical modules) | Silent failure detection |
| 10 | **Self-evolving agents** (learning in-house best practices) | Continuous quality improvement |
| 11 | **LLM fine-tuning** (in-house codebase) | In-house pattern learning |

### 12.2 Daily Workflow Example

**An embedded engineer's day (token-optimized version):**

```
09:00  Morning — Review code LLM generated yesterday (Token Zone output)
       └─ Check automated static analysis results
       └─ Focus review on Tier 3 code (DMA, ISR, security)

10:00  HW Testing — Flash review-passed code to board (Human Zone)
       └─ Verify timing with oscilloscope
       └─ Confirm actual SPI/I2C communication

12:00  Lunch

13:00  Start new module — Provide context package to LLM (Token Zone setup)
       └─ Extract relevant register maps from datasheet
       └─ Prepare SDK example code
       └─ Write prompt + request code generation

14:00  Iterate on LLM-generated code (Token Zone execution)
       └─ Compiler feedback loop 3-5 times
       └─ Apply static analysis feedback
       └─ Auto-generate test cases

15:00  Architecture review — Review LLM design suggestions (Human Zone judgment)
       └─ Finalize task structure decisions
       └─ Select IPC mechanisms
       └─ Confirm memory budget

16:00  Integration testing — New module + existing modules (Bridge Zone)
       └─ Verify basic operation in QEMU
       └─ Run real HW test on HIL farm (automated)

17:00  Set up tomorrow's work
       └─ Prepare next module context package
       └─ Request overnight batch code generation from LLM
```

**Key principle:** Morning is Human Zone (verification), afternoon is Token Zone (generation). **Verification must stay ahead of generation.**

### 12.3 Investment Decision Framework

```
When considering a new investment:

├── Solvable digitally?
│   ├── YES → Token Zone investment (increase token budget)
│   │         Cost: $100-$10K/month, immediate effect
│   └── NO
│       ├── Can infrastructure digitize it?
│       │   ├── YES → Bridge Zone investment
│       │   │         Cost: $10K-$100K initial + maintenance
│       │   │         Effect: 3-6 months out
│       │   └── NO → Human Zone investment (hire/train experts)
│       │             Cost: $50K-$150K/year/person
│       │             Effect: Immediate (experienced) or 1-2 years (training)
│       └── Uncertain → Bridge Zone pilot (small-scale experiment)
│                     Cost: $5K-$20K
│                     Decision: Evaluate ROI after 3 months
```

### 12.4 Common Mistakes and Responses

| Mistake | Consequence | Response |
|---------|------------|---------|
| Merging Tier 3 code without review | Field failures | Enforce per-category review rules |
| Skipping HW tests, trusting QEMU only | "Works but isn't safe" code | Make HW testing a release gate |
| Requesting DMA code from LLM without datasheet | API hallucination + cache issues | Provide RAG or manual context |
| Increasing only token budget without HW infrastructure | Accumulating unverifiable code | Prioritize Bridge Zone investment |
| Replacing expert review time with LLM output volume | Review bottleneck → quality degradation | Scale generation to match review capacity |
| Applying the same token strategy to all categories | Over-invest in Tier 1, under-invest in Tier 3 | Differentiated per-category strategies |

### 12.5 Measurement Metrics

Metrics for tracking the effectiveness of a team's token-scaling strategy:

| Metric | Measurement Method | Target |
|--------|-------------------|--------|
| **Code generation pass@1** | L0-L2 automated verification pass rate | Tier 1: >90%, Tier 2: >70%, Tier 3: >40% |
| **Review find rate** | Issues found in human review / LLM-generated code volume | Decreasing trend |
| **Verification speed ratio** | Code generation speed / HW verification speed | Maintain below 2:1 |
| **Field defect rate** | Field failures within 6 months of release | Decreasing trend |
| **Bridge coverage** | Test cases covered by Digital Twin + HIL | Increasing trend |
| **Token ROI** | (Time saved × hourly cost) / token cost | >5x |

---

## 13. Open Questions and Future Research

### 13.1 Open Questions

1. **Can Digital Twins reach 95% fidelity?**
   - Currently ~50-70%. The remainder is analog characteristics, EMI, thermal models.
   - Key: integrating physics simulation (SPICE level) with digital emulation.

2. **Can LLMs learn to ask for datasheets?**
   - Current: hallucinate when not in prompt.
   - Future: "I need the reset value of this register" — agent automatically searches datasheet.

3. **Can formal verification scale to the system level?**
   - Current: module level (individual functions, drivers).
   - Needed: inter-task communication, system-wide deadlock verification.

4. **Does a token scaling law exist for embedded?**
   - Token scaling laws for general SW have been empirically demonstrated.
   - An equivalent law for embedded **has not been studied yet**.
   - EmbedEval can provide the foundational data for this research.

5. **What's the ROI of fine-tuning on in-house codebases?**
   - Comparative study needed: public model + RAG vs fine-tuned model.
   - Cost-effectiveness analysis: fine-tuning cost vs RAG infrastructure cost.

### 13.2 EmbedEval's Role

EmbedEval can serve as a key tool for this token-scaling research:

- **Digital 70% benchmarking:** L0-L3 automated evaluation measures token strategy effectiveness
- **Ceiling detection:** Identifying the point where token investment no longer yields improvement for specific categories/technologies
- **Bridge effectiveness measurement:** Comparing pass@1 before and after RAG, Digital Twin, or HIL adoption
- **Scaling law formulation:** Collecting token investment vs pass@1 curve data

---

## 14. Sources

### Test-Time Compute & Token Scaling
- [Scaling LLM Test-Time Compute (arXiv 2408.03314)](https://arxiv.org/abs/2408.03314) — inference-time compute more effective than 14x model scaling
- [S*: Test Time Scaling for Code (arXiv 2502.14382)](https://arxiv.org/html/2502.14382v1) — test-time scaling for code generation
- [Thinking Longer, Not Larger (arXiv 2503.23803)](https://arxiv.org/html/2503.23803) — SWE-SynInfer+ patch verification
- [CodeMonkeys (arXiv 2501.14723)](https://arxiv.org/abs/2501.14723) — SW engineering test-time compute
- [The Art of Scaling Test-Time Compute (arXiv 2512.02008)](https://arxiv.org/abs/2512.02008) — TTS strategy comparison

### LLM + Embedded Systems
- [EmbedAgent (arXiv 2506.11003, ICSE 2026)](https://arxiv.org/html/2506.11003v2) — embedded LLM benchmark, RAG+feedback effect
- [Securing LLM-Generated Firmware (arXiv 2509.09970)](https://arxiv.org/abs/2509.09970) — agent-driven firmware security validation
- [Exploring LLMs for Embedded (arXiv 2307.03817)](https://arxiv.org/abs/2307.03817) — GPT-4 embedded code generation
- [HardSecBench (arXiv 2601.13864)](https://www.arxiv.org/pdf/2601.13864) — HW security benchmark
- [Specification-Driven LLM for Automotive (arXiv 2411.13269)](https://arxiv.org/html/2411.13269v1) — spec-driven automotive SW generation

### Autonomous Agents
- [Self-Organizing Multi-Agent Systems (arXiv 2603.25928)](https://arxiv.org/html/2603.25928v1) — multi-agent SW development
- [ALMAS (arXiv 2510.03463)](https://arxiv.org/html/2510.03463v1) — autonomous multi-agent SW framework
- [Measuring AI Agent Autonomy (Anthropic)](https://www.anthropic.com/research/measuring-agent-autonomy) — agent autonomy measurement

### Embedded DevOps & Verification
- [Embedded DevOps Survey (arXiv 2507.00421)](https://arxiv.org/html/2507.00421v1) — CI feasible, CD difficult
- [Don't Vibe Code Your Embedded System (Electronic Design)](https://www.electronicdesign.com/technologies/embedded/software/article/55311837/electronic-design-dont-do-it-vibe-code-your-embedded-system)
- [Vibe Coding Limitations 2026 (Newly)](https://newly.app/articles/vibe-coding-limitations)
- [Five Levels of AI Agent Autonomy (Swarmia)](https://www.swarmia.com/blog/five-levels-ai-agent-autonomy/)

### EmbedEval Internal Data
- [BENCHMARK-COMPARISON-2026-04-05.md](./BENCHMARK-COMPARISON-2026-04-05.md) — Haiku vs Sonnet comparison
- [LLM-EMBEDDED-FAILURE-FACTORS.md](./LLM-EMBEDDED-FAILURE-FACTORS.md) — 42 failure factors
- [LLM-EMBEDDED-CONSIDERATIONS.md](./LLM-EMBEDDED-CONSIDERATIONS.md) — 14 production-scale failure patterns
- [LLM-EMBEDDED-DEVELOPMENT-GUIDE.md](./LLM-EMBEDDED-DEVELOPMENT-GUIDE.md) — 7-phase workflow
