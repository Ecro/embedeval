# PLAN: Negative Test Validation

**Project:** embedeval
**Created:** 2026-03-25

---

## Executive Summary

> **TL;DR:** 의도적 오답 코드가 체크에 의해 FAIL되는지 검증하여 체크 자체의 precision을 측정.

### 왜 필요한가

현재는 레퍼런스 솔루션이 PASS하는 것만 확인. **틀린 코드를 잡는지는 검증 안 함.**

예: `volatile` 체크가 있는데, 실제로 volatile을 빠뜨린 코드가 통과해버리면?
→ 체크가 있지만 무의미 → false sense of security

### 설계

각 TC별로 `checks/negatives.py`에 오답 변형을 정의:

```python
# checks/negatives.py
NEGATIVES = [
    {
        "name": "missing_volatile",
        "description": "Shared flag without volatile qualifier",
        "mutation": lambda code: code.replace("volatile int", "int"),
        "must_fail": ["error_flag_is_volatile"],  # 이 체크가 FAIL해야 함
    },
    {
        "name": "missing_device_ready",
        "description": "No device readiness check",
        "mutation": lambda code: remove_lines_containing(code, "device_is_ready"),
        "must_fail": ["device_ready_check"],
    },
]
```

pytest에서 자동 검증:
```python
def test_negative(case_id, negative):
    ref_code = load_reference(case_id)
    bad_code = negative["mutation"](ref_code)
    results = run_checks(bad_code)
    for check_name in negative["must_fail"]:
        assert check_failed(results, check_name), f"{check_name} should FAIL on {negative['name']}"
```

---

## 대상 TC 선정 (10개 × 3 변형 = 30 negative tests)

| TC | 변형 1 | 변형 2 | 변형 3 |
|----|--------|--------|--------|
| dma-008 | volatile 제거 | dma_stop 제거 | error flag 체크 순서 역전 |
| isr-concurrency-003 | spinlock→mutex 교체 | k_spin_unlock 제거 | printk in ISR 추가 |
| isr-concurrency-008 | barrier 제거 | modulo 대신 bitwise 제거 | atomic 대신 plain int |
| linux-driver-001 | cleanup 제거 | copy_to_user 제거 | error check 제거 |
| ble-008 | conn_unref 제거 | scan_stop 순서 역전 | cross-platform API 추가 |
| gpio-basic-001 | device_is_ready 제거 | — | — |
| timer-007 | period == timeout 설정 | — | — |
| stm32-freertos-002 | xQueueSend (non-ISR) 사용 | portYIELD 제거 | — |
| esp-gpio-001 | Zephyr API 추가 | vTaskDelay 대신 busy-wait | — |
| watchdog-005 | health flag 무조건 feed | — | — |

---

## Implementation

### Phase 1: Framework

`tests/test_negatives.py` 생성:
- `cases/*/checks/negatives.py`가 있으면 자동 발견
- 각 NEGATIVE 항목에 대해 mutation 적용 → 체크 실행 → must_fail 검증

### Phase 2: 10개 TC에 negatives.py 작성

각 TC의 `checks/negatives.py`에 NEGATIVES 리스트 정의.
mutation은 lambda 또는 helper 함수로 코드 변형.

### Phase 3: 결과 분석

- 30개 negative test 중 몇 개가 정상 FAIL하는지 → check precision
- FAIL 안 되는 것 → 체크가 약한 것 → 체크 강화 필요

---

## Success Criteria

- [ ] 10개 TC에 negatives.py 작성
- [ ] 30+ negative test 정의
- [ ] pytest에서 자동 실행
- [ ] check precision 측정 (목표: 90%+)
- [ ] 기존 774 test 통과 유지
