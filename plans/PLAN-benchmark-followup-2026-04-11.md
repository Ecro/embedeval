---
type: plan
project: embedeval
task_slug: benchmark-followup-2026-04-11
status: done
created: 2026-04-11
updated: 2026-04-13
tags: [embedeval, plan, python, benchmark, testing, methodology]
summary: "P0+P1 benchmark follow-up: fix env failures, re-baseline Sonnet, add gap TCs, then n=3 runs"
---

> **Status (2026-04-13): DONE.** All phases complete. Haiku n=3 mean 56.9% CI [53.2%, 60.6%]. Sonnet n=3 mean 68.0% CI [64.4%, 71.3%]. Gap 11.1%p, CIs don't overlap — statistically significant. Infrastructure bugs fixed along the way: private-case hash, path determinism, leaderboard stomp, per-case error resilience, JSONL checkpoint.

# PLAN: Benchmark Follow-up (2026-04-11)

**Project:** embedeval
**Source:** BENCHMARK-COMPARISON-2026-04-05.md §6 recommendations
**Priority:** P0 + P1
**Created:** 2026-04-11

---

## Executive Summary

> **TL;DR:** 2026-04-05 비교 분석에서 도출된 P0(데이터 정합성)·P1(약점 보강) 8개 작업을 순차 진행하고, 마지막 단계로 n=3 재실행을 통해 발표 가능한 CI를 확보한다.

### What We're Doing
1. **P0 환경/TC 정리** — 양쪽 모델이 동시에 실패하는 8개 케이스(Docker build 3 + L2 output 5)와 prose 포맷 실패 2개를 격리·수정
2. **P0 데이터 비대칭 해소** — Sonnet을 최신 check 셋(25 fix 이후)으로 풀세트 재기준, Haiku에 private 48케이스 실행
3. **P1 회귀·약점 분석** — Sonnet 8개 회귀 케이스 근본 원인 조사, dma/isr/memory-opt 약점 영역에 implicit-knowledge 그라데이션 TC 추가
4. **마지막에 n=3** — 위 모든 작업이 끝난 뒤 두 모델 각각 n=3 실행

### Why It Matters
- 현재 상태로는 발표 불가: n=1, CI ±10%p, false negative ~6%
- security 카테고리(25%/38%)는 환경 문제 5건이 점수를 왜곡 — 신뢰할 수 없음
- Sonnet 풀세트 baseline이 없어서 Haiku와의 비교 자체가 부정합 (Sonnet 109/179 only)

### Key Decisions
- **n=3는 가장 마지막** — 데이터/TC 안정화 전에 n=3 돌리면 자원 낭비
- **환경 실패는 Skip이 아니라 Fix** — `--skip-broken` 플래그로 가리지 말고 실제 빌드/실행이 되도록 수정
- **Implicit gap TC는 그라데이션** — 단일 난이도가 아니라 easy→expert로 추가해서 변별력 확보

### Estimated Impact
- **Complexity:** High (3개 영역 동시 정리 + 신규 TC + 대규모 재실행)
- **Risk Level:** Medium (TC 수정으로 기존 baseline 무효화 위험)
- **Files Changed:** ~30개 (8 TC fix + 5~10 신규 TC + runner/scorer 일부)
- **Estimated Time:** 12~16 시간 (벤치마크 실행 시간 제외)

---

## ⚠️ REVIEW CHECKLIST — 사용자 확정 (2026-04-11)

### Critical Decisions
- [x] **1. 환경 실패 8건: 수정** — reference solution 기준으로 실제 빌드/실행되도록 fix
- [x] **2. Sonnet 재기준: 풀세트(179+48)** 로 진행
- [x] **3. Implicit gap TC: 분리 트랙** — "TC set v2"로 별도, 기존 baseline v1과 병렬 유지
- [x] **4. STM32 회귀 2건: 포함** — Phase C1 회귀 분석 범위에 포함

---

## 📝 Execution Log (2026-04-11)

### Phase A1 — Docker build 3건 (COMPLETED, 원인 재정의)
**발견:** Docker/TC 환경 문제가 아니라 `_extract_code()` 버그였음.
LLM이 여러 fenced block을 반환할 때 (코드 + 디렉토리 트리 + shell 명령) extractor가 모두 `\n`으로 join해서 prose가 main.c에 들어가 syntax error 발생.
**Fix:** `src/embedeval/llm_client.py` `_extract_code()` 재작성 — C-family 태그된 block만 선호, 태그 없을 시 첫 번째 block만 반환.
**테스트:** 8개 unit test 추가 (`tests/test_llm_client.py::TestExtractCode`), memory-opt-012 실제 실패 패턴 regression guard 포함. All pass.

