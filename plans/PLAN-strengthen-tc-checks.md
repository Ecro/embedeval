# PLAN: TC Check 강화 — 연구 기반 LLM 실패 탐지 개선

**Project:** embedeval
**Created:** 2026-03-24

---

## Executive Summary

> **TL;DR:** Sonnet 92% pass@1 (특히 isr/security/linux-driver 100%)은 체크가 너무 관대하다는 증거. 6가지 연구 기반 전략으로 기존 200 TC의 checks를 강화하여 실제 LLM 맹점을 탐지.

### Why It Matters
현재 벤치마크가 Sonnet에게 "쉬운" 이유는 3가지:
1. **체크가 `"keyword" in code` 수준** — 어디에 있든 pass
2. **학습 데이터에 풍부한 패턴만 테스트** — kconfig, device-tree 같은 "익숙한" 문제
3. **LLM이 설계한 TC를 LLM이 풀고 있음** — Homogenization Trap

### Research Foundation

| 논문 | 핵심 발견 | 적용 전략 |
|------|---------|----------|
| Unseen Horizons (ICSE 2025) | API 난독화 시 62.5% 하락 | 덜 알려진 API 요구 |
| Homogenization Trap (arXiv 2507.06920) | LLM 에러 클러스터링 | 인간 관점 체크 추가 |
| RLHF 편향 | "깔끔한 코드" 선호 → volatile 회피 | 비표준 제약 추가 |
| Backslash Security | secure-pass@1 < 12% | 보안 체크 심화 |
| LiveCodeBench | 시간 기반 오염 방지 | deprecated API 거부 |
| Sonnet 200-case 결과 | 100% pass 카테고리 9개 | 해당 카테고리 우선 강화 |

---

## 6가지 강화 전략

### Strategy 1: 맥락 기반 체크 (Context-Aware Checks)

**문제:** `"k_sleep" in generated_code` → 주석에 있어도, 다른 함수에 있어도 PASS

**해결:** 특정 함수 본문 내에서만 체크

```python
# AS-IS (관대)
has_sleep = "k_sleep" in generated_code

# TO-BE (엄격)
def _in_function_body(code, func_pattern, target):
    """Check if target string appears inside a specific function body."""
    match = re.search(func_pattern + r'\s*\{', code)
    if not match:
        return False
    # Count braces to find function end
    start = match.end()
    depth = 1
    for i, c in enumerate(code[start:], start):
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        if depth == 0:
            return target in code[start:i]
    return False

# ISR 함수 내에서 printk가 없는지 확인
isr_has_printk = _in_function_body(code, r'void\s+\w*isr\w*\([^)]*\)', 'printk')
```

**적용 대상:** isr-concurrency (ISR 본문 체크), threading (스레드 함수 내), power-mgmt (콜백 내)

### Strategy 2: 에러 경로 리소스 정리 체크

**문제:** LLM이 happy path에서만 free/cleanup하고, 에러 경로에서는 누락

**해결:** `if (ret < 0) { ... }` 블록 내에서 cleanup 호출 여부 확인

```python
# 에러 핸들링 블록에서도 psa_destroy_key가 호출되는지
error_blocks = re.findall(r'if\s*\([^)]*<\s*0[^)]*\)\s*\{([^}]+)\}', code)
cleanup_in_error = any('psa_destroy_key' in block for block in error_blocks)
```

**적용 대상:** security (키 파괴), linux-driver (리소스 해제), storage (파일 닫기), dma (dma_stop)

### Strategy 3: 덜 알려진 동등 API 요구 (API Defamiliarization)

**문제:** LLM이 가장 흔한 API만 알고, 동등한 대안 API를 모름

**해결:** prompt에서 특정 API 사용을 요구 (학습 데이터에 적은 것)

| 흔한 API | 덜 알려진 동등 API | 카테고리 |
|----------|------------------|---------|
| `k_timer` | `counter` API (HW counter) | timer |
| `k_fifo` | `k_pipe` | isr-concurrency |
| `k_msgq` | `k_mbox` (mailbox) | threading |
| `k_mutex` | `k_condvar` (condition variable) | threading |
| `nvs_write` | `settings_save_one` | storage |
| `printk` | `LOG_MODULE_REGISTER` + `LOG_INF` | 전체 |

