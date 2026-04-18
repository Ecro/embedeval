# Code Review: hiloop-transpile-readiness Phase 0-3
**Commits:** `21e9f09 feat(hiloop-ready)` + `d057bff feat(negatives)`
**Date:** 2026-04-19
**Reviewer:** Sonnet 4.6 (automated, three-area consensus pass)

---

## Grade: B+

Strong foundations — all 42 tests pass, mypy clean, ruff clean, wheel packages correctly. The load-bearing pieces (oracle gate contract, sync state transitions, per-check stats) are logically sound. Two correctness issues found: one real bug in the sync regression path, one behavioral inconsistency in the oracle counter. Everything else is warnings or doc gaps.

---

## Summary

| Metric | Count |
|--------|-------|
| Critical (must-fix) | 1 |
| Warnings (should-fix) | 4 |
| Suggestions (nice-to-have) | 4 |
| Grade | B+ |

---

## Critical Issues

### C1 — `sync_negatives_progress`: `in-progress` status missing from auto-promote test, `skipped` silently ignores negatives.py

**File:** `/home/noel/embedeval/scripts/sync_negatives_progress.py:127`

The auto-promote condition is correct — `old_status in ("pending", "in-progress")` — but neither path is tested. More importantly, a TC with `status="skipped"` that gains a `negatives.py` file falls through all three state-transition branches and lands in `stats.unchanged` with `status` still `"skipped"`. This creates a silent inconsistency: the file exists on disk, the oracle would pass, but `/negatives` will never visit it again because `pending` is the only resumable state.

**Reasoning:**
- OBSERVE: Lines 127, 135, 143 are the three state-transition branches. None matches `old_status == "skipped"`.
- TRACE: A skipped TC with `has_negatives=True` takes no branch; falls through to `stats.unchanged += 1` at line 150.
- INFER: The oracle script would PASS this TC, but the progress file still shows `skipped`. The `/negatives --status` output will report it as skipped, not done. `find cases -name negatives.py | wc -l` will exceed the done-count.
- CONCLUDE: Completion criteria (`find cases -name negatives.py == find cases -name static.py`) will appear unmet even when all files exist.

Whether "skipped + has_negatives" should auto-promote to `done` or log a warning is a judgment call. But silently staying `unchanged` is wrong in both cases.

**Fix — Option A (auto-promote skipped if negatives.py appears):**
```python
# Line 127: extend the auto-promote condition
if flags["has_negatives"] and old_status in ("pending", "in-progress", "skipped"):
    entry["status"] = "done"
    entry["completed_at"] = entry.get("completed_at") or str(date.today())
    note = entry.get("notes") or ""
    entry["notes"] = (
        note + " | auto-promoted: negatives.py authored outside command"
    ).strip(" |")
    stats.auto_promoted.append(case_id)
```

**Fix — Option B (log as a separate warning stat instead):** Add a `skipped_has_negatives` list to `SyncStats` and print a warning. Does not change status, but surfaces the inconsistency.

Option A is simpler and aligns with the completion-criteria contract.

---

## Warnings

### W1 — Oracle counter `negatives_checked` increments on failed entries

**File:** `/home/noel/embedeval/scripts/verify_negatives_oracle.py:162`

`result.negatives_checked += 1` runs at the bottom of the `for neg in negatives` loop unconditionally, even when `result.status` was already set to `"fail"` for that negative. This means a case with 3 negatives where 2 missed will report `negatives_checked=3` — which is technically accurate ("we checked 3") but the PASS print at line 213 uses the same field:

```python
print(f"PASS {r.case_id} ({r.negatives_checked} negatives)")
```

For PASS cases this is fine. For FAIL cases the counter is not printed, so no user confusion — but if the JSON report is consumed by downstream tooling expecting `negatives_checked` to mean "negatives that passed oracle", it will be wrong.

**Recommendation:** Rename to `negatives_attempted` in `OracleResult` for clarity, or only increment when no `must_fail` check missed. The latter matches the meaning implied by the PASS print message.

```python
# Current (bottom of for loop):
result.negatives_checked += 1

# Safer: only count if no missed entries were added for this negative
missed_before = len(result.missed)
# ... must_fail check loop ...
if len(result.missed) == missed_before:  # nothing new missed
    result.negatives_checked += 1
```

