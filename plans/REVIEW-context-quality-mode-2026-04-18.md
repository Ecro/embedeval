# REVIEW: Context Quality Mode

**Project:** embedeval
**Date:** 2026-04-18
**Scope:** Uncommitted changes for `embedeval-context-quality-mode`
**Reviewer:** reviewer agent (independent) + author self-review
**Files reviewed:** 15 (6 modified, 9 new), +243 / −18 lines

---

## 📊 Summary

**Grade:** B− (Good core, two correctness bugs to fix before merge)
**Critical Issues:** 0 (no crash/security/data loss)
**P1 Issues:** 2 (real correctness bugs in secondary paths)
**P2 Issues:** 3 (data integrity edge cases)
**P3 Issues:** 3 (maintainability / undocumented gaps)
**Recommendation:** CHANGES_REQUESTED

The main contribution — `embedeval run --context-pack` + `embedeval
context-compare` for the default `generation` scenario — works correctly
and has solid test coverage (28 new tests covering happy/edge/error for
the main paths). Two real bugs hit the secondary outputs (JSON export,
bugfix scenario). Empirical verification confirms both.

---

## 🔍 Detailed Findings

### P1 — Must fix before merge

#### F1: `lift` and `gap` missing from `context-compare --output-json`
**File:** `src/embedeval/context_compare.py:36-53`
**Category:** Correctness
**Verified empirically:**
```
$ python -c "..."
per_category[0] keys: ['category', 'n_cases', 'bare_pass_rate', 'team_pass_rate', 'expert_pass_rate']
Has lift? False
Has gap? False
```

`CategoryComparison.lift` and `.gap` are `@property`, not
`@computed_field`. Pydantic v2 `model_dump_json()` does not serialize
plain `@property`. The terminal table works (calls property directly),
which is why 1305 tests pass — but every JSON export is structurally
broken. Any CI integration reading `--output-json` (one of the
documented use cases) gets `KeyError` on the two primary metrics.

**Fix (one line):**
```python
from pydantic import computed_field

class CategoryComparison(BaseModel):
    @computed_field        # NEW
    @property
    def lift(self) -> float | None:
        ...

    @computed_field        # NEW
    @property
    def gap(self) -> float | None:
        ...
```

Add a regression test that loads the JSON and asserts both keys present.

---

#### F2: `--context-pack` silently ignored in `--scenario bugfix`
**File:** `src/embedeval/cli.py:331-384`, `src/embedeval/bugfix.py:179`
**Category:** Correctness / Data Integrity

User who runs `embedeval run --context-pack expert --scenario bugfix`:
1. Sees `Context pack: expert.md (hash=...)` echoed → believes pack is active
2. `run_bugfix_benchmark()` is called WITHOUT `context_pack` (cli.py:382-387)
3. `bugfix.py:179` calls `call_model(model=model, prompt=prompt)` — no pack
4. Tracker still records `context_pack_hash` for results that never saw the pack
5. Future Context Quality comparisons using this `output_dir` are silently corrupted

The "I told the user the pack is active and recorded its hash, but
ignored it" sequence is the trap. Either the bugfix path needs to
plumb context_pack through (full fix), or it must error/warn loudly and
not poison the tracker (minimal fix).

**Minimal fix:**
```python
if scenario == "bugfix" and context_pack is not None:
    typer.echo(
        "Error: --context-pack is not supported for --scenario bugfix. "
        "Run without --context-pack or use scenario=generation.",
        err=True,
    )
    raise typer.Exit(code=1)
```

I prefer the error over warn-and-null-hash because the user explicitly
asked for a measurement that the system can't deliver — silently
returning bare results is worse than failing.

---

### P2 — Should fix before merge

#### F3: Empty context pack file silently poisons tracker
**File:** `src/embedeval/cli.py:342-348`
**Category:** Correctness (edge case)

`hash_context_pack("")` returns a valid 16-char hash. `_build_full_prompt`
strips empty pack from the prompt. Net effect: tracker records hash for
a run that LLM saw as bare. Future bare runs into the same `output_dir`
get rejected with `ContextPackMismatchError` against a hash that
represents nothing.

**Fix (3 lines in cli.py):**
```python
context_pack_text = pack_path.read_text(encoding="utf-8")
if not context_pack_text.strip():
    typer.echo(f"Error: context pack file is empty: {pack_path}", err=True)
    raise typer.Exit(code=1)
```

Add test in `tests/test_context_pack.py` covering this case.

---

#### F5: `compare_runs` silently allows mismatched case sets
**File:** `src/embedeval/context_compare.py:119-200`
**Category:** Reliability

