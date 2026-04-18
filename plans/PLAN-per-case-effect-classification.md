# PLAN: Per-Case Effect Classification in context-compare

**Project:** embedeval
**Task:** `embedeval context-compare` 출력에 per-case effect (helpful / harmful / no-effect-fail / no-effect-pass) 를 first-class field 로 노출
**Priority:** Medium
**Created:** 2026-04-18

---

## Executive Summary

> **TL;DR:** 2026-04-18 trade-off analysis (REVIEW Addendum 2) 에서 발견된 **per-case effect 분류** 를 `context-compare` 의 정식 출력으로 승격. Aggregate Lift 가 dilute 되는 진짜 phenomenon (case별 sign 다름) 을 사용자가 즉시 볼 수 있게 함.

### What We're Doing

- `CaseEffect` enum 추가 (helpful / harmful / no-effect-fail / no-effect-pass)
- `PerCaseComparison` model: case별 bare/team/expert pass 상태 + bare→expert effect (+ bare→team if team provided)
- `CategoryComparison.effect_counts` computed field: per-category 집계 (`{helpful: 2, harmful: 1, ...}`)
- Table 에 effect breakdown 컬럼 추가 (`+H/−H/=F/=P` 형식)
- JSON 출력에 `per_case` 리스트 추가 (전체 case별 detail)

### Why It Matters

**Empirical 정당화:** 2026-04-18 14-TC 분석에서 aggregate Lift 가 0% 였지만 per-case는 +/−/0 가 섞여 있었음. Aggregate 만으로는 signal 손실. Per-case 노출로:

1. **사용자가 즉시 trade-off 패턴 인지** — "Lift +5pp" 가 "5/14 helpful, 1/14 harmful, 8/14 no-effect" 의 어떤 그림인지 알 수 있음
2. **EmbedEval check brittleness 디버깅 enabler** — harmful case 가 어떤 것인지 list 로 보고 generated code 비교 가능
3. **Pack curation 피드백** — pack 수정 후 어떤 case가 helpful로 전환됐는지 추적
4. **CI integration 강화** — JSON 의 per_case 로 회귀 감지 ("어제 helpful 이던 case가 오늘 harmful")

### Key Decisions

- **D1 — bare→expert effect 항상, bare→team effect optional** — bare→expert 가 "pack이 도움 됐는가" 의 dominant 질문. team이 제공되면 bare→team도 추가 (Lift 와 parallel).
- **D2 — Per-case detail 은 JSON 만, table 은 per-category 집계만** — 233 case × 4 category 가 stdout 에 dump 되면 무용. Table = compact, JSON = full.
- **D3 — Tracker 의 boolean 그대로 사용 (n>1 시 last-attempt only)** — 현재 tracker schema 가 `passed: bool` 단일값. n=multi 통계는 별도 tool (aggregate_n_runs.py). Documentation 으로 limitation 명시.
- **D4 — Effect 컬럼 형식: `+H/−H/=F/=P` 4숫자** — `+2/−1/=3/=4` 같은 compact form. 기호는 직관적 (helpful=+, harmful=−, no-effect=⊘ but ASCII로 =).
- **D5 — Backward compat: 기존 JSON consumer 깨지 않음** — 신규 필드만 추가, 기존 필드 (lift, gap, *_pass_rate) 모두 그대로.

### Estimated Impact

- **Complexity:** Medium
- **Risk Level:** Low (additive, 기존 동작 변경 없음)
- **Files Changed:** ~3 files
- **Phases:** 4 phases
- **Estimated Time:** 5-7h

---

## ⚠️ REVIEW CHECKLIST

> **Verify before /execute**

### 설계 검증
- [ ] **D1 적합성** — bare→team effect 도 default 로 보일지, --include-team-effect 같은 flag 로 opt-in 할지
- [ ] **D3 limitation** — n>1 attempts 에서 tracker가 last-only 인 점이 사용자 혼동 일으키지 않을지. 명시적 warning 필요?
- [ ] **D4 시각화** — `+2/−1/=3/=4` 가 직관적인지, 더 좋은 형식 있는지 (eg. `2H/1Hm/3F/4P`)

