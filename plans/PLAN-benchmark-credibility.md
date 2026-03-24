# PLAN: Benchmark Credibility — 7 Improvements

**Project:** embedeval
**Created:** 2026-03-24
**Source:** Insight #7 (Critical Self-Analysis)

---

## Executive Summary

> **TL;DR:** Insight #7에서 도출된 7개 개선 사항을 구현하여 EmbedEval의
> 학술적/실무적 신뢰성을 높인다.

---

## 7 Improvements — Detailed Plan

### 1. L1/L2 활성화 (Docker + west build)

**현재 상태:** Dockerfile, docker-compose.yml 이미 존재. `EMBEDEVAL_ENABLE_BUILD=1`로 제어.
evaluator.py에 L1(west build), L2(QEMU 실행) 로직 구현되어 있지만 Docker 없으면 skip.

**필요 작업:**
- [ ] GitHub Actions에 Docker build workflow 추가
- [ ] `docker-compose up` 으로 벤치마크 실행하는 스크립트 작성
- [ ] CI에서 `EMBEDEVAL_ENABLE_BUILD=1` + Zephyr SDK Docker 이미지로 L1/L2 테스트
- [ ] 각 TC에 `prj.conf` + `CMakeLists.txt` 추가 (현재 없는 케이스)
- [ ] native_sim 보드로 QEMU 없이 실행 가능한 케이스 우선 처리

**파일:**
- `.github/workflows/benchmark.yml` (신규)
- `scripts/run-docker-benchmark.sh` (신규)
- `cases/*/prj.conf` (케이스별 추가)
- `cases/*/CMakeLists.txt` (케이스별 추가)

**난이도:** High — 200개 케이스에 빌드 설정 추가 필요
**우선순위:** 1 (가장 중요)

---

### 2. pass@5 또는 3회 반복 평균

**현재 상태:** `--attempts N` CLI 옵션 이미 구현됨! scorer.py에 pass@1, pass@5 계산 로직 있음.

**필요 작업:**
- [ ] 기본 실행 시 `--attempts 3` 권장하는 문서 추가
- [ ] LEADERBOARD.md에 confidence interval 표시
- [ ] scorer.py에 표준편차/CI 계산 추가
- [ ] 3회 반복 벤치마크 실행 후 variance 리포트 생성

**파일:**
- `src/embedeval/scorer.py` — CI 계산 함수 추가
- `src/embedeval/reporter.py` — LEADERBOARD에 CI 표시
- `docs/METHODOLOGY.md` — 통계적 유의성 설명

**난이도:** Low — 핵심 인프라 이미 있음
**우선순위:** 2

---

### 3. Human Baseline

**현재 상태:** 없음. 비교 대상이 전혀 없음.

**필요 작업:**
- [ ] 20개 TC 선별 (카테고리당 1개, 난이도 medium)
- [ ] 임베디드 경력 1-3년 개발자 1명에게 시험 (시간 제한 없이)
- [ ] 결과를 `results/human-baseline/` 에 저장
- [ ] LEADERBOARD에 human baseline 행 추가

**대안 (개발자 구하기 어려우면):**
- [ ] 본인이 "주니어 모드"로 풀기 (데이터시트/SDK 문서 참고 허용, IDE 사용)
- [ ] 시간 제한 설정 (TC당 10분)

**파일:**
- `results/human-baseline/` (신규)
- `src/embedeval/reporter.py` — human baseline 표시

**난이도:** Medium (기술보다 사람 구하기가 어려움)
**우선순위:** 3

---

### 4. L3 명칭 → "static_heuristic"

**현재 상태:** evaluator.py와 reporter.py 두 곳에 정의.

```python
# evaluator.py
LAYER_NAMES = {3: "behavioral_assertion"}

# reporter.py
LAYER_DISPLAY_NAMES = {"behavioral_assertion": "L3 Behavior"}
```

**필요 작업:**
- [ ] `behavioral_assertion` → `static_heuristic` 변경 (evaluator.py)
- [ ] `L3 Behavior` → `L3 Heuristic` 변경 (reporter.py)
- [ ] 테스트 업데이트 (문자열 참조하는 곳)
- [ ] METHODOLOGY.md 업데이트

**파일:**
- `src/embedeval/evaluator.py` — LAYER_NAMES dict
- `src/embedeval/reporter.py` — LAYER_DISPLAY_NAMES dict
- `tests/` — 관련 assertion 문자열

**난이도:** Trivial
**우선순위:** 4

---

### 5. 부분 점수제 (Weighted Scoring)