---

### W2 — `check_no_cross_platform_apis` does not strip string literals for raw-substring APIs

**File:** `/home/noel/embedeval/src/embedeval/check_utils.py:175`

This was pre-existing, but the commit touched this function (changed `CROSS_PLATFORM_FORBIDDEN` to `get_cross_platform_forbidden()`), making it in-scope. The function calls `strip_comments(code)` but not `strip_string_literals`. APIs like `delay(`, `open(`, `close(`, `ioctl(`, `mmap(` are matched as raw substrings — they will false-positive if the pattern appears inside a string literal, e.g.:

```c
printk("use delay(100) for timing");  // trips Arduino check
printk("see open() for examples");     // trips Linux_Userspace check
```

`scoped_contains` was added in the same commit to solve exactly this class of bug. The inconsistency is that the new helper exists but the cross-platform checker doesn't use it.

**Fix:**
```python
def check_no_cross_platform_apis(code: str, skip_platforms: list[str] | None = None) -> list[tuple[str, str]]:
    stripped = strip_string_literals(strip_comments(code))  # was: strip_comments(code)
    ...
```

`has_api_call` (word-boundary) is safe either way; only the raw-substring branch (`api.endswith("(")`) needs the fix.

---

### W3 — `negatives.md` schema omits `orphaned` as a valid status value

**File:** `/home/noel/embedeval/.claude/commands/negatives.md:51`

The schema at line 51 documents `"pending | in-progress | done | skipped"` but the sync script also writes `orphaned`. The sync table at line 95 and the example totals at line 106 reference `orphaned` correctly, but an LLM running the command and reading only the schema line would never know `orphaned` is possible and might mishandle it.

**Fix:** Update line 51:
```
"status": "pending | in-progress | done | skipped | orphaned",
```

---

### W4 — `started_at` field is in the schema but never populated by any code

**File:** `/home/noel/embedeval/.claude/commands/negatives.md:52`

The progress schema shows `"started_at": "YYYY-MM-DD HH:MM"` but `sync_negatives_progress.py` always initializes it to `None`, and the command spec has no step that sets it. Every entry in `negatives-progress.json` will have `started_at: null` permanently. The field is vestigial unless the command explicitly sets it when a TC transitions to `in-progress`.

