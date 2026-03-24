# PLAN: Deep Embedded Checks — "Last Exam"

**Project:** embedeval
**Created:** 2026-03-24
**Estimated Time:** 3-4 hours
**Files Changed:** ~30 files (10 new behavior.py + 10 new prompt.md + 10 reference/main.c)

---

## Executive Summary

> **TL;DR:** 기존 200 TC가 Sonnet 91%를 달성하는 건 "임베디드 초급" 체크만 있기 때문.
> HW 메모리 모델, ISR 컨텍스트 제약, 실시간 타이밍, 리소스 정렬 같은 **심층 임베디드
> 지식**을 테스트하는 체크를 추가하여 "진짜 임베디드 전문가만 맞출 수 있는" 난이도로
> 올린다. 기존 10개 카테고리의 기존 케이스에 더 어려운 체크를 추가하는 방식.

### 핵심 전략

기존 200 케이스에 **새 TC를 추가하지 않고**, 기존 hard 케이스(007-010)의
behavior.py에 심층 체크를 추가한다. 이유:

1. 프롬프트와 레퍼런스는 이미 deep 패턴을 포함하고 있음 (volatile, aligned 등)
2. 체크만 약해서 Sonnet이 통과하는 것
3. 새 TC 추가보다 기존 TC 강화가 효율적

---

## Gap Analysis: 현재 vs 목표

| Concept | 현재 상태 | 목표 |
|---------|----------|------|
| **volatile on shared vars** | 프롬프트에 있지만 체크 안 함 (50 files) | ISR/callback 공유 변수에 volatile/atomic 체크 |
| **Memory barrier** | isr-008 프롬프트에만 언급, 체크 0 | compiler_barrier()/\_\_dmb() 존재 체크 |
| **Cache coherency** | dma-005만 체크 | DMA 케이스 전반으로 확대 |
| **Buffer alignment** | dma-005/006만 \_\_aligned 체크 | DMA 버퍼에 alignment 필수 체크 |
| **ISR forbidden** | isr-004만 extract_function_body | 더 많은 케이스에 ISR body 검사 |
| **Timing margin** | timer-007만 수치 비교 | watchdog, sensor 폴링에도 마진 체크 |
| **Init error rollback** | linux-driver-001만 error block 분석 | ota, networking init에도 확대 |
| **Priority inversion** | 0 coverage | threading에 mutex+priority 체크 |
| **SYS_INIT ordering** | 0 coverage | boot/device-tree에 init level 체크 |
| **Lock-free correctness** | isr-008에 프롬프트만 | atomic acquire/release 순서 체크 |

---

## Implementation Plan: 10 Cases × Deep Checks

### Phase 1: ISR & Concurrency Deep Checks (3 cases)

#### 1-1. isr-concurrency-003: volatile on shared counter

**현재:** k_spinlock 사용 여부만 체크
**추가 체크:**
- `shared_var_volatile_or_atomic`: ISR과 스레드 양쪽에서 접근하는 변수가
  `volatile` 또는 `atomic_t`로 선언됐는지 확인
- Implementation: `counter` 또는 `shared` 이름의 전역 변수 찾기 →
  선언부에서 `volatile` 또는 `atomic_t` 존재 체크

#### 1-2. isr-concurrency-008: memory barrier validation

**현재:** 프롬프트에 barrier 언급하지만 체크 없음
**추가 체크:**
- `memory_barrier_present`: lock-free SPSC 큐에서 `compiler_barrier()` 또는
  `__DMB()` 또는 `atomic_thread_fence` 존재 체크
- `produce_index_after_data`: 데이터 기록 후 인덱스 업데이트 순서
  (barrier가 이 순서를 강제해야 함)

#### 1-3. isr-concurrency-007: ISR priority differentiation

**현재:** IRQ_CONNECT 존재 + 우선순위 다른지만 체크
**추가 체크:**
- `higher_priority_irq_shorter_handler`: 높은 우선순위 IRQ의 핸들러가
  낮은 우선순위보다 짧아야 함 (함수 길이 비교)
- `no_shared_state_without_protection`: 두 ISR이 같은 변수에 접근하면
  spinlock 또는 irq_lock 필요

### Phase 2: DMA & Memory Deep Checks (3 cases)

#### 2-1. dma-006: cache + alignment combined

**현재:** \_\_aligned(32) 존재만 체크
**추가 체크:**
- `cache_flush_before_dma_start`: `sys_cache_data_flush_range()` 호출이
  `dma_start()` 또는 `dma_config()` **전**에 위치 (순서 체크)
- `cache_invalidate_in_callback`: DMA 완료 콜백 내에서
  `sys_cache_data_invd_range()` 호출 (함수 본문 내 체크)
- `alignment_value_cache_line`: alignment 값이 32 이상 (캐시 라인 크기)

#### 2-2. dma-008: volatile DMA error flag