### 코드 영향
- [ ] **`context_compare.py`** — schema 확장 (CaseEffect, PerCaseComparison). 기존 ContextComparison consumer 가 새 필드 무시할 수 있는지 (Pydantic v2 extra='ignore' 기본)
- [ ] **`cli.py`** — 새 옵션 없음 (per-case detail 은 항상 JSON에). 단, `--per-case` stdout flag 가 유용할지 검토
- [ ] **Test coverage** — n>1 scenario, mixed case sets, missing tracker entries 모두 커버

### 비-목표 (NON-GOALS)
- [ ] **harmful-real vs harmful-brittle 자동 분류** — 코드 inspection 필요, 별도 task (R8 follow-up)
- [ ] **Per-case stdout dump (--per-case flag)** — JSON 에서 충분, v2 검토
- [ ] **Cross-model effect comparison** — 같은 pack, 다른 model. 별도 task
- [ ] **n>1 statistical robustness** — aggregate_n_runs.py 영역, 이 PLAN은 single-run tracker 만

**✋ 위 항목 검토 완료 후에만 /execute 진행**

---

## Prior Work

### Related Documents

- [`plans/PLAN-context-quality-mode.md`](./PLAN-context-quality-mode.md) — Context Quality Mode 본 PLAN. R8 (per-case sign 다름) 이 본 task 의 motivation.
- [`plans/REVIEW-context-quality-mode-2026-04-18.md`](./REVIEW-context-quality-mode-2026-04-18.md) — **Addendum 2** 가 trade-off pattern empirical 발견. 본 task 가 그 발견을 first-class output 으로 승격.
- [`docs/CONTEXT-QUALITY-MODE.md`](../docs/CONTEXT-QUALITY-MODE.md) — "negative Lift는 real signal" 박스. Per-case 가 그 signal의 정확한 위치를 보여줌.
- [`src/embedeval/context_compare.py`](../src/embedeval/context_compare.py) — 현 구현. Per-category 까지만, per-case 는 없음.

### Decisions to Reuse

- `CategoryComparison.lift/gap` 패턴: `@computed_field + @property` (REVIEW F1) — JSON 직렬화에 필수. `effect_counts` 도 동일 패턴.
- `_per_category_pass_rates` 의 union (categories 모두) 처리 — case set 도 동일 (bare ∪ team ∪ expert).
- Mismatch warning (compare_runs F5) — 그대로. Effect counts 는 mismatch 영향 받음, 경고 reuse.

---

## Problem Analysis

### What

`context-compare` 출력에 다음을 추가:

1. **Per-category effect counts** (table + JSON):
   ```
   Category          n     Bare Expert   Lift   Gap   +H −H =F =P
   isr-concurrency  10      30%   80%  +50pp +20pp    3  1  2  4
   ```

2. **Per-case detail** (JSON only, 새 top-level field):
   ```json
   "per_case": [
     {
       "case_id": "isr-concurrency-001",
       "category": "isr-concurrency",
       "bare_passed": false,
       "team_passed": null,
       "expert_passed": true,
       "bare_to_expert_effect": "helpful",
       "bare_to_team_effect": null
     },
     ...
   ]
   ```

### Why

REVIEW Addendum 2 발견:
- N=14 에서 OVERALL Lift = 0%, but per-case = 2 helpful + 2 harmful + 7 no-effect-fail + 3 no-effect-pass
- Aggregate 만 보면 "no signal" 결론, per-case 보면 "signal exists, but cancels"

이걸 사용자가 코드 분석 없이 즉시 볼 수 있어야 함.

### Success Criteria

