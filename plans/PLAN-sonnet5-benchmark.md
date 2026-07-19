---
type: plan
task_slug: sonnet5-benchmark
status: complete
created: 2026-07-19
tags: [embedeval, plan, benchmark, sonnet-5]
---

# PLAN: Sonnet 5 전체 벤치마크 + 개선율 측정

**Task:** Sonnet 5(`claude-sonnet-5`)로 전체 267케이스 n=3 벤치마크를 돌리고, 기존 Sonnet 4.6 대비 순수 개선율(교집합 233케이스)과 신규 34케이스 절대 성능을 분리 보고한다.
**Created:** 2026-07-19

## Executive summary

**TL;DR:** Sonnet 5를 현재 267케이스에 n=3(801 LLM 콜)으로 돌리고, 4.6과 겹치는 233케이스만 delta 비교해 케이스 셋 변경분과 모델 개선분을 분리한다.

### What
`scripts/run_n_samples.sh 3 claude-code://claude-sonnet-5` 로 n=3 전체 실행 →
`scripts/aggregate_n_runs.py` 로 mean/stdev/95% CI 산출 →
신규 교집합 delta 스크립트로 4.6(2026-04-12 아카이브)과 공통 233케이스만 비교 →
`docs/BENCHMARK-n3-sonnet5.md` + `docs/BENCHMARK-DELTA-sonnet5-vs-sonnet46.md` 생성.

### Why
Sonnet 5 출시. 기존 파이프라인은 이미 n=3 방법론을 갖췄으나, 그 사이 케이스 셋이
233→267로 바뀌어(SDK-bucket 마이그레이션 + Phase B/C Linux TC 34개 추가) 단순 68.0%→X%
비교는 모델 개선분과 셋 변경분이 섞인다. 교집합 비교로 순수 개선율을 분리한다.

### Key decisions
- **모델 핀:** `claude-code://claude-sonnet-5` (알리아스 `sonnet` 대신 명시 ID — 리포트 재현성, `sonnet`는 "latest"라 시간이 지나면 의미가 바뀜)
- **샘플링:** n=3 (사용자 승인) — flaky 케이스 때문에 n=1은 ±2%p 노이즈라 "개선율" 단정 불가
- **베이스라인:** 교집합 233케이스 delta + 신규 34케이스 별도 (사용자 승인) — 추가 LLM 콜 0. 4.6 재실행(1602콜) 대신 저장된 2026-04-12 아카이브 재사용
- **private 포함:** `--include-private` (기존 방법론과 동일, 48케이스)

### Impact
- Complexity: Low (기존 파이프라인 재사용, 신규 코드는 delta 스크립트 1개)
- Risk: Medium (rate limit / 장시간 실행 / Docker 빌드 안정성)
- Files changed: ~4 (delta 스크립트 1, 리포트 2, MEMORY.md 1)
- Estimated effort: 실행 대기 시간 제외 실작업 2–3시간; 벤치마크 벽시계 시간은 별도(수 시간)

## Prior work

- `plans/PLAN-paper-level-benchmark.md`, `PLAN-benchmark-credibility.md`, `PLAN-benchmark-followup-2026-04-11.md` — n=3 방법론, Wilson CI, flaky 분석의 근거
- `scripts/run_n_samples.sh` — n=K 실행 오케스트레이션(쿨다운/재시도/run-id 분리). 그대로 재사용
- `scripts/aggregate_n_runs.py` — per-run pass@1, mean, stdev, Wilson CI, case stability, pass-count 분포. 그대로 재사용
- `docs/BENCHMARK-n3-sonnet.md` — 출력 포맷 템플릿(4.6 결과)
- `docs/BENCHMARK-COMPARISON-2026-04-05.md` — Haiku vs Sonnet 비교 리포트 포맷(adjusted pass@1 = env/format 실패 제외)
- CLAUDE.md 교정: "Run-scoped artifacts MUST go under run_dir/ not output_dir/" (2026-04-19) — n=3 아카이브가 서로 안 덮어씀을 보장하는 `--run-id` 규약 근거
- MEMORY.md: 4.6 n=3 = **68.0%**, 95% CI [64.4%, 71.3%], case stability 87.1%, flaky 30개(13%) — 비교 기준값

## Problem analysis

### Current state
- 케이스: public 219 + private 48 = **267** (`iter_case_dirs`로 확인)
- 4.6 n=3 아카이브 존재: `results/runs/2026-04-12_claude-code___sonnet_n{1,2,3}/` — 각 233 detail JSON, `case_id`+`passed` 필드 보유
- 모델 경로: `src/embedeval/llm_client.py:124` — `claude-code://X` → `claude -p --model X` 로 그대로 전달. `claude --model claude-sonnet-5 -p` 동작 검증 완료(OK 응답)
- 케이스당 LLM 콜 1회(attempts=1); L0~L4는 로컬/Docker라 추가 콜 없음 → n=3 full = **801 콜**
- 케이스 ID는 dir 이름 기반으로 마이그레이션 후에도 안정 → 교집합 매칭 가능

