---
type: plan
project: embedeval
task_slug: hiloop-transpile-readiness
status: planning
created: 2026-04-19
tags: [embedeval, plan, python, embedded, testing, benchmark, process]
related:
  - "[[plans/PLAN-negative-tests]]"
  - "[[plans/PLAN-subtle-negatives]]"
  - "[[plans/PLAN-strengthen-tc-checks]]"
  - "[[docs/LLM-EMBEDDED-FAILURE-FACTORS]]"
  - "[[docs/METHODOLOGY]]"
summary: "Prepare EmbedEval checks for Hiloop transpile consumption: 100% negatives coverage, scope discipline, per-check metrics, shared-rule extraction"
---

# PLAN: Hiloop Transpile Readiness (P1–P4 bundled)

**Project:** embedeval
**Task:** EmbedEval-side changes that simultaneously improve benchmark quality AND make EmbedEval consumable as a transpile source for Hiloop's YAML rule authoring
**Priority:** High (benchmark quality) / Medium (Hiloop enabler)
**Due:** TBD — suggest 4-week rolling schedule
**Created:** 2026-04-19

---

## 🎯 Executive Summary

> **TL;DR:** Close four EmbedEval gaps (negatives coverage, scope discipline, per-check metrics, shared-rule extraction) that are each justified standalone by benchmark quality and collectively unblock Hiloop's transpile pipeline.

### What We're Doing

Four independent workstreams, all in the EmbedEval repo, all deliberately scoped so the benefit exists even if Hiloop is never built:

- **P1** Expand `checks/negatives.py` from 30 → 185 cases (100% coverage).
- **P2** Systematize check scope discipline: comment/string stripping + structural context for all substring checks.
- **P3** Emit structured per-check failure rates to the run summary JSON so Hiloop (or any consumer) has deterministic evidence.
- **P4** Extract hardcoded API blacklists from `check_utils.py` into a declarative data file that both EmbedEval and Hiloop rule pack can share.

Hiloop itself is NOT modified here — its transpile script, `LLMProvider`, reproducibility stamping, and MCP engine are Hiloop-repo concerns and preserve the "rules are data" boundary.

### Why It Matters

- L4 mutation oracle is currently dark on 84% of cases (`evaluator.py:779` short-circuits to pass when no `negatives.py`). Check precision is unproven at scale.
- Half the substring checks (e.g. `static.py:11` `"k_malloc" in generated_code`) can match inside comments or string literals — false signal on both directions.
- `results/LEADERBOARD.md` only has category-level pass rates. Per-check failure frequency (the highest-value signal for both reviewers and downstream tools) is computed transiently in `reporter.py:596` and never persisted.
- `check_utils.check_no_cross_platform_apis` hardcodes a blacklist that is semantically a reusable rule, not TC-local logic.

### Key Decisions

- **Decision 1:** Do NOT rewrite Python checks into YAML/tree-sitter inside EmbedEval. Transpile is Hiloop's job; EmbedEval stays Python-native. Chosen because mixing rule-engine concerns into the benchmark couples two products that should remain independent.
- **Decision 2:** Do NOT extend `CheckDetail.check_type` enum to match Hiloop's 8 modes. Chosen because it would rewrite 185 case files for a Hiloop-only benefit; Hiloop transpile can infer mode from Python AST.
- **Decision 3:** Treat P1 as the critical-path blocker. P2/P3/P4 can ship in parallel but P1 gates any transpile gate in Hiloop.
- **Decision 4:** Ship each P as its own PR with its own tests — no mega-PR. Review discipline matters more than speed here.

### Estimated Impact

- **Complexity:** Medium (P1 is mechanical bulk; P2 is tedious but straightforward; P3 is small; P4 is small)
- **Risk Level:** Medium (P2 has the highest risk of accidentally changing benchmark numbers — must audit before merging)
- **Files Changed:** ~200 (155 new `negatives.py`, ~50 edited `static.py`, ~3 core source files)
- **Estimated Time:** 20–30 hours (P1: 12–18h, P2: 6–8h, P3: 2–3h, P4: 2h)

