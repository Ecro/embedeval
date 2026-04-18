---
type: wrapup
project: embedeval
task_slug: hiloop-transpile-readiness
phase: 0-3
status: completed
created: 2026-04-19
tags: [embedeval, wrapup, completed, python, embedded, testing, benchmark]
related:
  - "[[plans/PLAN-hiloop-transpile-readiness]]"
  - "[[plans/SESSION-hiloop-transpile-readiness-2026-04-19]]"
summary: "Phase 0–3 landed: P4 forbidden_apis.yaml + P3 per_check_stats + P2 scoped_contains/audit. 29 new tests, all green. P1+P5 queued."
---

# WRAPUP: Hiloop Transpile Readiness — Phase 0–3

**Project:** embedeval
**Task:** hiloop-transpile-readiness
**Phase covered:** 0–3 (Phase 4 P1 negatives + Phase 5 docs deferred)
**Completed:** 2026-04-19

---

## ✅ Summary

Shipped the infrastructure portion of PLAN-hiloop-transpile-readiness: P4 extracted the cross-platform forbidden-API blacklist to `src/embedeval/data/forbidden_apis.yaml` so both EmbedEval and downstream tools (Hiloop shared rule pack) read the same source of truth; P3 added `PerCheckStat` aggregation to `summary.json` giving per-check failure rates with `failing_tc_ids` traceability; P2 landed `scoped_contains`/`strip_string_literals` helpers plus an AST-based audit script that found 1982 unscoped substring sites across 325 check files (baseline snapshot saved for future migration diff).

Phase 4 (155 new `negatives.py` files) and Phase 5 (docs/HILOOP-HANDOFF.md) are not in this commit — those are mass-authoring jobs better sequenced across subsequent sessions per PLAN.

---

## 📋 References

- [PLAN](PLAN-hiloop-transpile-readiness.md)
- [SESSION](SESSION-hiloop-transpile-readiness-2026-04-19.md)

---

## 🧪 Testing

**pytest:** ✅ 1423 passed (up from 1400 — +23 net new tests)
**ruff check** on touched files: ✅ All checks passed
**mypy src/:** ✅ Success: no issues found in 24 source files
**sync_docs.py:** ✅ README.md updated, METHODOLOGY.md already current

**New tests added:**
- `tests/test_forbidden_apis.py` — 9 tests (P4)
- `tests/test_per_check_stats.py` — 9 tests (P3)
- `tests/test_scoped_contains.py` — 11 tests (P2 helper)

---

## 📊 Metrics

- **Development time:** ~1 hour
- **Files changed:** 11 (4 edited, 7 new)
- **Lines:** ~900 code + ~14,000 JSON audit baseline
- **Tests added:** 29
- **Tests passing:** 1423 / 1423
- **Coverage gap closed:** 1 of 3 (P4/P3/P2-helper done; P1 mass-authoring + P2 migration pending)

---

## 💡 Learnings

### What Went Well
- Sequencing P4 → P3 → P2-helper was the right call — all three are additive, backward-compatible, and shipped without touching any existing benchmark numbers.
- `_calculate_per_check_stats` correctly excludes `check_type == "mutation"` (L4 synthetic checks don't reflect model behavior). Caught this during design, not after.
- Audit tool surfaced that P2 scope is much larger than the PLAN estimated (1982 vs ~50 sites) — that's useful intel for sequencing migration batches.

### What Could Be Improved
- PLAN's P2 estimate (~50 files, 6–8h) was off by ~40x for the raw finding count. Most findings are header-include checks that don't actually need migration — but the PLAN didn't distinguish "raw count" vs "needs-change count." Future PLANs estimating refactor scope should run the audit tool first.

### CLAUDE.md Corrections
- **None required.** No TESTER failures, STUCK escalations, or rework during this session. The one blocker encountered (Pydantic forward ref in `models.py`) was self-caught in the first test run and resolved by reordering declarations — a normal debug iteration, not a correction-worthy mistake.

---

## ➡️ Follow-up

### Next Session (Phase 4 — P1 negatives authoring)
Priority order (weakest Haiku categories first — highest signal):
1. `dma` remaining 11 cases
2. `isr-concurrency` remaining 11 cases
3. `threading` remaining 7 cases
4. `memory-opt` remaining 15 cases
5. Remaining categories sweep

### Following Session (Phase 3 — P2 migration)
Start with `isr-concurrency` (13 TCs). Per-category PR. Flip-allow + `BENCHMARK-DELTA-*.md` documentation policy.

### Final Session (Phase 5)
`docs/HILOOP-HANDOFF.md` — single source of truth for Hiloop repo consumers (summary.json schema, negatives.py schema, forbidden_apis.yaml location).

### Track 2 (after Track 1 done)
`PLAN-yocto-coverage-expansion.md`: yocto 8→25, linux-driver 8→20, Yocto failure-factor layer. Directly targets user's Yocto-primary practice.