- [ ] `embedeval context-compare ...` table 에 effect 컬럼 표시
- [ ] `--output-json` 결과에 `per_case: [...]` + `per_category[*].effect_counts`
- [ ] 모든 effect 4종 (helpful/harmful/no-effect-fail/no-effect-pass) 정확 분류
- [ ] team 제공 시 `bare_to_team_effect` 도 채워짐, 미제공 시 None
- [ ] Mixed case sets (bare 가진 case가 expert 에 없음) graceful 처리 (effect=None)
- [ ] 기존 unit tests 전체 green, 기존 JSON consumer 깨지지 않음 (additive only)
- [ ] 신규 tests ≥6 (4 effect 종류 × happy + edge + integration)
- [ ] `mypy --strict` 변경 파일 clean
- [ ] `docs/CONTEXT-QUALITY-MODE.md` 새 필드 설명 추가

---

## Code Review

### Current State

- `context_compare.py:89-101` — `_per_category_pass_rates(tracker, model)` returns `{category: (passed, total)}`. **Per-case 정보 손실** — case별 pass/fail 를 모름.
- `compare_runs` 에서 per_category 만 build, per_case 없음.
- `format_comparison_table` 가 lift/gap 까지만 표시.
- JSON output 은 `report.model_dump_json()` 으로 ContextComparison schema 직접 직렬화.

### Affected Components

| File | 변경 |
|------|------|
| `src/embedeval/context_compare.py` | CaseEffect enum, PerCaseComparison model, classify_effect(), per-case build, effect_counts computed field, table 컬럼 추가 |
| `tests/test_context_compare.py` | per-case classification tests, JSON schema tests, table render tests |
| `docs/CONTEXT-QUALITY-MODE.md` | 새 필드 설명 + sample JSON + table 예시 |

### Dependencies

- 신규 라이브러리 없음 (enum, pydantic 기존)
- `_per_category_pass_rates` refactor 필요 — per-case data 도 같이 반환하거나 별도 함수로 분리

---

## Technical Design

### Schema Additions

```python
from enum import Enum

class CaseEffect(str, Enum):
    """How a context pack changed a single case's pass/fail status."""
    HELPFUL = "helpful"              # bare fail → packed pass (pack unblocked)
    HARMFUL = "harmful"              # bare pass → packed fail (pack broke)
    NO_EFFECT_FAIL = "no-effect-fail"  # both fail (LLM hard-limit)
    NO_EFFECT_PASS = "no-effect-pass"  # both pass (no headroom)


class PerCaseComparison(BaseModel):
    """Per-case pass/fail status across packs + effect classification.

    bare_to_expert_effect is the dominant question ("did the pack help?").
    bare_to_team_effect mirrors the Lift dimension when team is provided.
    Either may be None when one side lacks the case (mixed case sets).
    """
    case_id: str
    category: str
    bare_passed: bool | None = None
    team_passed: bool | None = None
    expert_passed: bool | None = None
    bare_to_expert_effect: CaseEffect | None = None
    bare_to_team_effect: CaseEffect | None = None
```

### Classification Function

```python
def classify_effect(bare_passed: bool, packed_passed: bool) -> CaseEffect:
    """Classify the per-case effect of a pack on bare baseline.

    Truth table:
        bare  packed   effect
        ────  ──────   ─────────────
        F     T        HELPFUL
        T     F        HARMFUL
        F     F        NO_EFFECT_FAIL
        T     T        NO_EFFECT_PASS

    n>1 attempts limitation: tracker stores only the most recent attempt's
    pass status. For statistical robustness across attempts, use
    scripts/aggregate_n_runs.py before running context-compare.
    """
    if not bare_passed and packed_passed:
        return CaseEffect.HELPFUL
    if bare_passed and not packed_passed:
        return CaseEffect.HARMFUL
    if not bare_passed:
        return CaseEffect.NO_EFFECT_FAIL
    return CaseEffect.NO_EFFECT_PASS
```

### Aggregation per Category

```python
class CategoryComparison(BaseModel):
    # ... existing fields ...

    # Counts of per-case effects, bare→expert dimension. Sums to n_cases
    # for cases where both bare and expert have data.
    @computed_field  # type: ignore[prop-decorator]
    @property
    def effect_counts(self) -> dict[str, int]:
        # Computed from per_case at compare_runs time, stored as
        # ContextComparison field. CategoryComparison doesn't know
        # about per_case directly; we attach effect_counts as an
        # eagerly-computed dict (not @computed_field) — see design
        # alternative below.
        ...
```