---

## ⚠️ REVIEW CHECKLIST — Action Required

### Critical Decisions to Verify
- [ ] **Scope boundary:** Agree EmbedEval should NOT absorb Hiloop 8-mode / tree-sitter concerns into its own check format.
- [ ] **P1 mutation style:** Each negative must mutate the *reference solution*, not arbitrary candidate code — confirm this matches existing 30 examples (it does: see `isr-concurrency-008/checks/negatives.py:10`).
- [x] **P2 re-baseline policy: flip 허용 + 문서화** (user decision 2026-04-19). Any TC verdict flip caused by scope tightening is accepted; each flip must be enumerated in the merging PR description and a BENCHMARK-DELTA-<date>.md written. No case-by-case veto.
- [ ] **P3 schema:** Extending `summary.json` with a new field is backward-compatible if consumers (sync_docs.py, external dashboards) ignore unknown keys. Verify before shipping.
- [ ] **P4 file format:** YAML vs JSON for the extracted API data. Recommendation: YAML (matches existing `external_benchmarks.yaml`, `metadata.yaml`).
- [ ] **Yocto relevance (2026-04-19):** User's primary practice is Yocto/Embedded Linux. This PLAN's direct Yocto benefit is ~15% (P1 partial + P3 partial; P2/P4 mostly C/RTOS-biased). User must decide: proceed with full PLAN, prune to P1+P3, or defer in favor of `PLAN-yocto-coverage-expansion` (not yet written).

### Code Impact to Review
- [ ] **File: `src/embedeval/evaluator.py:770-858`** — `_run_mutant_checks`. P1 exercises this more heavily; confirm failure paths handle 155 new call sites without perf regression.
- [ ] **File: `src/embedeval/check_utils.py:143-168`** — `check_no_cross_platform_apis` list moves to data. Confirm all callers (grep shows ~20 `behavior.py` callers) still work with new signature if any.
- [ ] **File: `src/embedeval/reporter.py:583-596`** — transient per-check failure computation. P3 promotes this to persisted output; confirm no double-counting between "Most Common Failure Patterns" table and new per-check field.
- [ ] **File: `src/embedeval/models.py:148`** — `CheckDetail` model. P3 may add optional `stable_id` or `source` fields; verify Pydantic v2 serialization matches other computed fields (known gotcha: plain `@property` is NOT serialized; use `@computed_field`).
- [ ] **Dependencies:** No new Python dependencies.

### Testing Coverage
- [ ] Every new `negatives.py` must: (a) mutate the reference, (b) pass through `evaluator._run_mutant_checks` with all `must_fail` checks detecting the seeded bug on the *mutated* reference, and (c) the unmutated reference must still pass all checks.
- [ ] P2 audit needs a diff report: for every TC, run old-scope vs new-scope checks against stored sonnet/haiku n=3 generations — flag any case that changes verdict. Manual review each flag.
- [ ] P3 summary.json schema test: load a generated summary, assert new field present and schema-valid.
- [ ] P4 shared API YAML round-trip: `yaml.safe_load` must return the same list as the current hardcoded one (byte-for-byte equivalence after normalization).

### Business Logic
- [ ] Does P1+P2 change benchmark pass@1 numbers? **Expected: P1 no; P2 possibly yes, small** — document delta in commit message and update `BENCHMARK-COMPARISON` if any case flips.
- [ ] Acceptance criterion for P1: `find cases -name negatives.py | wc -l` = `find cases -name static.py | wc -l`.
- [ ] Acceptance criterion for P3: a Hiloop-style consumer can read per-check failure rates from one JSON file without scraping markdown.

**✋ Stop here if P2 risk (benchmark re-baseline) is unacceptable — that P alone can be deferred without blocking P1/P3/P4.**

---

## 📚 Prior Work (Knowledge Retrieval)

