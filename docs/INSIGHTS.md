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

---

## #7. "Embedded Last Exam" 비판적 자기 분석 (2026-03-24)

**방법:** 임베디드 전문가 + LLM 벤치마크 전문가 관점에서 COT 분석.

### 치명적 비판 (Show-stopper)

**S1. 코드를 컴파일 안 하는 "코드 벤치마크"**
L1/L2 비활성. `"volatile" in code` regex를 "behavioral check"라 부르는 건 overclaiming.
진짜 behavioral = QEMU 실행 + ThreadSanitizer + 타이밍 측정.
컴파일도 안 해본 코드의 pass@1은 의미가 약하다.

**S2. 재현 불가능한 단일 시행**
pass@1, 1회. LLM은 stochastic → 같은 실험을 다시 돌리면 다른 결과.
n=10/카테고리에서 1건 변동 = 10%p 차이. confidence interval 없는 "91%"는 통계적으로 무의미.

### 심각한 비판 (Major)

**M1. Construct Validity: "임베디드 능력" ≠ "API 암기"**
프롬프트가 API를 알려주면 95%, 안 알려주면 60%. 이건 "프롬프트 따르기"이지
"도메인 지식"이 아니다. 진짜 임베디드 = 데이터시트 + 회로 + 빌드시스템 + 디버깅인데
이 중 아무것도 테스트 안 함.

**M2. 플랫폼 편향: "Embedded" ≠ "Zephyr"**
200 TC 중 Zephyr가 90%+. ESP-IDF, STM32 HAL, bare-metal, AUTOSAR는 0.
"Embedded 벤치마크"가 아니라 "Zephyr RTOS 벤치마크"가 정직한 이름.

**M3. Human Baseline 없음**
"91%"가 좋은지 나쁜지 모름. 주니어가 95% 맞추면 Sonnet은 주니어보다 못한 것.
비교 대상 없는 절대 점수는 의미 없다.

**M4. 프롬프트 민감도 = 측정 불안정성**
프롬프트 문구만 바꿔도 점수가 달라진다. 좋은 벤치마크는 합리적 변형에 robust해야 함.
단, implicit TC는 의도적 설계(도메인 지식 측정 목표)이므로 이건 양면이 있다.

**M5. Toy 복잡도: 50줄 단일 파일**
실제 프로젝트: 수만 줄, 수십 모듈. EmbedEval은 "함수 하나"이지 "시스템 설계"가 아님.

### 중요한 비판 (Moderate)

- **D1. Binary 채점**: 10개 체크 중 9개 통과해도 FAIL. 부분 점수 없음.
- **D2. Check 정확도 미검증**: 의도적 오답→FAIL 확인(negative test) 안 함.
- **D3. 벤치마크 오염**: public repo + reference solution 노출.
- **D4. 평가자 편향**: 단일 관점의 TC/체크. 다른 전문가가 만들면 다른 결과.

### 공정한 반론

| 비판 | 반론 |
|------|------|
| 200문제 부족 | EmbedAgent(ICSE 2026)는 59문제. 임베디드 특화로는 많은 편 |
| L3 static 무의미 | 코드 리뷰도 static 분석. volatile 누락은 regex로도 잡을 가치 있음 |
| Single-shot 비현실적 | HumanEval 등 대부분의 코드 벤치마크가 single-shot |
| "Last Exam" 과장 | first mover value — 임베디드 LLM 벤치마크 자체가 거의 없음 |

### 정직한 Positioning

| 과장 | 정직한 대안 |
|------|-----------|
| "Embedded Last Exam" | "Zephyr RTOS 코드 생성 벤치마크" |
| "Behavioral evaluation" | "Static pattern heuristics" |
| "pass@1 = 91%" | "pass@1 = 91% (single run, n=10/cat)" |
| "LLM embedded capability" | "API recall + safety pattern awareness" |

### 우선순위화된 개선 로드맵

