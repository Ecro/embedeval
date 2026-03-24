# Insight: Implicit vs Explicit Knowledge in LLM Embedded Code

**Date:** 2026-03-24
**Source:** Sonnet 200-case benchmark + 16 deep embedded check experiment

---

## Core Discovery

LLM의 임베디드 코드 품질은 **프롬프트에 요구사항이 명시적인지 암묵적인지**에 따라
극적으로 갈린다.

```
명시적 요구: "volatile 키워드를 써라"     → Sonnet 통과율 ~95%
암묵적 요구: (ISR 공유 변수니까 당연히)    → Sonnet 통과율 ~60%
```

### 실험 결과

**실험 1: 기존 TC (암묵적 요구)**
- 200 cases, 프롬프트에 에러 처리/volatile/cleanup을 명시 안 함
- pass@1 = 91% (182/200)
- 18건 실패 — 모두 "프롬프트에 안 쓰였지만 당연히 해야 하는" 패턴

**실험 2: 심층 체크 추가 (프롬프트에 명시된 패턴 검증)**
- 16개 deep embedded checks (volatile, barrier, alignment, ISR priority 등)
- 15/16 통과 — **프롬프트에 요구하면 거의 다 맞춤**
- 1건만 실패 (magic number — 이것도 암묵적 요구)

### 결론

| 요구 방식 | 예시 | Sonnet 통과율 |
|-----------|------|--------------|
| **Explicit** (프롬프트에 직접 언급) | "volatile 써라", "cache flush 해라" | ~95% |
| **Implicit** (도메인 지식에서 도출) | ISR 공유 변수→volatile, init 실패→cleanup | ~60% |

---

## Why This Matters

### 1. TC 설계 원칙

**나쁜 TC:** "volatile int flag를 선언하고 ISR에서 설정해라"
→ LLM이 그대로 복사 → 통과 → 변별력 없음

**좋은 TC:** "ISR과 메인 스레드 간에 flag로 통신하라"
→ LLM이 volatile을 스스로 추론해야 함 → 도메인 지식 검증

### 2. 벤치마크 설계 원칙

```
                    프롬프트
                    ┌─────────────────────────────┐
                    │ "DMA callback에서 에러 시    │
                    │  flag 설정하고 main에서 체크" │
                    │                             │
                    │  (volatile은 언급 안 함)      │
                    └─────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
               LLM A (전문가)        LLM B (초급)
               volatile int flag    int flag
               ✅ PASS              ❌ FAIL
```

**핵심:** 프롬프트는 "무엇을 하라"만 말하고, "어떻게 안전하게 하라"는 말하지 않아야 함.

### 3. 실무 활용 원칙

LLM을 임베디드 개발에 활용할 때:

| LLM이 잘하는 것 | LLM이 못하는 것 |
|----------------|----------------|
| 명시된 API 패턴 따르기 | 암묵적 안전 규칙 도출 |
| 보일러플레이트 코드 생성 | 에러 경로 설계 |
| 프롬프트의 요구사항 구현 | "당연히 해야 하는" 것 추론 |
| 단일 함수 구현 | 크로스-컨텍스트 제약 (ISR↔Thread) |

---

## Implicit Knowledge Categories

LLM이 빠뜨리는 암묵적 지식을 체계화하면:

### Level 1: 언어 수준 (C 전문가라면 아는 것)
- `volatile` on shared variables
- `const` correctness
- Named constants instead of magic numbers
- Resource cleanup on all exit paths

### Level 2: OS 수준 (RTOS 개발자라면 아는 것)
- ISR에서 blocking API 금지
- k_spin_lock (ISR) vs k_mutex (thread) 구분
- K_NO_WAIT in ISR, K_FOREVER in thread
- Stack size ≥ 2048 for work queues

### Level 3: HW 수준 (임베디드 전문가라면 아는 것)
- DMA 버퍼 cache line alignment (≥ 32)
- Cache flush before DMA TX, invalidate after DMA RX
- Timer period < WDT timeout (timing margin)
- device_is_ready() before any HW access
- Memory barriers in lock-free code

### Level 4: 안전 수준 (시스템 엔지니어라면 아는 것)
- OTA rollback path on download failure
- Error path cleanup in reverse allocation order
- Fail-fast in security code (no flag accumulation)
- Conditional WDT feed (health monitoring, not blind feed)

**현재 TC 커버리지:**
- Level 1: ~50% (magic number, cleanup 일부)
- Level 2: ~70% (ISR forbidden 잘 테스트됨)
- Level 3: ~40% (cache/alignment 일부만)
- Level 4: ~30% (OTA rollback, cleanup 일부)

---

## TC Design Methodology: "Implicit Requirement Injection"

### Before (기존 방식)
```
Prompt: "DMA 전송 구현. __aligned(32) 버퍼 사용.
         콜백에서 volatile flag 설정.
         에러 시 dma_stop 호출."

Check: __aligned 있는지, volatile 있는지, dma_stop 있는지
```
→ 프롬프트를 복사하면 통과 → 변별력 없음

### After (암묵적 요구 방식)
```
Prompt: "DMA 전송 구현. src→dst 복사.
         콜백에서 완료/에러 구분.
         main에서 결과 확인."

Check: __aligned 있는지, volatile 있는지, dma_stop 있는지,
       cache flush/invalidate 있는지, error flag 동기화 순서
```
→ 도메인 지식이 있어야 통과 → 진짜 변별력

### Methodology

1. **기능 요구만 명시**: "ISR과 thread 간 counter 공유"
2. **안전 요구는 생략**: volatile, spinlock, error handling 언급 안 함
3. **레퍼런스에는 포함**: 레퍼런스 솔루션은 모든 안전 패턴 포함
4. **체크에서 검증**: behavior.py가 암묵적 패턴 체크
5. **결과**: LLM이 도메인 지식 보유 여부로 변별

---

## Quantified Impact

| 메트릭 | Explicit TC | Implicit TC | 차이 |
|--------|------------|------------|------|
| Sonnet pass@1 | ~95% | ~60% | **35%p** |
| 변별력 (모델 간 차이) | 낮음 | 높음 | |
| 실무 예측력 | 낮음 | 높음 | |
| TC 작성 난이도 | 낮음 | 높음 | |

**35%p 차이**는 같은 LLM이 같은 코드를 생성하는데, 프롬프트 작성 방식만으로
pass@1이 95%→60%로 떨어진다는 것. 즉, **현재 벤치마크가 LLM 능력을 35%p
과대평가**하고 있을 가능성이 높다.

---

## Action Items

1. **단기**: 기존 100% 카테고리 프롬프트에서 explicit hint 제거
2. **중기**: 전 카테고리 프롬프트를 "기능만 명시" 방식으로 재작성
3. **장기**: Implicit Level 1-4별 pass@1 측정 → LLM 도메인 지식 레벨 정량화

---

## Related Documents

- [Benchmark Analysis](./BENCHMARK-ANALYSIS-2026-03-24.md) — 21건 실패 상세 분석
- [LLM Failure Patterns](../memory/llm-embedded-failure-patterns.md) — 7대 실패 영역
- [PLAN: Deep Embedded Checks](../plans/PLAN-deep-embedded-checks.md) — 심층 체크 구현 계획