### Related Documents Found
- [[plans/PLAN-negative-tests]] — original design for `negatives.py` schema. Already validated on the existing 30 cases.
- [[plans/PLAN-subtle-negatives]] — adds "should_fail" soft negatives (second-order checks). Relevant for P1 extension beyond must_fail.
- [[plans/PLAN-strengthen-tc-checks]] — precedent for bulk check edits across all TCs. Process template.
- [[docs/LLM-EMBEDDED-FAILURE-FACTORS]] — 42-factor taxonomy used when designing mutations. P1 should tag each negative to a factor for traceability.
- [[plans/PLAN-per-case-effect-classification]] — per-case classification pattern; P3 can reuse aggregation approach.

### What Worked Before
- The 30 existing `negatives.py` follow a clean pattern (lambda mutation + `must_fail` list + optional `should_fail`). Same shape scales.
- `check_utils.py` already exists as a shared-utilities hub; P4 belongs there in spirit, as data rather than code.
- `scripts/verify_references_build.py` precedent for per-case scripts that validate repository-wide invariants.

### Known Blockers & Solutions
- 2026-03-29: `Check regexes must accept API variants` (see CLAUDE.md). P1 mutations must respect API-variant awareness or they'll be caught by the wrong check.
- 2026-03-29: `Content hashing must use file bytes, not st_mtime`. P3 field additions affect result hashing; verify hash input is file bytes only.
- 2026-04-18: `Pydantic v2 plain @property is NOT serialized`. If P3 adds a derived field to `CheckDetail`, use `@computed_field`.

### Decisions to Reuse/Reconsider
- Reuse: `NEGATIVES` list-of-dict schema. No Pydantic model — keeps negatives.py readable and diffable.
- Reconsider: should each negative link back to a `LLM-EMBEDDED-FAILURE-FACTORS` factor ID? (Recommend yes in P1 — cheap to add now, expensive to retrofit.)

---

## 📋 Problem Analysis

### What (per workstream)

| P | Workstream | State | Target |
|---|---|---|---|
| P1 | `negatives.py` coverage | 30/185 (16%) | 185/185 (100%) |
| P2 | Substring check scope | Inconsistent — some strip comments (`behavior.py`), some don't (`static.py:11`) | Uniform: all checks run on `strip_comments`-ed source unless scope needs raw |
| P3 | Per-check failure rate emission | Transient in `reporter.py:596`, not in summary.json | Persisted per-check map in summary.json |
| P4 | Shared API blacklist | Hardcoded in `check_utils.py:143` | `data/forbidden_apis.yaml` loaded at import time |

### Why

- **P1:** L4 mutation oracle is the only evidence that a check actually catches what it claims to catch. Without it, a passing reference + a vacuous check can masquerade as precision.
- **P2:** `strip_comments` was added for `behavior.py` but `static.py` uses raw `generated_code` — checks like `"k_malloc" in generated_code` will match `// no k_malloc allowed` in a comment. Produces both false positive (comment says forbidden API) and false negative (string literal `"use k_malloc"`).
- **P3:** Anyone (internal analysis, Hiloop transpile, external researcher) currently has to scrape `report.md` or walk `details/*.json` to compute per-check rates. Costly and error-prone.
- **P4:** The blacklist is semantically "platform-agnostic contamination detector" — reusable by any tool, not TC-local.

### Success Criteria

- [ ] P1: `negatives.py` exists in every case dir; CI check enforces it.
- [ ] P1: every `must_fail` check actually fails on its seeded mutation (already enforced by `evaluator._run_mutant_checks`).
- [ ] P2: all substring checks run against `strip_comments`ed input by default; any exception is explicitly opted out with comment rationale.
- [ ] P3: `summary.json` contains `per_check_stats: {check_name: {pass_rate, fail_count, total, tc_ids}}`.
- [ ] P4: `check_utils.check_no_cross_platform_apis` reads from `data/forbidden_apis.yaml`; byte-equivalent behavior to current.
- [ ] All 4: existing tests pass; no drop in documented benchmark numbers except an intentional P2 re-baseline documented in commit.

---

## 🔍 Code Review

### Current State