| 순위 | 개선 | 효과 | 난이도 |
|------|------|------|--------|
| 1 | L1/L2 활성화 (Docker + west build) | 신뢰성 극적 향상 | High |
| 2 | pass@5 또는 3회 반복 평균 | 통계적 유의성 | Low |
| 3 | Human baseline (주니어 1명) | 절대 점수 의미 부여 | Medium |
| 4 | L3 명칭 → "static_heuristic" | 정직한 프레이밍 | Trivial |
| 5 | 부분 점수제 (weighted scoring) | 세밀한 모델 비교 | Medium |
| 6 | Private test set 분리 | 오염 방지 | Medium |
| 7 | Multi-platform (ESP-IDF 추가) | 범위 확대 | High |

---

## #8. Cross-Benchmark Comparison Strategy (2026-03-24)

**발견:** Human baseline 대신 기존 공개 코딩 벤치마크와 비교하면 더 효과적.

### 핵심 아이디어

모델 출시 시 공개되는 일반 코딩 벤치마크 (HumanEval, MBPP, SWE-bench)와
EmbedEval 점수를 나란히 놓으면, **"일반 코딩 → 임베디드 코딩"의 성능 하락폭(Gap)**
자체가 모델의 도메인 전문성을 나타냄.

```
Model       | HumanEval | SWE-bench | EmbedEval | Embed Gap
------------|-----------|-----------|-----------|----------
Sonnet 4.6  |   93.7%   |   72.2%   |    ??%    | -??.?%p
Haiku 4.5   |   84.0%   |   48.2%   |    ??%    | -??.?%p
GPT-4o      |   92.0%   |   66.0%   |    ??%    | TBD
```

### 왜 Human Baseline보다 나은가

| 비교 방식 | 장점 | 단점 |
|-----------|------|------|
| Human baseline | 절대적 의미 부여 | 사람 구하기 어려움, 1명이면 편향, 재현 불가 |
| Cross-benchmark | 데이터 이미 공개됨, 모델마다 비교 가능, 재현 가능 | 벤치마크 간 난이도 차이 보정 필요 |

### 핵심 메트릭: "Embedded Gap"

```
Embedded Gap = EmbedEval pass@1 - HumanEval pass@1
```

- Gap이 작을수록 → 모델이 임베디드 도메인에도 강함
- Gap이 클수록 → 일반 코딩은 잘하지만 임베디드 특화 지식 부족
- 모델 간 Gap 비교로 "어떤 모델이 임베디드에 더 적합한지" 판단 가능

### 구현 방향

1. **LEADERBOARD.md에 공개 벤치마크 점수 참조 컬럼 추가**
2. **Embedded Gap 자동 계산** (외부 점수는 수동 입력 또는 config)
3. **모델별 Gap 비교 차트** (markdown 테이블로)

### 활용 시나리오

"Sonnet은 HumanEval 93.7%인데 EmbedEval은 85%라 Gap이 -8.7%p.
반면 Haiku는 HumanEval 84%인데 EmbedEval은 60%라 Gap이 -24%p.
→ Sonnet이 임베디드에서 상대적으로 강하다."

이런 분석이 가능해짐. Human baseline 1명 구하는 것보다 훨씬 신뢰성 있음.

---

## #9. Sonnet 재벤치마크 결과 — Before vs After (2026-03-25)

**변경 사항 적용 후 첫 완전한 재벤치마크.**

### 결과

| 항목 | Before (explicit, 200 TC) | After (implicit + deep, 210 TC) |
|------|--------------------------|--------------------------------|
| pass@1 | 91.0% (182/200) | **89.5% (188/210)** |
| Failures | 18 | **22** |
| 100% categories | 6 | **4** (ble, boot, kconfig, yocto) |
| Embed Gap | N/A | **-4.2%p** (vs HumanEval 93.7%) |

### 새로운 실패 (implicit/deep check 효과)