### 케이스 셋 불일치(핵심 함정)
- 4.6 데이터: 233케이스 (185 public + 48 private, 2026-04-12 기준)
- 현재: 267케이스 (219 public + 48 private)
- 차이: public +34 (Phase B/C Linux 커널·OTA·네트워킹 — 고난이도 계열)
- 결론: 단순 68.0% vs X% 비교는 **모델 개선분 + 셋 변경분**이 혼재. 교집합 233케이스로 분리 필요.

### Success criteria
- [x] Sonnet 5 n=3 (n1/n2/n3) 아카이브 3개가 `results/runs/`에 run-id 분리 저장(상호 비파괴)
- [x] `docs/BENCHMARK-n3-sonnet5.md`: per-run pass@1, mean, stdev, Wilson 95% CI, case stability, pass-count 분포
- [x] `docs/BENCHMARK-DELTA-sonnet5-vs-sonnet46.md`: **교집합 233케이스** delta(순수 개선율) + **신규 34케이스** 절대 pass@1(별도)
- [x] 개선/퇴행 케이스 목록(4.6 pass→5 fail 및 그 반대)을 카테고리별로 집계
- [x] MEMORY.md 벤치마크 섹션에 Sonnet 5 결과 반영
- [x] Quality gates 통과(신규 delta 스크립트 대상 ruff/mypy/pytest)

## Design

### Approach
기존 n=3 파이프라인을 그대로 실행하되 모델만 `claude-code://claude-sonnet-5`로 바꾼다.
개선율은 4.6 저장 아카이브를 재사용해 **추가 콜 없이** 교집합 delta로 계산한다.

1. **실행:** `scripts/run_n_samples.sh 3 claude-code://claude-sonnet-5`
   - 내부적으로 `--cases cases/ --private-cases ../embedeval-private/cases/ --include-private --run-id n{i}`
   - `EMBEDEVAL_ENABLE_BUILD=docker`, `COOLDOWN_SECS`로 rate limit 완충
   - **백그라운드 실행**(장시간). 로그는 `/tmp/embedeval_n3_*`
2. **집계:** `scripts/aggregate_n_runs.py --model claude-code://claude-sonnet-5 --run-ids n1,n2,n3 --output docs/BENCHMARK-n3-sonnet5.md`
3. **교집합 delta (신규 스크립트 `scripts/compare_models_intersection.py`):**
   - 두 모델의 n=3 아카이브에서 per-case pass를 `case_id`→`passed`로 로드(aggregate_n_runs와 동일 로직 재사용)
   - per-case 판정은 **majority vote of 3 runs**(2/3+ pass = pass)로 안정화
   - 공통 case_id 집합 = 교집합(예상 233), 4.6에 없는 = 신규(예상 34)
   - 출력: 교집합 pass@1(5) vs pass@1(4.6) + %p delta, 신규 34 pass@1(5만), 개선/퇴행 케이스 리스트(카테고리별)
4. **리포트 작성:** delta 문서 + comparison 문서 업데이트, MEMORY.md 반영

### Alternatives considered
- **4.6도 현재 267셋으로 재실행:** 가장 깨끗한 동일-셋 비교지만 +801콜(총 1602). 사용자가 rate limit 부담으로 반려. 교집합 비교로 순수 개선율은 확보되므로 불필요.
- **n=1 빠른 확인:** flaky 노이즈로 "개선율" 단정 불가. 반려.
- **CLI에 `compare` 서브커맨드 추가:** context-compare 패턴 존재하나, 1회성 모델간 비교라 독립 스크립트가 가볍고 파이프라인 오염 없음. 스크립트로 결정.

### Affected files
- `scripts/compare_models_intersection.py` — 신규. 두 n=3 아카이브 교집합/차집합 delta 계산
- `docs/BENCHMARK-n3-sonnet5.md` — 신규(aggregate 출력)
- `docs/BENCHMARK-DELTA-sonnet5-vs-sonnet46.md` — 신규(교집합 + 신규 케이스 분리 리포트)
- `tests/test_compare_models_intersection.py` — 신규(delta 로직 유닛 테스트)
- MEMORY.md, `docs/BENCHMARK-COMPARISON-2026-04-05.md` — Sonnet 5 결과 추가
- `results/LEADERBOARD.md` — 자동 갱신(runner가 씀)

## Implementation phases

### Phase 0: 사전 점검 (실행 전)
- [x] `claude --model claude-sonnet-5 -p "OK"` 재확인(이미 통과) — 알리아스가 아닌 명시 ID 동작 보장
- [x] Docker 데몬 up 및 `EMBEDEVAL_ENABLE_BUILD=docker` 환경 확인
- [x] `git status` clean 확인, reddit-*.md 등 untracked는 별건(무시)
- [x] 디스크 여유 확인(details/ 3× 아카이브 = 267×3 JSON)