**L4 flow (`src/embedeval/evaluator.py:770-858`):**
- Reads `negatives.py::NEGATIVES` via `_load_negatives`.
- Applies each mutation to `generated_code`.
- Runs L0 + L3 checks on mutated code.
- Asserts each `must_fail` check actually fails.
- L4 failures DO NOT affect case pass/fail (by design — `evaluator.py:166` comment).

**Check scope (inconsistent):**
- `cases/isr-concurrency-001/checks/static.py:11`: `"k_malloc" in generated_code` (raw)
- `cases/isr-concurrency-001/checks/behavior.py:18`: `stripped = strip_comments(generated_code)` (scoped)
- `check_utils.find_isr_bodies` provides per-function-body scope when needed.

**Reporter aggregation (`src/embedeval/reporter.py:583-596`):**
- `pattern_counts` dict built per `BenchmarkReport`, not per-model-per-check.
- Emitted as markdown table "Most Common Failure Patterns" only.
- `summary.json` schema: models list with `layer_pass_rates`, categories list with `pass_at_1`. No per-check field.

**Shared data:**
- `check_utils.py:143` hardcodes cross-platform API list.
- Same list re-read per TC × per run. Refactor cost is low.

### Affected Components

- `src/embedeval/evaluator.py` — P1 exercises `_run_mutant_checks` more heavily (no code change, but test surface expands).
- `src/embedeval/check_utils.py` — P4 converts hardcoded list to YAML load.
- `src/embedeval/reporter.py` — P3 adds per-check aggregation to summary emission.
- `src/embedeval/models.py` — P3 may add `PerCheckStats` Pydantic model.
- `cases/*/checks/negatives.py` — P1 creates 155 new files.
- `cases/*/checks/static.py` — P2 may edit up to 185 files (audit-guided).
- `data/forbidden_apis.yaml` — P4 new file.
- `tests/` — new tests for P3, P4. P1 coverage is mechanically enforced by evaluator.
- `scripts/sync_docs.py` — P3 may add a per-check top-failure table to README.

### Dependencies

- PyYAML (already a dep — `pyproject.toml`)
- pytest (already a dev dep)
- No new deps.

---

## 🏗️ Technical Design

### P1: negatives.py Coverage Expansion

**Pattern (from `isr-concurrency-008/checks/negatives.py:32`):**

```python
NEGATIVES = [
    {
        "name": "<short_mutation_name>",
        "description": "<what the bug is, cite factor ID if applicable>",
        "mutation": lambda code: <transform>,
        "must_fail": ["<check_name_from_static.py_or_behavior.py>", ...],
        # Optional for subtle negatives:
        "should_fail": ["<check_name>"],
        "bug_description": "<why subtle — when check SHOULD flag but MAY miss>",
        # New recommended field (P1):
        "factor_id": "F3.2",  # from docs/LLM-EMBEDDED-FAILURE-FACTORS.md
    },
    ...
]
```

