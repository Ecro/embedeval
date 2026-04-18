# PLAN: Context Quality Mode

**Project:** embedeval
**Task:** `embedeval run --context-pack` + `embedeval context-compare` — 팀의 implicit context가 LLM 임베디드 코드 품질에 미치는 효과를 정량 측정
**Priority:** High
**Created:** 2026-04-18

---

## Executive Summary

> **TL;DR:** 같은 LLM에 (1) bare prompt (2) 팀 컨텍스트 (3) expert 컨텍스트를 각각 주입하여 pass rate를 비교하는 모드를 추가한다. 출력은 **Context Lift** (팀 컨텍스트 효과)와 **Context Gap** (expert까지의 잔여)로, CI에 넣을 수 있는 객관 지표가 된다.

### What We're Doing

- `embedeval run`에 `--context-pack PATH` 플래그 추가 → 모든 TC prompt 앞에 prepend
- 같은 TC를 다른 context pack으로 N번 돌린 결과를 비교하는 `embedeval context-compare` 신설
- `context_packs/expert.md` 큐레이션 — `LLM-EMBEDDED-FAILURE-FACTORS.md` 핵심 압축 (~1.5K tokens)
- Tracker에 `context_pack_hash` 기록 → 잘못된 cross-run 비교 차단

### Why It Matters

