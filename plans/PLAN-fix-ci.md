---
type: plan
project: embedeval
task_slug: fix-ci
status: planning
created: 2026-04-05
tags: [embedeval, plan, python, ci, github-actions]
summary: "Fix CI failures: commit uv.lock and upgrade GitHub Actions to Node.js 24"
---

# PLAN: Fix CI Failures

**Project:** embedeval
**Task:** Fix CI pipeline — missing uv.lock + Node.js 20 deprecation
**Priority:** High (CI is broken)
**Created:** 2026-04-05

---

## Executive Summary

> **TL;DR:** CI fails because `uv.lock` is gitignored (cache key missing) and uses deprecated Node.js 20 actions.

### What We're Doing
1. Remove `uv.lock` from `.gitignore` and commit the lock file
2. Upgrade all 3 workflows from `actions/checkout@v4` + `astral-sh/setup-uv@v4` to `@v6` and `@v5` respectively

### Why It Matters
All CI jobs (Test, Type Check, Lint) are failing. The Node.js 20 deprecation deadline is June 2, 2026.

### Key Decisions
- **setup-uv@v5 (not v8):** v5 is the last version with standard tag support. v8+ requires commit hash pinning (no `@v8` tags). v5 also enables caching by default.
- **checkout@v6:** Latest stable with Node.js 24 runtime.

### Estimated Impact
- **Complexity:** Low
- **Risk Level:** Low
- **Files Changed:** 4 files
- **Estimated Time:** <15 minutes

---

## REVIEW CHECKLIST

### Critical Decisions to Verify
- [ ] **uv.lock committed:** Should `uv.lock` be committed? (Yes — uv recommends it for reproducible installs)
- [ ] **setup-uv@v5 vs @v8:** v5 is safe and well-tested. v8 requires hash pinning — worth it?
- [ ] **checkout@v6:** Any breaking changes? (Minimal — persists credentials to separate file)

### Code Impact to Review
- [ ] `.gitignore` — Remove `uv.lock` entry
- [ ] `.github/workflows/ci.yml` — Update action versions
- [ ] `.github/workflows/validate-cases.yml` — Update action versions
- [ ] `.github/workflows/benchmark.yml` — Update action versions

---

## Problem Analysis

### Root Cause 1: Missing uv.lock
- `astral-sh/setup-uv@v4` with `enable-cache: true` uses `uv.lock` as cache key
- `.gitignore` line 51: `uv.lock` — prevents the file from being committed
- CI error: `No file matched to [**/uv.lock]`

### Root Cause 2: Node.js 20 Deprecation
- `actions/checkout@v4` and `astral-sh/setup-uv@v4` run on Node.js 20
- GitHub warning: forced Node.js 24 starting June 2, 2026
- Node.js 20 removed from runners September 16, 2026

---

## Implementation Plan

### Phase 1: Fix .gitignore
- [ ] `.gitignore`: Remove `uv.lock` line (line 51)
- [ ] Stage and commit `uv.lock`

### Phase 2: Upgrade GitHub Actions
- [ ] `ci.yml`: `actions/checkout@v4` -> `@v6`, `astral-sh/setup-uv@v4` -> `@v5`
- [ ] `validate-cases.yml`: Same upgrades
- [ ] `benchmark.yml`: Same upgrades (including `actions/upload-artifact@v4` — check if needs update)

### Phase 3: Verify
- [ ] Push and confirm CI passes

---

## Testing Strategy

- Push to a branch, verify all 3 CI jobs pass (Lint, Type Check, Test)
- Validate-cases only triggers on `cases/**` changes — may need manual trigger or path touch

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| setup-uv@v5 cache behavior change | Low | v5 enables cache by default — we already set `enable-cache: true`, so no change |
| checkout@v6 breaking change | Low | v6 is backward compatible for standard checkout usage |
| uv.lock conflicts | Low | Lock file is auto-generated, easy to resolve |

---

## Sources

- [actions/checkout releases](https://github.com/actions/checkout/releases) — v6 = Node.js 24
- [astral-sh/setup-uv releases](https://github.com/astral-sh/setup-uv/releases) — v5+ available
- [astral-sh/setup-uv repo](https://github.com/astral-sh/setup-uv) — cache docs
- [Bump setup-uv v4 to v5 (FastAPI example)](https://github.com/fastapi/fastapi/pull/13096)