**적용:** 기존 TC의 prompt를 수정하지 않고, **새로운 변형 TC를 추가**하거나 기존 hard TC의 prompt에 제약 추가

### Strategy 4: Deprecated/Wrong API 거부 체크

**문제:** LLM이 구버전 API나 다른 플랫폼 API를 사용해도 현재 체크가 못 잡음

**해결:** 금지 API 목록을 behavior.py에 추가

```python
# Zephyr deprecated APIs (v4.0+)
DEPRECATED_APIS = [
    "device_get_binding",    # → DEVICE_DT_GET
    "gpio_pin_configure",    # → gpio_pin_configure_dt
    "i2c_configure",         # → i2c_configure_dt
    "spi_config",            # old struct → spi_dt_spec
    "device_pm_control",     # → PM_DEVICE_DT_DEFINE
]

# Cross-platform forbidden APIs
CROSS_PLATFORM = [
    "xTaskCreate", "vTaskDelay", "xQueueSend",      # FreeRTOS
    "analogRead", "digitalWrite", "Serial.print",    # Arduino
    "HAL_GPIO_WritePin", "HAL_SPI_Transmit",         # STM32 HAL
    "pthread_create", "pthread_mutex_lock",           # POSIX
]
```

**적용 대상:** 모든 100% pass 카테고리의 static.py에 추가

### Strategy 5: 수치/논리 불변식 강화

**문제:** `timer_period < wdt_timeout` 같은 수치 관계를 체크하지 않는 TC가 많음

**해결:** 코드에서 수치 값을 추출하여 도메인 불변식 검증

```python
# 타이머 주기가 WDT 타임아웃보다 짧아야 함
period_match = re.search(r'K_MSEC\s*\(\s*(\d+)\s*\)', code)
timeout_match = re.search(r'window\.max\s*=\s*(\d+)', code)
if period_match and timeout_match:
    period_ok = int(period_match.group(1)) < int(timeout_match.group(1))
```

**적용 대상:** timer+watchdog (period < timeout), dma (block_size > 0 && aligned), threading (stack_size >= 256), ble (MTU size)

### Strategy 6: "컴파일되지만 틀린" 함정 (Compile-but-Wrong Traps)

**문제:** LLM 코드가 컴파일되고 실행되지만 **의미적으로 틀린** 경우를 못 잡음

**해결:** prompt에 의도적인 함정을 설치하고 behavior.py에서 검증

예시:
- **security:** "AES-128을 사용하되, **절대로 ECB 모드를 사용하지 마라**" → ECB 사용 여부 체크
- **ota:** "이미지 확인 전에 반드시 **자체 테스트를 3회** 실행하라" → 테스트 횟수 체크
- **isr:** "ISR에서 **k_sem_give만** 호출하고, k_fifo_put은 사용하지 마라" → k_fifo_put 거부 체크
- **threading:** "뮤텍스 잠금 순서를 **반드시 알파벳순**으로 하라" → 잠금 순서 검증

---

## Implementation Plan

### Phase 1: 100% pass 카테고리 체크 강화 (최우선)

9개 카테고리의 behavior.py 강화:

| Category | 현재 pass@1 | 강화 내용 | 예상 후 pass@1 |
|----------|-----------|----------|--------------|
| isr-concurrency | 100% | ISR 본문 맥락 체크, k_fifo 대신 k_pipe 요구, memory barrier 체크 | 50-60% |
| security | 100% | 에러 경로 키 파괴, ECB 모드 거부, 키 추출 방지 | 40-50% |
| linux-driver | 100% | 에러 경로 cleanup, deprecated gpio_request 거부, sysfs bounds check | 50-60% |
| ble | 100% | MTU 크기 검증, 연결 상태 확인 후 GATT, 보안 레벨 체크 | 60-70% |
| kconfig | 100% | 환각 CONFIG 거부, deprecated 옵션 감지 | 70-80% |
| device-tree | 100% | 셀 카운트 검증, 주소 범위 체크, phandle 유효성 | 70-80% |
| boot | 100% | 상충 옵션 조합 감지, 버전 호환성 체크 | 70-80% |
| ota | 100% | 자체 테스트 횟수, 타임아웃 수치, 상태 머신 완전성 | 60-70% |
| yocto | 100% | SPDX 형식 엄격 검증, inherit 누락, 변수 override 문법 | 70-80% |