**Design alternative:** `effect_counts` 를 `@computed_field` 가 아니라 일반 `dict[str, int]` field 로 두고, `compare_runs` 에서 채워넣는 게 단순함. CategoryComparison 이 per_case 를 모르므로 `@computed_field` 로 lazy compute 가 어려움. → **eager populated regular field** 채택.

```python
class CategoryComparison(BaseModel):
    # ... existing ...
    effect_counts: dict[str, int] = Field(default_factory=dict)  # NEW
    # Same shape: {"helpful": 2, "harmful": 1, "no-effect-fail": 3, "no-effect-pass": 4}
```

### Top-level Output Schema

```python
class ContextComparison(BaseModel):
    model: str
    runs: list[RunSummary]
    per_category: list[CategoryComparison]
    overall: CategoryComparison
    per_case: list[PerCaseComparison] = Field(default_factory=list)  # NEW
```

### Table Format

```
  Category              n     Bare Expert   Lift   Gap   +H −H =F =P
  --------------------------------------------------------------------
  isr-concurrency      10      30%   80%  +50pp +20pp    3  1  2  4
  dma                   8       0%   75%  +75pp +25pp    6  0  2  0
  --------------------------------------------------------------------
  OVERALL              18      17%   78%  +61pp +22pp    9  1  4  4

  +H = helpful (bare fail → packed pass)
  −H = harmful (bare pass → packed fail) — inspect generated code, may be brittleness
  =F = no-effect, both fail (LLM hard-limit)
  =P = no-effect, both pass (no headroom)
```

When `team` provided, table stays bare→expert dimension only (avoid 8 effect columns). team→bare effect is exposed in JSON only.

### Why bare→expert (not team→expert)

PLAN context: "expert" 는 EmbedEval 이 ship 하는 reference ceiling. "team" 은 사용자의 CLAUDE.md. 가장 흔한 질문:
1. "내 프로젝트에서 expert pack 이 도움 되는가?" → bare→expert
2. "내 팀 컨텍스트가 도움 되는가?" → bare→team (when team provided)
3. "Expert 가 team 보다 얼마나 더 나은가?" → team→expert (already captured by Gap %)

Per-case effect 는 1번 + 2번 만 노출. 3번은 aggregate Gap 으로 충분.

### Mixed Case Sets

`bare_dir` 에는 case A 가 있고 `expert_dir` 에는 없는 경우:
- `PerCaseComparison.expert_passed = None`
- `bare_to_expert_effect = None`
- 해당 case 는 `effect_counts` 합계에서 제외 (sum < n_cases 가능)

JSON consumer 가 case별 missing 을 처리할 수 있어야 함. 기존 mismatch warning (F5) 가 케이스 카운트 차이를 미리 alert.

---

## Implementation Plan

### Phase 1 — Classification Primitives (1-2h)

**1.1 `src/embedeval/context_compare.py`**

- `CaseEffect` str enum 추가 (4 values)
- `classify_effect(bare_passed, packed_passed) -> CaseEffect` 추가
- `PerCaseComparison` model 추가 (5 fields + 2 effect)

**1.2 `tests/test_context_compare.py` — primitives**

```python
class TestClassifyEffect:
    def test_bare_fail_packed_pass_helpful(self):
        assert classify_effect(False, True) == CaseEffect.HELPFUL

    def test_bare_pass_packed_fail_harmful(self):
        assert classify_effect(True, False) == CaseEffect.HARMFUL

    def test_both_fail_no_effect_fail(self):
        assert classify_effect(False, False) == CaseEffect.NO_EFFECT_FAIL

    def test_both_pass_no_effect_pass(self):
        assert classify_effect(True, True) == CaseEffect.NO_EFFECT_PASS

class TestPerCaseComparison:
    def test_required_fields_minimal(self):
        ...
    def test_serializes_effect_as_string(self):
        # CaseEffect(str, Enum) → JSON value is "helpful" not 0
        ...
```