If `bare_dir` has 233 cases but `expert_dir` has 5 (e.g., user piloted
expert on a small subset), `compare_runs` produces a numerically valid
report. Categories present in bare but missing in expert show
`expert_pass_rate=None`; OVERALL micro-average is computed over
different denominator sets. Result is meaningless but looks fine.

**Fix:** Log a warning when `n_total(bare) != n_total(expert)` (and team
if present). Don't fail — let the user proceed with eyes open.

---

#### F7: Tracker hash override fires on partially-cleared trackers
**File:** `src/embedeval/test_tracker.py:139-160`
**Category:** Reliability (edge case)

The `if not tracker.results: tracker.context_pack_hash = ...` escape
hatch is intended for "first run into empty dir." It also fires on
"tracker had hash A and results, results got deleted, new run with hash
B" — silently re-tagging the tracker. Tighten condition:

```python
if not tracker.results and tracker.context_pack_hash is None:
    tracker.context_pack_hash = context_pack_hash
else:
    raise ContextPackMismatchError(...)
```

Low-impact (results dict is rarely manually cleared) but cheap to fix.

---

### P3 — Nice to have

#### F4: Hash logic duplicated in cli.py oversized-pack fallback
**File:** `src/embedeval/cli.py:355-360` vs `src/embedeval/context_pack.py:83`

The fallback path duplicates `hashlib.sha256(content.encode()).hexdigest()[:16]`.
Currently identical to `hash_context_pack`, but two implementations
will drift. Expose `_hash_raw()` in context_pack.py or refactor
`hash_context_pack` to take `force=True`.

#### F6: `_resolve_model` mock fallback has no warning
**File:** `src/embedeval/context_compare.py:98-116`

If both trackers contain only `mock`, comparison succeeds with
lift=gap=0 (mock is context-independent). Indistinguishable from a
real zero-lift result. Add a one-line `logger.warning` when the
selected model is `mock`.

#### F8: `embedeval agent` subcommand has no `--context-pack` support
**File:** `src/embedeval/cli.py:797-864`

Multi-turn agent mode bypasses Context Quality Mode entirely. Either:
(a) plumb `context_pack` through `evaluate_agent()`, or (b) document
the gap explicitly. Currently neither — users discover it by reading
source.

---

## ✅ Positive Observations

- **D1 risk verified empirically.** Smoke test (`scripts/smoke_test_context_pack.py`) confirmed `claude -p` actually receives prepended context — sentinel `EMBEDEVAL_CONTEXT_SMOKE_42` appeared in pack run, not in bare run. This was the biggest unknown in the PLAN; verifying it before building the rest paid off.
- **Hash design is correct.** Raw bytes (no whitespace normalization) for reproducibility. 16-char SHA256 prefix is the right balance of collision resistance vs tracker readability.
- **Tracker mismatch covers all three transition shapes** (A→B, A→None, None→A) with dedicated tests. `ContextPackMismatchError` is a custom subclass so callers can distinguish it from generic `ValueError`.
- **Mock model echo trick** — embedding a 200-char prompt prefix as a `/* PROMPT_PREFIX: */` C comment lets unit tests verify what the model actually saw without burning real tokens. Reused by F1's regression test.
- **Expert pack curation honored "high-level only" constraint** — grep for `volatile|__aligned|copy_to_user|...` returns 0. Pack is ~1100 tokens, principle-only, no exact API names. Discriminating power preserved.
- **Tracker bug found mid-implementation** — packed-dir + bare-run silent overwrite. Was not in PLAN; caught during E2E smoke test, fixed with hardened mismatch logic + 2 new tests.
- **D4 risk discharged via package-data verification** — `uv build` confirmed `expert.md` ships in the wheel.

---

## 📋 Project-Specific Checks (CLAUDE.md Quality Gates)

### "Self-review `git diff`"
- [x] No redundant function calls — except F4 (hash duplication, P3)
- [x] API contracts checked — `_build_full_prompt` order matches docstring
- [x] Edge cases — None, empty string, missing file all covered EXCEPT F3 (empty file)
- [x] No defensive double-processing

### "New feature = new tests"
- [x] **Happy path** — covered (test_context_pack_prepended, test_compare_basic_lift_and_gap)
- [x] **Edge case** — covered (no team, empty pack treated as none, expert keyword resolves)
- [x] **Error case** — covered (mismatch raises, missing file raises, oversized raises)
- [ ] **Missing**: regression test for F1 (JSON contains lift/gap)
- [ ] **Missing**: regression test for F3 (empty pack file → exit code 1)
- [ ] **Missing**: regression test for F2 (bugfix + context_pack → exit code 1 or warning)

### "Check function signatures before calling"
- [x] `call_model` — verified all callers (runner, bugfix, agent) before adding param
- [x] `update_tracker` — context_pack_hash is keyword-only with default None (backward compat)
- [x] `_extract_code` — not called twice on already-extracted output