### Phase 2: 80% pass 카테고리 체크 정밀화

5개 카테고리 — 이미 변별력 있지만 체크 정밀도 향상:

| Category | 강화 내용 |
|----------|----------|
| dma | 캐시 라인 alignment 수치 검증, 순환 모드 reload 위치 |
| gpio-basic | 비동기 UART 콜백 위치, ADC 오버샘플링 수치 |
| networking | 버퍼 크기 경계, DNS 타임아웃 수치, TLS 자격증명 순서 |
| power-mgmt | PM 상태 enum 혼동 감지, 배터리 임계값 논리 |
| storage | settings init 순서, flash erase alignment |

### Phase 3: 크로스 플랫폼 혼동 체크 공통화

모든 카테고리의 static.py에 공통 금지 API 체크 추가:

```python
# shared_checks.py (신규 모듈)
FORBIDDEN_IN_ZEPHYR = [
    ("xTaskCreate", "FreeRTOS"),
    ("vTaskDelay", "FreeRTOS"),
    ("analogRead", "Arduino"),
    ("HAL_GPIO_WritePin", "STM32 HAL"),
    ("pthread_create", "POSIX"),
]

def check_no_cross_platform(code: str) -> list[CheckDetail]:
    ...
```

### Phase 4: 맥락 기반 체크 유틸리티

`src/embedeval/check_utils.py` (신규):

```python
def extract_function_body(code: str, func_pattern: str) -> str | None:
    """Extract function body between matching braces."""
    ...

def find_in_function(code: str, func_name: str, target: str) -> bool:
    """Check if target appears inside a specific function."""
    ...

def extract_error_blocks(code: str) -> list[str]:
    """Extract all if(ret < 0) { ... } blocks."""
    ...

def extract_numeric_value(code: str, pattern: str) -> int | None:
    """Extract numeric value from #define or assignment."""
    ...
```

### Phase 5: 벤치마크 재실행 + 결과 비교

1. 강화된 체크로 Sonnet 재실행
2. 이전 결과 (92%)와 비교
3. 목표: **전체 pass@1 60-75%** (현재 92%에서 하락)
4. 카테고리별 변별력 확인
5. False positive 없는지 검증 (reference 솔루션은 여전히 100% pass)

---

## Success Criteria

- [ ] 모든 200 reference 솔루션이 강화된 체크도 통과
- [ ] Sonnet pass@1이 92% → **65-75%로 하락** (적절한 난이도)
- [ ] 100% pass 카테고리가 **0개** (모든 카테고리에 최소 1개 실패)
- [ ] `check_utils.py` 공통 유틸리티로 체크 코드 중복 제거
- [ ] 크로스 플랫폼 금지 API 체크가 모든 Zephyr 카테고리에 적용

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Reference 솔루션이 강화된 체크에 실패 | 높음 | 체크 추가 후 즉시 reference 검증 |
| 체크가 너무 엄격해서 올바른 코드도 거부 | 높음 | 다양한 올바른 변형도 허용하도록 regex 설계 |
| 체크 로직 복잡도 증가로 유지보수 어려움 | 중간 | check_utils.py로 공통 로직 추출 |
| Sonnet 외 모델에서 pass@1이 0%에 수렴 | 중간 | 카테고리별로 easy TC는 관대하게 유지 |

---

## Files Changed

| File | Change Type |
|------|-------------|
| `src/embedeval/check_utils.py` | 신규 — 공통 체크 유틸리티 |
| `cases/*/checks/static.py` | 수정 — 금지 API 체크 추가 (100% pass 카테고리) |
| `cases/*/checks/behavior.py` | 수정 — 맥락 기반 + 수치 체크 강화 |
| `tests/test_check_utils.py` | 신규 — 유틸리티 테스트 |