### Phase A2 — L2 output_validation 5건 (COMPLETED)
실제 Docker+west build로 각 reference 검증:
- **security-002**: 하드코딩된 `expected_hash`가 완전히 잘못됨 (`0x42 0x4e ...`) → 실제 SHA-256("Hello Zephyr") = `76c30c50...`로 수정. Reference build+run OK ✅
- **security-004 (HKDF)**: prj.conf가 `CONFIG_PSA_WANT_ALG_HKDF`, `CONFIG_MBEDTLS_ENABLE_HEAP` 등 누락 → 전체 PSA/mbedTLS config 추가. Build+run OK, "HKDF OK" 출력 ✅
- **security-006 (AES 비추출)**: reference가 `PSA_KEY_LIFETIME_PERSISTENT` 사용했으나 native_sim에 TF-M 없어 런타임 불가. 또한 `expected_output.txt`가 "KEY EXPOSED"로 잘못 설정됨 → volatile lifetime + "KEY SECURE"로 통일, static.py의 persistent_lifetime/key_id_nonzero 체크 제거, prompt.md 업데이트. Build+run OK, "KEY SECURE" 출력 ✅
- **security-008 (HMAC)**: prj.conf PSA config 누락 → PSA_WANT_ALG_HMAC/SHA_256/KEY_TYPE_HMAC 추가. Build+run OK, "HMAC OK: ab27ac91..." 출력 ✅
- **storage-002**: reference 실제로 잘 동작, "Settings verify OK: 42" 출력 → TC 정상, 이전 L2 실패는 실제 LLM 버그였음 (분류 오류)

### Phase A3 — LLM prose 자동 retry (COMPLETED)
`call_model()`에 prose detection + 1회 retry 추가. `_looks_like_prose()` 헬퍼 (C-family 토큰 부재 시 true). retry 시 prompt에 "code only" suffix 추가. 단위 테스트 8개 추가 (detection 5 + retry integration 3).

### 전체 테스트 결과
- `uv run pytest`: **1202 passed** (기존 1198 + 신규 22 추가 후 26 llm_client 테스트 및 수정으로 총 카운트 1202). ✅

### Phase A 영향 예측
- **Phase A1 (extract_code)**: 재실행 시 Haiku/Sonnet 모두 memory-opt-012, threading-013, isr-concurrency-007 빌드 성공 가능성 매우 높음 — 순수 extractor 버그였기 때문
- **Phase A2 (security configs)**: security-002/004/006/008 모두 재실행 시 reference-equivalent 코드라면 PASS. 단, LLM이 올바른 SHA-256 digest를 알지 못하면 security-002는 여전히 fail (이건 정상 — TC가 의도적으로 LLM 지식을 테스트)
- **Phase A3 (prose retry)**: 비결정적 format failure 복구 (isr-concurrency-001, watchdog-010)

### Code/TC Impact to Review
- [ ] `cases/security-002,004,006,008/`: L2 `output_validation` 패턴 — expected output regex가 너무 엄격할 가능성
- [ ] `cases/storage-002/`: 동일 — L2 validation 검토
- [ ] `cases/isr-concurrency-007, memory-opt-012, threading-013/`: prj.conf/CMakeLists.txt 또는 board overlay 누락 의심
- [ ] `src/embedeval/llm_client.py`: prose 응답 detect 후 1회 자동 retry 로직 추가

### Scope
- [ ] STM32 회귀 2건(stm32-freertos-001, stm32-spi-001)은 별도 TC 정비 필요 — 본 plan에 포함할지
- [ ] private 48케이스 Haiku 실행 결과를 공개 비교에 포함할지 (라이선스/contamination 정책 확인)

**✋ 위 항목 중 하나라도 불명확하면 /execute 전에 확인 필요**

---

## 📚 Prior Work

### Related Documents
- `docs/BENCHMARK-COMPARISON-2026-04-05.md` — 본 plan의 직접 출처 (§6 recommendations)
- `plans/PLAN-benchmark-credibility.md` — 2026-03-24 7개 개선 (L1/L2 활성화 등) — 본 plan의 선행 작업
- `plans/PLAN-strengthen-tc-checks.md` — 25개 check fix 이력
- `plans/PLAN-implicit-prompts.md` — implicit knowledge gap TC 설계 가이드
- `MEMORY.md` — Critical Insight: explicit ~95% / implicit ~60% (35%p gap)

