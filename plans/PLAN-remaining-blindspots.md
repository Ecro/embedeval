# PLAN: Remaining 6 Blind Spots — Precision 60% → 80%+

**Project:** embedeval
**Created:** 2026-03-26

---

## 6 Remaining Blind Spots

### 1. dma-008: error_detected_but_no_return
**문제:** `should_fail` 타겟이 `error_flag_read_after_sync`인데, 이 체크는 위치만 확인.
새로 추가한 `error_flag_causes_return`은 이걸 잡을 수 있지만 negatives.py가 이 체크를 타겟하지 않음.
**수정:** negatives.py의 should_fail을 `error_flag_causes_return`으로 변경.

### 2. isr-003: spinlock_key_hardcoded_zero
**문제:** `key_passed_to_unlock` 체크가 `k_spinlock_key_t` 변수명 존재만 확인.
mutation은 `key = k_spin_lock(...)` 대신 `k_spin_lock(...); key = {0};`으로 바꿈.
**수정:** `key_passed_to_unlock` 체크를 강화 — `key = k_spin_lock(` 패턴 확인 (대입문에서 반환값 저장).

### 3. linux-001: partial_cleanup_only
**문제:** mutation이 `unregister_chrdev_region`을 주석처리하지만, `__exit` 함수에 같은 호출이 있어서 체크 통과.
**수정:** `init_error_path_cleanup`이 `__init` 함수 범위 내에서만 확인하도록 이미 수정했으나, mutation이 다른 방식으로 우회.
→ negatives.py mutation을 다시 확인하고 정확히 뭐가 통과하는지 디버그.

### 4. linux-001: error_check_no_return
**문제:** 첫 번째 `return ret;`만 제거하는데, 다른 error block의 return이 남아있어서 체크 통과.
**수정:** error block 내 return 존재를 체크하는 로직 추가. 또는 mutation을 더 정확하게.

### 5. stm32-002: from_isr_with_null_wake_flag
**문제:** `isr_yield_after_queue_send` 체크가 `portYIELD_FROM_ISR` 존재만 확인.
NULL을 넘겨도 매크로 자체는 있으므로 통과.
**수정:** `BaseType_t` 또는 `higher_priority_woken` 변수 선언 확인 추가.

### 6. watchdog-005: check_and_clear_race (CHECK_NOT_FOUND)
**문제:** negatives.py가 타겟하는 체크명 `feed_conditional_not_unconditional`이 behavior.py에 없음.
**수정:** 실제 체크명을 확인하고 negatives.py 수정.

---

## 수정 전략

| # | 수정 유형 | 파일 |
|---|----------|------|
| 1 | negatives.py 타겟 변경 | dma-008/checks/negatives.py |
| 2 | 체크 강화 | isr-003/checks/behavior.py |
| 3 | 디버그 + 체크/mutation 수정 | linux-001 |
| 4 | 체크 추가 (error block return) | linux-001/checks/behavior.py |
| 5 | 체크 추가 (wake flag 변수) | stm32-002/checks/behavior.py |
| 6 | negatives.py 체크명 수정 | watchdog-005/checks/negatives.py |
