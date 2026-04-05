# PLAN: TC 재구성 + Safety Guide 리포트

**Project:** embedeval
**Task:** 220 TC를 3-Tier로 재분류, 추론 유형 태깅, Leaderboard + Safety Guide 이중 리포트 생성
**Created:** 2026-03-28

---

## Executive Summary

> **TL;DR:** TC를 삭제하지 않고 3-Tier(Sanity/Core/Challenge)로 분류 + 추론 유형(reasoning_type) 메타데이터 추가. 리포트를 Leaderboard(연구자용) + Safety Guide(개발자용) 2종으로 분리.

### What We're Doing
1. 각 TC에 `tier` (sanity/core/challenge)와 `reasoning_type` (api_recall/rule_application/cross_domain/system_reasoning) 메타데이터 추가
2. Leaderboard는 Core+Challenge TC만으로 pass@1 산출 (Sanity는 사전 필터)
3. Safety Guide는 추론 유형별 성공률, 위험 작업 체크리스트, LLM Capability Boundary 포함

### Why It Matters
- 현재 "pass@1 = 89.5%"는 easy TC가 점수를 끌어올림 → 과대평가
- 엔지니어에게 필요한 건 점수가 아니라 "어디서 LLM을 믿으면 안 되는가"
- BigCodeBench-Hard가 148/1140으로 줄이고 더 유의미한 변별력을 얻은 것과 같은 전략

### Key Decisions
- **TC 삭제 안 함** — Tier 분류만 (기존 220개 유지)
- **추론 유형 4단계** — API Recall → Rule Application → Cross-Domain → System Reasoning
- **IRT 기반 Tier 결정** — 실측 데이터로 Sanity/Core/Challenge 경계 결정

### Estimated Impact
- **Complexity:** Medium
- **Risk Level:** Low (메타데이터 추가 + 리포트 분리)
- **Files Changed:** ~10 files + 220 metadata.yaml

---

## TC Tier 분류 기준

### Tier 정의

| Tier | 목적 | TC 수 (목표) | 선별 기준 | 점수 반영 |
|------|------|-------------|----------|----------|
| **Sanity** | 모델 기본 작동 확인 | 15-30 | 모든 모델 90%+ 통과 (IRT discrimination < 0.1) | 미반영 (pass/fail만) |
| **Core** | 주요 평가 지표 | 100-120 | Medium 난이도, solve rate 30-90% | **pass@1 (primary)** |
| **Challenge** | 모델 간 차별화 | 60-80 | Hard 난이도, solve rate <50%, 높은 discrimination | pass@1 (secondary) |

### Tier 결정 프로세스

```
Step 1: 최소 2개 모델(Sonnet + Haiku) 벤치마크 실행
Step 2: difficulty.py로 IRT 파라미터 추정
Step 3: 자동 분류:
  - empirical_pass_rate > 0.9 AND discrimination < 0.1 → Sanity
  - empirical_pass_rate < 0.5 → Challenge
  - 나머지 → Core
Step 4: 수동 검증 (카테고리별 최소 1개 Core, 1개 Challenge 보장)
```

### 예상 분류 (현재 데이터 기준)

| 카테고리 | Sanity 후보 | Core 후보 | Challenge 후보 |
|----------|-----------|----------|---------------|
| kconfig | 001, 002 | 003-007 | 008-010 |
| boot | 001, 002 | 003-007 | 008-010 |
| gpio-basic | 001, 002 | 003-007 | 008-010 |
| isr-concurrency | — | 001-004 | 005-010 (전부 어려움) |
| linux-driver | — | 001-004 | 005-010 |
| dma | — | 001-004 | 005-010 |

---

## 추론 유형 (Reasoning Type) 분류

### 4-Level 추론 모델

| Level | 이름 | 설명 | LLM 성공률 | 리뷰 필요 |
|-------|------|------|-----------|----------|
| L1 | `api_recall` | 단일 API 호출, 설정 패턴 | 95%+ | 가볍게 확인 |
| L2 | `rule_application` | 알려진 규칙 적용 (ISR 차단 금지 등) | 80-90% | 일반 리뷰 |
| L3 | `cross_domain` | C + RTOS + HW 도메인 결합 | 60-75% | 전문가 리뷰 |
| L4 | `system_reasoning` | 역방향 추론, 전체 시스템 상태 | 50-65% | 직접 작성 권장 |

### Check → Reasoning Type 매핑