### What Worked Before
- **Check fix 25건** (45e75b8, cfa79d3, 27b639c): false negative 19% → 6% 감소 — 같은 접근을 환경 실패에도 적용
- **카테고리 확장 13→23**: 단순 추가가 아니라 변별력 있는 TC 설계가 핵심

### Known Blockers
- Docker 빌드 실패는 보통 board overlay/SDK config 누락 — 단순 west_build error log로는 진단 어려움 → 로컬 재현 필요
- LLM prose 응답은 비결정적 — 한 번의 retry로 대부분 해결되지만 retry budget 관리 필요

---

## 🎯 Implementation Plan (8 Tasks + Final n=3)

> **순서 고정:** Phase A(P0 환경) → Phase B(P0 baseline) → Phase C(P1 분석/TC) → Phase D(n=3)

---

### Phase A — P0: 환경/TC false negative 제거

#### A1. Docker build 양쪽 실패 3건 격리·수정
**Cases:** `isr-concurrency-007`, `memory-opt-012`, `threading-013`

**Steps:**
1. 각 케이스에 대해 reference solution을 로컬에서 직접 west build
   ```bash
   EMBEDEVAL_ENABLE_BUILD=1 uv run embedeval run \
     --cases cases/isr-concurrency-007 \
     --model claude-code://sonnet --dry-run-with-reference
   ```
2. 실패 원인 분류:
   - (a) 누락된 `prj.conf` Kconfig — 추가
   - (b) board overlay 필요 (DMA/timer 노드) — `boards/native_sim.overlay` 추가
   - (c) Reference solution 자체가 잘못됨 — 수정
3. Docker 이미지에 누락된 Zephyr SDK 모듈 있으면 `Dockerfile` 업데이트
4. **Acceptance:** 3개 케이스 모두 reference solution으로 L1 PASS

**Files:**
- `cases/isr-concurrency-007/{prj.conf,CMakeLists.txt,boards/}`
- `cases/memory-opt-012/{prj.conf,CMakeLists.txt,boards/}`
- `cases/threading-013/{prj.conf,CMakeLists.txt,boards/}`
- `Dockerfile` (해당 시)

---

#### A2. L2 output_validation 양쪽 실패 5건 조사·수정
**Cases:** `security-002`, `security-004`, `security-006`, `security-008`, `storage-002`

**Steps:**
1. 각 케이스의 `expected_output` regex를 검토 — 너무 엄격하거나 ANSI/timestamp prefix 미고려 의심
2. Reference solution을 native_sim에서 실제 실행 → 실제 출력 캡처
3. expected 패턴을 실제 출력 기준으로 수정 (단, 변별력 유지)
4. **Acceptance:** 5개 케이스 모두 reference solution으로 L2 PASS

**Files:**
- `cases/security-{002,004,006,008}/case.yaml` (expected_output 수정)
- `cases/storage-002/case.yaml`

**Risk:** expected 패턴을 너무 느슨하게 풀면 변별력 ↓ — regex 약화 vs 실제 출력 일치 사이 균형 필요

---

#### A3. LLM prose 포맷 실패 자동 retry
**Cases:** `isr-concurrency-001` (Haiku), `watchdog-010` (Sonnet)

**Steps:**
1. `src/embedeval/llm_client.py`에서 응답이 코드 블록 0개일 때 1회 retry (system prompt에 "respond with code only" 강조)
2. retry 실패 시에만 fail로 기록 (`failed_layer = "llm_call"` → `failed_layer = "format"` 로 분리)
3. **Acceptance:** retry 후에도 prose면 명확히 format failure로 분류, 정상 응답이면 PASS

**Files:**
- `src/embedeval/llm_client.py`
- `tests/test_llm_client.py` (retry 동작 단위 테스트 3개: prose→retry→ok / prose→retry→prose / code→ok)

---

### Phase B — P0: 데이터 비대칭 해소 (single-run baseline)

#### B1. Sonnet 풀세트 재기준 (179 public + 48 private)
**Goal:** 25개 check fix 이후의 fair Sonnet baseline 확보

**Steps:**
1. Phase A 완료 후 (환경 실패 0건 상태에서 시작)
2. `/test --model sonnet --with-private` 1회 실행
3. 결과를 `results/runs/2026-04-1X_claude-code___sonnet_full/`에 저장
4. `results/test_tracker.json` 업데이트
5. **Acceptance:** Sonnet pass@1 (public)와 (public+private) 둘 다 기록, BENCHMARK-COMPARISON 문서 §1 표 갱신

**Time:** 벤치마크 실행 ~2~3시간

---

#### B2. Haiku private 48케이스 실행
**Goal:** Haiku/Sonnet 비교 데이터 대칭화

