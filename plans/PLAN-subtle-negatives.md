# PLAN: Subtle Negative Tests — Check Blind Spot Discovery

**Project:** embedeval
**Created:** 2026-03-25

---

## Executive Summary

> **TL;DR:** 체크를 우회하면서 의미적으로 틀린 "교묘한 오답"을 만들어 체크의 실제 precision을 측정.
> 목표: 15개 subtle mutation 중 ~50%가 잡히지 않아야 정상 — 잡히지 않는 것이 체크 강화 방향.

### 기존 vs 새로운 접근

| | 기존 (trivial) | 새로운 (subtle) |
|---|---|---|
| 방식 | 코드 완전 제거 | 체크 우회 + 버그 유지 |
| 예상 결과 | 100% caught | **~50% caught** |
| 가치 | 체크가 존재하는지 확인 | **체크의 한계를 발견** |

---

## 15 Subtle Mutations

### Evasion Category: "키워드는 있지만 의미가 틀림"

| # | TC | Mutation | 왜 교묘한가 |
|---|-----|---------|-----------|
| 1 | dma-008 | `volatile int unused_var; int dma_error_flag;` | volatile이 코드에 존재하지만 다른 변수에 |
| 2 | dma-008 | `if(dma_error_flag) printk("err");` (return 없음) | 에러 감지하지만 처리 안 함 |
| 3 | isr-003 | `irq_lock()/irq_unlock()` 대체 | mutex가 아니라 irq_lock — 더 나쁜 패턴 |
| 4 | isr-003 | `k_spin_unlock(&lock, (k_spinlock_key_t){0})` | key 0으로 하드코딩 — 인터럽트 미복원 |
| 5 | isr-008 | `volatile uint32_t` 대신 `atomic_t` | volatile은 atomic이 아님 (반대 방향) |
| 6 | linux-001 | `__copy_to_user` | copy_to_user의 substring — access_ok 스킵 |
| 7 | linux-001 | 3개 cleanup 중 2개만 | 불완전 cleanup — 일부 리소스 누수 |
| 8 | ble-008 | unref가 정상 경로에만 | 에러 경로에서 conn ref leak |
| 9 | esp-gpio-001 | `for(volatile int i=0;i<999999;i++);` | busy-wait — vTaskDelay도 Arduino delay도 아님 |
| 10 | timer-007 | period = timeout - 1 | 기술적으로 < 이지만 마진 1ms |
| 11 | stm32-002 | `xQueueSendFromISR(q, &v, NULL)` | FromISR 맞지만 wake 플래그 NULL |
| 12 | watchdog-005 | check→clear→feed 순서 (clear가 check 바로 뒤) | race condition window |
| 13 | gpio-001 | `device_is_ready(dev);` return 무시 | 함수 호출은 있지만 결과 미사용 |
| 14 | sensor-003 | sleep이 에러 경로에만 | 정상 루프에서 busy-poll |
| 15 | linux-001 | error 체크 있지만 fallthrough | `if(ret) printk("err");` 후 계속 |

---

## 프레임워크 변경

`negatives.py`에 새 필드 `"should_fail"` 추가:

```python
NEGATIVES = [
    # 기존: must_fail (반드시 잡혀야)
    {"name": "...", "mutation": ..., "must_fail": [...]},

    # 신규: should_fail (잡히면 좋지만, 못 잡으면 blind spot 기록)
    {"name": "...", "mutation": ..., "should_fail": [...],
     "bug_description": "왜 이 코드가 틀린지"},
]
```

`test_negatives.py` 수정:
- `must_fail`: assert → 실패하면 테스트 FAIL (기존)
- `should_fail`: 결과 기록 → PASS해도 테스트는 성공하지만 blind spot 리포트

---

## Success Criteria

- [ ] 15개 subtle mutation 작성
- [ ] ~50%가 현재 체크에 잡히지 않음 (blind spot 발견)
- [ ] Blind spot 리포트 생성
- [ ] INSIGHTS.md에 #11 추가 (check precision 실측)
- [ ] 기존 794 test 유지