```python
CHECK_REASONING_MAP = {
    # L1: API Recall
    "led_configured_output": "api_recall",
    "button_configured_input": "api_recall",
    "fops_read_write": "api_recall",
    "k_sleep_present": "api_recall",

    # L2: Rule Application
    "no_forbidden_apis_in_isr": "rule_application",
    "no_cross_platform_apis": "rule_application",
    "no_mutex_in_isr": "rule_application",
    "device_ready_check": "rule_application",

    # L3: Cross-Domain
    "volatile_shared": "cross_domain",
    "spinlock_used_in_both_contexts": "cross_domain",
    "cache_aligned": "cross_domain",
    "cyclic_enabled": "cross_domain",
    "reload_in_callback": "cross_domain",

    # L4: System Reasoning
    "init_error_path_cleanup": "system_reasoning",
    "error_path_returns": "system_reasoning",
    "cleanup_reverse_order": "system_reasoning",
    "wdt_feed_is_conditional": "system_reasoning",
}
```

### metadata.yaml 확장

```yaml
# 기존
id: isr-concurrency-003
category: isr-concurrency
difficulty: hard
# 신규
tier: challenge          # sanity | core | challenge
reasoning_types:         # TC가 요구하는 추론 유형 (복수 가능)
  - rule_application     # ISR 차단 금지
  - cross_domain         # spinlock + volatile 결합
```

---

## 이중 리포트 구조

### Report 1: Leaderboard (연구자/논문용)

기존 LEADERBOARD.md 확장:

```markdown
## EmbedEval Leaderboard

### Overall (Core + Challenge only)
| Model | pass@1 | 95% CI | Cases | Embed Gap |
|-------|--------|--------|-------|-----------|
| Sonnet | 85.2% | [80.1%, 89.4%] | 170 | -8.5%p |
| Haiku | 71.3% | [65.2%, 77.0%] | 170 | -12.7%p |

### By Tier
| Tier | Sonnet | Haiku | Delta |
|------|--------|-------|-------|
| Sanity (n=30) | 100% | 97% | 3%p |
| Core (n=100) | 90% | 78% | 12%p |
| Challenge (n=70) | 72% | 58% | 14%p |

### By Reasoning Type
| Type | Sonnet | Haiku | Delta |
|------|--------|-------|-------|
| L1 API Recall | 97% | 93% | 4%p |
| L2 Rule Application | 88% | 79% | 9%p |
| L3 Cross-Domain | 72% | 58% | 14%p |
| L4 System Reasoning | 58% | 42% | 16%p |
```

### Report 2: Safety Guide (임베디드 개발자용)

**새로운 파일: `SAFETY-GUIDE.md`**

```markdown
# LLM Embedded Code Safety Guide

## LLM Capability Boundary

### LLM이 잘하는 것 (90%+ 신뢰)
- Kconfig/prj.conf 설정
- 기본 GPIO, UART, SPI 초기화
- 스레드 생성, 메시지 큐
- Device Tree 노드

### LLM이 도움되지만 리뷰 필수 (60-85%)
- ISR 핸들러 — volatile, spinlock 빠뜨릴 수 있음
- DMA 설정 — alignment, cyclic mode 오류 가능
- BLE 스택 — 연결/해제 lifecycle 불완전
- 에러 처리 — happy path만 구현, cleanup 누락

### LLM이 할 수 없는 것
- 보드 브링업, 전원 시퀀싱
- 실제 HW 타이밍 검증 (오실로스코프)
- EMC/EMI 대응
- 센서 캘리브레이션
- 안전 인증 (IEC 61508, ISO 26262)
- 양산 테스트 설계

## 작업별 LLM 위험도

### ISR/인터럽트 코드
**위험도: 높음** | 성공률: ~70%

필수 체크리스트:
- □ 공유 변수에 volatile?
- □ ISR 내 차단 호출(mutex, sleep, printk) 없는가?
- □ spinlock key가 lock→unlock 전달?
- □ ISR + thread 양쪽 spinlock 보호?

대표 실패: LLM이 mutex를 ISR에 사용 → deadlock

### 에러 복구 경로
**위험도: 높음** | 성공률: ~60%

필수 체크리스트:
- □ 모든 init 반환값 체크?
- □ if (ret < 0) 후 return/goto?
- □ cleanup이 init 역순?
- □ 주석이 아닌 실제 코드로 cleanup?

대표 실패: 3단계 init 중 2단계 실패 → 1단계 리소스 누수

### DMA 전송
**위험도: 높음** | 성공률: ~65%

필수 체크리스트:
- □ 버퍼 cache-line 정렬 (32B/64B)?
- □ cyclic mode: 콜백에서 reload?
- □ 완료 대기 (세마포어/폴링)?
- □ 에러 시 dma_stop?

대표 실패: cache alignment 없이 DMA → 간헐적 데이터 손상

## 실패 패턴 통계 (근거 데이터)

| 패턴 | 전체 실패 중 비중 | 추론 유형 |
|------|-----------------|----------|
| Happy path 편향 | 39% | L4 System |
| HW 의미론 오류 | 28% | L3 Cross-Domain |
| 리소스 불균형 | 11% | L4 System |
| 순서 위반 | 11% | L3 Cross-Domain |
| 플랫폼 혼동 | 6% | L2 Rule |
| API 환각 | 5% | L1 API |
```