### Phase 1: 벤치마크 실행 (백그라운드, 장시간)
- [x] `COOLDOWN_SECS=300 MAX_RETRIES=2 scripts/run_n_samples.sh 3 claude-code://claude-sonnet-5` 백그라운드 실행
- [x] 로그 폴링으로 각 run 완료/실패 모니터링(`/tmp/embedeval_n3_*`)
- [x] 실패 run은 스크립트 내장 재시도에 위임, 3회 소진 시 수동 개입
- [x] 완료 후 `results/runs/<date>_claude-code___claude-sonnet-5_n{1,2,3}/` 3개 아카이브 존재 확인

### Phase 2: 집계
- [x] `aggregate_n_runs.py --model claude-code://claude-sonnet-5 --run-ids n1,n2,n3 --output docs/BENCHMARK-n3-sonnet5.md`
- [x] mean pass@1, stdev, 95% CI, case stability, flaky 수 확인

### Phase 3: 교집합 delta 스크립트 + 리포트
- [x] `scripts/compare_models_intersection.py` 작성(majority-vote per-case, 교집합/차집합 분리)
- [x] 유닛 테스트 작성(happy/edge/error) 후 통과 확인
- [x] Sonnet 5 vs 4.6(2026-04-12) 실행 → `docs/BENCHMARK-DELTA-sonnet5-vs-sonnet46.md` 생성
- [x] 순수 개선율(교집합) + 신규 34 절대값 + 개선/퇴행 케이스 카테고리별 표 작성

### Phase 4: 검증 & 문서 동기화
- [~] `scripts/verify_results.py` — 2단계 레이아웃 미대응(0건 검증, false all-clear)으로 자동 교차검증 불가 → regressed 케이스 수동 표본검사로 대체
- [x] MEMORY.md 벤치마크 섹션에 Sonnet 5 결과 추가
- [x] `docs/BENCHMARK-COMPARISON-2026-04-05.md`에 Sonnet 5 열 추가
- [x] `scripts/sync_docs.py` 실행(cases 미변경이라 no-op 예상이나 확인)

## Testing strategy

- Unit tests (`tests/test_compare_models_intersection.py`):
  - Happy: 겹치는 케이스 + 신규 케이스 혼재 시 교집합/차집합 정확히 분리, delta 부호/값 정확
  - Edge: 교집합 공집합, 신규 공집합, majority-vote 동률(3run 중 정확히 pass/fail 분포) 경계
  - Error: 아카이브 경로 없음, detail JSON에 `case_id` 결측, run-id 개수 불일치
- Integration: Sonnet 5 n=3 실제 실행이 곧 end-to-end 검증. `verify_results.py`로 저장 결과 vs 재실행 교차검증
- Quality gates: `uv run ruff format --check src/ scripts/`, `uv run ruff check src/ scripts/`, `uv run mypy src/`, `uv run pytest tests/`
- Doc sync: `scripts/sync_docs.py` (cases/src/tests 변경 시 필수 — 본 작업은 scripts/docs/tests 변경이므로 실행해 확인)

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| 장시간 실행 중 rate limit / 세션 중단 | High | run_n_samples.sh의 COOLDOWN(300s)+MAX_RETRIES(2), run-id 분리로 부분 재개 가능. 백그라운드 실행 |
| `sonnet` 알리아스와 `claude-sonnet-5` 혼동으로 4.6/5 뒤섞임 | High | 항상 명시 ID `claude-code://claude-sonnet-5` 사용. 아카이브 slug에 모델명 박힘으로 사후 식별 가능 |
| Docker 빌드 불안정으로 L1/L2 env-failure 급증(모델 무관) | Med | verify_results.py + adjusted pass@1(env/format 제외) 병기. 기존 리포트 관행 준수 |
| 신규 34케이스가 고난이도라 전체 aggregate가 4.6보다 낮게 보임 | Med | **교집합 233 delta가 순수 개선율**임을 리포트 최상단에 명시. 전체값은 셋 변경 각주와 함께 |
| 케이스 ID 불안정(마이그레이션으로 rename) | Low | `case_id` 필드 기준 매칭, dir rename 여부 사전 확인(현재 동일 확인됨) |
| 교집합이 233이 아닐 수 있음(예상과 다른 차집합) | Low | 스크립트가 실제 교집합/차집합 개수를 출력, 하드코딩 금지. 233은 예상치일 뿐 |

## Review checklist (verify before /execute)

- [ ] Scope correct — n=3 실행 + 교집합 비교, 4.6 재실행은 범위 밖(승인됨)
- [ ] Design sound — 저장 아카이브 재사용으로 추가 콜 0, majority-vote per-case 안정화
- [ ] Affected-files list complete — delta 스크립트/테스트/리포트 2종/MEMORY
- [ ] Tests cover every success criterion — 교집합/차집합/delta/에러 케이스
- [ ] Risks identified — rate limit, 알리아스 혼동, Docker env-failure, 셋 변경 오해