- 임베디드 팀이 CLAUDE.md / system prompt를 잘 작성하면 LLM reviewer/coder 정확도가 의미 있게 올라간다는 게 2025 연구 합의 ([arXiv:2505.20206](https://arxiv.org/html/2505.20206v1)). 그러나 **팀의 컨텍스트가 충분한가**를 객관 측정하는 도구는 없음.
- EmbedEval은 LLM 자체를 측정하는 유일한 도구이므로, 같은 LLM에 다른 context를 주입한 결과 비교는 **EmbedEval만이 만들 수 있는 출력**. Semgrep도 hiloop도 LLM reviewer도 못 만듦.
- B2B 스토리: "이번 CLAUDE.md 변경으로 ISR 카테고리 +12%p" — CI 회귀 테스트 가능한 지표.
- EmbedEval의 implicit-vs-explicit 35%p gap (MEMORY.md) 이 추상 통찰에서 **사용자가 자기 팀에 대해 측정 가능한 지표**로 변환됨.

### Key Decisions

- **D1 — Prepend to user prompt (system role 아님)** — `claude-code://` CLI도 지원해야 하므로 messages API 의존 X. litellm 모델 한정으로 v2에서 system role 옵션 추가 가능.
- **D2 — `--context-pack`은 기존 `context_files`와 별도 채널** — 전자는 run-wide team config, 후자는 per-case task material. 의미가 다르므로 합치지 않음.
- **D3 — Tracker에 content hash 기록** — path가 아닌 내용을 SHA256. 같은 내용 다른 경로의 cache miss를 막고, 다른 컨텐츠를 같은 run으로 합치는 사고를 차단.
- **D4 — Expert pack은 ship-with-EmbedEval** — 사용자에게 reference ceiling을 제공. `FAILURE-FACTORS.md`에서 자동 생성하는 스크립트 포함하여 stale 방지.

### Estimated Impact

- **Complexity:** Medium
- **Risk Level:** Low (additive, 기존 동작 변경 없음)
- **Files Changed:** ~10 files
- **Phases:** 4 phases
- **Estimated Time:** 12-18h

---

## ⚠️ REVIEW CHECKLIST

> **Verify before /execute**

### 설계 검증
- [ ] **D1 적합성:** `claude-code://` 모드에서 prepend가 실제로 적용되는지 — `_call_claude_code()`가 단일 prompt만 받는지 재확인
- [ ] **D2 분리:** 사용자가 `--context-pack`을 per-case 자료로 오해할 가능성 — README/help 문구로 충분히 구분되는가
- [ ] **D3 hash 충돌:** SHA256 8자 vs 16자 truncation — tracker file 가독성 vs 충돌 가능성 trade-off
- [ ] **D4 expert pack 분량:** ~1.5K tokens가 적절한가 — 너무 길면 LLM이 무시, 너무 짧으면 의미 없음

### 코드 영향
- [ ] **`llm_client.call_model`** — signature 변경 (`context_pack: str | None` 추가). 기존 호출자 전부 호환 (default None)
- [ ] **`runner.py`** — `_run_one_case()` chain에 context_pack 전파. feedback retry path에도 동일 적용
- [ ] **`test_tracker.py`** — `context_pack_hash` 필드. 기존 tracker JSON 호환 (Optional, default None)
- [ ] **`reporter.py` / 신규 `context_compare.py`** — 별도 모듈 vs reporter 확장 — 후자가 모듈 비대화 우려

### 검증
- [ ] Bare vs expert pack 차이가 통계적으로 유의미한가 — 5개 TC × 3 runs로 사전 검증
- [ ] Token usage 증가량을 리포트에 표시 — 사용자가 cost trade-off 인지

### 비-목표 (NON-GOALS)
- [ ] LLM의 system prompt API 직접 사용 — 추후 v2
- [ ] Context pack 자동 생성 (RAG over codebase) — hiloop 영역
- [ ] Per-category context pack — 일단 글로벌만

**✋ 위 항목 검토 완료 후에만 /execute 진행**

---

## Prior Work (Knowledge Retrieval)

### Related Documents

- [`plans/PLAN-implicit-prompts.md`](./PLAN-implicit-prompts.md) — implicit knowledge gap 발견 작업. 이 PLAN은 그 통찰을 사용자가 자기 팀에 측정 가능한 지표로 변환하는 후속 작업.
- [`plans/PLAN-paper-level-benchmark.md`](./PLAN-paper-level-benchmark.md) — pass@k unbiased estimator 등 통계 인프라. context-compare가 같은 통계 도구 재사용.
- [`docs/LLM-EMBEDDED-FAILURE-FACTORS.md`](../docs/LLM-EMBEDDED-FAILURE-FACTORS.md) — expert pack의 source-of-truth. 42 factors → 1.5K token summary로 압축.
- [`src/embedeval/safety_guide.py`](../src/embedeval/safety_guide.py) — 이미 capability boundary + per-task checklist를 텍스트로 보유. expert pack 생성에 그대로 재활용.
- [`src/embedeval/ablation.py`](../src/embedeval/ablation.py) — layer 기여도 분석 패턴. context-compare는 동일 구조의 "context configuration ablation."

### What Worked Before

- `context_files` mechanism 자체는 이미 존재 (per-case context 주입). 같은 prepend pattern을 글로벌 channel로 확장하면 됨 → 새 인프라 만들지 않음.
- `safety_guide.py`의 `CAPABILITY_BOUNDARY` + `TASK_CHECKLISTS` 텍스트가 expert pack의 80% 재료. curation overhead 낮음.

### Decisions to Reuse

- LLM client → runner → tracker 흐름은 기존 그대로. `context_pack`은 일급 객체가 아닌 부가 정보로 취급.
- Hash + tracker enforcement는 PLAN-paper-level-benchmark의 contamination prevention과 동일 사상.

---

## Problem Analysis

### What

EmbedEval 사용자가 자기 팀의 CLAUDE.md / system prompt 파일을 EmbedEval에 입력하면, 같은 LLM에 (a) 컨텍스트 없음 (b) 팀 컨텍스트 (c) expert 컨텍스트를 각각 주입한 pass rate를 측정하고, 둘의 차이로 컨텍스트 효과를 정량화한다.

### Why

1. **EmbedEval 차별화:** semgrep/LLM reviewer/hiloop 어느 것도 "LLM에 다른 context를 주입한 비교"를 못함. EmbedEval의 LLM-측정 본질에서 자연스럽게 나오는 출력.
2. **사용자의 의사결정 도구:** "우리 CLAUDE.md를 보강해야 하나?" → Context Gap이 크면 yes. "이 변경이 효과 있었나?" → Lift로 확인.
3. **Implicit Knowledge Gap (35%p) 의 사용자화:** 추상 메트릭을 자기 팀의 구체적인 숫자로 변환.

### Success Criteria

- [ ] `embedeval run --context-pack mypack.md --cases cases/isr-concurrency-001 --models claude-code://sonnet` 실행 성공
- [ ] Tracker에 `context_pack_hash` 정확 기록, 다른 hash 결과끼리 섞이면 명시적 에러
- [ ] `embedeval context-compare bare/ team/ expert/` 가 per-category Lift/Gap 표 생성
- [ ] 5-TC × 3 context × 3 runs 사전 검증에서 monotonic 경향 확인 (bare ≤ team ≤ expert가 카테고리의 ≥50%)
- [ ] 신규 코드 ≥3 unit test (happy / edge / error), 기존 테스트 전체 green

---

## Code Review

### Current State

- `llm_client.call_model(model, prompt, context_files=[...])` — context_files는 per-case 보조 자료를 prompt 위에 prepend ([llm_client.py:47-69](../src/embedeval/llm_client.py))
- `runner._run_one_case()` 이 `_collect_context_files(case_dir)` 로 per-case context를 모음
- `safety_guide.py` 에 이미 capability boundary + checklist 텍스트 존재 (~3K tokens) — expert pack 재료
- `test_tracker.py` 가 model × case 별 결과 + run metadata 저장 — 여기에 context hash 추가

### Affected Components

| File | 변경 |
|------|------|
| `src/embedeval/llm_client.py` | `call_model` 에 `context_pack` param 추가, prepend 로직 |
| `src/embedeval/runner.py` | `--context-pack` path 받아 한 번 로드, call_model에 전파 (feedback retry 포함) |
| `src/embedeval/cli.py` | `run` 커맨드에 `--context-pack PATH` 옵션, 신규 `context-compare` 커맨드 |
| `src/embedeval/test_tracker.py` | `context_pack_hash: str | None` 필드, mismatch 시 명시적 처리 |
| `src/embedeval/models.py` | RunMetadata 에 `context_pack_hash` 추가 (있다면) |
| `src/embedeval/context_compare.py` | **신규** — 비교 reporter |
| `src/embedeval/context_packs/expert.md` | **신규** — curated context pack |
| `scripts/build_expert_pack.py` | **신규** — `FAILURE-FACTORS.md` → expert.md 자동 생성 |
| `tests/test_context_pack.py` | **신규** — 4-6 unit tests |
| `docs/CONTEXT-QUALITY-MODE.md` | **신규** — 사용법, 해석 가이드, CI 예제 |

### Dependencies

- 신규 라이브러리 없음 (hashlib stdlib, 기존 typer/pydantic)
- `LLM-EMBEDDED-FAILURE-FACTORS.md` 가 source-of-truth로 기능 의존

---

## Technical Design

### Context Injection Flow

```
embedeval run --context-pack pack.md --cases ... --models ...
          │
          ▼
runner: load pack.md once, hash it (SHA256[:16])
          │
          ▼
for each case:
    prompt = load_prompt(case)
    prompt = inject_board_target(prompt, meta)
    response = call_model(
        model=model,
        prompt=prompt,
        context_pack=pack_text,    ← NEW
        context_files=per_case_context_files,
    )
          │
          ▼
llm_client._build_full_prompt():
    parts = []
    if context_pack: parts.append("## Team Context\n" + context_pack)
    if context_files: parts.append(_build_context(context_files))
    parts.append(user_prompt)
    return "\n\n".join(parts)
          │
          ▼
tracker.record(model, case_id, result, context_pack_hash=hash)
```

### Hash & Mismatch Enforcement

```python
# tracker append-time check
if existing_run.context_pack_hash != new.context_pack_hash:
    raise ValueError(
        f"Context pack mismatch in tracker for {model}: "
        f"existing={existing_run.context_pack_hash[:8]} "
        f"new={new.context_pack_hash[:8]}. "
        f"Use --output-dir to separate runs."
    )
```

→ 사용자가 다른 pack 결과를 한 디렉터리에 쏟지 못하게 막음.

### Comparison Output (context-compare)

```
$ embedeval context-compare \
    --bare runs/bare/ \
    --team runs/team/ \
    --expert runs/expert/

Context Quality Comparison (model: claude-code://sonnet, n=3 each)

Category            Bare     Team     Expert    Lift     Gap
─────────────────────────────────────────────────────────────────
isr-concurrency     32%      54%      78%      +22%p   +24%p
dma                 41%      47%      71%       +6%p   +24%p
threading           38%      62%      85%      +24%p   +23%p
gpio-basic          88%      90%      94%       +2%p    +4%p
...
─────────────────────────────────────────────────────────────────
Overall             58%      69%      87%      +11%p   +18%p

Interpretation:
- Lift > 10%p: 팀 컨텍스트가 효과적
- Gap > 15%p: 컨텍스트 보강 여지 큼 (특히 isr/dma/threading)
- Gap < 5%p: 이 카테고리에서 LLM 한계, 컨텍스트로 안 됨 → hiloop/HIL 필요

Total tokens used:
  Bare:    1.2M  ($X.XX)
  Team:    1.4M  ($X.XX)  +17% tokens
  Expert:  1.6M  ($X.XX)  +33% tokens
```

→ Gap이 작으면 "LLM 한계 영역"이라는 신호 — 사용자에게 hiloop/runtime 단계로 가라는 자연스러운 routing.

### Expert Pack Content (Sketch)

`context_packs/expert.md` (~1.5K tokens):

```markdown
# Embedded Firmware Implicit Rules

## ISR Context
- All variables shared between ISR and thread MUST be `volatile`
- Memory barriers required after ISR-shared writes (compiler_barrier or arch barrier)
- ISR MUST NOT call: mutex_lock, sleep, printk (use LOG_*), malloc
- Use spinlock (not mutex) for ISR-thread synchronization

## DMA
- Buffers MUST be cache-line aligned (typically __aligned(32))
- Cache flush before DMA write, invalidate before DMA read on coherent platforms
- Configure peripheral BEFORE starting DMA (init order)

## Memory & Allocation
- Static allocation strongly preferred over dynamic in deeply embedded
- Stack sizes must account for ISR worst-case nesting
- Check every alloc/init return value, cleanup in reverse order

## Linux Kernel Drivers
- Use copy_to_user/copy_from_user, never direct user pointer deref
- Hold spinlock for shortest possible critical section
- RCU dereferences require rcu_read_lock or appropriate lock held

## Build Configuration
- Verify CONFIG_* dependencies before assuming features available
- DT bindings must match driver compatible strings exactly
- Pin conflicts checked across overlay + base device tree
```

자동 생성 스크립트: `scripts/build_expert_pack.py` 가 `FAILURE-FACTORS.md` 의 high-impact factors를 카테고리별 그룹화 → 위 형식으로 출력. CI에서 weekly regen 가능.

### Why NOT system role API

| Mode | system role 지원 | 결정 |
|------|-----------------|------|
| `mock` | N/A | prepend |
| `claude-code://` (CLI) | `claude -p`는 단일 prompt | prepend 강제 |
| litellm (API) | `messages=[{role:system}]` 가능 | prepend (일관성) |

→ 모든 모드에서 동일 동작 보장. 결과 비교 가능성이 system role 의 약간의 정확도 이득보다 중요.

---

## Implementation Plan

### Phase 1 — MVP Wiring (4-6h)

**목표:** `--context-pack` 플래그가 동작하고 tracker에 hash가 기록됨.

**1.1 `src/embedeval/llm_client.py`**

```python
def call_model(
    model: str,
    prompt: str,
    context_files: list[str] | None = None,
    context_pack: str | None = None,        # NEW
    timeout: float = 300.0,
    max_retries: int = 3,
    rate_limit_delay: float = 1.0,
) -> LLMResponse:
    ...
    full_prompt = _build_full_prompt(prompt, context_files, context_pack)
    ...

def _build_full_prompt(
    prompt: str,
    context_files: list[str] | None,
    context_pack: str | None,
) -> str:
    parts: list[str] = []
    if context_pack:
        parts.append(f"## Team Context\n\n{context_pack.strip()}")
    file_ctx = _build_context(context_files or [])
    if file_ctx:
        parts.append(file_ctx)
    parts.append(prompt)
    return "\n\n".join(parts)
```

**1.2 `src/embedeval/cli.py`** — `run` 커맨드에 옵션 추가:

```python
context_pack: Annotated[
    Optional[Path],
    typer.Option(
        "--context-pack",
        help="Path to a global context file prepended to every prompt "
             "(e.g., team's CLAUDE.md). Use 'expert' for the bundled expert pack.",
    ),
] = None,
```

특수값 `expert` → `embedeval/context_packs/expert.md` 로 resolve.

**1.3 `src/embedeval/runner.py`**

```python
def run_benchmark(
    ...,
    context_pack_path: Path | None = None,
) -> BenchmarkReport:
    context_pack_text: str | None = None
    context_pack_hash: str | None = None
    if context_pack_path:
        context_pack_text = context_pack_path.read_text(encoding="utf-8")
        context_pack_hash = hashlib.sha256(
            context_pack_text.encode("utf-8")
        ).hexdigest()[:16]
        logger.info(
            "Using context pack %s (hash=%s, %d chars)",
            context_pack_path.name, context_pack_hash, len(context_pack_text)
        )
    ...
    # propagate to call_model + feedback retry
```

**1.4 `src/embedeval/test_tracker.py`** — RunMetadata에 `context_pack_hash: str | None` 추가, append-time mismatch 검사.

**1.5 `tests/test_context_pack.py`** — 4 tests:
- `test_context_pack_prepended_to_prompt` (mock model)
- `test_context_pack_hash_stable` (같은 내용 → 같은 hash)
- `test_tracker_rejects_hash_mismatch`
- `test_missing_context_pack_file_raises`

**Phase 1 종료 조건:** `embedeval run --context-pack mypack.md --models mock --cases <단일 case>` 실행 후 tracker JSON에 hash 확인 가능.

---

### Phase 2 — Comparison Reporter (4-6h)

**목표:** `embedeval context-compare` 가 표 생성.

**2.1 `src/embedeval/context_compare.py` (신규)**

```python
class ContextComparison(BaseModel):
    model: str
    runs: dict[str, RunSummary]   # "bare", "team", "expert"
    per_category: list[CategoryComparison]
    overall: CategoryComparison

def compare_runs(
    bare_dir: Path,
    team_dir: Path | None,
    expert_dir: Path,
    model: str | None = None,
) -> ContextComparison:
    """Load tracker from each dir, compute per-category lift/gap."""
    ...
```

**2.2 `src/embedeval/cli.py`** — 신규 커맨드:

```python
@app.command("context-compare")
def context_compare(
    bare: Annotated[Path, typer.Option("--bare")],
    team: Annotated[Optional[Path], typer.Option("--team")] = None,
    expert: Annotated[Path, typer.Option("--expert")] = ...,
    model: Annotated[Optional[str], typer.Option("--model")] = None,
    output: Annotated[Optional[Path], typer.Option("--output")] = None,
) -> None:
    """Compare benchmark runs across context packs."""
```

출력: stdout 표 + (옵션) `output.json` / `output.md`.

**2.3 `tests/test_context_compare.py`** — synthetic tracker 3개로 비교 결과 검증.

**Phase 2 종료 조건:** synthetic 데이터로 표 생성 + ≥1 real run pair (mock 모델 OK) 로 end-to-end 동작 확인.

---

### Phase 3 — Expert Pack Curation (2-4h)

**3.1 `scripts/build_expert_pack.py`** — `FAILURE-FACTORS.md` 파싱:
- 카테고리별로 high-impact factor 추출 (frequency × severity)
- ~1.5K tokens 한계 내에서 압축
- output: `src/embedeval/context_packs/expert.md`
- CI에서 `FAILURE-FACTORS.md` 변경 시 자동 재생성 + diff PR

**3.2 `src/embedeval/context_packs/expert.md`** — 1차 수동 큐레이션. `safety_guide.py` 의 CAPABILITY_BOUNDARY + TASK_CHECKLISTS 재사용.

**3.3 검증** — 5 TC subset (isr-001, dma-005, threading-003, gpio-001, watchdog-001) 에 (bare, expert) 두 번씩 돌려서 expert > bare 인지 확인. 아니면 expert pack 재조정.

**Phase 3 종료 조건:** `embedeval run --context-pack expert ...` 동작, 5-TC 검증에서 ≥3개 카테고리에서 expert > bare.

---

### Phase 4 — Documentation & CI Recipe (1-2h)

**4.1 `docs/CONTEXT-QUALITY-MODE.md`** — 사용법:
- "팀의 CLAUDE.md를 EmbedEval로 검증하기"
- Lift / Gap 해석 가이드
- 결과가 의미하는 것 (Gap 큼 = 컨텍스트 보강 / Gap 작음 = LLM 한계, hiloop 필요)

**4.2 `docs/CONTEXT-QUALITY-MODE.md` 내 CI 예제** — GitHub Action snippet:

```yaml
- name: Context Quality Regression
  run: |
    embedeval run --models claude-code://sonnet --output runs/bare/ ...
    embedeval run --models claude-code://sonnet --context-pack ./CLAUDE.md --output runs/team/ ...
    embedeval context-compare --bare runs/bare/ --team runs/team/ --expert runs/expert/ \
      --output context-report.json
    python scripts/check_context_regression.py context-report.json
    # exits non-zero if Lift drops vs main branch
```

**4.3 README.md** — Context Quality Mode 섹션 1단락 + 링크.

**Phase 4 종료 조건:** doc PR-ready, CI snippet copy-paste 가능.

---

## Testing Strategy

### Unit Tests (`tests/test_context_pack.py`, `tests/test_context_compare.py`)

| Test | 목적 |
|------|-----|
| `test_context_pack_prepended_to_prompt` | mock model 호출 시 prompt가 `## Team Context\n...\n\n<original>` 구조 |
| `test_context_pack_hash_stable` | 같은 bytes → 같은 hash, whitespace 1 char 차이 → 다른 hash |
| `test_context_pack_hash_independent_of_path` | 같은 내용 다른 파일 경로 → 같은 hash |
| `test_tracker_rejects_hash_mismatch` | 기존 hash A인 tracker에 hash B 결과 append → 명시적 ValueError |
| `test_missing_context_pack_file_raises` | 존재하지 않는 path → FileNotFoundError with helpful message |
| `test_special_value_expert_resolves` | `--context-pack expert` → bundled file path |
| `test_compare_lift_calculation` | synthetic bare/team/expert tracker → 정확한 lift/gap |
| `test_compare_handles_missing_team` | `--team` 생략 시 lift 컬럼 N/A |

### Integration Test

`tests/test_context_quality_mode_e2e.py`:
- `mock` 모델로 5-TC 서브셋 × 3 context (none / 짧은 / expert) → tracker 3개 생성 → context-compare 실행 → JSON output schema 검증.

### Manual Testing

1. 실제 모델 (Haiku, 빠른 모델) 로 5-TC × 3 context 돌려서 Lift/Gap이 비현실적이지 않은지 (e.g., bare 90%, expert 10% 같은 역전이 없어야 함)
2. expert.md 의 token 수 측정 (`tiktoken` 또는 휴리스틱) — 1500±300 범위 확인
3. `--context-pack` 없이 `embedeval run` 했을 때 기존 동작 100% 동일 확인 (regression)

---

## Risks & Mitigation

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|------------|--------|------------|
| R1 | `claude-code://` CLI가 prepended context를 system이 아닌 user message로 받아 효과가 약화 | Medium | Medium | 그게 정확히 우리가 측정하려는 것 — 실제 사용자도 CLAUDE.md를 같은 방식으로 주입함. 의도된 동작 |
| R2 | Context pack이 너무 길어 모델 무시 (≥4K tokens) | Medium | Low | expert.md ≤2K token 가이드라인, 사용자 pack 길이 경고 (3K 초과 시 stderr warn) |
| R3 | Expert pack이 너무 explicit해서 모든 implicit gap을 닫음 → 모든 카테고리 90%+ → discrimination 잃음 | Medium | Medium | Phase 3 검증에서 모니터링. 일부러 high-level 원칙만 적고 exact API name 회피 |
| R4 | Tracker schema 변경으로 기존 tracker 파일 깨짐 | Low | High | `context_pack_hash` Optional, missing → None 으로 backward compat. v1 tracker 자동 마이그레이션 path |
| R5 | 사용자가 같은 dir에 다른 pack 결과 누적 → 비교 무의미 | Medium | High | hash mismatch 시 tracker append 단계에서 명시적 raise (D3) |
| R6 | Token 비용 33% 증가 → 사용자 불만 | Medium | Low | 리포트에 token usage 명시, doc에 trade-off 설명. CI 모드에서는 subset만 돌리도록 권장 |
| R7 | Expert pack curation이 stale (FAILURE-FACTORS 변경 추종 안 됨) | High | Medium | `scripts/build_expert_pack.py` + CI weekly check |
| **R8** | **Expert pack effect는 case별로 sign이 다름 (도움 / 무영향 / 역효과 모두 존재). Implementation 후 empirically 발견된 risk** | **High** | **Medium** | **TC별 effect direction을 측정·노출. "expert > bare" 단순 가정 금지. 2026-04-18 검증 참조.** |

---

## Success Criteria (재확인)

### Implementation completeness
- [x] `embedeval run --context-pack mypack.md` 동작, tracker에 hash 기록
- [x] `embedeval run --context-pack expert ...` 동작
- [x] `embedeval context-compare --bare X --team Y --expert Z` 표 생성
- [x] hash mismatch 시 명시적 에러 (3 transition shapes 모두)
- [x] 신규 코드 ≥8 unit tests (실제 37개), 기존 테스트 전부 green (1314)
- [x] `mypy --strict` 변경 파일 clean (전체 src/ 미검증 — gap)
- [x] `docs/CONTEXT-QUALITY-MODE.md` PR-ready

### Real-LLM validation (2026-04-18)

5-TC × n=3 × bare/expert 검증 결과 (Haiku, headroom-rich cases):

- [ ] **≥50% 카테고리에서 monotonic (bare ≤ expert)** — 4/5 만족 (1/5 isr-concurrency-003 100→0% 역전). 조건 부분 충족.
- [x] R3 (over-explicit, 90%+ blowout) — 실증적으로 mitigated (overall 27%→27%, 어떤 카테고리도 ceiling forced 안 됨)
- [ ] **새 발견: R8 (trade-off effect)** — 위 R8 참조

### Outstanding gaps (all closed 2026-04-19)
- [x] **Token usage report** — Closed by commit `7a255e8` (Phase A). `RunSummary.input_tokens`/`output_tokens`/`cost_usd` summed from `CaseResult` aggregates; table footer shows `+NN% input vs bare` delta.
- [x] **`scripts/build_expert_pack.py`** (R7 mitigation) — Closed by commit `7a255e8` (Phase C). Drift detector parses FAILURE-FACTORS.md, emits `expert-coverage.md`, CI gates on drift. Intentionally NOT a generator to preserve R3 mitigation (principles, not APIs).
- [x] **Separate e2e test file** — Closed by commit `ab067fd` (Phase E). `tests/test_context_quality_mode_e2e.py` drives full CLI pipeline: 3x `embedeval run` (bare/team/expert) → 3 trackers → `context-compare --output-json` → schema validation. Runs in ~9s on mock + uart category.
- [x] **`mypy --strict` full src/** — Verified clean 2026-04-19 (commit `be08371`). Note: `strict = true` is already the project-wide default in `pyproject.toml` and CI has been enforcing it via `uv run mypy src/` since before this PLAN. The "gap" was a false alarm on our tracking. What WAS drifting: `ruff format --check src/` on 5 files (fixed in `be08371`).

### R8 follow-up (per-case effect measurement)
- [x] **Per-case effect classification** — Closed by PLAN-per-case-effect-classification (commit `d7d054f`). `context-compare` now emits per-case effect (`helpful`/`harmful`/`no-effect-*`) both in the table (`H/Hm/F/P` column) and in JSON (`per_case[]`), with `--include-team-effect` opt-in for the bare→team dimension.
- [x] **Harmful sub-classification** — Closed by commit `7a255e8` (Phase B). New `embedeval harmful-inspect` CLI classifies each harmful case using the `failed_at_layer` heuristic (L0→brittleness, L1+→real).

---

## Estimated Effort

| Phase | 범위 | 시간 |
|-------|------|-----|
| Phase 1 | CLI flag + plumbing + tracker hash + tests | 4-6h |
| Phase 2 | context-compare reporter + tests | 4-6h |
| Phase 3 | expert.md curation + auto-build script + 검증 | 2-4h |
| Phase 4 | docs + CI recipe + README | 1-2h |
| **Total** | | **12-18h** |

---

## Out of Scope (NON-GOALS)

- LLM API의 system role 직접 사용 (litellm `messages` 옵션) — 모드 일관성 우선, v2 검토
- 자동 context pack 생성 (RAG over 사용자 codebase) — hiloop 영역
- Per-category context pack — 글로벌 우선, 데이터 보고 향후 분기
- Context pack diff 시각화 — 단순 문자열 diff는 사용자가 git으로 함
- Context pack registry / sharing platform — 너무 이름. expert pack 한 개만 ship

---

## Follow-up Work (이 PLAN 완료 후 후속 후보)

1. **A4 (Self-Review Experiment)** — 같은 모델이 자기 코드를 review했을 때 catch rate 측정. context-pack 모드와 결합하면 "context-rich self-review" 의 한계 정량화 가능 → publishable.
2. **A1 (Differential Detection Matrix)** — semgrep/hiloop/LLM-reviewer 와 EmbedEval의 catch coverage Venn diagram. context-pack 모드의 결과가 이 매트릭스의 행을 추가함 ("context-rich reviewer" 행).
3. **A8 (Longevity Failure Category)** — `failure_horizon` 태깅 + L5 layer. EmbedEval이 못 잡는 영역을 명시적으로 카탈로그화.

---

## References

- 이전 리서치: 2026-04-18 /research 세션 — Context-rich LLM reviewer 효과 입증 ([arXiv:2505.20206](https://arxiv.org/html/2505.20206v1)), enterprise tool 사례 (Greptile, Qodo, Cubic), longevity testing gap (Mbed/LittleFS soak test)
- [`docs/LLM-EMBEDDED-FAILURE-FACTORS.md`](../docs/LLM-EMBEDDED-FAILURE-FACTORS.md) — expert pack source-of-truth
- [`docs/LLM-EMBEDDED-DEVELOPMENT-GUIDE.md`](../docs/LLM-EMBEDDED-DEVELOPMENT-GUIDE.md) — context template 참고
- [`memory/MEMORY.md`](../.claude/memory/MEMORY.md) — Implicit-vs-explicit 35%p gap 메모

---

**Status:** Draft v1 — 2026-04-18

**Next:** Review checklist 확인 후 `/execute embedeval-context-quality-mode` 로 Phase 1부터 진행.