**현재 상태:** Binary (전체 PASS/FAIL). CheckDetail에 passed: bool만 있음.

**필요 작업:**
- [ ] `CheckDetail`에 `weight: float = 1.0` 필드 추가
- [ ] `LayerResult`에 `score: float` 필드 추가 (0.0~1.0, weighted average)
- [ ] `EvalResult`에 `total_score: float` 추가 (전체 가중 평균)
- [ ] scorer.py에 weighted score 집계 로직
- [ ] LEADERBOARD에 pass@1 옆에 avg_score 표시
- [ ] 기존 passed: bool 유지 (하위 호환)

**예시:**
```
Case: linux-driver-001
  check 1: copy_to_user (weight=2.0) → PASS → 2.0/2.0
  check 2: cleanup (weight=3.0) → FAIL → 0.0/3.0
  check 3: fops (weight=1.0) → PASS → 1.0/1.0
  Total: 3.0/6.0 = 50% score (but passed=False)
```

**파일:**
- `src/embedeval/models.py` — CheckDetail, LayerResult, EvalResult
- `src/embedeval/evaluator.py` — score 계산
- `src/embedeval/scorer.py` — weighted aggregation
- `src/embedeval/reporter.py` — score 표시

**난이도:** Medium
**우선순위:** 5

---

### 6. Private Test Set 분리

**현재 상태:** 200 TC 전부 public (GitHub에 노출).

**필요 작업:**
- [ ] `CaseMetadata`에 `visibility: Literal["public", "private"] = "public"` 추가
- [ ] CLI에 `--visibility` 필터 추가
- [ ] 20개 TC를 private으로 마킹 (카테고리당 1개, hard 난이도)
- [ ] Private TC는 `.gitignore`에 추가하거나 별도 repo로 분리
- [ ] CI에서만 private TC 포함하여 실행

**대안:**
- [ ] TC rotation: 매 분기 public↔private 교체 (LiveCodeBench 방식)
- [ ] Parameterized TC: 같은 구조, 다른 숫자/이름으로 변형 생성

**파일:**
- `src/embedeval/models.py` — CaseMetadata에 visibility 필드
- `src/embedeval/runner.py` — visibility 필터링
- `src/embedeval/cli.py` — --visibility 옵션
- `cases/*/metadata.yaml` — 20개에 visibility: private 추가

**난이도:** Medium
**우선순위:** 6

---

### 7. Multi-platform (ESP-IDF 추가)

**현재 상태:** Zephyr 90%+, FreeRTOS 일부, Linux driver 일부.

**필요 작업:**
- [ ] ESP-IDF 카테고리 신설 또는 기존 카테고리에 ESP-IDF variant 추가
- [ ] 10개 ESP-IDF TC 작성 (gpio, spi, wifi, ble, ota, nvs 등)
- [ ] ESP-IDF Docker 이미지 (espressif/idf:v5.x)
- [ ] L1 빌드: `idf.py build` 지원 추가
- [ ] check_utils.py에 ESP-IDF API 금지 목록 추가 (Zephyr TC에서)
- [ ] 기존 cross-platform 체크에 ESP-IDF API 추가

**파일:**
- `cases/esp-gpio-001/` ~ `cases/esp-ota-010/` (신규)
- `src/embedeval/evaluator.py` — ESP-IDF 빌드 로직
- `src/embedeval/check_utils.py` — ESP-IDF API 목록
- `Dockerfile.esp` (신규)

**난이도:** High — 새 플랫폼 전체 지원
**우선순위:** 7 (v2 scope)

---

## Implementation Order

```
Phase A (Quick Wins — 1일):
  4. L3 명칭 변경 (Trivial)
  2. pass@5 CI 계산 추가 (Low)

Phase B (Core Credibility — 1주):
  5. 부분 점수제 (Medium)
  6. Private test set (Medium)

Phase C (Infrastructure — 2주):
  1. L1/L2 Docker 활성화 (High)
  3. Human baseline 수집 (Medium)

Phase D (v2 — 추후):
  7. Multi-platform ESP-IDF (High)
```

---

## Success Criteria

- [ ] L3 명칭 "static_heuristic"으로 변경됨
- [ ] `--attempts 3` 실행 시 CI/표준편차 리포트 생성
- [ ] 부분 점수 (0.0~1.0)가 LEADERBOARD에 표시됨
- [ ] 20개 TC에 visibility: private 마킹됨
- [ ] Docker에서 최소 10개 TC의 west build 성공
- [ ] Human baseline 1개 이상 수집됨
- [ ] 685 기존 pytest 통과 유지