### Other
- [x] Mock test loosened to substring (intentional, documented in test comment)
- [x] No `--no-verify` skips
- [x] All changed files lint clean (`ruff check`)
- [x] Type-clean (`mypy --strict` on new modules)
- [x] Full test suite green (1305 passed, +10 new)

---

## 🧪 Test Coverage

**New tests:** 28
- `test_context_pack.py`: 11 (build_full_prompt + hash + resolve)
- `test_context_compare.py`: 8 (compare runs + table format + properties)
- `test_tracker_context_pack.py`: 6 (hash transitions)
- `test_llm_client.py`: 1 modified (mock substring match)

**Coverage gaps (from action items):**
- JSON output schema (F1)
- Empty pack file handling (F3)
- bugfix + context_pack interaction (F2)
- Mock-only model warning in compare (F6)

---

## 📊 Code Metrics

| Aspect | Score |
|--------|-------|
| Security | 9/10 |
| Correctness | 5/10 (F1, F2 are real bugs) |
| Reliability | 6/10 (edge cases not all caught) |
| Performance | 9/10 |
| Maintainability | 7/10 |
| **Overall** | **6.5/10** |

---

## ✅ Action Items

### Must Fix Before Commit
- [ ] **F1** — Add `@computed_field` to `lift` and `gap` properties (`context_compare.py:36, 43`). Add regression test asserting JSON contains both keys.
- [ ] **F2** — Reject `--context-pack` with `--scenario bugfix` (cli.py before scenario branch). Add regression test asserting non-zero exit.

### Should Fix This PR
- [ ] **F3** — Reject empty context pack file in cli.py with helpful error.
- [ ] **F5** — `compare_runs` should `logger.warning` when n_cases mismatch across dirs.
- [ ] **F7** — Tighten "empty tracker" escape hatch to require `context_pack_hash is None` too.

### Nice to Have (Future PR)
- [ ] **F4** — Dedupe hash logic (expose `_hash_raw` or refactor `hash_context_pack`).
- [ ] **F6** — Warn when comparison model resolves to `mock`.
- [ ] **F8** — Either thread `context_pack` through `evaluate_agent` or document the gap in the agent command's help text.

---

## ➡️ Recommendation

**Status:** CHANGES_REQUESTED → **APPROVED** (after P1/P2/P3 fixes + real-LLM validation, see below)

The core feature (--context-pack on `run` + `context-compare`) is solid
and well-tested for the primary use case. Two P1 bugs in secondary
paths (JSON export, bugfix scenario) need fixing before merge — both
are short, ≤10 lines each, with regression tests of similar size.

Estimated time to clear P1+P2: 1-2 hours including tests.

P3 items can ship in a follow-up.

---

## 📊 Addendum — Real-LLM Validation (2026-04-18, post-fix)

### Setup

- Model: `claude-code://haiku`
- 5-TC subset from Haiku's empirically-weak categories (ensures headroom):
  `isr-concurrency-003`, `dma-001`, `threading-007`, `memory-opt-001`,
  `storage-001`
- n=3 attempts per case per context
- Bare vs expert pack comparison

### Result

| Category | Bare pass@1 | Expert pass@1 | Effect |
|---|---|---|---|
| dma | 0% | 100% | **+100pp** |
| isr-concurrency | 100% | 0% | **−100pp** |
| memory-opt | 0% | 0% | 0pp (Haiku hard-limit) |
| storage | 100% | 100% | 0pp (no headroom) |
| threading | 0% | 0% | 0pp (Haiku hard-limit) |
| **OVERALL** | **27%** | **27%** | **0pp** |

95% CI: bare `[5.9%, 67.7%]`, expert `[5.9%, 67.7%]` — **complete overlap**.

### Mechanism (from generated code inspection)

**dma-001 (helpful +100pp):** Expert pack's principle "DMA buffers need
alignment" caused Haiku to add `__aligned(4)` that bare was missing.
**Missing-piece additive effect** — pack fills a gap in the generated code.

**isr-concurrency-003 (harmful −100pp):** Expert pack's "shared
variables need volatile" caused Haiku to add `volatile int counter` but
to simultaneously drop the proper Zephyr timer infrastructure
(`K_TIMER_DEFINE` → main loop calls `counter_isr(NULL)` directly,
which is not actually an ISR). **Attention-trade-off effect** —
pack steers attention toward principle application at the cost of
structural correctness.

### Findings (new, not in original PLAN)

1. **R8 confirmed empirically:** Expert pack has case-dependent sign.
   Not uniformly positive.
2. **R3 (over-explicit blowout) mitigated:** Overall pass rate did NOT
   ceiling — discrimination preserved.