**Fix (minimal):** Either remove `started_at` from the schema docs and model (it's dead weight), or add a line to Step 4 of the command spec:

> When working a TC, update its progress entry: `"status": "in-progress"`, `"started_at": "<today YYYY-MM-DD>"`.

---

## Suggestions

### S1 — Add tests for `in-progress` auto-promote and `skipped+negatives` edge cases

**File:** `/home/noel/embedeval/tests/test_sync_negatives_progress.py`

The two paths that are code-correct but untested:
1. `in-progress` TC gains `negatives.py` → should auto-promote to `done` (same as `pending`).
2. `skipped` TC gains `negatives.py` → currently stays `skipped`; after fixing C1, should promote.

Both are ~10-line additions modeled after `test_pending_tc_auto_promoted_when_negatives_added`.

---

### S2 — `verify_negatives_oracle.py`: separate "check not found" from "check passed" in missed report

**File:** `/home/noel/embedeval/scripts/verify_negatives_oracle.py:140-160`

Currently both failure modes emit to `result.missed`. Downstream JSON consumers (e.g., CI output parsing) can't distinguish "the check name typo in must_fail" from "the mutation doesn't trip the check". The former is an authoring error; the latter is an oracle weakness. Adding `"failure_mode": "check_not_found" | "check_passed"` to the missed entry dict would help.

---

### S3 — Oracle script: apply mutation to the first reference file only, document multi-file behavior

**File:** `/home/noel/embedeval/scripts/verify_negatives_oracle.py:53-61`

`_read_reference` returns `matches[0]` (first alphabetically) when multiple files exist under `reference/`. Cases with two `.c` files (e.g., `main.c` + `helper.c`) will silently ignore `helper.c`. If a check that references `helper.c` content is in `must_fail`, the mutation on `main.c` won't cause it to fail — the oracle will erroneously report "missed". A comment in the function stating this limitation would help future authors.

---

### S4 — `scoped_contains` docstring: note wide-string and raw-string non-support

**File:** `/home/noel/embedeval/src/embedeval/check_utils.py:39`

The docstring is clear about its scope but doesn't mention that `L"wide string"` and GNU C `__attribute__` strings are not handled (both are rare in Zephyr firmware). A one-line note prevents future confusion: `# Note: L"..." wide strings and __asm__ strings are treated as code, not literals.`

---

## Positive Observations

1. **Oracle-evaluator semantic split is intentional and correct.** `verify_negatives_oracle.py` applies mutations to `reference/` (authoring gate), while `evaluator.py` L4 applies to LLM-generated code (runtime check). These serve different purposes and the distinction is well-understood.

2. **Mutation error handling is correct in both oracle and evaluator.** A mutation lambda that raises is treated as a FAIL (oracle) / skipped-but-pass (evaluator). The oracle fails loudly; the evaluator is lenient to avoid penalizing LLM for a broken TC. This is the right asymmetry.

3. **"mutation did not change reference" is a gated FAIL in oracle, graceful skip in evaluator.** The oracle rejects no-op mutations at authoring time, preventing permanently silent negatives. The evaluator's leniency (treating no-change as soft-pass) is appropriate for runtime.

4. **`PerCheckStat` L4 exclusion is documented and correct.** Mutation checks measure benchmark quality, not LLM capability. Excluding `check_type == "mutation"` is the right semantic boundary. No other synthetic check types exist in the current codebase, so the exclusion is complete.

5. **YAML packaging verified end-to-end.** Both wheel and sdist contain `embedeval/data/forbidden_apis.yaml`. The `__init__.py` in `data/` is the load-bearing mechanism; `source-include` in `pyproject.toml` provides belt-and-suspenders for future sdist scenarios.

6. **`_load_forbidden_apis` lru_cache is tested for identity, not just equality.** `test_loader_is_cached` uses `assert a is b` — the right check for cache behavior.

7. **Notes appending with `or ""` pattern handles `None` correctly.** All five note-appending sites in `sync_negatives_progress.py` use `(entry.get("notes") or "") + " | text"` before `.strip(" |")`, which correctly handles `None`, empty string, and existing notes.

8. **`scoped_contains` ordering is correct.** `strip_comments` before `strip_string_literals` ensures that `// foo "bar"` is fully neutralized (comment stripped first, no string residue), and block comments containing quotes don't leave orphaned string fragments.

---

## Project-Specific Quality Gates (CLAUDE.md)

| Gate | Status |
|------|--------|
| Self-review: API contracts | Pass — oracle vs evaluator API distinction clear |
| Self-review: redundant calls | Pass — no double-processing detected |
| Self-review: edge cases | Warning — see C1 (skipped+negatives), W1 (counter) |
| New feature = new tests | Pass for all new modules |
| Check function signatures before calling | Pass — `run_checks()` return type matches expected `CheckDetail` usage |

---

## Action Items (Priority Order)

**Must fix before P1 (negatives authoring) begins:**

1. **C1** — Fix `skipped+negatives.py` edge case in `sync_negatives_progress.py`. Add the state transition, add two tests to `test_sync_negatives_progress.py`.

**Should fix this iteration:**

2. **W1** — Clarify `negatives_checked` semantics; rename to `negatives_attempted` or count only oracle-passing negatives to match the PASS print message.

3. **W2** — Apply `strip_string_literals` in `check_no_cross_platform_apis` for raw-substring APIs.

4. **W3** — Add `orphaned` to the status enum in `negatives.md`.

5. **W4** — Either remove `started_at` from the progress schema or add instruction to set it in the command spec.

**Nice to have:**

6. **S1** — Two missing test cases for sync edge paths.

7. **S2** — Split `failure_mode` in oracle missed-entry dicts.

---

## Verdict

**CHANGES_REQUESTED**

The implementation is solid and all tests pass. The state-machine logic and oracle contract are correct for the primary paths. C1 (skipped+negatives silent drop) must be fixed before P1 authoring begins, because it will cause the completion criteria (`find cases -name negatives.py | wc -l == find cases -name static.py | wc -l`) to silently miscount if any TCs were previously skipped and then authored outside the command. The fix is a 3-line change + 2 new tests.

W2 (`check_no_cross_platform_apis` string literals) can be batched with the bulk `scoped_contains` migration in P2 if preferred, rather than as a standalone fix now.
