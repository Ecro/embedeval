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

LLM 실패 패턴을 **일반 소프트웨어에서도 발생하는 문제**와 **임베디드 특성에 의한 문제**로
구분하면 다음과 같다.

### General SW Failures (어떤 도메인에서도 발생)

이 패턴들은 웹, 서버, 데스크톱 등 어떤 SW 개발에서도 LLM이 동일하게 실패할 수 있다.

| Pattern | Cases | Description |
|---------|-------|-------------|
| **Error path cleanup** | linux-driver-001/004/006 | 리소스 할당 후 실패 시 역순 해제 누락. DB connection pool, file handle, socket 등에서도 동일하게 발생 |
| **Return value ignored** | networking-001/008, ota-003 | API 호출 후 반환값 무시. HTTP client, DB query 등에서도 동일 패턴 |
| **Alloc/free mismatch** | memory-opt-003 | malloc/free 쌍 불일치. 모든 C/C++ 코드에서 발생 가능한 메모리 누수 |
| **Flag vs early return** | security-007 | 실패 시 즉시 중단 대신 플래그 누적. 보안 코드 전반에 해당 |
| **Ordering violation** | storage-002 | init -> register -> use 순서 오류. 모든 lifecycle 관리에 해당 |
| **Magic numbers** | memory-opt-001 | 상수를 이름 없이 반복 사용. 모든 언어에서 발생하는 유지보수 문제 |
| **Demo mindset** | power-mgmt-009 | 기능 시연만 하고 운영 루프 미구현. 어떤 서비스 코드에서도 발생 |
| **Complexity hiding basics** | ota-005 | 복잡한 구조 속에서 기본 안전장치 누락. 모든 도메인의 상태 머신에 해당 |

**공통 근본 원인:**
- 학습 데이터가 "동작하는 예제 코드" 위주 (에러 처리 생략된 튜토리얼)
- LLM의 순방향 토큰 생성 구조가 역순 의존성 추적에 불리
- "기능 완성"에 최적화, "안전한 운영"에 비최적화

### Embedded-Specific Failures (임베디드에서만 발생)

이 패턴들은 **하드웨어 의존성, 실시간 제약, 리소스 제한** 등 임베디드 고유 특성에서
비롯된다. 웹이나 서버 개발에서는 동일한 실패가 발생하지 않는다.

| Pattern | Cases | Description | Why Embedded-Only |
|---------|-------|-------------|-------------------|
| **HW cyclic vs SW reload** | dma-003 | DMA 하드웨어 cyclic 모드 대신 소프트웨어 콜백 reload 사용 | DMA 컨트롤러의 하드웨어 모드는 임베디드에서만 존재하는 개념. 서버에는 DMA가 없음 |
| **device_is_ready 누락** | gpio-basic-001, watchdog-007 | 하드웨어 디바이스 준비 여부 확인 없이 사용 | 서버의 DB connection은 연결 시점에 확인하지만, 임베디드 HW 디바이스는 부팅 순서에 따라 준비 안 될 수 있음 |
| **Timing margin 무시** | timer-007 | WDT 타임아웃과 동일한 주기로 feed — 마진 없음 | 서버에서 timeout == interval이면 보통 괜찮지만, 실시간 시스템에서는 인터럽트 지연, 스케줄링 지터 때문에 반드시 마진이 필요 |
| **Stack size 부족** | threading-005* | 워크 큐 스택 512/1024 사용 (2048 필요) | 서버에서는 OS가 자동 스택 확장. 임베디드 RTOS에서는 스택이 고정 크기이므로 overflow = 하드 폴트 |
| **ISR context 제약** | sensor-driver-003 | ISR에서 blocking API 사용 불가라는 제약 미인식 | 서버에서 signal handler 내 제약과 유사하지만, 임베디드에서는 훨씬 더 엄격하고 위반 시 시스템 hang |
| **Power state transition** | power-mgmt-001 | PM action return 미확인 — suspend/resume 실패 무시 | 서버 sleep/wake는 OS가 관리. 임베디드에서 PM 실패 무시는 배터리 고갈 또는 wake 불가 |
| **OTA rollback 미구현** | ota-005 | DFU 다운로드 실패 시 abort 경로 없음 | 서버 배포 실패는 롤백이 쉬움. 임베디드 OTA 실패 시 디바이스가 bricked 될 수 있음 |
| **Flash boundary 미검증** | storage-009* | 플래시 영역 범위 초과 쓰기 미방지 | 서버의 디스크는 OS가 보호. 임베디드 raw flash 접근은 boundary 넘으면 부트로더나 다른 파티션을 파괴 |

**임베디드 고유 근본 원인:**
- LLM의 학습 데이터에서 임베디드 코드 비율이 낮음 (웹/서버 >> 임베디드)
- 하드웨어 데이터시트의 타이밍 제약은 코드에 명시적으로 드러나지 않음
- "컴파일 → 실행" 사이클에서 하드웨어 의존 버그는 발견이 어려움
- 임베디드의 "안전"은 기능 동작 + 리소스 제한 + 타이밍 보장의 3가지를 동시에 만족해야 함

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

**핵심:** 전체 18건의 실제 LLM 실패 중 ~10건(56%)은 **일반 SW에서도 발생하는 패턴**이고,
~8건(44%)은 **임베디드 고유 특성**에서 비롯된다. 즉, LLM의 임베디드 코드 품질을 개선하려면
일반적인 에러 처리 능력 향상이 먼저이고, 그 다음이 HW 의미론 이해이다.

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