**Phase 1 종료 조건:** primitives 단독 테스트 통과, 기존 테스트 깨지지 않음.

---

### Phase 2 — Wire into compare_runs (2-3h)

**2.1 새 helper: `_build_per_case`**

```python
def _build_per_case(
    bare_tracker: TrackerData,
    expert_tracker: TrackerData,
    team_tracker: TrackerData | None,
    model: str,
) -> list[PerCaseComparison]:
    bare = bare_tracker.results.get(model, {})
    expert = expert_tracker.results.get(model, {})
    team = team_tracker.results.get(model, {}) if team_tracker else {}
    all_ids = sorted(set(bare) | set(expert) | set(team))
    out: list[PerCaseComparison] = []
    for cid in all_ids:
        b = bare.get(cid)
        e = expert.get(cid)
        t = team.get(cid) if team_tracker else None
        b_pass = b.passed if b else None
        e_pass = e.passed if e else None
        t_pass = t.passed if t else None
        be_eff = (
            classify_effect(b_pass, e_pass)
            if b_pass is not None and e_pass is not None
            else None
        )
        bt_eff = (
            classify_effect(b_pass, t_pass)
            if b_pass is not None and t_pass is not None
            else None
        )
        out.append(PerCaseComparison(
            case_id=cid,
            category=_category_of(cid),
            bare_passed=b_pass,
            team_passed=t_pass,
            expert_passed=e_pass,
            bare_to_expert_effect=be_eff,
            bare_to_team_effect=bt_eff,
        ))
    return out
```

**2.2 새 helper: `_aggregate_effect_counts`**

```python
def _aggregate_effect_counts(
    per_case: list[PerCaseComparison],
    category: str | None = None,
    dimension: str = "bare_to_expert_effect",
) -> dict[str, int]:
    counts = {e.value: 0 for e in CaseEffect}
    for pc in per_case:
        if category is not None and pc.category != category:
            continue
        eff = getattr(pc, dimension)
        if eff is not None:
            counts[eff.value] += 1
    return counts
```

**2.3 `compare_runs` refactor**

- 호출 끝에 `per_case = _build_per_case(...)` 추가
- per_category 빌드 시 `effect_counts = _aggregate_effect_counts(per_case, cat)` 채움
- overall 빌드 시 `effect_counts = _aggregate_effect_counts(per_case)`
- ContextComparison 에 `per_case=per_case` 추가

**2.4 Schema 변경**

```python
class CategoryComparison(BaseModel):
    # existing fields...
    effect_counts: dict[str, int] = Field(default_factory=dict)

class ContextComparison(BaseModel):
    # existing fields...
    per_case: list[PerCaseComparison] = Field(default_factory=list)
```

**2.5 Tests**

```python
def test_compare_runs_includes_per_case():
    # synthetic 3-case tracker, verify per_case length and content

def test_compare_runs_effect_counts_per_category():
    # verify counts match expected for known synthetic data

def test_per_case_handles_missing_in_one_dir():
    # case in bare but not in expert → effect = None

def test_team_effect_filled_when_team_provided():
    # bare_to_team_effect is non-None when team_dir given
```

**Phase 2 종료 조건:** synthetic data 로 schema/JSON 검증, 기존 27 tests 그대로 통과.

---

### Phase 3 — Table Display (1-2h)

**3.1 `format_comparison_table` 수정**

새 4-column block (`+H −H =F =P`) 추가. 기존 has_team 분기와 함께:

```python
header = (
    f"  {'Category':<22} {'n':>4}  "
    f"{'Bare':>6} {'Team':>6} {'Expert':>6}  "  # if team
    f"{'Lift':>7} {'Gap':>7}  "
    f"{'+H':>3} {'−H':>3} {'=F':>3} {'=P':>3}"
)
```

각 row 끝에 effect 4값 추가:
```python
ec = c.effect_counts or {}
h = ec.get("helpful", 0)
hm = ec.get("harmful", 0)
nf = ec.get("no-effect-fail", 0)
np = ec.get("no-effect-pass", 0)
row += f"  {h:>3} {hm:>3} {nf:>3} {np:>3}"
```

