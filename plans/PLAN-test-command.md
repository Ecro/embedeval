# PLAN: /test Custom Command for EmbedEval

**Project:** embedeval
**Created:** 2026-03-24

---

## Executive Summary

> **TL;DR:** `/test` 커맨드를 만들어 벤치마크 실행 → 상세 결과 저장 → 실패 분석 → TC 개선 피드백까지 한번에 처리

### What We're Doing
Claude Code `/test` 슬래시 커맨드를 생성하여:
1. LLM 벤치마크를 실행
2. Per-case 상세 결과 (어떤 check이 pass/fail, 생성된 코드 포함) 저장
3. 실패 패턴 분석 리포트 생성
4. TC 개선 제안 (너무 쉬운 TC, false positive TC 식별)

### Why It Matters
- 현재: 집계 결과만 저장 → 실패 원인 분석 불가
- 목표: 모든 실행 결과를 영구 보존 → TC 추가/개선 시 참고

---

## Current Problems

| 문제 | 현재 | 목표 |
|------|------|------|
| Per-case 결과 | 없음 (집계만) | 케이스별 L0-L4 check 상세 |
| 생성된 코드 | 없음 (버려짐) | 실행별로 저장 |
| 실패 분석 | 수동 | 자동 실패 패턴 리포트 |
| 히스토리 | 없음 | 날짜별 결과 아카이브 |
| TC 피드백 | 없음 | pass@1 > 90% TC 식별 → 강화 제안 |

---

## Technical Design

### 1. 결과 저장 구조

```
results/
├── runs/                              # 실행별 상세 결과
│   └── 2026-03-24_sonnet/
│       ├── summary.json               # 집계 결과
│       ├── details/                    # per-case 상세
│       │   ├── kconfig-001.json        # {generated_code, checks, pass/fail}
│       │   ├── kconfig-002.json
│       │   └── ...
│       └── report.md                  # 실패 분석 리포트
├── history.json                       # 모든 실행의 요약 히스토리
└── LEADERBOARD.md                     # 최신 리더보드
```

### 2. Per-case 상세 JSON

```json
{
  "case_id": "isr-concurrency-004",
  "category": "isr-concurrency",
  "difficulty": "hard",
  "model": "claude-code://sonnet",
  "attempt": 1,
  "passed": false,
  "failed_at_layer": 3,
  "generated_code": "... (full LLM output) ...",
  "layers": [
    {
      "layer": 0, "name": "static_analysis", "passed": true,
      "checks": [
        {"check_name": "atomic_t_for_index", "passed": true, "expected": "...", "actual": "..."},
        ...
      ]
    },
    {
      "layer": 3, "name": "behavioral_assertion", "passed": false,
      "checks": [
        {"check_name": "k_sleep_present", "passed": false, "expected": "...", "actual": "missing"}
      ]
    }
  ],
  "duration_seconds": 12.3,
  "token_usage": {"input": 500, "output": 300, "total": 800},
  "cost_usd": 0.05
}
```

### 3. 실패 분석 리포트 (report.md)

```markdown
# Benchmark Report: sonnet / 2026-03-24

## Summary
- Model: claude-code://sonnet
- Cases: 200 (pass: 170, fail: 30)
- pass@1: 85%

## Failure Analysis

### By Category
| Category | pass@1 | Failed Cases |
|----------|--------|-------------|
| isr-concurrency | 90% | isr-concurrency-004 |
| security | 60% | security-006, 007, 009, 010 |

### By Failure Pattern
| Pattern | Count | Cases |
|---------|-------|-------|
| k_sleep missing (busy-wait) | 3 | isr-004, timer-008, ... |
| API hallucination | 5 | gpio-008, ble-006, ... |
| Error handling missing | 8 | ... |
| volatile/atomic missing | 4 | ... |

### By Difficulty
| Difficulty | Total | Passed | pass@1 |
|------------|-------|--------|--------|
| Easy | 28 | 27 | 96% |
| Medium | 88 | 78 | 89% |
| Hard | 84 | 65 | 77% |

## TC Improvement Suggestions

### Too Easy (100% pass → 강화 필요)
- kconfig-001, kconfig-002, ... (모든 모델이 쉽게 통과)
- 제안: 더 깊은 의존성 체인 추가, 환각 유도 트랩 강화

### False Positive Suspects (reference도 fail)
- (없으면 좋음)

### Most Discriminating TCs (모델간 차이 큼)
- isr-concurrency-004: Sonnet FAIL, (other model TBD)
```

### 4. /test 커맨드 플로우

```
/test sonnet                             # 전체 200 cases
/test sonnet kconfig                     # 특정 카테고리만
/test sonnet isr-concurrency,security    # 여러 카테고리 (쉼표)
/test sonnet --attempts 5                # pass@5 측정
/test sonnet kconfig --attempts 5        # 카테고리 + attempts
/test compare sonnet opus                # 두 모델 비교
/test history                            # 실행 히스토리 조회
/test analyze                            # 최근 결과 실패 분석
```

---

## Implementation Plan

### Phase 1: Per-case 상세 결과 저장

**File: `src/embedeval/reporter.py`**
- `generate_detailed_results(results, output_dir)` 함수 추가
- EvalResult를 per-case JSON으로 저장 (generated_code 포함)

**File: `src/embedeval/cli.py`**
- `run` 커맨드에서 상세 결과도 저장하도록 수정
- 결과 디렉토리를 `results/runs/YYYY-MM-DD_model/`로 구조화

### Phase 2: 실패 분석 리포트 생성

**File: `src/embedeval/analyzer.py`** (신규)
- `analyze_failures(results)` → 실패 패턴 분류
- `generate_analysis_report(results, output)` → Markdown 리포트

### Phase 3: 히스토리 추적

**File: `src/embedeval/history.py`** (신규)
- `append_history(run_summary)` → `results/history.json`에 추가
- `load_history()` → 히스토리 조회
- `compare_runs(run_a, run_b)` → 두 실행 비교

### Phase 4: /test 슬래시 커맨드

**File: `.claude/commands/test.md`**
- Claude Code 슬래시 커맨드 정의
- 벤치마크 실행 + 결과 저장 + 분석 리포트 생성
- 결과를 memory에도 기록

### Phase 5: TC 개선 제안

**`analyzer.py`에 추가:**
- `suggest_tc_improvements(history)` → 100% pass TC 식별
- `find_false_positives(results)` → reference가 fail하는 TC
- `find_discriminating_tcs(history)` → 모델간 차이가 큰 TC

---

## Success Criteria

- [ ] `/test sonnet` 실행하면 벤치마크 돌리고 상세 결과 저장
- [ ] 실패한 케이스의 어떤 check이 왜 실패했는지 JSON으로 확인 가능
- [ ] 생성된 코드가 보존되어 나중에 분석 가능
- [ ] 실패 패턴 분석 리포트 자동 생성
- [ ] TC 추가 시 기존 결과 참고 가능 (어떤 TC가 너무 쉬운지)
