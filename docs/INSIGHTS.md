# EmbedEval Insights

벤치마크와 TC 개발 과정에서 발견한 핵심 인사이트를 누적 기록한다.

---

## #1. Implicit vs Explicit Gap (2026-03-24)

**발견:** LLM은 프롬프트에 명시하면 거의 다 맞추지만, 암묵적 도메인 지식은 빠뜨린다.

| 요구 방식 | 예시 | Sonnet 통과율 |
|-----------|------|--------------|
| Explicit | "volatile 써라", "cache flush 해라" | ~95% |
| Implicit | ISR 공유 변수→volatile, init 실패→cleanup | ~60% |

**근거:**
- 16개 심층 체크 (volatile, barrier, alignment 등)를 프롬프트에 명시한 상태로 검증 → 15/16 통과
- 기존 200 TC에서 암묵적으로 요구한 동일 패턴 → 18건 실패

**TC 설계 원칙:**
- 나쁜 TC: "volatile int flag를 선언하고 ISR에서 설정해라" → 복사하면 통과
- 좋은 TC: "ISR과 메인 스레드 간에 flag로 통신하라" → 도메인 지식 필요

**시사점:** 현재 벤치마크가 LLM 능력을 ~35%p 과대평가할 가능성.

---

## #2. General SW vs Embedded-Specific Failures (2026-03-24)

**발견:** LLM 실패의 56%는 임베디드 고유가 아닌 일반 SW 문제.

| 유형 | 건수 | 대표 패턴 |
|------|------|----------|
| General SW | 10 (56%) | 에러 경로 cleanup, 반환값 무시, alloc/free 불균형 |
| Embedded | 8 (44%) | HW cyclic vs SW reload, device_ready 누락, 타이밍 마진 |

**핵심:** linux-driver가 같은 패턴(init_error_path_cleanup)으로 3건을 차지해서
General SW가 많아 보이는 것. 실제로는 임베디드 체크가 아직 얕아서 Embedded 실패가
적게 잡히는 것이 원인.

**시사점:** LLM의 임베디드 코드 품질 개선은 (1) 일반적 에러 처리 능력 향상이 먼저,
(2) 그 다음이 HW 의미론 이해.

---

## #3. LLM Failure Taxonomy — 6 Patterns (2026-03-24)

**발견:** 21건 실패(TC 버그 3건 제외 = 18건)를 6개 패턴으로 분류 가능.

| # | 패턴 | 건수 | 핵심 |
|---|------|------|------|
| 1 | Happy Path 편향 | 7 | 정상 경로만 구현, 에러 cleanup 누락 |
| 2 | 의미론적 맥락 무시 | 5 | 컴파일되지만 HW 의미가 틀림 |
| 3 | 리소스 균형 실패 | 2 | alloc만 하고 free 안 함 (데모 마인드) |
| 4 | 순서 의존성 위반 | 2 | init→register→use 순서 오류 |
| 5 | 매직 넘버 | 1 | 상수를 이름 없이 반복 사용 |
| 6 | 운영 루프 미구현 | 1 | 한 번 체크하고 끝 (주기적 모니터링 필요) |

**#1이 압도적** — 에러 경로 cleanup이 LLM의 최대 약점. 원인: 순방향 토큰 생성이
역순 의존성 추적에 구조적으로 불리.

---

## #4. Implicit Knowledge 4-Level Model (2026-03-24)

**발견:** LLM이 빠뜨리는 암묵적 지식을 4단계로 체계화할 수 있다.

| Level | 누가 아는가 | 예시 | TC 커버리지 |
|-------|-----------|------|-----------|
| L1 C언어 | C 전문가 | volatile, const, named constants, cleanup | ~50% |
| L2 RTOS | RTOS 개발자 | ISR blocking 금지, spinlock vs mutex, K_NO_WAIT | ~70% |
| L3 HW | 임베디드 전문가 | cache alignment ≥32, flush/invalidate, timing margin | ~40% |
| L4 안전 | 시스템 엔지니어 | OTA rollback, 역순 cleanup, fail-fast, conditional WDT feed | ~30% |

**시사점:** Level이 높을수록 LLM이 더 실패하고, 현재 TC 커버리지도 낮다.
Level 3-4 체크를 강화하면 벤치마크 변별력이 크게 올라갈 것.

---

## #5. Syntactic vs Behavioral Gap (2026-03-24)

**발견:** LLM은 구문적 정확성에서는 거의 완벽하지만, 행동적 정확성에서 실패한다.

```
L0 Static (구문):     99.5%
L1 Compile (빌드):    100%
L2 Runtime (실행):    100%
L3 Behavioral (행동): 90%   ← 여기서 갈림
```

**시사점:** "컴파일되고 실행되는 코드"와 "프로덕션에서 안전한 코드"의 차이를
LLM은 구분하지 못한다. 벤치마크가 L0-L2만 측정하면 LLM 능력을 과대평가.
L3 체크가 진짜 변별기.

---

## #6. Implicit Prompt Rewrite — Partial Validation (2026-03-24)

**실험:** 16개 프롬프트에서 explicit safety hint 제거 후 Sonnet 재벤치마크.

**수정한 힌트 유형:**
- `volatile int flag` → "callback과 main이 공유하는 flag"
- `__aligned(32)` → "DMA에 적합한 alignment 보장"
- `copy_to_user()` → "안전하게 user space로 데이터 전송"
- `k_spinlock` → "ISR-safe 동기화"
- `compiler_barrier()` → "메모리 순서 보장"
- `device_is_ready()` → "디바이스 초기화 확인"

**부분 결과 (50/200 cases, 벤치마크 중간 타임아웃):**

| 구간 | Before (Explicit) | After (Implicit) | 변화 |
|------|-------------------|------------------|------|
| ble (10) | 10/10 | 10/10 | 변화 없음 (수정 안 함) |
| boot (10) | 10/10 | 10/10 | 변화 없음 (수정 안 함) |
| device-tree (10) | 10/10 | 10/10 | 변화 없음 (수정 안 함) |
| dma (10) | 9/10 | **8/10** | **dma-004 NEW FAIL** |
| gpio-basic (10) | 9/10 | **8/10** | **gpio-basic-007 NEW FAIL** |

**새로 실패한 케이스:**
- **dma-004**: 프롬프트에서 hint 제거 → 새로운 behavioral check 실패
- **gpio-basic-007**: 프롬프트에서 hint 제거 → 새로운 behavioral check 실패

**초기 결론:**
- 수정된 카테고리(dma, gpio)에서 실패율 상승 확인
- 수정 안 한 카테고리(ble, boot, device-tree)는 변화 없음 (대조군)
- 50건 기준 pass@1: 92% → 92% (전체는 변화 적지만, 수정된 카테고리만 보면 90%→80%)
- **전체 200건 재벤치마크 필요** — isr-concurrency에서 타임아웃 발생, 재시도 필요

**임시 결론:** Implicit 프롬프트가 변별력을 높이는 방향으로 작동하는 것은 확인됨.
다만 16개만 수정해서 전체 pass@1 변화는 아직 미미. 더 많은 프롬프트 수정 필요.