Footer 에 effect 약어 의미 추가.

**3.2 Tests**

```python
def test_table_renders_effect_columns():
    # assert "+H" "−H" "=F" "=P" all in output
    # assert numeric counts appear

def test_table_footer_explains_effect_abbreviations():
    # assert "helpful" "harmful" "no-effect" all in footer
```

**Phase 3 종료 조건:** Mock model run + context-compare → 표 출력에 새 컬럼 보임.

---

### Phase 4 — Documentation (30min)

**4.1 `docs/CONTEXT-QUALITY-MODE.md`**

- "Per-case effect classification" 새 섹션 추가
- `effect_counts` JSON 예시
- `per_case` JSON 예시 (1-2 entries)
- Table 의 새 컬럼 의미 (+H/−H/=F/=P)
- "Harmful = always inspect generated code" warning (brittleness vs real)

**4.2 No README change** — README 의 Context Quality Mode 섹션은 high-level intro 만, 세부는 docs/ 로 link.

**Phase 4 종료 조건:** docs PR-ready.

---

## Testing Strategy

### Unit Tests (`tests/test_context_compare.py`)

| Test | 목적 |
|------|-----|
| `test_classify_effect_helpful` | bare F + packed T → HELPFUL |
| `test_classify_effect_harmful` | bare T + packed F → HARMFUL |
| `test_classify_effect_no_effect_fail` | both F → NO_EFFECT_FAIL |
| `test_classify_effect_no_effect_pass` | both T → NO_EFFECT_PASS |
| `test_per_case_serializes_enum_as_string` | JSON value 가 "helpful" string |
| `test_compare_runs_includes_per_case` | per_case list non-empty after compare |
| `test_per_case_handles_missing_in_one_dir` | mixed case sets → effect None |
| `test_team_effect_filled_when_team_provided` | bare_to_team_effect populated |
| `test_team_effect_none_when_no_team` | bare_to_team_effect = None |
| `test_effect_counts_per_category` | 합계 = 해당 카테고리 case 수 (excluding None) |
| `test_effect_counts_overall_sums_to_total` | overall.effect_counts 합 = 전체 |
| `test_table_renders_effect_columns` | "+H/−H/=F/=P" 표시 |
| `test_json_export_includes_per_case` | model_dump_json 에 per_case key 존재 |

### Integration

E2E mock run: `embedeval run --model mock --output-dir /tmp/...` × 2 + `context-compare --output-json` → JSON 에 새 필드 검증. (이미 있는 mock e2e 패턴 재활용.)

### Backward Compat Check

- 기존 27 tests 모두 통과 (additive only)
- `model_dump_json()` 결과에 기존 필드 모두 존재 (lift, gap, *_pass_rate)
- `--output-json` JSON 의 기존 consumer 가 새 필드를 ignore 가능 (Pydantic v2 추가 필드는 backward compat)

---

## Risks & Mitigation

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|------------|--------|------------|
| R1 | Schema 확장으로 기존 JSON consumer 깨짐 | Low | High | additive only — 기존 필드 변경 없음. 기존 JSON test 회귀로 검증 |
| R2 | n>1 attempts 시 last-only effect 가 misleading | Medium | Medium | classify_effect docstring + docs 에 명시. n>1 사용자는 aggregate_n_runs.py 안내 |
| R3 | Mixed case sets 처리 — None effect 가 헷갈림 | Low | Low | effect_counts 는 None 제외하고 합산. 합 < n_cases 가능, 이게 정상이라고 docs 에 명시 |
| R4 | Table 가 너무 wide — terminal 크기 (80 cols) 초과 | Medium | Low | Effect column 4개 = 16 chars. 기존 with-team 헤더 + 16 = ~95 chars. 90 cols 환경 권장으로 README 명시 |
| R5 | "+H/−H/=F/=P" 약어가 직관적이지 않음 | Medium | Low | Footer 에 풀어 설명. 5분 학습이면 이해 가능 |
| R6 | Effect counts 가 dict[str, int] 라 type-checker 가 keys 검증 못함 | Low | Low | docstring 에 4 known keys 명시. test_effect_counts_keys_complete 추가 |
| R7 | Per-case list 가 233 entries 까지 커져서 JSON file 크기 부담 | Low | Low | 233 entry × ~150 bytes = ~35KB. CI artifact 로 무리 없음 |