**현재:** volatile int dma_error_flag 존재만 체크
**추가 체크:**
- `error_flag_checked_in_main`: main 함수에서 dma_error_flag를 체크하는
  if문 존재 확인 (선언만 하고 안 읽는 패턴 방지)
- `callback_sets_flag_on_error`: DMA 콜백 내에서 status < 0일 때
  error flag를 설정하는 패턴 (함수 본문 내 체크)

#### 2-3. memory-opt-004: stack canary & overflow detection

**현재:** 기본 체크만
**추가 체크:**
- `stack_sentinel_or_canary`: 스택 보호 패턴 존재 —
  `CONFIG_STACK_SENTINEL=y` 또는 `CONFIG_STACK_CANARIES=y` 또는
  수동 canary 체크 코드
- `no_vla_in_embedded`: Variable-Length Array 금지 —
  `[size]` 패턴에서 size가 const가 아닌 경우 감지

### Phase 3: Threading & Scheduling Deep Checks (2 cases)

#### 3-1. threading-008: priority inversion awareness

**현재:** 기본 mutex 체크만
**추가 체크:**
- `mutex_not_spinlock_in_thread`: 스레드 간 동기화에 k_mutex 사용
  (k_spin_lock은 ISR용) — 현재 반대 방향만 체크됨
- `thread_priorities_distinct`: 모든 스레드의 우선순위가 서로 다른지 체크
  (같은 우선순위 = 스케줄링 비결정성)
- `higher_priority_thread_has_shorter_work`: 높은 우선순위 스레드의
  작업이 짧아야 함 (긴 작업 = 우선순위 역전 유발)

#### 3-2. threading-010: work queue error handling

**현재:** 기본 체크만
**추가 체크:**
- `work_handler_return_void`: 워크 핸들러가 void 반환 — 에러 코드를
  반환하면 작업 큐가 처리할 수 없음
- `no_infinite_reschedule_without_condition`: 워크 핸들러가 무조건
  자기 자신을 재스케줄하면 CPU를 독점 — 조건부 재스케줄 필요

### Phase 4: Timer & Watchdog Deep Checks (2 cases)

#### 4-1. watchdog-005: multi-thread WDT feed coordination

**현재:** 기본 체크만
**추가 체크:**
- `all_threads_report_health`: 각 스레드가 health flag를 설정하고,
  supervisor가 **모든** flag를 확인한 후에만 WDT feed
- `health_flags_are_atomic`: health flag가 atomic_t로 선언됨
  (volatile만으로는 부족 — read-modify-write race)
- `supervisor_clears_flags`: feed 후 flag 초기화
  (안 하면 정지된 스레드를 감지 못함)

#### 4-2. timer-006: timer callback not blocking

**현재:** 기본 체크만
**추가 체크:**
- `timer_callback_no_blocking`: 타이머 콜백 본문에서 k_sleep,
  k_mutex_lock, k_sem_take(K_FOREVER) 금지 (ISR 컨텍스트와 동일 제약)
- `timer_period_not_zero`: K_MSEC(0) 또는 period=0 방지
  (0이면 one-shot인데 periodic으로 착각하는 패턴)

---

## Success Criteria

### Quantitative
- [ ] 기존 685 pytest 전부 통과 (레퍼런스 솔루션이 새 체크 통과)
- [ ] 심층 체크 총 25+ 개 추가
- [ ] 6개 이상 카테고리에 심층 체크 분포

### Qualitative
- [ ] 각 심층 체크가 "컴파일은 되지만 의미적으로 틀린" 패턴을 감지
- [ ] 체크가 false positive 없음 (레퍼런스 통과 확인)
- [ ] 체크 이름만 봐도 무엇을 테스트하는지 알 수 있음

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| 레퍼런스 솔루션이 심층 패턴을 안 가지고 있을 수 있음 | High | 먼저 레퍼런스 읽고, 없으면 레퍼런스도 수정 |
| 체크 regex가 LLM의 다양한 코드 스타일을 못 잡음 | Medium | 여러 변형 패턴을 regex에 포함 |
| false positive로 정상 코드를 실패 처리 | High | 레퍼런스 + 벤치마크 LLM 코드 둘 다 검증 |

---

## Testing Strategy

각 체크 추가 후:
1. `uv run pytest tests/ -x -q` — 레퍼런스 통과 확인
2. 벤치마크 저장된 LLM 코드로 체크 실행 — 적절한 실패 확인
3. 전체 추가 완료 후 Sonnet 재벤치마크 — pass@1 하락 확인

---

## Execution Order

```
Phase 1: ISR & Concurrency (isr-003, isr-008, isr-007)
  ↓
Phase 2: DMA & Memory (dma-006, dma-008, memory-opt-004)
  ↓
Phase 3: Threading (threading-008, threading-010)
  ↓
Phase 4: Timer & Watchdog (watchdog-005, timer-006)
  ↓
Final: pytest + 재벤치마크
```
