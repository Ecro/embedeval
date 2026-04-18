# PLAN: `embedeval context-diagnose` — Factor-Level Context Coverage Feedback

**Project:** embedeval
**Task:** New CLI command that tells a team **which FAILURE-FACTORS categories (and by extension, which High-strength factor IDs) their CLAUDE.md / context pack fails to cover**, based on their own benchmark run vs. the expert reference.
**Priority:** High (sole remaining EmbedEval product play before maintenance mode)
**Created:** 2026-04-19

---

## 🎯 Executive Summary

> **TL;DR:** Map every failed check in a team tracker to its FAILURE-FACTORS category and surface categories where the team trails the expert pack, along with the High-strength factor IDs they should encode into CLAUDE.md.

### What We're Doing

New subcommand `embedeval context-diagnose --team X --expert Y` that:

1. Parses `docs/LLM-EMBEDDED-FAILURE-FACTORS.md` to build a `check_name → category_letter` map (the `**EmbedEval checks mapped:**` lines already encode this — no human curation needed).
2. Loads the team + expert trackers, tallies each tracker's **failed checks per category**.
3. Flags categories where team failure rate exceeds expert failure rate by ≥10pp (configurable).
4. For each flagged category, lists the High-strength factor IDs from `expert-coverage.md` so the user knows which principles to add.

### Why It Matters

After the context-quality mode session, the whole stack now tells a team **that** their context is weak (Lift/Gap, per-case effect, harmful breakdown). But it does not tell them **where** — which specific embedded principles to encode. Factor-level diagnosis closes that loop. It is also the one diagnostic no competing tool can produce: semgrep doesn't understand context, hiloop catches code bugs not context gaps.

This feature locks in EmbedEval's thought-leadership angle ("measure & diagnose team context") so the project can go into maintenance while hiloop takes over commercial work.

### Key Decisions

- **D1 — Category-level diagnosis only, factor-level deferred to v2.** Reason: the `**EmbedEval checks mapped:**` lines in FAILURE-FACTORS are per-category. Per-factor mapping would need human curation of ~100 check names. Ship value with zero curation cost; factor-level only if v1 gets real usage.
- **D2 — Compare team → expert, NOT bare → team.** Reason: the right question is "does team's CLAUDE.md cover the principles expert.md covers?" Bare is the baseline; the measurement we want is the *residual gap to the ceiling*.
- **D3 — New command, not a flag on `context-compare`.** Reason: different intent (diagnostic, not comparison) and different output shape (per-category failed_check aggregation, not pass-rate delta). Separate UX surface is clearer for the sales pitch ("run diagnose → get action items"), even though both share tracker loading.
- **D4 — Extract the factor parser into a reusable module.** Reason: `scripts/build_expert_pack.py` already parses factor tables; extending it with `**EmbedEval checks mapped:**` parsing while keeping script + new diagnose module in sync argues for moving `parse_factors` to `src/embedeval/failure_factors.py`. Both callers import from there.
- **D5 — Unmapped checks log a warning, don't fail.** Reason: new checks may be added to case static.py before FAILURE-FACTORS gets updated. Graceful degradation beats hard failure; drift shows up in stderr.

### Estimated Impact

- **Complexity:** Medium (new module + CLI + parser refactor; no schema changes)
- **Risk Level:** Low (additive, no existing behavior changes)
- **Files Changed:** ~7 files
- **Estimated Time:** 10-12h (1.5-2 days)

---

## ⚠️ REVIEW CHECKLIST — Verify before `/execute`

### Critical Decisions to Verify

