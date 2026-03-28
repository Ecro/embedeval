# PLAN: Bug Fix Scenario

**Project:** embedeval
**Task:** Add "Bug Fix" evaluation scenario — LLM must identify and fix seeded bugs in embedded code
**Priority:** Medium (Phase 8A of paper-level upgrade)
**Created:** 2026-03-26

---

## Executive Summary

> **TL;DR:** Add a bug-fix scenario that reuses existing negatives.py mutations as seeded bugs, testing whether LLMs can diagnose and repair embedded firmware defects.

### What We're Doing
현재 EmbedEval은 "코드를 처음부터 생성하라" (generation) 1가지 시나리오만 평가.
Bug Fix 시나리오는 reference solution에 negatives.py의 mutation을 적용한 buggy code를 LLM에 제공하고,
"이 코드의 문제를 찾아 수정하라"는 프롬프트로 평가. 수정된 코드가 기존 behavior check를 통과하면 성공.

### Why It Matters
- **논문 차별화**: LiveCodeBench는 4 시나리오, BigCodeBench는 2 시나리오 — EmbedEval도 최소 2 시나리오 필요
- **실무 현실성**: 실제 개발에서 LLM은 코드 생성보다 버그 수정에 더 자주 사용됨
- **기존 인프라 재활용**: negatives.py의 mutation이 이미 10 TC에 45개 mutation 정의 — 새 TC 안 만들어도 됨

### Key Decisions
- **Mutation 재활용** — negatives.py의 `must_fail` mutation을 buggy code 소스로 사용
- **프롬프트 표준화** — "이 코드에 [카테고리] 관련 버그가 있습니다. 찾아서 수정하세요."
- **기존 check 재사용** — 수정된 코드를 동일한 behavior.py로 평가 (새 체크 불필요)

### Estimated Impact
- **Complexity:** Medium
- **Risk Level:** Low (기존 인프라 재활용)
- **Files Changed:** ~5 files
- **New TC Content:** 0 (mutation 재활용)

---

## Technical Design

### Architecture

```
Reference Solution → Apply Mutation → Buggy Code
                                         ↓
                              Bugfix Prompt Template
                                         ↓
                                    LLM Response
                                         ↓
                              Existing behavior.py checks
                                         ↓
                                    PASS / FAIL
```

### Data Flow

1. `runner.py`가 case 디렉토리 로드
2. `reference/main.c` 읽기
3. `checks/negatives.py`에서 `must_fail` mutation 적용 → buggy code 생성
4. bugfix 프롬프트 템플릿에 buggy code 삽입
5. LLM 호출 → 수정된 코드 수신
6. 기존 `evaluator.py`로 수정된 코드 평가 (L0 + L3)

### Bugfix Prompt Template

```
The following embedded C code contains a bug. The code is intended for {platform}
({category} task: {title}).

## Buggy Code

```c
{buggy_code}
```

## Bug Description

{mutation_description}

## Task

Find and fix the bug. Output ONLY the complete corrected C source file.
```

### CLI Integration

```bash
# Run bug fix scenario on all cases with negatives
uv run embedeval run --model claude-code://sonnet --cases cases/ --scenario bugfix

# Run on specific category
uv run embedeval run --model claude-code://sonnet --cases cases/ --scenario bugfix -c isr-concurrency
```

---

## Implementation Plan

### Phase 1: Core Bugfix Runner

**File: `src/embedeval/bugfix.py` (신규)**

```python
class BugfixCase:
    case_id: str
    mutation_name: str
    buggy_code: str
    description: str
    original_case_dir: Path

def discover_bugfix_cases(cases_dir: Path) -> list[BugfixCase]:
    """Discover all cases with negatives.py must_fail mutations."""
    # For each case with checks/negatives.py:
    #   Load reference/main.c
    #   Load NEGATIVES list
    #   For each must_fail mutation:
    #     Apply mutation to reference → buggy code
    #     Create BugfixCase

def generate_bugfix_prompt(
    buggy_code: str,
    mutation_description: str,
    metadata: CaseMetadata,
) -> str:
    """Generate standardized bug fix prompt."""

def run_bugfix_benchmark(
    cases_dir: Path,
    model: str,
    filters: Filters | None = None,
) -> list[EvalResult]:
    """Run bug fix scenario benchmark."""
    # Discover bugfix cases
    # For each: generate prompt → call LLM → evaluate fixed code
```

### Phase 2: CLI Integration

**File: `src/embedeval/cli.py`**

- `--scenario` 옵션 추가: `generation` (기본) | `bugfix`
- `bugfix` 시나리오일 때 `run_bugfix_benchmark()` 호출

### Phase 3: Reporter Integration

**File: `src/embedeval/reporter.py`**

- 리포트에 시나리오 구분 표시
- Bug fix pass rate vs generation pass rate 비교 테이블

### Phase 4: Tests

- `test_bugfix.py`: bugfix case 발견, 프롬프트 생성, mutation 적용, 평가 흐름
- E2E: reference solution이 bugfix 시나리오에서도 pass (mutation 없는 원본)

---

## Testing Strategy

### Unit Tests
- `discover_bugfix_cases()`: 10개 TC에서 45개 bugfix case 생성 확인
- `generate_bugfix_prompt()`: 프롬프트 포맷 검증
- mutation 적용 후 behavior check FAIL 확인 (buggy code가 실제로 buggy한지)
- mutation 수정 후 behavior check PASS 확인 (reference가 다시 통과하는지)

### Integration Tests
- Mock LLM으로 전체 bugfix 파이프라인 E2E
- 실제 LLM으로 1-2개 케이스 수동 검증

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Mutation이 너무 쉬움 (description이 답을 줌) | Medium | description을 간접적으로 변경 |
| 10 TC만 negatives.py 보유 | Medium | Phase 4에서 더 많은 TC에 negatives 추가 예정 |
| LLM이 buggy code를 무시하고 처음부터 작성 | Low | 프롬프트에 "수정만 하라" 강조 |

---

## Success Criteria

- [ ] `discover_bugfix_cases()`가 기존 10 TC에서 20+ bugfix case 생성
- [ ] bugfix 프롬프트 생성이 표준화됨
- [ ] `--scenario bugfix` CLI 옵션 동작
- [ ] buggy code가 behavior check FAIL 확인 (mutation 유효성)
- [ ] 전체 기존 테스트 regression 없음

---

## Next Step

```
/execute bugfix-scenario
```