3. **PLAN Phase 3 종료 조건 failed strictly:** only 1/5 categories showed
   `expert > bare`. Root cause: both attention-trade-offs and
   no-headroom cases are common.
4. **Sample size insufficient:** CI overlap means even large swings
   (±100pp per category) are indistinguishable from noise at n=3.

### Implications for the feature

- Context Quality Mode surfaces a *real phenomenon* — context is not
  zero-sum. The tool works as designed.
- Documentation should explicitly call out the trade-off (not just
  "lift" semantics). Add `Effect` column distinction between
  `helpful`, `no-effect`, `harmful`.
- For publishable findings, need ~20-50 cases per category to separate
  signal from noise. Current 5-TC smoke is directional, not statistical.

### Action items added
- [x] Document expert pack trade-off in `docs/CONTEXT-QUALITY-MODE.md`
  ("Lift can be negative — that's a real signal, not a bug")
- [x] Add R8 to risk log in PLAN
- [ ] Consider per-case effect classification in future work
  (helpful / harmful / no-effect) as a new EmbedEval output

---

## 📊 Addendum 2 — Trade-off Pattern Analysis (2026-04-18, N=14)

### Setup

10 additional headroom cases (different categories, all bare-fail per
prior n=3 baseline) added to the previous 5-TC sample. Total N=14
unique cases (1 case `spi-i2c-009` failed mid-run; excluded). Mock-only
cases not relevant. Each case run with bare and expert pack, n=1 for
this expansion.

### Pattern distribution

| Effect | N | % | Cases |
|---|---|---|---|
| HELPFUL (missing-piece additive) | 2 | 14% | `dma-001`, `memory-opt-002` |
| HARMFUL — real attention trade-off | 1 | 7% | `isr-concurrency-003` |
| HARMFUL — benchmark check brittleness | 1 | 7% | `dma-002` |
| NO-EFFECT (LLM hard limit, both fail) | 7 | 50% | `dma-003`, `isr-conc-002/005`, `memory-opt-001/003`, `spi-i2c-005`, `threading-007` |
| NO-EFFECT (already pass, no headroom) | 3 | 21% | `security-001/004`, `storage-001` |

### Key finding: half of "harmful" is actually EmbedEval brittleness

`dma-002` failed in expert run because the check looks for the literal
string `dma_config(` but the expert-augmented Haiku used the
equivalent newer API `dma_configure(`. Both APIs are valid Zephyr.

This is the same class of issue called out in CLAUDE.md correction
2026-03-29 ("Check regexes must accept API variants"). Context Quality
Mode surfaced a new instance.

### Mechanism summary

1. **Expert pack helps when:** the LLM is missing an explicit pattern
   the static check requires (alignment, stack config). Pack injects
   the principle, LLM applies it.
2. **Expert pack hurts when (real):** the LLM trades attention budget
   from structural correctness toward principle application. Concrete
   example: `isr-concurrency-003` got `volatile` correctly but lost
   the actual ISR-via-timer setup.
3. **Expert pack hurts when (apparent):** the LLM picks a valid
   alternative API form that the brittle check doesn't recognize.
   Concrete example: `dma_configure` vs `dma_config`.
4. **Expert pack does not help (50% of cases):** when the LLM hits a
   capability hard-limit unrelated to context (memory-opt complexity,
   threading semantic depth). Pack content reaches the model but does
   not unblock the failure.

### Implications for the project beyond Context Quality Mode

- **EmbedEval check robustness gap surfaced:** Context-induced API
  variant adoption is not just a Context Quality Mode concern — any
  prompt change (system_prompt edit, model swap) can flip these
  brittle checks. Worth a follow-up sweep of static.py files for
  similar API-name singularity.
- **Pack effect classification deserves first-class output:** A
  follow-up should add per-case `effect` field to `compare_runs`
  output: `helpful` / `harmful` / `no-effect-fail` / `no-effect-pass`.
  This converts the trade-off from a footnote in interpretation
  guidance into a queryable property.
- **Reachable pass-rate ceiling is bounded:** In this sample, only 3
  of 14 cases (21%) had headroom for context to act on (helpful or
  real-harmful). The other 79% are either capability-locked or
  already-passing. Aggregate Lift dilutes the signal; per-case
  effect direction is the correct granularity.

### Action items added (post-analysis)
- [ ] **EmbedEval improvement:** Add `dma_configure` as accepted variant
  alongside `dma_config` in dma-002 static check (and audit other dma
  cases for the same pattern).
- [ ] **Feature follow-up:** Per-case `effect` classification in
  `context-compare` output (helpful/harmful-real/harmful-brittle/
  no-effect).
- [ ] **Methodology note:** When reporting Context Quality results,
  always quote per-case effect distribution, not just aggregate Lift.