---

## Implementation Plan

### Phase 1: 메타데이터 확장 + Tier 자동 분류

**File: `src/embedeval/models.py`**
```python
class CaseTier(str, Enum):
    SANITY = "sanity"
    CORE = "core"
    CHALLENGE = "challenge"

class ReasoningType(str, Enum):
    API_RECALL = "api_recall"
    RULE_APPLICATION = "rule_application"
    CROSS_DOMAIN = "cross_domain"
    SYSTEM_REASONING = "system_reasoning"

class CaseMetadata(BaseModel):
    # 기존 필드...
    tier: CaseTier = CaseTier.CORE
    reasoning_types: list[ReasoningType] = []
```

**File: `scripts/classify_tiers.py` (신규)**
- 벤치마크 결과 JSON 로드
- IRT 파라미터로 자동 Tier 분류
- metadata.yaml에 `tier:` 필드 업데이트
- 수동 오버라이드 지원

**File: `scripts/tag_reasoning_types.py` (신규)**
- 각 TC의 behavior.py check_name 분석
- CHECK_REASONING_MAP으로 reasoning_types 자동 태깅
- metadata.yaml 업데이트

### Phase 2: Scorer + Reporter 수정

**File: `src/embedeval/scorer.py`**
- `score()` 함수에 tier 기반 점수 분리 추가
- Sanity tier → 합격/불합격만 (pass@1 미반영)
- Core + Challenge → 주요 pass@1

**File: `src/embedeval/reporter.py`**
- Leaderboard: Tier별, Reasoning Type별 테이블 추가
- Safety Guide: 새 함수 `generate_safety_guide()`

### Phase 3: Safety Guide 생성기

**File: `src/embedeval/safety_guide.py` (신규)**
```python
def generate_safety_guide(
    results: list[EvalResult],
    output: Path,
) -> None:
    """Generate LLM Embedded Code Safety Guide from benchmark results."""
    # 1. LLM Capability Boundary (정적 — 코드에 하드코딩)
    # 2. 작업별 위험도 (동적 — 벤치마크 결과에서 산출)
    # 3. 체크리스트 (정적 — check_name에서 도출)
    # 4. 실패 패턴 통계 (동적 — failure_taxonomy에서)
```

### Phase 4: CLI 통합 + 테스트

**File: `src/embedeval/cli.py`**
- `--tier core,challenge` 필터 (기본: core+challenge)
- `embedeval guide` 서브커맨드 (Safety Guide 생성)

**Tests:**
- `test_tier_classification.py`: Tier 자동 분류 로직
- `test_safety_guide.py`: Safety Guide 생성 검증
- E2E: 기존 220 TC가 tier 필드 추가 후에도 전부 통과

---

## Execution Order

```
Phase 1 (메타데이터) → Phase 2 (Scorer/Reporter) → Phase 3 (Safety Guide) → Phase 4 (CLI/Tests)
```

Phase 1은 벤치마크 실행 결과(Sonnet + Haiku)가 있어야 IRT 기반 분류 가능.
결과가 없으면 난이도 라벨 기반 임시 분류로 시작.

---

## Success Criteria

- [ ] 220개 TC에 `tier` 필드 추가됨
- [ ] 220개 TC에 `reasoning_types` 필드 추가됨
- [ ] Leaderboard가 Tier별, Reasoning Type별 테이블 포함
- [ ] Safety Guide가 Capability Boundary + 체크리스트 + 실패 통계 포함
- [ ] `--tier` CLI 필터 동작
- [ ] 기존 테스트 regression 없음

---

## Next Step

```
/execute tc-restructure
```

Phase 1 (메타데이터 확장)부터 시작. 벤치마크 결과 없이도 난이도 기반 임시 분류 가능.