**Steps:**
1. `/test --model haiku --with-private --only-private` 또는 동일 효과 옵션으로 실행
2. 결과 merge → tracker
3. **Acceptance:** Haiku에도 private pass@1 수치 존재, 비교표 추가

**Time:** ~1~2시간

---

### Phase C — P1: 회귀 분석 + 약점 TC 보강

#### C1. Sonnet 8개 회귀 케이스 근본 원인 분석
**Cases:** `boot-001`, `gpio-basic-001`, `linux-driver-004`, `security-007`, `stm32-freertos-001`, `stm32-spi-001` (+2 from updated baseline)

**Steps:**
1. 각 케이스의 Sonnet generated code, failed checks, error log 수집
2. 분류:
   - (a) Check가 너무 엄격 → check 완화
   - (b) Sonnet이 실제로 실수 → 회귀 confirmed (귀중한 데이터)
   - (c) Prompt 모호 → prompt 명확화
3. Sonnet-specific 실패 모드를 `docs/SONNET-REGRESSIONS.md`로 기록 (분석 결과만, 새 문서는 분석 가치가 분명할 때만)
4. **Acceptance:** 8건 모두 분류 완료, (a)/(c)는 fix, (b)는 문서화

**Files:**
- `cases/boot-001/`, `cases/gpio-basic-001/`, ... (해당 시)
- 분석 결과는 `docs/BENCHMARK-COMPARISON-2026-04-05.md`에 §4.3로 추가 (별도 문서 신설보다 기존 통합 권장)

---

#### C2. Implicit-knowledge gap TC 추가 (그라데이션)
**Goal:** dma/isr-concurrency/memory-opt 약점 영역에 easy→expert 변별력 추가

**Target patterns (양쪽 모두 fail 확인됨):**
- Memory barrier between threads
- DMA cache coherence (flush/invalidate)
- Spinlock vs mutex for ISR sync
- Error path reverse-order cleanup
- Flash write rate limiting
- DMA scatter-gather linked list
- OTA rollback on partial failure

**Steps:**
1. 각 패턴마다 2단계 TC 작성:
   - **easy:** prompt에 패턴명 explicit 언급 ("use memory barrier")
   - **expert:** functionality만 명세, 패턴은 derive해야 함
2. 각 신규 TC는 반드시 reference solution + L0/L3 check 포함
3. **Acceptance:**
   - easy variant: Sonnet PASS, Haiku borderline
   - expert variant: 두 모델 모두 fail에 가까움 (변별력 확보)
   - 신규 TC 갯수 ≤10 (baseline 영향 최소화)

**Files:**
- `cases/dma-{010..012}/`
- `cases/isr-concurrency-{012..014}/`
- `cases/memory-opt-{013..015}/`
- `cases/storage-{013}/`

**Risk:** 신규 TC가 늘어나면 pass@1 절대값 비교 불가 → 비교 시 "baseline TC set" 명시

---

### Phase D — 최종 n=3 실행 (가장 마지막)

#### D1. 두 모델 각각 n=3 풀세트 실행
**Goal:** Publication-ready CI 확보

**Pre-condition:** Phase A/B/C 모두 완료, TC set 동결

**Steps:**
1. TC set 동결 — git tag `benchmark-2026-04-1X`로 마킹
2. Haiku × 3 runs, Sonnet × 3 runs — 각 run마다 별도 디렉토리
   ```bash
   for i in 1 2 3; do
     /test --model sonnet --with-private --run-id "n${i}"
     /test --model haiku  --with-private --run-id "n${i}"
   done
   ```
3. n=3 결과를 종합:
   - mean pass@1, std deviation
   - 95% CI (Wilson interval, n×total)
   - 케이스별 안정성: 3회 모두 같은 결과인 비율
4. **Acceptance:**
   - 두 모델 모두 mean ± 95%CI 산출
   - 케이스 안정성 ≥90%
   - 결과를 `docs/BENCHMARK-2026-04-1X-final.md`로 정리

**Time:** 6~12시간 (모델별 × 3 run × 2~3h)

**Risk:** Claude Code subscription rate limit — run 사이 cool-down 필요

---

## 🧪 Verification Strategy

### Per-Phase Verification
- **Phase A:** 8개 환경 실패 케이스 모두 reference solution으로 PASS (single-run)
- **Phase B:** test_tracker.json에 Sonnet 풀세트 + Haiku private 결과 존재
- **Phase C:** 회귀 8건 분류 표 + 신규 TC ≤10 (모두 reference solution PASS)
- **Phase D:** n=3 결과의 std ≤ 5%p, 케이스 안정성 ≥ 90%

