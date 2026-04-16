---
type: session
project: embedeval
task_slug: launch-embedeval-public
status: in-progress
created: 2026-04-16
tags: [embedeval, session, python, launch, documentation, marketing]
related:
  - "[[plans/PLAN-launch-embedeval-public]]"
  - "[[ROADMAP]]"
  - "[[LAUNCH-COPY]]"
  - "[[docs/METHODOLOGY]]"
summary: "Day 1 — 모든 코드/문서/시각자산 정비. 5개 PNG, ROADMAP, LAUNCH-COPY, HF Space, Issue 템플릿."
---

# SESSION: Launch EmbedEval — Day 1

**Project:** embedeval
**Task:** launch-embedeval-public — Day 1 (자산 정비)
**Date:** 2026-04-16 (화)
**Duration:** ~3h

---

## Plan Reference

[plans/PLAN-launch-embedeval-public.md](PLAN-launch-embedeval-public.md)

---

## What Was Done

Day 1 of the 5-day launch sprint. All assets, docs, and visual artifacts in
place. Code path untouched (1277 tests still pass; 185 reference solutions
still validate). Mid-session scope changes from the user: arXiv excluded,
Korean channels removed, LinkedIn deferred to sustain phase, neutral tone
enforced, emojis stripped.

---

## Changes Made

| File | Status | Lines | Purpose |
|------|--------|-------|---------|
| `ROADMAP.md` | new | 130 | v0.2 / v0.3 / v1.0 roadmap. GPT/Gemini intentionally vague ("expand model coverage"). |
| `LAUNCH-COPY.md` | new | ~440 | Copy for HN, 3 subreddits, Twitter thread (8), Zephyr Discord, DM template, response templates. LinkedIn = sustain only. Korean sections removed per user request. |
| `scripts/generate_launch_assets.py` | new | ~310 | matplotlib script that builds 5 PNGs from inlined n=3 data. Re-runnable. |
| `assets/launch/heatmap.png` | new | — | 23 categories × 2 models, RdYlGn |
| `assets/launch/implicit-gap.png` | new | — | explicit 95% vs implicit 60% |
| `assets/launch/architecture.png` | new | — | 5-layer pipeline diagram |
| `assets/launch/model-comparison.png` | new | — | Sonnet vs Haiku n=3 + 95% CI bars |
| `assets/launch/twitter-card.png` | new | — | 1200×630 social composite |
| `space/app.py` | new | ~190 | Gradio leaderboard + heatmap + per-model bar + methodology tab |
| `space/requirements.txt` | new | 3 | gradio, plotly, pandas |
| `space/README.md` | new | ~30 | HF Space frontmatter + minimal landing copy |
| `.github/ISSUE_TEMPLATE/model-evaluation-request.md` | new | ~40 | Template for new model eval requests |
| `.github/ISSUE_TEMPLATE/case-contribution.md` | new | ~40 | Template for new case proposals |
| `.github/ISSUE_TEMPLATE/methodology-question.md` | new | ~25 | Template for methodology critique |
| `README.md` | edit | +47 / -10 | Hero heatmap + implicit-gap images, EmbedAgent paragraph, Roadmap section, Citation BibTeX, neutral CTA, FreeRTOS added to platform list |
| `docs/METHODOLOGY.md` | edit | +52 / -8 | L4 mutation testing section rewritten to address "L3 = regex" critique upfront |
| `plans/PLAN-launch-embedeval-public.md` | edit | several | Mid-session updates reflecting user decisions (no Korean, no LinkedIn on D-Day, no arXiv, no external feedback) |

Net: 13 new files, 3 edits, no source code changes.

---

## Implementation Log

### Phase 1.1 — ROADMAP.md
Wrote v0.2 / v0.3 / v1.0. Decision: name candidate work but never promise
specific models. "Expand model coverage" reads as forward-looking without
committing.

### Phase 1.2 — LAUNCH-COPY.md
Drafted nine channel templates, then removed three (LinkedIn KR, GeekNews,
Disquiet) and deferred LinkedIn EN to sustain after user feedback. Final
D-Day scope: HN, 3 subreddits, Twitter, Zephyr Discord. Response templates
preserved for the predictable critiques (no GPT/Gemini, regex L3, Wilson CI,
contamination control, Zephyr bias, single-file scope).

### Phase 1.3 — Visual assets
Wrote `scripts/generate_launch_assets.py`. Inlined n=3 numbers from
`results/LEADERBOARD.md` (sync notes in script header). matplotlib only —
no seaborn dep. All five PNGs generated cleanly on first run, total 408 KB.

### Phase 1.4 — HF Space
`space/app.py` is a self-contained Gradio app with four tabs: Leaderboard,
Heatmap, Per-model breakdown, How it works. Static data (no live evaluation).
Uses plotly for interactive charts.

### Phase 1.5 — Issue templates
Three templates under `.github/ISSUE_TEMPLATE/`:
- model evaluation request (with willingness-to-contribute checkbox)
- case contribution (with anti-gaming checkbox: "describe what, not how")
- methodology question (encourages explicit "what would change my mind")