---

## Success Criteria (재확인)

- [ ] `CaseEffect` enum + `PerCaseComparison` + `classify_effect` 구현 + tests
- [ ] `compare_runs` 가 `per_case: list[PerCaseComparison]` 채움
- [ ] `CategoryComparison.effect_counts: dict[str, int]` 채움 (per-category, OVERALL 모두)
- [ ] `format_comparison_table` 에 `+H/−H/=F/=P` 컬럼 + footer 설명
- [ ] `--output-json` 결과에 `per_case` + `effect_counts` 모두 존재
- [ ] team 제공 시 `bare_to_team_effect` 도 채워짐
- [ ] Mixed case sets — effect None 처리, count 에서 제외
- [ ] 신규 ≥10 unit tests, 기존 1318 tests 전부 green
- [ ] `mypy --strict src/embedeval/context_compare.py` clean
- [ ] `docs/CONTEXT-QUALITY-MODE.md` per-case 섹션 추가

---

## Estimated Effort

| Phase | 범위 | 시간 |
|-------|------|-----|
| Phase 1 | Primitives (enum, model, classify) + tests | 1-2h |
| Phase 2 | compare_runs refactor + per_case build + JSON tests | 2-3h |
| Phase 3 | Table 컬럼 추가 + tests | 1-2h |
| Phase 4 | Docs (CONTEXT-QUALITY-MODE.md 섹션) | 30min |
| **Total** | | **5-7h** |

---

## Out of Scope (NON-GOALS)

- **Harmful sub-classification (real vs brittleness)** — 코드 inspection 필요. 별도 task로, R8 follow-up. 본 PLAN 은 "harmful" 까지만, 사용자가 docs 의 warning 따라 inspect.
- **Per-case stdout dump (--per-case flag)** — JSON 으로 충분, terminal noise 우려. 사용자 요청 시 v2.
- **n>1 statistical effect (e.g., "consistently helpful at 3/3 attempts")** — tracker schema 변경 필요 (passed: bool → pass_rate: float). aggregate_n_runs.py 영역.
- **Cross-model effect** — 같은 pack 다른 model 비교. 별도 reporter.
- **Effect direction prediction (ML)** — 본 PLAN 은 measurement 만. Prediction 은 별도 연구 task.

---

## Follow-up Work (이 PLAN 완료 후)

1. **Harmful sub-classification** — `harmful` case 의 generated code 를 자동 분석하여 (a) real attention trade-off (b) benchmark check brittleness 판별. SDK API variant DB 필요.
2. **`--per-case` stdout flag** — 사용자가 specific case 를 즉시 보고 싶을 때.
3. **Effect 추세 추적** — CI 에서 매번 per_case JSON 비교 → "어제 helpful 이던 case가 오늘 harmful" alert.
4. **Pack 수정 가이드** — harmful case 의 패턴에서 pack 의 어느 문장이 문제인지 추적 (LLM-aided diff).

---

## References

- [`plans/PLAN-context-quality-mode.md`](./PLAN-context-quality-mode.md) — Context Quality Mode 본 PLAN
- [`plans/REVIEW-context-quality-mode-2026-04-18.md`](./REVIEW-context-quality-mode-2026-04-18.md) Addendum 2 — empirical motivation
- 2026-04-18 trade-off analysis (Haiku N=14): 2 helpful, 2 harmful, 7 no-effect-fail, 3 no-effect-pass

---

**Status:** Draft v1 — 2026-04-18

**Next:** Review checklist 확인 후 `/execute per-case-effect-classification` 로 Phase 1부터 진행.