- [ ] **D1 scope call** — category-level enough for v1, or do we need factor-level from day one? (My position: category ships in 1.5 days, factor needs ~3 days of curation and hasn't been validated by a user.)
- [ ] **D2 comparison direction** — diagnose against expert (ceiling) vs. against bare (baseline). Different questions, different outputs.
- [ ] **D3 separate command vs. flag** — `context-diagnose` as a new command vs. `context-compare --diagnose-factors`. Duplication risk is low because the diagnosis output shape is different enough.
- [ ] **Threshold for "needs coverage"** — default 10pp gap feels right but is unvalidated. Configurable via `--gap-threshold`.

### Code Impact to Review

- [ ] **New module `src/embedeval/failure_factors.py`** — check that moving `parse_factors` from `scripts/build_expert_pack.py` keeps the drift CI passing.
- [ ] **New module `src/embedeval/context_diagnose.py`** — factor rollup, category aggregation.
- [ ] **`src/embedeval/cli.py`** — add `context-diagnose` subcommand following the same pattern as `context-compare` and `harmful-inspect`.
- [ ] **No schema changes** — `CaseResult.failed_checks` and `TrackerData` stay as-is.

### Testing Coverage

- [ ] Mapping parser: every `**EmbedEval checks mapped:**` line yields the right category letter for every listed check.
- [ ] Unknown check in tracker logs warning but doesn't crash diagnosis.
- [ ] Threshold boundary: gap exactly at threshold → flagged or not (spec the exact semantics).
- [ ] E2E: uart mock run → diagnose → JSON schema check.
- [ ] Regression: `build_expert_pack.py` still works after `parse_factors` move.

### Business Logic

- [ ] Does category-level output actually give users enough to act? Example output: "Category D: 8 failed checks (expert: 1). High-strength factors in D: D1, D2, D4, D5. Start with D5." Is this the right unit of advice?
- [ ] Does the command work without a bare tracker? (Decision: yes — diagnose is team-vs-expert, bare is optional context.)
- [ ] Output when team == expert (well-covered): what does success look like? ("No gaps found. Your context matches the expert reference ceiling.")

---

## 📚 Prior Work

### Related Documents

- [[plans/PLAN-context-quality-mode]] — parent feature. `context-diagnose` is the factor-level extension of what `context-compare` started.
- [[plans/PLAN-per-case-effect-classification]] — per-case direction of effect. `context-diagnose` is the category aggregate of the same signal.
- [`docs/LLM-EMBEDDED-FAILURE-FACTORS.md`](../docs/LLM-EMBEDDED-FAILURE-FACTORS.md) — the source of truth for factor taxonomy and `check → category` mapping.
- [`src/embedeval/context_packs/expert-coverage.md`](../src/embedeval/context_packs/expert-coverage.md) — machine-generated factor-by-category reference that `context-diagnose` points users back to.
- [`src/embedeval/harmful_inspect.py`](../src/embedeval/harmful_inspect.py) — precedent for "new CLI command that reads trackers and produces diagnostic output". Same architectural shape.
- [`scripts/build_expert_pack.py`](../scripts/build_expert_pack.py) — already parses factor tables; will be refactored to share a common factor-parsing module.

### What Worked Before

- `harmful-inspect` shows the pattern works: read trackers, classify, emit JSON + table, pure offline analysis. No new storage, no schema migrations, ~300 lines of code.
- `build_expert_pack.py` shows `**EmbedEval checks mapped:**` is reliably parseable — the drift CI has been green.

### Known Blockers / Pitfalls

- `CaseResult.failed_checks` is populated from `CheckDetail.check_name`. These names are the same tokens used in FAILURE-FACTORS' mapping lines (`volatile_error_flag`, `dma_config_called`, etc.). Verified empirically in `cases/threading-001/checks/static.py`.
- Some checks may appear in multiple categories' mapping lines (shared-use checks). Spec says: a check belongs to the **first category** it appears in (by alphabetical letter), and we emit a test that asserts no duplicates exist unless intentional.

### Decisions to Reuse

- Pydantic v2 frozen models with `@computed_field` for serialized derived values (CategoryComparison pattern).
- CLI command structure mirrors `context-compare` and `harmful-inspect`: `--bare` / `--team` / `--expert` with `--output-json`.
- `_resolve_model` helper pattern from `harmful_inspect.py` — shared across commands that load multiple trackers.

---

## 📋 Problem Analysis

### What

After running EmbedEval with their team's CLAUDE.md, the user sees Lift/Gap numbers but has no actionable mapping to "which principles is my CLAUDE.md missing?". The FAILURE-FACTORS doc spells out 42 factors across 6 categories and maps checks to categories, but nobody wires this into the run output.

### Why

Three strategic reasons:

1. **Closes the context-quality loop**: measurement without prescription stops at "you're below expert". Diagnosis converts that into "here are the factor IDs to add to CLAUDE.md".
2. **EmbedEval's unique value**: hiloop catches code bugs, semgrep catches patterns, neither can tell a team where their implicit-knowledge encoding is weak. Factor-level diagnosis can, because the measurement substrate is the team's own LLM output.
3. **Enables hiloop sales motion**: "EmbedEval CQM + diagnose first → only the residual Gap is a hiloop problem". A concrete funnel from free research tool to paid verification product.

### Success Criteria

- [ ] `embedeval context-diagnose --team X --expert Y` emits a table of categories ranked by gap, with High-strength factor IDs listed per flagged category.
- [ ] `--output-json` writes the full breakdown (every category, every failed check, every factor ID).
- [ ] Unmapped checks produce a warning with the unmapped names but don't crash.
- [ ] CI drift gate still passes (refactored `parse_factors` stays in sync with expert-coverage.md).
- [ ] `--gap-threshold <pp>` configurable (default: 10.0).
- [ ] ≥10 new unit tests + 1 e2e test.
- [ ] `mypy --strict` and `ruff` clean on all changed files.

---

## 🔍 Code Review

### Current State

- `scripts/build_expert_pack.py` has `parse_factors(markdown)` returning `list[Category]`. It parses the `| A1 | ... |` rows but **does not parse** the `**EmbedEval checks mapped:**` trailer lines — we need to add that.
- `src/embedeval/harmful_inspect.py` is a clean template for a new CLI-oriented analysis command. Reuse its structure (enum + pydantic model + classifier + formatter + CLI plumbing).
- `src/embedeval/test_tracker.py::CaseResult.failed_checks` is already populated with check names that match FAILURE-FACTORS vocabulary. No migration needed.

### Affected Components

| File | Change |
|------|--------|
| `src/embedeval/failure_factors.py` | **NEW** — extracted `Factor`, `Category`, `parse_factors`, plus new `parse_check_category_map` |
| `src/embedeval/context_diagnose.py` | **NEW** — `CategoryDiagnosis`, `CoverageDiagnosis`, `diagnose_coverage`, `format_diagnosis` |
| `src/embedeval/cli.py` | New `context-diagnose` subcommand |
| `scripts/build_expert_pack.py` | Import `Factor`, `Category`, `parse_factors` from `failure_factors` module — no duplicate parsing logic |
| `tests/test_failure_factors.py` | **NEW** — parser tests (categories, factors, check-category map) |
| `tests/test_context_diagnose.py` | **NEW** — diagnose module unit tests |
| `tests/test_context_quality_mode_e2e.py` | Extend with `context-diagnose` e2e |
| `docs/CONTEXT-QUALITY-MODE.md` | New section after "Per-case effect classification" |

### Dependencies

- No new third-party libs. Pure stdlib `re` for parsing; Pydantic v2 for schema; Typer for CLI (already in deps).

---

## 🏗️ Technical Design

### Data Flow

```
docs/LLM-EMBEDDED-FAILURE-FACTORS.md
           │
           ▼
failure_factors.parse_check_category_map()  →  dict[str, str]  (check → category letter)
                                                     │
results/team/test_tracker.json ─┐                    │
                                ├─► context_diagnose.diagnose_coverage(trackers, map)
results/expert/test_tracker.json ┘                   │
                                                     ▼
                                              CoverageDiagnosis
                                                     │
                                    ┌────────────────┼───────────────┐
                                    ▼                ▼               ▼
                               stdout table     --output-json    warnings (stderr)
```

### Schema

```python
class CategoryDiagnosis(BaseModel):
    category: str                    # "D"
    category_title: str              # "Memory Model & Concurrency"
    team_failed_checks: list[str]    # sorted, unique
    expert_failed_checks: list[str]
    team_failure_rate: float         # team_failed / total_checks_in_category
    expert_failure_rate: float
    gap: float                       # team_failure_rate - expert_failure_rate
    needs_coverage: bool             # gap > threshold
    high_strength_factors: list[str] # ["D1", "D2", "D4", "D5"] for flagged categories
    factor_names: dict[str, str]     # {"D1": "volatile misuse", ...}

class CoverageDiagnosis(BaseModel):
    model: str
    gap_threshold: float
    per_category: list[CategoryDiagnosis]  # sorted by gap desc
    unmapped_checks: list[str]             # checks in tracker with no factor mapping
```

### Parser Extension

`failure_factors.parse_check_category_map(markdown)` finds every line matching:

```
**EmbedEval checks mapped:** `check_a`, `check_b`, `check_c`, ...
```

inside each `## X. Title` section, and emits `{check_a: X, check_b: X, ...}`. The parser state machine already in `parse_factors` tracks the current category letter; the new parser reuses that.

### Output Sample

```
Context Coverage Diagnosis (model: claude-code://sonnet)

  Gap threshold: 10pp  (categories above this need CLAUDE.md improvement)

  Category                                Team  Expert   Gap   High factors to cover
  -------------------------------------------------------------------------------
  D. Memory Model & Concurrency            53%     7%  +46pp   D1, D2, D4, D5
  E. Error Handling & Safety Patterns      38%    12%  +26pp   E1, E2, E3, E4, E7
  B. Temporal & Real-Time Constraints      20%    10%  +10pp   B1, B3, B4
  -------------------------------------------------------------------------------
  A. Hardware Awareness Gap                18%    15%   +3pp   (within threshold)
  C. Memory & Resource Constraints         12%    10%   +2pp   (within threshold)
  F. Toolchain, SDK & Platform Knowledge    8%     7%   +1pp   (within threshold)

  To improve coverage:
    D. Memory Model & Concurrency → add principles for factors D1, D2, D4, D5
       See docs/LLM-EMBEDDED-FAILURE-FACTORS.md#d-memory-model--concurrency
    E. Error Handling & Safety Patterns → add principles for factors E1, E2, E3, E4, E7
       See docs/LLM-EMBEDDED-FAILURE-FACTORS.md#e-error-handling--safety-patterns

  Unmapped checks (warning): 3
    new_check_001, new_check_002, new_check_003
    These check names aren't mapped in FAILURE-FACTORS.md. Update it, or
    the checks don't affect any category's diagnosis.
```

### Why NOT factor-level in v1

The `**EmbedEval checks mapped:**` lines group checks **by category**, not by factor. Going factor-level means:

1. Manually annotating ~100 check names with factor IDs (`volatile_error_flag` → D1, `memory_barrier_present` → D2, etc.).
2. Shipping a `check_factor_map.yaml` as a new hand-curated artifact.
3. Accepting the curation drift risk (a new check added to static.py has no factor ID until someone updates the map).

For v1, category-level already gives users the actionable pointer ("add principles for D category, here are the 4 factors"). If users report that's too coarse, factor-level in v2 takes 1 more day.

---

## 📝 Implementation Plan

### Phase 1 — Extract `failure_factors` module (2-3h)

- [ ] Create `src/embedeval/failure_factors.py`.
- [ ] Move `Factor`, `Category`, `_CATEGORY_RE`, `_ROW_RE`, `parse_factors` from `scripts/build_expert_pack.py` to the new module.
- [ ] Add new `parse_check_category_map(markdown) -> dict[str, str]` that iterates sections and captures `**EmbedEval checks mapped:**` lines.
- [ ] Update `scripts/build_expert_pack.py` to import from the new module.
- [ ] Verify `uv run python scripts/build_expert_pack.py --check` still passes.

### Phase 2 — `context_diagnose` module (3-4h)

- [ ] Create `src/embedeval/context_diagnose.py` with `CategoryDiagnosis`, `CoverageDiagnosis`, `diagnose_coverage`, `format_diagnosis`.
- [ ] Compute `team_failed_checks` / `expert_failed_checks` by iterating `tracker.results[model][case].failed_checks` and de-duplicating within each tracker.
- [ ] Failure rate denominator: total checks mapped to the category (sum over all mapped check names in that tracker's model, whether pass or fail). If a check name never appears in any case result, it's not in the denominator.
- [ ] Gap = team_rate − expert_rate (negative gap = team is better → no coverage problem, keep in output but `needs_coverage=False`).
- [ ] Collect unmapped checks (checks in tracker that aren't in the check → category map) into `CoverageDiagnosis.unmapped_checks` and emit a single `logger.warning` at the end.
- [ ] `high_strength_factors` is sourced from `parse_factors` output filtered to `Factor.strength == "High"` within the category letter.

### Phase 3 — CLI (1-2h)

- [ ] Add `context-diagnose` command to `cli.py` with `--team` (required), `--expert` (required), `--bare` (optional, reserved), `--model`, `--gap-threshold` (default 10.0), `--output-json`.
- [ ] Error out when `--team` and `--expert` share the same `context_pack_hash` (same warning pattern as `context-compare`).

### Phase 4 — Tests (2h)

**`tests/test_failure_factors.py`** (new):
- [ ] `test_parse_factors_extracts_all_six_categories` — 42 factors, 6 categories.
- [ ] `test_parse_check_category_map_covers_known_checks` — assert `volatile_error_flag → D`, `dma_config_called → A`, etc.
- [ ] `test_parse_check_category_map_handles_multi_line_trailer` — a category whose mapping line wraps across multiple lines (unlikely per current format but regression-proofed).
- [ ] `test_no_duplicate_check_mapping_across_categories` — fail if a check appears in 2+ categories' mapping lines.

**`tests/test_context_diagnose.py`** (new):
- [ ] `test_diagnose_flags_category_above_threshold` — synthetic tracker with 5 D-category checks all failing in team, 0 in expert → D flagged, gap 100%.
- [ ] `test_diagnose_does_not_flag_category_below_threshold` — 5% gap < 10pp default → `needs_coverage=False`.
- [ ] `test_diagnose_negative_gap_is_not_flagged` — team better than expert → not flagged.
- [ ] `test_diagnose_returns_high_strength_factors_per_flagged_category` — D flagged → `high_strength_factors` includes D1, D2, D4, D5 (from FAILURE-FACTORS).
- [ ] `test_diagnose_unmapped_check_logs_warning_not_crash` — check `nonexistent_thing` in tracker → appears in `unmapped_checks`, diagnosis still succeeds.
- [ ] `test_diagnose_json_export_has_full_schema` — round-trip via `model_dump_json`, assert every field present.
- [ ] `test_diagnose_sorts_by_gap_descending` — largest gap first.

**`tests/test_context_quality_mode_e2e.py`** (extend):
- [ ] `test_context_diagnose_cli_produces_json_with_full_schema` — uart × mock × bare/team/expert → `embedeval context-diagnose` CLI → JSON schema check.

### Phase 5 — Docs (1h)

- [ ] Add "Diagnosing context coverage gaps" section to `docs/CONTEXT-QUALITY-MODE.md`, after "Per-case effect classification" and before "Inspecting harmful cases".
- [ ] Example output + workflow ("run context-compare → see Gap → run context-diagnose → see factor IDs → add to CLAUDE.md → re-run").
- [ ] Update `README.md` if there's a CLI command list (there isn't — skip).

---

## 🧪 Testing Strategy

### Unit Tests

Covered per phase above. Targets:

- **Parser:** every category produces the right check list; no duplicates; all 42 factors parsed.
- **Aggregation:** correct gap calc, correct threshold behavior, correct sorting.
- **Serialization:** `CaseEffect`-style string enum serialization; `model_dump_json` round-trip.
- **Error path:** unmapped check doesn't crash; empty tracker errors cleanly.

### Integration / E2E

- Extend existing `test_context_quality_mode_e2e.py` with one new test that runs the full `embedeval context-diagnose` CLI path with mock model + uart category. Validates schema, doesn't validate content (mock is context-independent).

### Manual Testing

1. `embedeval run --model mock --category isr-concurrency --output-dir runs/team` (no pack — simulates weak team).
2. `embedeval run --model mock --category isr-concurrency --context-pack expert --output-dir runs/expert`.
3. `embedeval context-diagnose --team runs/team --expert runs/expert` — confirm table rendering.

---

## ⚠️ Risks & Mitigation

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|------------|--------|------------|
| R1 | FAILURE-FACTORS format drift breaks the parser | Medium | High | CI drift check already enforces this (`build_expert_pack.py --check`); `test_parse_check_category_map_covers_known_checks` adds a content-level regression |
| R2 | Some checks in cases/ aren't in any FAILURE-FACTORS mapping line | High | Low | `unmapped_checks` warning surfaces the gap; doesn't block diagnosis; follow-up task updates FAILURE-FACTORS |
| R3 | Category-level too coarse, users want factor-level | Medium | Medium | Ship v1 and listen for signal; factor-level v2 is ~1 day of work on top of v1 |
| R4 | Moving `parse_factors` out of `scripts/build_expert_pack.py` breaks the drift CI | Low | Medium | Phase 1 keeps the script's public behavior identical; drift test re-runs as part of the move |
| R5 | Team vs. expert comparison misleading when trackers cover different case sets | Medium | Medium | Reuse the case-count mismatch warning from `context_compare.compare_runs` — emit at diagnosis time too |
| R6 | Duplicate check name appears in multiple categories' "checks mapped" lines | Low | Low | Unit test enforces no duplicates; document policy (first-alphabetical wins if ever needed) |

---

## ✅ Success Criteria (Recap)

- [ ] `embedeval context-diagnose --team X --expert Y` prints a ranked table and exits 0.
- [ ] `--output-json` round-trips a full `CoverageDiagnosis` payload.
- [ ] `--gap-threshold <float>` tunable; default 10.0.
- [ ] Unmapped checks warn, don't crash.
- [ ] `parse_factors` extraction to new module leaves `build_expert_pack.py --check` green.
- [ ] ≥10 new unit tests + 1 e2e test all pass.
- [ ] `uv run mypy src/` and `uv run ruff check src/` clean.
- [ ] `docs/CONTEXT-QUALITY-MODE.md` has a "Diagnosing context coverage gaps" section.
- [ ] Full test suite passes (1364 + 10 ≈ 1374).

---

## 📊 Estimated Effort

| Phase | Scope | Time |
|-------|-------|------|
| Phase 1 | `failure_factors` module extract + check-category parser | 2-3h |
| Phase 2 | `context_diagnose` module (aggregation, warnings, schema) | 3-4h |
| Phase 3 | CLI wiring | 1-2h |
| Phase 4 | Tests (unit + e2e) | 2h |
| Phase 5 | Docs | 1h |
| **Total** | | **10-12h** (1.5-2 days) |

---

## 🚫 Out of Scope (NON-GOALS)

- **Factor-level mapping.** Requires human curation of ~100 check names. Revisit only if v1 sees real usage and users ask for more specificity.
- **Principle text auto-suggestion from expert.md.** Expert.md sections don't have machine-readable factor-ID tags. v2 could add a `factor_ids:` YAML frontmatter to each expert.md section; not now.
- **Hiloop rule targeting.** JSON output is enough for a sister tool to consume; active integration (emit hiloop-compatible rule IDs) is hiloop's side to pick up when it wants the flywheel closed.
- **CI regression gate for Lift drop.** The CI recipe in `docs/CONTEXT-QUALITY-MODE.md` already points at context-compare's JSON; a gate on diagnose output is a separate follow-up.
- **Per-model category prior** (e.g., "Haiku is known to be weak in D, correct for that"). This is measurement normalization; out of scope.

---

## 🔄 Follow-up Work (After This PLAN)

1. **Factor-level diagnosis (v2)** — requires `src/embedeval/context_packs/check_factor_map.yaml` (hand-curated). About 1 day if users ask.
2. **`--suggest-principles`** — emit a ready-to-paste CLAUDE.md snippet per flagged category, sourced from the relevant `expert.md` principle paragraph. Requires section-level factor_id tagging in expert.md.
3. **Hiloop integration memo** — write down the handshake so hiloop can consume `context-diagnose --output-json` to scope which rule packs to recommend for a given team's weak categories.
4. **EmbedEval goes into maintenance mode** — with this feature shipped, the public surface is stable. Only additions after this: new TCs and new check definitions as hiloop telemetry reveals gaps.

---

## 📖 References

- [`plans/PLAN-context-quality-mode.md`](./PLAN-context-quality-mode.md) — parent measurement feature
- [`plans/PLAN-per-case-effect-classification.md`](./PLAN-per-case-effect-classification.md) — sibling diagnostic
- [`docs/LLM-EMBEDDED-FAILURE-FACTORS.md`](../docs/LLM-EMBEDDED-FAILURE-FACTORS.md) — factor + check taxonomy
- [`docs/CONTEXT-QUALITY-MODE.md`](../docs/CONTEXT-QUALITY-MODE.md) — user-facing docs the new section will join
- [`scripts/build_expert_pack.py`](../scripts/build_expert_pack.py) — will be refactored to share `failure_factors` module

---

**Status:** Draft v1 — 2026-04-19

**Next:** Review the `⚠️ REVIEW CHECKLIST` above. Decide on D1/D2/D3 and threshold default. Then `/execute context-diagnose` runs Phase 1–5.
