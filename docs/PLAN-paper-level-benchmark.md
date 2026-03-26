# PLAN: Paper-Level Benchmark Upgrade

**Project:** embedeval
**Task:** EmbedEval을 EMNLP/ACL Findings Insight Paper 수준으로 업그레이드 (P0-P3 전체)
**Priority:** Critical
**Created:** 2026-03-26

---

## Executive Summary

> **TL;DR:** EmbedEval의 methodology를 논문 수준으로 강화 — pass@k 통계, L1 컴파일, AST 체크, 오염 방지, 프롬프트 민감도, 난이도 보정, ablation study 등 12개 개선 항목 구현.

### What We're Doing
현재 regex 기반 static heuristic + naive pass@k로 동작하는 EmbedEval을 (1) 통계적으로 엄밀하고, (2) 컴파일 검증이 포함되며, (3) 오염에 강건하고, (4) 체크 정밀도가 높은 벤치마크로 업그레이드.

### Why It Matters
경쟁 벤치마크(EmbedAgent ICSE'26, LiveCodeBench ICLR'25, BigCodeBench ICLR'25) 대비 methodology가 약해 논문 심사에서 reject될 가능성 높음. EmbedEval의 독창적 기여(Implicit Knowledge Gap 35%p, 4-Level Model)는 강력하나, 이를 뒷받침할 methodology 신뢰성이 부족.

### Key Decisions
- **Option B (Insight Paper)** — TC 규모나 인프라가 아닌, "LLM이 임베디드에서 왜 실패하는가"에 대한 인사이트 중심
- **P0-P3 전체 적용** — 논문 수준 최소 요건(P0)부터 차별화(P3)까지 전부 구현

### Estimated Impact
- **Complexity:** High
- **Risk Level:** Medium
- **Files Changed:** ~15 files
- **Phases:** 8 phases

---

## Implementation Plan

### Phase 1: pass@k Unbiased Estimator + 통계 인프라 [P0]

**목표:** naive pass@k → unbiased estimator, 신뢰 구간, 반복 실험 지원

**File: `src/embedeval/scorer.py`**

1. `_calculate_pass_at_k()` 수정 — unbiased estimator 구현:
   ```python
   from math import comb

   def _calculate_pass_at_k(results: list[EvalResult], k: int) -> float:
       """Unbiased pass@k estimator: 1 - C(n-c,k)/C(n,k)"""
       by_case: dict[str, list[EvalResult]] = defaultdict(list)
       for r in results:
           by_case[r.case_id].append(r)

       if not by_case:
           return 0.0

       scores = []
       for case_results in by_case.values():
           n = len(case_results)
           c = sum(1 for r in case_results if r.passed)
           if n < k:
               # Not enough samples, fall back to empirical
               scores.append(1.0 if c > 0 else 0.0)
           elif n - c < k:
               scores.append(1.0)
           else:
               scores.append(1.0 - comb(n - c, k) / comb(n, k))
       return sum(scores) / len(scores)
   ```

2. 신뢰 구간 계산 추가 — Wilson score interval:
   ```python
   def _wilson_ci(pass_rate: float, n: int, z: float = 1.96) -> tuple[float, float]:
       """Wilson score confidence interval for pass rate."""
       if n == 0:
           return (0.0, 0.0)
       denom = 1 + z**2 / n
       center = (pass_rate + z**2 / (2 * n)) / denom
       spread = z * ((pass_rate * (1 - pass_rate) / n + z**2 / (4 * n**2)) ** 0.5) / denom
       return (max(0.0, center - spread), min(1.0, center + spread))
   ```

3. `avg_score` 제거 → 의미 없는 pass@1/3/5 평균 삭제

**File: `src/embedeval/models.py`**

4. `ModelScore`에 CI 필드 추가:
   ```python
   pass_at_1_ci: tuple[float, float] = (0.0, 0.0)  # 95% Wilson CI
   n_samples: int = 1  # samples per case for pass@k
   ```

5. `BenchmarkReport`에 메타데이터 추가:
   ```python
   temperature: float = 0.0
   n_samples_per_case: int = 1
   n_runs: int = 1
   ```

**File: `src/embedeval/cli.py`**

6. `--temperature` 옵션 추가 (기록용)
7. `--runs` 옵션 추가 (반복 실험, 기본값=1)

**Tests:**
- `test_scorer.py`: unbiased estimator 검증 (n=10, c=3, k=5 → 정확한 결과 비교)
- `test_scorer.py`: Wilson CI 검증
- `test_scorer.py`: k > n edge case

---

### Phase 2: L1 Compilation 활성화 [P0]

**목표:** Docker 기반 Zephyr SDK에서 실제 `west build` 실행

**File: `Dockerfile.zephyr` (신규)**
```dockerfile
FROM ghcr.io/zephyrproject-rtos/ci:v0.26.13
RUN west init /zephyr && cd /zephyr && west update
ENV ZEPHYR_BASE=/zephyr/zephyr
WORKDIR /workspace
```

**File: `src/embedeval/evaluator.py`**

1. `_run_compile_gate()` Docker 모드 추가:
   - 생성된 코드를 임시 디렉토리에 쓰기 (case_dir 오염 방지)
   - `docker run --rm -v tmpdir:/workspace zephyr-eval west build -b {board} /workspace`
   - 타임아웃 300초
   - stderr 캡처로 에러 메시지 보존

2. `_build_env_available()` 확장:
   - `EMBEDEVAL_ENABLE_BUILD=docker` → Docker 모드
   - `EMBEDEVAL_ENABLE_BUILD=1` → 로컬 west (기존)
   - 미설정 → skip (기존)

3. case_dir 쓰기 제거 — tmpdir에 쓰기:
   ```python
   with tempfile.TemporaryDirectory() as tmpdir:
       # Copy case files to tmpdir
       shutil.copytree(case_dir, Path(tmpdir) / "case", dirs_exist_ok=True)
       # Write generated code
       (Path(tmpdir) / "case" / "src" / "main.c").write_text(generated_code)
       # Run west build in docker
   ```

**File: `docker-compose.eval.yml` (신규)**
- Zephyr SDK 서비스 정의
- ESP-IDF SDK 서비스 정의 (추후)

**Tests:**
- `test_evaluator.py`: Docker mock으로 L1 경로 테스트
- Integration test: 실제 Docker로 reference solution 컴파일

---

### Phase 3: Private Held-out Set + 오염 방지 [P1]

**목표:** 50 TC를 private으로 설정 + temporal cutoff 지원

**현재 상태:** `Visibility` enum과 `--visibility` 필터 이미 존재.

**File: 50개 TC의 `metadata.yaml`**

1. 각 카테고리에서 2-3개 TC를 `visibility: private`로 변경
   - 대상: 각 카테고리의 가장 어려운 TC (e.g., `-008`, `-009`, `-010`)
   - 총 50/220 = 23% → 적절한 비율

2. Private TC의 `prompt.md`와 `reference/main.c`를 `.gitignore`에 추가:
   ```gitignore
   # Private benchmark cases (held-out set)
   cases/*/prompt.md.private
   cases/*/reference/main.c.private
   ```

3. 대안 접근 (Git LFS/별도 repo 분리는 과도):
   - Public repo에는 `metadata.yaml`만 유지 (TC 존재를 공개)
   - `prompt.md`, `reference/main.c`, `checks/` → 별도 private 디렉토리
   - CLI에서 `--include-private` 옵션으로 private TC 포함

**File: `src/embedeval/runner.py`**

4. 기본 필터를 `visibility=public`으로 변경:
   ```python
   # run_benchmark의 기본 filters
   effective_filters = filters or Filters(visibility=Visibility.PUBLIC)
   ```

**File: `docs/METHODOLOGY.md`**

5. 오염 방지 전략 섹션 추가:
   - Private held-out set (23%)
   - Temporal cutoff (created_date vs model training cutoff)
   - Future: 주기적 TC 교체

**Tests:**
- `test_runner.py`: private 필터링 기본 동작 확인

---

### Phase 4: AST 기반 Check Precision 향상 [P1]

**목표:** check precision 40% → 80%+. 핵심 논문 기여.

**File: `pyproject.toml`**
```toml
[project.optional-dependencies]
ast = ["pycparser>=2.22", "tree-sitter>=0.23", "tree-sitter-c>=0.23"]
```

**File: `src/embedeval/ast_utils.py` (신규)**

핵심 AST 유틸리티:

```python
"""AST-based code analysis utilities using tree-sitter-c."""

import tree_sitter_c as tsc
from tree_sitter import Language, Parser

def parse_c(code: str) -> tree_sitter.Tree:
    """Parse C code into AST."""

def find_variable_with_qualifier(tree, qualifier: str) -> list[str]:
    """Find variables declared with a specific qualifier (e.g., 'volatile')."""
    # Returns [(var_name, scope)] — 위치까지 검증

def check_return_after_error(tree, api_call: str) -> bool:
    """Verify that error check on api_call is followed by return/goto."""
    # if (ret < 0) { ... return ... } 패턴 확인

def check_cleanup_order(tree, init_calls: list[str]) -> bool:
    """Verify cleanup calls are in reverse order of init calls."""

def find_api_in_function(tree, api_name: str, func_name: str) -> bool:
    """Check if api_name appears inside func_name body."""
    # "volatile이 어디에 있는가" → 정확한 함수 범위 내 검증

def check_word_boundary(code: str, api: str) -> bool:
    """Word-boundary check to prevent substring aliasing."""
    # __copy_to_user vs copy_to_user 구분
```

**File: `src/embedeval/check_utils.py` 수정**

5. `check_no_cross_platform_apis()` — word boundary 적용:
   ```python
   # Before: if api in stripped
   # After:  if re.search(rf'\b{re.escape(api)}', stripped)
   ```

6. 기존 `"volatile" in code` → `find_variable_with_qualifier(tree, "volatile")`

**File: 10개 대표 TC의 `checks/behavior.py` 업그레이드**

우선 Blind Spot이 확인된 10개 TC부터:
- `isr-concurrency-003`: volatile 위치 검증 (AST)
- `isr-concurrency-008`: barrier 순서 + atomic 변수 타입 (AST)
- `linux-driver-001`: copy_to_user word boundary (regex → word boundary)
- `gpio-basic-001`: device_is_ready가 GPIO 사용 전에 호출 (AST 흐름)
- `dma-003`: reload가 callback 함수 body 안에 있는지 (AST scope)
- `dma-008`: cache alignment 값 검증 (AST numeric)
- `timer-007`: 에러 체크 후 return 확인 (AST flow)
- `ble-008`: 연결 해제 시 cleanup 역순 (AST order)
- `watchdog-005`: conditional WDT feed (AST condition)
- `stm32-freertos-002`: ISR에서 FromISR 변종 사용 (AST scope)

**File: `checks/negatives.py` 확대**

7. 현재 10개 → 전체 220개 TC에 negatives.py 추가
   - 최소 2개 must_fail mutation per TC
   - Phase 4에서는 AST 업그레이드한 10개 TC만
   - 나머지는 Phase 8에서 점진적으로

**Check Precision 측정 스크립트:**

8. `scripts/measure_check_precision.py` (신규):
   ```python
   """Measure check precision by running all negatives."""
   # For each TC with negatives.py:
   #   Run must_fail mutations → count caught/total
   #   Run should_fail mutations → record blind spots
   # Report: overall precision, per-category, per-check-type
   ```

**Tests:**
- `test_ast_utils.py`: AST 파싱, volatile 위치, return after error, cleanup order
- `test_negatives.py` 확장: 새로운 negatives 검증

---

### Phase 5: 프롬프트 민감도 분석 [P2]

**목표:** 프롬프트 변형에 대한 robustness 측정

**File: `src/embedeval/sensitivity.py` (신규)**

```python
"""Prompt sensitivity analysis for benchmark robustness."""

def generate_variants(prompt: str, n: int = 3) -> list[str]:
    """Generate n paraphrased variants of a prompt.

    Variant types:
    1. Reorder requirements (shuffle bullet points)
    2. Rephrase key instructions (synonyms)
    3. Change output format instructions
    """

def run_sensitivity_analysis(
    cases_dir: Path,
    model: str,
    sample_cases: int = 30,  # Random sample
    variants_per_case: int = 3,
) -> SensitivityReport:
    """Run benchmark with prompt variants and measure stability."""

class SensitivityReport(BaseModel):
    """Prompt sensitivity analysis results."""
    robustness_score: float  # 1 - max_variance
    per_case_variance: dict[str, float]
    most_sensitive_cases: list[str]
    most_robust_cases: list[str]
```

**File: `src/embedeval/cli.py`**

1. `embedeval sensitivity` 서브커맨드 추가

**실행 방법:**
- 30개 TC 랜덤 샘플 × 3 variants × n=5 samples = 450 LLM 호출
- 각 variant별 pass rate 비교
- Robustness score = 1 - (max_pass - min_pass) / max(max_pass, 0.01)

**논문 활용:**
- Table: "Prompt Sensitivity Analysis" — per-category robustness score
- 결론: "EmbedEval results are robust to reasonable prompt variations (avg robustness = X%)"

---

### Phase 6: 난이도 IRT 보정 [P2]

**목표:** 사후 난이도 보정으로 TC 변별력 정량화

**File: `src/embedeval/difficulty.py` (신규)**

```python
"""Item Response Theory (IRT) difficulty calibration."""

from dataclasses import dataclass

@dataclass
class IRTParams:
    """IRT 2PL model parameters for a test case."""
    case_id: str
    difficulty: float     # b parameter: higher = harder
    discrimination: float # a parameter: higher = better differentiator
    empirical_pass_rate: float
    assigned_difficulty: str  # original easy/medium/hard label

def calibrate_difficulty(
    results: list[EvalResult],
    min_models: int = 2,
) -> list[IRTParams]:
    """Calibrate IRT parameters from multi-model results.

    Requires results from at least 2 models to estimate discrimination.
    Uses simplified 2PL: P(correct) = sigmoid(a * (theta - b))
    where theta = model ability, b = item difficulty, a = discrimination.
    """

def validate_labels(params: list[IRTParams]) -> dict:
    """Compare assigned difficulty labels vs IRT-estimated difficulty.

    Returns mislabel rate and suggested reclassifications.
    """
```

**논문 활용:**
- Figure: IRT difficulty distribution (scatter plot: assigned vs estimated)
- Table: "X% of cases have misaligned difficulty labels"
- Insight: "easy-labeled cases that are actually hard reveal implicit knowledge gaps"

---

### Phase 7: Ablation Study + 실패 분류 체계 [P3]

**목표:** 각 layer/check 유형의 기여도 정량화 + 실패 원인 자동 분류

**File: `src/embedeval/ablation.py` (신규)**

```python
"""Ablation study: measure contribution of each evaluation layer."""

def run_ablation(
    results: list[EvalResult],
) -> AblationReport:
    """Calculate pass rates under different layer configurations.

    Configurations:
    - L0 only
    - L0 + L3
    - L0 + L1 (compilation adds what?)
    - L0 + L1 + L3
    - Full pipeline (L0-L4)
    """

class AblationReport(BaseModel):
    configs: dict[str, float]  # config_name -> pass_rate
    layer_contributions: dict[str, float]  # layer_name -> delta
    # e.g., "L1 adds 5%p discrimination" = L0_only pass rate - L0+L1 pass rate
```

**File: `src/embedeval/failure_taxonomy.py` (신규)**

```python
"""Automated failure classification based on check results."""

class FailurePattern(str, Enum):
    HAPPY_PATH_BIAS = "happy_path_bias"        # Error path cleanup missing
    SEMANTIC_MISMATCH = "semantic_mismatch"      # Compiles but wrong HW semantics
    RESOURCE_IMBALANCE = "resource_imbalance"    # alloc without free
    ORDER_VIOLATION = "order_violation"           # init→register→use order
    MAGIC_NUMBER = "magic_number"                 # Unnamed constants
    MISSING_OPERATION_LOOP = "missing_op_loop"   # One-shot instead of periodic
    API_HALLUCINATION = "api_hallucination"       # Non-existent API
    CROSS_PLATFORM_CONFUSION = "cross_platform"  # Wrong platform API

def classify_failure(result: EvalResult) -> FailurePattern | None:
    """Auto-classify failure based on which checks failed."""
    # Map check_name patterns to FailurePattern
    # e.g., "error_handling" failed → HAPPY_PATH_BIAS
    # e.g., "no_cross_platform_apis" failed → CROSS_PLATFORM_CONFUSION
```

**논문 활용:**
- Table: "Ablation Study — Layer Contribution to Discrimination"
- Figure: "Failure Pattern Distribution" (pie/bar chart)
- Key finding: "L3 (behavioral heuristic) catches X% of failures that L1 (compilation) misses"

---

### Phase 8: Multi-Scenario + 동적 업데이트 + Human Validation [P3]

**이 phase는 논문 제출 후 v2에서 구현 가능. 여기서는 scaffolding만.**

**A. Multi-Scenario (Bug Fix mode)**

**File: `cases/bugfix/` (신규 디렉토리)**

10개 bug-fix TC 시범 생성:
- 의도적 버그가 있는 코드 + "이 코드의 문제를 찾고 수정하라" 프롬프트
- 기존 reference solution에서 mutation 적용 → buggy code 자동 생성 가능

**File: `src/embedeval/cli.py`**
- `embedeval run --scenario bugfix` 옵션

**B. 동적 업데이트**

- `metadata.yaml`에 `version: "v1"` 필드 추가
- 분기별 10 TC 추가 계획 문서화
- `--benchmark-version v1` 필터 추가

**C. Human Validation Documentation**

- `docs/HUMAN_VALIDATION.md` — 검토 프로토콜 정의
  - 검토자 자격 요건
  - 검토 항목 체크리스트 (프롬프트 명확성, check 타당성, reference 정확성)
  - IAA 측정 방법 (Fleiss' kappa)
- 최소 3명 검토자 확보 계획

---

## Testing Strategy

### Unit Tests (per phase)
| Phase | Test File | Key Cases |
|-------|-----------|-----------|
| 1 | `test_scorer.py` | Unbiased estimator, Wilson CI, edge cases |
| 2 | `test_evaluator.py` | Docker mock, tmpdir isolation, L1 pass/fail |
| 3 | `test_runner.py` | Default public filter, private exclusion |
| 4 | `test_ast_utils.py` | volatile scope, return-after-error, cleanup order |
| 5 | `test_sensitivity.py` | Variant generation, robustness calculation |
| 6 | `test_difficulty.py` | IRT calibration, label validation |
| 7 | `test_ablation.py` | Layer configs, failure classification |

### Integration Tests
- 전체 220 reference solutions이 업그레이드된 check로도 PASS (regression)
- Docker L1에서 최소 5개 reference solution 컴파일 성공

### E2E Tests
- `uv run embedeval run --model mock --cases cases/ --attempts 5` → unbiased pass@k 계산 확인
- `uv run embedeval sensitivity --model mock --sample 5` → sensitivity report 생성

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| AST 파서가 LLM 생성 코드 파싱 실패 | High | tree-sitter는 partial parsing 지원. Fallback to regex. |
| Docker L1이 CI에서 느림 | Medium | `--skip-compile` 플래그로 선택적 실행 |
| Check precision 향상이 reference solution도 FAIL시킴 | High | E2E regression test 필수. Reference 먼저 검증. |
| IRT 보정에 최소 3개 모델 결과 필요 | Medium | Sonnet + Haiku + 1개 추가(GPT-4o or Opus) |
| tree-sitter-c 의존성 추가 | Low | optional dependency로 관리 |

---

## Success Criteria

- [ ] pass@k unbiased estimator가 `comb()` 기반으로 정확하게 동작
- [ ] 95% Wilson CI가 모든 모델 점수에 보고됨
- [ ] Docker로 최소 Zephyr native_sim 컴파일 성공 (L1 활성화)
- [ ] Check precision 80%+ (negatives.py 기준)
- [ ] 50 TC가 private으로 설정됨
- [ ] 프롬프트 민감도 분석 실행 가능
- [ ] IRT 난이도 보정 결과 생성 가능
- [ ] Ablation study 결과 테이블 생성 가능
- [ ] 실패 분류 자동화 동작
- [ ] 모든 기존 테스트 PASS (regression 없음)

---

## Execution Order

```
Phase 1 (P0, Low)  ──→  Phase 2 (P0, High)  ──→  Phase 3 (P1, Medium)
                                                       │
Phase 4 (P1, High) ←─────────────────────────────────┘
    │
    ├──→ Phase 5 (P2, Medium) ──→ Phase 6 (P2, Medium)
    │
    └──→ Phase 7 (P3, Medium) ──→ Phase 8 (P3, High, partial)
```

**Phase 1 먼저** — 가장 간단하고 즉시 논문 신뢰성 향상.
**Phase 2 다음** — 논문의 가장 큰 약점 해소 (코드 실행 없음).
**Phase 4 병렬** — AST 체크는 독립적으로 진행 가능.

---

## Next Step

```
/execute paper-level-benchmark
```

Phase 1 (pass@k unbiased estimator)부터 시작. 가장 빠르고 확실한 개선.