**Design rules:**
1. Each TC has ≥1 `must_fail` negative per distinct check in `static.py` + `behavior.py`. (Not 1:1 — some checks share a mutation; that's OK.)
2. Mutation operates on the *reference* solution, not arbitrary text. `evaluator._run_mutant_checks` passes `generated_code` but for must_fail gating we practically run it against reference during a new test.
3. Mutation must actually change the code (evaluator already asserts `mutated_code != generated_code`).
4. Tag each negative to a factor ID for traceability to the 42-factor taxonomy.

**Batch authoring approach:**
- Group by category (`dma`, `isr-concurrency`, `threading` first — highest-value, weakest Haiku scores).
- Write 3–5 TCs at a time, run `uv run pytest tests/test_mutations.py` (new), iterate.
- Do NOT use LLM to write mutations — they must be deterministic, audited Python.

### P2: Scope Discipline Audit

**Change:** Introduce a convention helper in `check_utils.py`:

```python
def scoped_contains(code: str, needle: str, *, scope: str = "stripped") -> bool:
    """Check needle in code with explicit scope.

    scope='stripped'  — strip comments + string literals (default)
    scope='raw'       — match anywhere (rare; must justify with comment)
    scope='code_only' — strip comments but keep string literals
    """
```

**Migration:** Replace bare `"X" in generated_code` with `scoped_contains(code, "X")` across `static.py` files. Opt out ONLY where intentional (e.g. matching a header include line pattern may legitimately scan raw — document inline).

**Re-baseline policy (user decision 2026-04-19):** Flips are allowed and documented, not vetoed. Process per category-PR:
1. Run replay on stored LLM generations (`results/runs/2026-04-12*/details/`).
2. Diff old vs new verdicts; enumerate all flipped case IDs in PR description.
3. Append a row per flip to `docs/BENCHMARK-DELTA-2026-xx.md` with: case ID, old verdict, new verdict, which check changed, one-line rationale.
4. Update `docs/BENCHMARK-COMPARISON-*.md` aggregate numbers after all P2 PRs land.
5. No case-by-case veto required. Reviewer checks only that flip rationale is plausible, not that flip itself is rejected.

### P3: Per-Check Metrics Emission

**Schema addition (`models.py`):**

```python
class PerCheckStat(BaseModel):
    check_name: str
    category: str  # case category (facilitates filtering)
    total_runs: int
    fail_count: int
    pass_rate: float = Field(ge=0.0, le=1.0)
    failing_tc_ids: list[str]  # unique TC ids where this check failed
```

**Addition to `ModelScore` (in `models.py`):**

```python
per_check_stats: list[PerCheckStat] = Field(default_factory=list)
```

**Aggregation (`scorer.py` new function):** Walk `EvalResult.layers[*].details[*]` grouping by `(model, check_name, case_category)`. Emit into `ModelScore.per_check_stats`.

**Backward compat:** Field is optional with default; old consumers ignore.

**Hiloop consumer contract** (informational, not enforced here):
> `summary.json.models[].per_check_stats[].{check_name, pass_rate, fail_count, failing_tc_ids}` is the authoritative evidence source for rule provenance. Hiloop transpile reads this file, not `report.md`.

### P4: Shared API Blacklist Extraction

**New file:** `src/embedeval/data/forbidden_apis.yaml`

```yaml
# Cross-platform API contamination detector.
# Consumed by: embedeval.check_utils.check_no_cross_platform_apis
#              (and any Hiloop shared rule pack referencing same data).
platforms:
  FreeRTOS:
    - xQueueSend
    - xQueueReceive
    - xTaskCreate
    # ... (move existing list)
  Arduino:
    - Serial.begin
    - digitalWrite
    # ...
  POSIX:
    - pthread_mutex_lock
    - pthread_create
    # ...
  STM32_HAL:
    - HAL_GPIO_WritePin
    # ...
  Linux_Userspace:
    - open
    - read
    # ...
```

**Loader (`check_utils.py`):**

```python
from functools import lru_cache
from importlib.resources import files

@lru_cache(maxsize=1)
def _load_forbidden_apis() -> dict[str, list[str]]:
    text = files("embedeval.data").joinpath("forbidden_apis.yaml").read_text()
    return yaml.safe_load(text)["platforms"]
```

**Packaging:** add `[tool.hatch.build.targets.wheel] packages = ["src/embedeval"]` include rule — already handled by uv_build, but verify `data/*.yaml` ships.

### Data Flow

```
                                   ┌──────────────────────┐
                                   │ data/forbidden_apis.yaml │   (P4)
                                   └──────────┬───────────┘
                                              │ load_forbidden_apis()
                                              ▼
cases/*/checks/static.py  ────┐    ┌──────────────────────┐
cases/*/checks/behavior.py ───┼───▶│   check_utils         │
cases/*/checks/negatives.py ──┤    │   (scoped_contains,  │   (P2, P4)
(P1 expands this)              │    │    shared checkers)   │
                                └──▶└──────────┬───────────┘
                                              │
                                              ▼
                                   ┌──────────────────────┐
                                   │ evaluator._run_*     │
                                   │  L0/L3/L4 pipeline   │
                                   └──────────┬───────────┘
                                              │
                                              ▼
                                   ┌──────────────────────┐
                                   │ scorer               │
                                   │  + per_check_stats   │   (P3)
                                   └──────────┬───────────┘
                                              │
                                              ▼
                                   summary.json + report.md
                                              │
                                              ▼
                              [Hiloop transpile consumes JSON —
                               post-LLM evidence injection]
```

### API Changes

- `CheckDetail` — unchanged (important: don't touch benchmark row schema).
- `ModelScore.per_check_stats` — new optional list.
- `check_utils.scoped_contains` — new helper; existing callers untouched unless migrated.
- No breaking changes to CLI.

---

## 📝 Implementation Plan

### Phase 0: Shared Foundations (week 0, ~2h)

- [ ] Add `src/embedeval/data/` package dir with `__init__.py` (empty).
- [ ] Add `tests/test_shared_data.py` scaffold.
- [ ] Decide P2 re-baseline policy with user — either "yes, re-baseline and document" or "P2 limited to tighter-only changes."

### Phase 1: P4 Extract Shared API List (week 1, ~2h)

- [ ] Create `src/embedeval/data/forbidden_apis.yaml` by copying current hardcoded list from `check_utils.py:143-168`.
- [ ] Refactor `check_no_cross_platform_apis` to load YAML via `importlib.resources`.
- [ ] Add `tests/test_forbidden_apis.py`:
  - loads YAML; returns same platforms set as before
  - `check_no_cross_platform_apis` produces identical verdict on fixture inputs
- [ ] Verify package data ships (`uv build` + inspect wheel).
- [ ] Commit: `refactor(check-utils): extract forbidden APIs to data/forbidden_apis.yaml`

### Phase 2: P3 Per-Check Metrics (week 1, ~3h)

- [ ] Add `PerCheckStat` model in `models.py`.
- [ ] Extend `ModelScore` with `per_check_stats: list[PerCheckStat] = Field(default_factory=list)`.
- [ ] Implement aggregation in `scorer.py` — walk `EvalResult.layers[*].details[*]`, group, emit.
- [ ] Wire into `reporter.generate_json` — field naturally serializes via pydantic.
- [ ] Add `tests/test_per_check_stats.py`:
  - fixture summary with 3 cases, 2 failing same check → pass_rate == 1/3, failing_tc_ids == 2 TCs
  - ensure aggregation works across categories
- [ ] (Optional) `sync_docs.py` addition to surface top failing checks in README.
- [ ] Commit: `feat(scorer): persist per-check failure stats in summary.json`

### Phase 3: P2 Scope Discipline (weeks 2, ~6–8h)

- [ ] Add `scoped_contains` helper in `check_utils.py` (+ tests).
- [ ] Add audit script `scripts/audit_check_scope.py` — parses every `static.py`/`behavior.py`, flags raw `"X" in generated_code` patterns.
- [ ] Run audit, save report `plans/audit-scope-2026-xx.md`.
- [ ] Category-by-category migration (one PR per category for reviewability):
  - [ ] `isr-concurrency` (13 TCs)
  - [ ] `dma` (13 TCs)
  - [ ] `threading` (8 TCs)
  - [ ] `memory-opt` (16 TCs) — known flaky on Haiku
  - [ ] other categories in decreasing weakness order
- [ ] After each migration PR: run full benchmark replay on stored generations (`results/runs/2026-04-12*/details/`) — flag flipped verdicts, review each.
- [ ] Final: update CLAUDE.md boundaries with "scoped_contains is the default; raw match requires comment justification".

### Phase 4: P1 Negatives Coverage (weeks 2–4, ~12–18h, parallel with P2)

- [ ] Add CI enforcement: `scripts/verify_negatives_coverage.py` — fails CI if any case has `static.py` but no `negatives.py`.
- [ ] Expand `scripts/verify_references_build.py` pattern to `verify_negatives_oracle.py` — run `_run_mutant_checks` against reference for every case, fail if any `must_fail` check misses.
- [ ] Prioritized batch authoring (by weak-category-first):
  - [ ] Batch A: `dma` remaining 11 cases (Haiku 7.7% → high-value mutations)
  - [ ] Batch B: `isr-concurrency` remaining 11 cases
  - [ ] Batch C: `threading` remaining 7 cases
  - [ ] Batch D: `memory-opt` remaining 15 cases
  - [ ] Batch E: all other categories sweep
- [ ] Each TC negative must:
  - mutate reference solution (not random text)
  - cite factor_id from `LLM-EMBEDDED-FAILURE-FACTORS.md`
  - pass `_run_mutant_checks` at authoring time
- [ ] Final: flip CI enforcement to required (previously warning).
- [ ] Commit per batch: `test(negatives): add mutation oracles for <category> (N TCs)`

### Phase 5: Integration + Docs (week 4, ~2h)

- [ ] Update `docs/METHODOLOGY.md` — L4 mutation oracle now universal.
- [ ] Update `README.md` via `sync_docs.py` — show negatives coverage stat.
- [ ] Write `docs/HILOOP-HANDOFF.md` (optional) — canonical description of EmbedEval → Hiloop transpile consumption surface: summary.json schema, negatives.py schema, forbidden_apis.yaml location. Single source of truth so Hiloop repo doesn't need to reverse-engineer.
- [ ] Run full benchmark re-evaluation — publish refreshed `BENCHMARK-COMPARISON` with notes on any P2-induced deltas.

---

## 🧪 Testing Strategy

### Unit Tests

- `tests/test_forbidden_apis.py` — P4 YAML load, byte-equivalence to prior hardcoded list.
- `tests/test_per_check_stats.py` — P3 aggregation correctness.
- `tests/test_scoped_contains.py` — P2 scope helper: comments stripped, string literals stripped, raw mode works.
- `tests/test_negatives_structure.py` — P1 meta-test: every `negatives.py` parses, exports `NEGATIVES` list-of-dict, each dict has required keys.

### Integration Tests

- `tests/test_mutations_vs_reference.py` — iterate all cases, apply each negative's mutation to reference, confirm `must_fail` checks actually fail. **This is the mutation oracle gate.**
- `tests/test_scope_regression.py` (P2) — take 3–5 adversarial fixtures (forbidden API in comment, in string literal, in code), assert verdict matches human expectation.
- `tests/test_summary_schema.py` — P3 `summary.json` has `per_check_stats` and schema validates.

### Manual Testing

1. After each P2 category migration, run:
   ```
   uv run embedeval replay --from results/runs/2026-04-12_claude-code___haiku_n2/details/ --category <cat>
   ```
   (Note: `replay` mode may need a tiny addition — confirm exists or add.)
2. Diff old vs new verdicts. Review every flip.
3. After P3, load `summary.json` in a notebook, verify per-check stats match human spot-checks.

---

## ⚠️ Risks & Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| P2 flips many TC verdicts → benchmark re-baseline chaos | Medium | **Policy 2026-04-19: flip 허용 + 문서화.** Each PR enumerates flips in description and appends to `docs/BENCHMARK-DELTA-*.md`. No veto; reviewer checks rationale plausibility only. |
| P1 mutation authoring errors → false must_fail assertions | Medium | Authoring-time gate: `verify_negatives_oracle.py`. No merge without it passing. |
| P3 summary.json schema change breaks external consumers | Low–Medium | Field is additive + optional. Document in `docs/HILOOP-HANDOFF.md`. Version stamp already exists in summary. |
| P4 import-time YAML load introduces load-order bugs | Low | `@lru_cache`; `importlib.resources` path. Add explicit error if data file missing. |
| Scope creep: someone proposes Hiloop-specific metadata in `CheckDetail` | Medium | **REJECT in review.** This PLAN's contract is "EmbedEval-side changes justified standalone". |
| LLM-assisted negative authoring (instead of hand-written) | Medium | **Forbidden in this PLAN.** Mutations are audit-critical; must be deterministic Python authored by human reviewer. |

---

## ✅ Success Criteria

- [ ] `find cases -type d -name checks | xargs -I{} test -f {}/negatives.py` — all 185 cases present.
- [ ] `uv run python scripts/verify_negatives_oracle.py` — all `must_fail` checks detect their mutations.
- [ ] `uv run python scripts/audit_check_scope.py --strict` — zero unscoped substring checks (or every exception documented inline).
- [ ] `summary.json` contains `per_check_stats` with ≥1 entry per unique check across all cases.
- [ ] `src/embedeval/data/forbidden_apis.yaml` is the sole source of truth for platform API blacklist.
- [ ] `uv run pytest` — all tests pass.
- [ ] `uv run ruff check src/ tests/` — clean.
- [ ] `uv run mypy src/` — clean.
- [ ] Benchmark re-evaluation post-P2: any flipped case documented in commit, no regression in overall methodology integrity.
- [ ] `docs/HILOOP-HANDOFF.md` exists and accurately describes the transpile consumption surface (single source of truth for Hiloop repo).

---

## 📊 Estimated Effort

| Phase | P | Hours | Risk |
|---|---|---|---|
| 0 Foundations | — | 2 | Low |
| 1 Forbidden APIs | P4 | 2 | Low |
| 2 Per-check Metrics | P3 | 3 | Low |
| 3 Scope Discipline | P2 | 6–8 | Medium |
| 4 Negatives Coverage | P1 | 12–18 | Medium |
| 5 Integration + Docs | — | 2 | Low |
| **Total** | | **27–35** | |

- **Complexity:** Medium (bulk mechanical + 1 high-judgment phase P2)
- **Estimated Time:** 27–35 hours over 4 weeks if paced; 1 focused week if full-time.
- **Files Changed:** ~200 (155 new negatives, ~50 static.py edits, 3 src core, 1 data YAML, 6 test files, 3 doc updates)

---

## 🚦 Sequencing (user decision 2026-04-19: Option B — full P1–P4, then Yocto expansion)

### Track 1: This PLAN (Weeks 1–4)
1. **Week 1:** P4 → P3 (both small, both low-risk, both unblock measurement).
2. **Week 2–3:** P1 (highest-value, parallelizable across categories, no risk to existing numbers).
3. **Week 2–3:** P2 (parallel with P1, PER-CATEGORY merges. Flip policy: 허용 + 문서화. No veto.)
4. **Week 4:** Docs + `HILOOP-HANDOFF.md` + final benchmark re-run + `BENCHMARK-DELTA-2026-xx.md`.

### Track 2: Queued after Track 1 (Weeks 5–7) — Yocto Coverage Expansion
- User's primary practice is Yocto/Embedded Linux. Track 1 gives ~15% direct Yocto benefit.
- After Track 1 lands, write and execute `PLAN-yocto-coverage-expansion.md`:
  - yocto TCs: 8 → 25 (DEPENDS/RDEPENDS, PACKAGECONFIG, SRC_URI checksums, inherit order, FILES packaging, kernel fragment patterns, devtool workflows)
  - linux-driver TCs: 8 → 20 (platform driver + DT binding, uapi/ioctl, IIO/V4L2, DMA mapping, dev_pm_ops)
  - Add Yocto layer to `LLM-EMBEDDED-FAILURE-FACTORS.md` (bitbake expansion order, sstate poisoning, multilib, PREFERRED_PROVIDER conflicts)
  - Optional new category: `systemd-unit` or `embedded-linux-runtime` (service ordering, capabilities, udev rules, initramfs)
- Expected outcome: Yocto/Linux coverage jumps from 14% → ~30% of benchmark, giving the user a directly-relevant signal for their daily work.

### Total Timeline
- Track 1 (this PLAN): 4 weeks / 27–35h
- Track 2 (Yocto expansion): 3 weeks / ~20–25h
- **Combined: 7 weeks / ~50–60h**

Track 2 PLAN is not yet authored — draft it after Track 1 reaches Phase 3 or later.