| Case | 원인 |
|------|------|
| device-tree-003 | 새 behavioral check |
| isr-concurrency-003 | deep check (spinlock) |
| isr-concurrency-008 | barrier 순서 체크 |
| spi-i2c-004 | 새 check |
| storage-004 | 새 check |
| timer-006 | implicit 전환 (device_is_ready 제거) |
| watchdog-010 | private case |
| threading-008 | deep check (magic number) |
| esp-adc-001, esp-nvs-001 | 신규 ESP-IDF (LLM이 ESP API 혼동) |

### 핵심 해석

1. **100% 카테고리 6→4개** — device-tree, isr-concurrency가 떨어짐. 체크 강화 효과 확인.
2. **Embed Gap = -4.2%p** — 예상(-8~-15%p)보다 작음. L3가 static heuristic이라 실제 behavioral 오류를 놓치는 것이 원인. L1/L2 활성화 시 Gap 확대 예상.
3. **ESP-IDF 2/10 실패 (80%)** — Zephyr(~90%)보다 낮음. 학습 데이터에 ESP-IDF가 적기 때문.
4. **isr-concurrency 90%→80%** — deep check(spinlock, barrier) 추가가 가장 효과적이었음.

---

## #10. Sonnet vs Haiku — Cross-Model Comparison (2026-03-25)

**최초의 모델 간 비교. 벤치마크의 변별력 검증.**

### 결과

| Metric | Sonnet | Haiku | Delta |
|--------|--------|-------|-------|
| pass@1 | 89.5% | **78.1%** | **-11.4%p** |
| Failures | 22/210 | 46/210 | +24 |
| Embed Gap (vs HumanEval) | -4.2%p | **-5.9%p** | -1.7%p |

### 카테고리별 격차 (큰 순)

| Category | Sonnet | Haiku | Delta | 해석 |
|----------|--------|-------|-------|------|
| spi-i2c | 92% | 58% | **-34%p** | HW 프로토콜 지식 부족 |
| device-tree | 90% | 60% | **-30%p** | DT 문법 혼동 |
| ble | 100% | 73% | **-27%p** | BLE 스택 API 복잡도 |
| timer | 91% | 64% | **-27%p** | 타이밍 제약 무시 |
| isr-concurrency | 80% | 60% | **-20%p** | ISR 동시성 규칙 |
| dma | 90% | 70% | **-20%p** | 캐시/정렬 패턴 |
| boot | 100% | 100% | 0 | Kconfig는 크기 무관 |
| kconfig | 100% | 100% | 0 | 단순 설정 — 쉬움 |
| linux-driver | 80% | 80% | 0 | error cleanup은 크기 무관 |
| threading | 90% | 90% | 0 | 기본 스레드 패턴 |

### 핵심 발견

1. **전체 11.4%p 차이** — EmbedEval이 모델 크기별 차이를 잘 변별함.
2. **HW 관련 카테고리에서 격차 최대** — spi-i2c(-34%p), device-tree(-30%p), ble(-27%p).
   작은 모델일수록 HW 프로토콜/문법 지식이 부족.
3. **소프트웨어 패턴 카테고리는 격차 없음** — boot, kconfig, linux-driver, threading.
   이건 일반 SW 지식으로 풀 수 있는 문제라 모델 크기가 덜 중요.
4. **Embed Gap: Sonnet -4.2%p vs Haiku -5.9%p** — Haiku가 임베디드에서 상대적으로 더 약함.
   하지만 차이(1.7%p)가 예상보다 작음 — L3 static heuristic의 한계.
5. **Haiku도 boot/kconfig 100%** — 이 카테고리는 모든 모델이 풀 수 있는 수준.
   벤치마크 변별력의 바닥(floor)을 나타냄.

### 시사점

- **EmbedEval은 모델 간 변별력이 있다** — Sonnet vs Haiku에서 11.4%p 차이 확인.
- **HW 도메인 지식이 변별기** — SW 패턴(boot, kconfig)은 차이 없고, HW 관련(spi, dt, ble)에서 차이 극대화.
- **L1/L2 활성화 시 Gap이 더 벌어질 것** — Haiku의 코드가 컴파일 실패하는 경우가 더 많을 것으로 예상.