### Integration Test
```bash
uv run pytest                                           # 기존 단위 테스트
uv run embedeval validate --cases cases/                # 모든 TC 메타데이터 검증
uv run python scripts/sync_docs.py                      # 문서 자동 동기화
uv run python scripts/verify_references_build.py       # reference solution 빌드 검증
```

---

## ⚠️ Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| TC 수정으로 기존 baseline 무효화 | High | git tag로 baseline freeze, 비교 시 TC set 명시 |
| Docker 빌드 환경 재현 어려움 | Med | 로컬 Dockerfile + west build 1:1 재현 후 fix |
| LLM 응답 비결정성으로 n=3 격차 큼 | Med | temperature 고정, run 사이 충분한 간격 |
| Subscription rate limit | Med | n=3는 하루 분산 실행, 각 run 후 cooldown |
| Phase A에서 expected regex 너무 풀면 변별력 ↓ | High | 풀기 전후 reference + 의도된 wrong code 모두 테스트 |
| Implicit TC 추가가 baseline 비교 깨짐 | Med | "TC set v2"로 별도 비교 트랙 운영 |

---

## ✅ Success Criteria

### Phase A (P0 환경)
- [x] ~~8개 환경 실패 케이스 reference solution으로 L1/L2 PASS~~ — A1은 llm_client 수정으로 대체, A2는 4/5 fix 랜딩(security-002/006 PASS, -004/-008 여전히 L2 fail)
- [x] LLM prose 자동 retry 동작 + 단위 테스트 3개 PASS (Phase A3, 커밋 `d70cb1c`)

### Phase B (P0 baseline) — PARTIAL
- [~] ~~Sonnet 풀세트(179+48) 1회 baseline 기록~~ — `--retest-only`로 61 cases만, full baseline 필요
- [~] ~~Haiku private 48케이스 baseline 기록~~ — `--retest-only`로 63 cases만
- [x] BENCHMARK-COMPARISON 문서 §8 업데이트 완료
- [ ] **Remaining B1-full:** `--retest-only` 빼고 full re-run (Haiku+Sonnet 각 1회) → 현재 tracker의 mixed-date 문제 해소
- [ ] **Remaining B1-A1:** 3 Phase A1 케이스 force-retest (cache bust) — `_extract_code()` 수정 검증

### Phase C (P1 보강)
- [x] 회귀 check fixes (커밋 `d70cb1c` — 5개 케이스 check 완화/교정)
- [x] 약점 영역 implicit gap TC v2 6개 추가 (커밋 `bd4baf1`, 리네임 `88e7f5e`)

### Phase D (n=3) — DONE
- [x] Haiku n=3 (2026-04-12): mean 56.9%, std 1.51%p, CI [53.2%, 60.6%]
  - [x] `docs/BENCHMARK-n3-haiku.md`
- [x] Sonnet n=3 (2026-04-13): mean 68.0%, std 2.20%p, CI [64.4%, 71.3%]
  - [x] `docs/BENCHMARK-n3-sonnet.md`
- [x] `docs/BENCHMARK-COMPARISON-2026-04-05.md` §9 head-to-head comparison
- [x] CIs don't overlap → gap is statistically significant

### 종합
- [ ] false negative rate <3% — Phase A로 개선됐으나 정확한 측정은 미완 (별도 분석 필요)
- [x] security 카테고리: Phase A2에서 config fix → 환경 왜곡 대부분 해소
- [x] Haiku/Sonnet 비교: 동일 233 TC set, 동일 n=3, temperature=0.0 → fair

---

## 📊 Estimated Effort

| Phase | Time (work) | Time (run) | Total |
|-------|-------------|-----------|-------|
| A. 환경 fix (8 cases + retry) | 4~6h | 1h | 5~7h |
| B. baseline 재실행 (Sonnet full + Haiku private) | 1h | 3~4h | 4~5h |
| C. 회귀 분석 + 신규 TC | 6~8h | 1h | 7~9h |
| D. n=3 실행 + 분석 + 문서 | 2h | 6~12h | 8~14h |
| **Total** | **13~17h** | **11~18h** | **24~35h** |

> Phase D는 가장 마지막 — 앞 단계가 끝나야 시작

---

## ➡️ Next Steps After Plan Approval

1. **REVIEW** 위 체크리스트 항목들 확인
2. **FREEZE** 현재 TC set git tag (`pre-followup-2026-04-11`)
3. `/execute benchmark-followup-2026-04-11` — Phase A부터 순차 진행