### Phase 1.6 — README.md upgrade
Added hero `heatmap.png` directly under the description, then `implicit-gap.png`
under the Key Insight section. Strengthened the EmbedAgent comparison from a
single table row to a paragraph that explicitly states the differentiation.
Added Roadmap, Citation BibTeX, neutral inline CTA. Stripped emoji bullets
after user feedback.

### Phase 1.7 — METHODOLOGY.md L4 rewrite
The L4 section was previously buried at the bottom and read as
"meta-verification, optional". Rewrote to lead with "L4 exists because L3
uses regex heuristics" — addresses the most predictable external critique
(SWE-bench Verified comment-thread pattern) at the source rather than in
post-launch responses.

---

## Issues Encountered

### Issue 1: Mid-session scope reduction (Korean channels)
- **Encountered:** after LAUNCH-COPY.md was complete with 9 channel sections
- **Impact:** ~140 lines of Korean copy and the entire Korean half of the D-Day timetable became dead weight
- **Solution:** removed `LinkedIn (한국어)`, `GeekNews`, `Disquiet` sections via `sed -i '403,544d'`. Updated D-Day timetable to compress into 50 minutes (T+0 to T+50min) instead of two hours

### Issue 2: LinkedIn deferred mid-edit
- **Encountered:** during D-Day timetable revision
- **Impact:** LinkedIn EN was already drafted and slotted at T+15min
- **Solution:** kept the LinkedIn EN copy in LAUNCH-COPY.md but added "sustain phase, not D-Day" header. Plan updated to post LinkedIn on Day 9 once HN response is known so the post can quote the most-discussed comment

### Issue 3: AI-typical patterns / emoji noise
- **Encountered:** initial draft used emoji bullets in CTA (`🚀 📊 🗺️ 🤝`) and section headers
- **Impact:** would have telegraphed "AI-generated launch material"
- **Solution:** swept all new files for emoji codepoints with a Python regex; replaced with plain-text bullets and inline links. Only checkmarks left are CLI stdout markers in `generate_launch_assets.py` (not user-facing)

---

## Test Results

```
$ uv run pytest --tb=short -q
1277 passed in 12.44s

$ uv run embedeval validate --cases cases/
Validation: 185 passed, 0 failed

$ uv run python scripts/sync_docs.py
All documentation is already up to date.

$ uv run python scripts/generate_launch_assets.py
  ✓ heatmap.png
  ✓ implicit-gap.png
  ✓ architecture.png
  ✓ model-comparison.png
  ✓ twitter-card.png
Done.
```

HF Space `app.py` not yet smoke-tested locally — Day 2 task before HF push.

---

## Success Criteria Check (Day 1 portion of PLAN)

- [x] ROADMAP.md committed (drafted, awaiting commit)
- [x] LAUNCH-COPY.md committed (drafted, awaiting commit)
- [x] scripts/generate_launch_assets.py committed (drafted, awaiting commit)
- [x] assets/launch/ — 5 PNG generated
- [x] README.md upgraded (hero image, EmbedAgent paragraph, Roadmap, BibTeX)
- [x] METHODOLOGY.md L4 mutation testing section rewritten
- [x] .github/ISSUE_TEMPLATE/ — 3 templates
- [x] uv run pytest — 1277 passed
- [x] uv run embedeval validate — 185 passed
- [x] uv run python scripts/sync_docs.py — clean

Deferred to Day 2:
- [ ] HF Space deployment (`huggingface.co/spaces/ecro/embedeval`)
- [ ] EdgeLog English launch post
- [ ] Demo GIF recording

---

## Git Status

Branch: `main`. **Not yet committed** — awaiting user review per CLAUDE.md
quality gate.

```
M  README.md
M  docs/METHODOLOGY.md
?? .github/ISSUE_TEMPLATE/
?? LAUNCH-COPY.md
?? ROADMAP.md
?? assets/
?? plans/PLAN-launch-embedeval-public.md
?? plans/SESSION-launch-embedeval-public-2026-04-16.md
?? scripts/generate_launch_assets.py
?? space/
```

The file `docs/PLAN-docs-update-n3-results.md` was already untracked from a
prior session — not part of this session.

---

## Metrics

- **Files added:** 13
- **Files edited:** 3 (README, METHODOLOGY, PLAN)
- **Lines added:** ~1100 (mostly LAUNCH-COPY + script)
- **Lines removed:** ~140 (Korean channel sections)
- **Tests added:** 0 (no source code change)
- **Regression risk:** none — pytest + validate clean
- **Active duration:** ~3h

---

## Next Steps

1. **User review** of all 13 new files + 3 edits before commit
2. Commit Day 1 in 2-3 logical groups (suggested):
   - `feat(launch): roadmap, issue templates, contribution surfaces`
   - `feat(launch): visual assets script + 5 PNGs + HF Space code`
   - `docs(launch): launch copy, README upgrade, METHODOLOGY L4 rewrite`
3. Day 2 (Wed 04-17): EdgeLog English launch post, then publish
4. Day 3 (Thu 04-18): Push HF Space, record demo GIF
