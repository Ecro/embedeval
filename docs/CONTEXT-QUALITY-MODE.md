# Context Quality Mode

EmbedEval can measure how much your team's "implicit context" (CLAUDE.md,
system prompt, coding standard) actually helps an LLM write embedded code.

The mechanism: run the same benchmark cases with three different context
configurations and compare per-category pass rates.

| Configuration | What you pass | Represents |
|---|---|---|
| `bare` | nothing (no `--context-pack`) | The LLM out-of-the-box |
| `team` | `--context-pack /path/to/your/CLAUDE.md` | Your team's current context |
| `expert` | `--context-pack expert` | Reference ceiling — bundled embedded principles |

Two metrics fall out of the comparison:

- **Context Lift** = `team − bare`. How much your context pack actually
  helps the LLM, in percentage points. Larger is better.
- **Context Gap** = `expert − team` (or `expert − bare` when no team
  pack). How much further the LLM could go with better context. A small
  Gap on a category means the LLM has hit a hard limit there — context
  alone won't fix it.

> **Lift can be negative — that is a real signal, not a bug.**
> Empirical 2026-04-18 Haiku validation found cases where the expert
> pack drops pass rate by up to 100pp on a single TC, while
> simultaneously raising it by 100pp on another. The mechanism:
> pack content focuses LLM attention on principle application
> (e.g., adding `volatile`) but can distract from structural
> correctness (e.g., setting up the actual ISR). Read per-category
> Lift as direction, not as universal benefit. Aggregate Lift near
> zero with high per-case variance is informative — it tells you
> the pack helps some cases and hurts others.

## Why this matters

Recent research shows that giving an LLM problem context measurably
improves code review accuracy ([arXiv:2505.20206]). What hasn't existed
is a way to objectively measure whether *your* team's context is good
enough. Context Quality Mode is that measurement.

It also tells you when to stop tuning prompts and reach for stronger
tools (static analyzers, runtime verification on real hardware): if a
category's Gap is small even with the expert pack, the LLM is unlikely
to learn that class of failure from any prompt.

[arXiv:2505.20206]: https://arxiv.org/html/2505.20206v1

## Quick start

```bash
# 1. Bare baseline
embedeval run --model claude-code://sonnet \
              --category isr-concurrency \
              --output-dir runs/bare

# 2. Your team's context
embedeval run --model claude-code://sonnet \
              --category isr-concurrency \
              --context-pack ./CLAUDE.md \
              --output-dir runs/team

# 3. Expert reference
embedeval run --model claude-code://sonnet \
              --category isr-concurrency \
              --context-pack expert \
              --output-dir runs/expert

# 4. Compare
embedeval context-compare \
    --bare runs/bare \
    --team runs/team \
    --expert runs/expert
```

Sample output:

```
Context Quality Comparison (model: claude-code://sonnet)

  bare    hash=<none>            n= 10  pass_rate= 30.0%
  team    hash=4af1e8c2b3d5a7f0  n= 10  pass_rate= 60.0%
  expert  hash=1ba6c696b70694b4  n= 10  pass_rate= 80.0%

  Category              n     Bare   Team Expert     Lift     Gap  Effect (H/Hm/F/P)
  -----------------------------------------------------------------------------------
  isr-concurrency      10      30%    60%    80%   +30pp   +20pp       5H/0Hm/2F/3P
  -----------------------------------------------------------------------------------
  OVERALL              10      30%    60%    80%   +30pp   +20pp       5H/0Hm/2F/3P

  Lift = team − bare  (effect of team's context pack)
  Gap  = expert − team  (room to improve toward expert pack)
  Gap < 5pp on a category → likely an LLM hard-limit, not a context problem.
  Effect (bare → expert): H=helpful (F→T), Hm=harmful (T→F), F=both fail, P=both pass.
  Hm cases: always inspect generated code — may be real trade-off or EmbedEval check brittleness.
```

Read this as: "Our CLAUDE.md gets us +30pp on ISR cases. The expert pack
adds another +20pp, so there's still room to strengthen our context.
Most of the improvement is in our reach."

## Per-case effect classification

Aggregate Lift hides a real phenomenon: on any given category the same
pack can help some cases and hurt others. The 2026-04-18 Haiku N=14
validation found cases where expert pack flipped `bare:T → packed:F`
on one TC while flipping `bare:F → packed:T` on another, with aggregate
Lift ≈ 0. Reading only Lift would conclude "pack does nothing"; reading
per-case shows "pack changes behavior in both directions".

Every case falls into one of four effect buckets relative to the bare
baseline:

| Symbol | Name | Meaning | Read as |
|--------|------|---------|---------|
| **H** | helpful | bare fail → packed pass | pack unblocked the case |
| **Hm** | harmful | bare pass → packed fail | pack broke it — inspect code |
| **F** | no-effect-fail | bare fail + packed fail | LLM hard-limit |
| **P** | no-effect-pass | bare pass + packed pass | no headroom to show effect |

The comparison dimension is **bare → expert** by default: it answers "did
the expert pack help?", which is the dominant question when you have
one. Use `--include-team-effect` to also classify **bare → team** in the
JSON output (`bare_to_team_effect` per case) when you want to dig into
how the team pack itself changed behavior.

### Inspecting harmful cases

An `Hm` count > 0 means the pack regressed at least one case. Two causes
look identical in the counts but require different fixes:

1. **Real attention trade-off.** Pack content focused the LLM on one
   principle (e.g., adding `volatile`) and distracted from another
   (e.g., setting up the ISR). Fix is to refine the pack.
2. **EmbedEval check brittleness.** The generated code used a valid
   API variant the checks don't yet accept (`dma_config` vs
   `dma_configure`). Fix is in `cases/<case>/checks/static.py`, not the
   pack.

Use `embedeval harmful-inspect` to sub-classify each harmful case
automatically, using the layer at which the expert run failed:

```bash
embedeval harmful-inspect --bare runs/bare --expert runs/expert \
    --output-json runs/harmful.json
```

Sample output:

```
Harmful cases: 3 total
  likely-brittleness: 2  (inspect cases/*/checks/static.py)
  likely-real:        1  (edit the context pack)
  uncertain:          0  (manual inspection)

  Case                          L   Classification        Failed checks
  ---------------------------------------------------------------------
  dma-002                       L0  likely-brittleness    check_dma_config_api
  dma-007                       L0  likely-brittleness    check_alignment_macro
  isr-concurrency-003           L1  likely-real           compile_zephyr
```

The heuristic uses the failure layer:

| Layer | Name | Classification | Why |
|-------|------|----------------|-----|
| L0 | Static (regex) | likely brittleness | regex rejects valid API variants |
| L1 | Compile | likely real | code doesn't compile |
| L2 | Runtime | likely real | runtime divergence |
| L3 | Behavioral (regex on output) | uncertain | could be reworded log or real change |
| L4 | Mutation | likely real | mutation meta-check caught it |

`likely-real` cases point at the pack; `likely-brittleness` cases point
at `cases/<case>/checks/static.py`. `uncertain` cases need a manual
diff of `runs/bare/<case>/generated.py` vs `runs/expert/<case>/generated.py`.

### JSON output

`--output-json` carries a `per_case` list and a `per_category[*].effect_counts`
block suitable for CI regression checks ("yesterday helpful, today
harmful"):

```json
{
  "per_category": [
    {
      "category": "isr-concurrency",
      "n_cases": 10,
      "bare_pass_rate": 0.3,
      "team_pass_rate": 0.6,
      "expert_pass_rate": 0.8,
      "lift": 0.3,
      "gap": 0.2,
      "effect_counts": {
        "helpful": 5,
        "harmful": 0,
        "no-effect-fail": 2,
        "no-effect-pass": 3
      }
    }
  ],
  "per_case": [
    {
      "case_id": "isr-concurrency-001",
      "category": "isr-concurrency",
      "bare_passed": false,
      "team_passed": true,
      "expert_passed": true,
      "bare_attempts": 1,
      "team_attempts": 1,
      "expert_attempts": 1,
      "bare_to_expert_effect": "helpful",
      "bare_to_team_effect": null
    }
  ]
}
```

`effect_counts` sums to the number of cases with data on both sides of
the comparison; in mixed case sets (a case appears in bare but not in
expert) the missing case has `bare_to_expert_effect: null` and is
excluded from the totals.

### Multi-attempt runs (n>1)

The tracker stores only the most recent attempt's pass status per case.
When `embedeval run --attempts 3` populated the trackers,
`context-compare` surfaces `attempts_max=3` in the run summary header
and emits a banner warning:

```
Note: n>1 attempts detected — per-case effect is computed on last-attempt pass status only.
Use scripts/aggregate_n_runs.py for statistical robustness across attempts.
```

For publication-quality effect distributions across multi-attempt runs,
pre-aggregate with `scripts/aggregate_n_runs.py` and feed the resulting
single-attempt-equivalent trackers into `context-compare`.

## Diagnosing context coverage gaps

Lift and Gap tell you *that* your CLAUDE.md is below the expert ceiling.
They don't tell you *which* embedded principles to add. `context-diagnose`
closes that loop by rolling every failed check up to its FAILURE-FACTORS
category and listing the High-strength factor IDs to encode in CLAUDE.md.

```bash
embedeval context-diagnose --team runs/team --expert runs/expert \
    --output-json runs/diagnosis.json
```

Sample output:

```
Context Coverage Diagnosis (model: claude-code://sonnet)

  Gap threshold: 10pp  (categories above this need CLAUDE.md improvement)

  Category                                    Team Expert     Gap   High factors to cover
  ---------------------------------------------------------------------------------------
  D. Memory Model & Concurrency                53%     7%   +46pp   D1, D2, D4, D5
  E. Error Handling & Safety Patterns          38%    12%   +26pp   E1, E2, E3, E4, E7
  B. Temporal & Real-Time Constraints          20%    10%   +10pp   (within threshold)
  A. Hardware Awareness Gap                    18%    15%    +3pp   (within threshold)
  C. Memory & Resource Constraints             12%    10%    +2pp   (within threshold)
  F. Toolchain, SDK & Platform Knowledge        8%     7%    +1pp   (within threshold)

  To improve coverage:
    D. Memory Model & Concurrency → add principles for factors D1, D2, D4, D5
       See docs/LLM-EMBEDDED-FAILURE-FACTORS.md#d-memory-model--concurrency
    E. Error Handling & Safety Patterns → add principles for factors E1, E2, E3, E4, E7
       See docs/LLM-EMBEDDED-FAILURE-FACTORS.md#e-error-handling--safety-patterns
```

### Workflow

The intended usage pattern is a loop:

1. Run `embedeval context-compare` to get Lift/Gap.
2. If Gap > 5pp, run `embedeval context-diagnose` to see which
   categories drive the Gap and which factor IDs belong in the team
   pack.
3. Edit CLAUDE.md with one principle paragraph per listed factor —
   phrased as the principle (not the API), following `expert.md` as
   the style reference.
4. Rerun `embedeval run --context-pack team/CLAUDE.md --output-dir runs/team`
   and re-diagnose. Repeat until the remaining Gap is below the
   `--gap-threshold` (default 10pp) across all categories.

### Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--team` | required | `output_dir` of the run with the team's CLAUDE.md |
| `--expert` | required | `output_dir` of the run with `--context-pack expert` |
| `--model` | auto-resolve | Required when both trackers carry multiple models |
| `--gap-threshold` | `10.0` (pp) | Categories with `gap > threshold` are flagged |
| `--output-json` | none | Writes the full `CoverageDiagnosis` payload |

### JSON schema

`--output-json` emits a `CoverageDiagnosis` payload suitable for CI
regression gates (for example: "alert when any category's `gap`
exceeds yesterday's value"):

```json
{
  "model": "claude-code://sonnet",
  "gap_threshold": 0.10,
  "per_category": [
    {
      "category": "D",
      "category_title": "Memory Model & Concurrency",
      "team_failed_checks": ["memory_barrier_present", "volatile_error_flag"],
      "expert_failed_checks": [],
      "team_failed_occurrences": 18,
      "expert_failed_occurrences": 2,
      "total_check_occurrences": 34,
      "team_failure_rate": 0.53,
      "expert_failure_rate": 0.06,
      "gap": 0.47,
      "needs_coverage": true,
      "high_strength_factors": ["D1", "D2", "D4", "D5"],
      "factor_names": {
        "D1": "`volatile` misuse",
        "D2": "Memory barriers & fences",
        "D4": "Race conditions",
        "D5": "ISR context restrictions"
      }
    }
  ],
  "unmapped_checks": []
}
```

### Unmapped checks

When `cases/*/checks/static.py` introduces a new check before
`docs/LLM-EMBEDDED-FAILURE-FACTORS.md` is updated to include it in a
category's `**EmbedEval checks mapped:**` line, diagnosis continues —
the new check lands in `unmapped_checks` and `logger.warning` surfaces
the list. The fix is to add the new check name to the appropriate
category's mapping line in FAILURE-FACTORS.md.

### Why category-level, not factor-level

The `**EmbedEval checks mapped:**` lines group checks by category, not
by factor. Factor-level diagnosis would require hand-curating ~100
check-to-factor mappings and paying the drift cost every time a new
check is added. Category-level is zero-curation (the mapping line is
parsed directly) and already tells the user which factor IDs to add —
surfacing all High-strength factors in each flagged category as the
action pointer. Factor-level is deferred to v2 if users report the
category grain is too coarse.

## How `--context-pack` works

The pack content is prepended to every prompt sent to the LLM, ahead of
any per-case context files:

```
## Team Context

<your pack content>

<per-case context files, if any>

<original case prompt>
```

This is intentionally the same channel as a typical `CLAUDE.md` — what
the LLM sees during a real coding session. The mode does not use the
provider's `system` role API; that keeps results comparable across the
`mock`, `claude-code://`, and `litellm` modes.

## The bundled expert pack

`embedeval/context_packs/expert.md` is a curated set of high-level
embedded engineering principles. Design choices:

- **No exact API names.** It says "mark shared variables with whatever
  the language provides to defeat caching of stale values," not "use
  `volatile`." The LLM must derive the implementation. This preserves
  EmbedEval's discriminating power — packs that hand the LLM the answer
  pull every score toward 100% and tell you nothing.
- **~1100 tokens.** Enough to cover the 6-7 principle areas (ISR/DMA/
  memory/kernel/build/error/hardware), short enough not to dilute
  attention.
- **Curated by hand**, not auto-generated. Auto-extracting from
  `LLM-EMBEDDED-FAILURE-FACTORS.md` re-introduces specific API names
  from the failure data, which violates the "principle, not recipe"
  rule.

If the expert pack pulls every category to 95%+, it's too explicit —
file an issue and we'll generalize it further.

### Coverage drift check

`scripts/build_expert_pack.py` is a drift detector, not a generator:
it parses the factor tables in `LLM-EMBEDDED-FAILURE-FACTORS.md` and
writes `src/embedeval/context_packs/expert-coverage.md`, a
machine-generated reference listing every factor by category and
strength. CI runs `--check` and fails if the checked-in coverage file
is out of sync.

When a PR adds a new High-strength factor to FAILURE-FACTORS, the CI
gate forces a deliberate decision:

```bash
uv run python scripts/build_expert_pack.py
# Review the diff, then update expert.md if the new factor lacks
# principle coverage. Commit both files together.
```

The script does NOT rewrite `expert.md` itself — principle-level
curation stays human, and the coverage reference just makes drift
visible.

## Tracker safety

`embedeval run --context-pack` records a 16-char SHA256 hash of the
pack content into `test_tracker.json`'s `context_pack_hash` field.

A second run into the same `--output-dir` must use the same pack (same
hash, or both no pack). Otherwise the tracker raises
`ContextPackMismatchError` and exits non-zero. This prevents silently
mixing bare and packed results into a single output that downstream
tools (leaderboard, comparison) would then misinterpret.

To run with a different pack, use a different `--output-dir`. The
comparison command then loads each tracker separately.

## What about the LLM's `system` role?

We don't use it. Reasons:

- `claude-code://` calls `claude -p` with stdin, which carries a single
  user message. There is no `system` channel.
- Different providers compose system + user differently. Prepending
  to user keeps the comparison fair.
- For most teams, "context" lives in `CLAUDE.md` files that the editor
  passes as user-message context, not system prompts. We measure the
  channel users actually use.

## Recommended workflow

1. Run a small subset (one or two categories, single attempt) first to
   sanity-check that the context pack reaches the model. Use
   `scripts/smoke_test_context_pack.py --model haiku` if you want to
   verify the plumbing without running a full benchmark.
2. Pick categories where you suspect your context is weak — `dma`,
   `isr-concurrency`, `threading` are usual suspects.
3. Run the three configurations with the same model, attempts, and
   filter so the comparison is apples-to-apples.
4. Read the table. Lift > 10pp means your pack is doing real work.
   Gap > 15pp means you have headroom in your context. Gap < 5pp
   means the LLM has hit a wall — invest in static analysis or HIL
   verification for that category, not more prompt engineering.

## CI integration

Suggested GitHub Action snippet:

```yaml
- name: Context quality regression
  run: |
    embedeval run --model claude-code://sonnet --category isr-concurrency \
                  --output-dir runs/team --context-pack ./CLAUDE.md
    embedeval run --model claude-code://sonnet --category isr-concurrency \
                  --output-dir runs/expert --context-pack expert
    # Bare baseline updated less frequently — checked into the repo
    embedeval context-compare \
        --bare baselines/bare-runs \
        --team runs/team \
        --expert runs/expert \
        --output-json runs/context-quality.json
```

A separate script can then read `context-quality.json`, compare overall
Lift to the previous main-branch value, and fail the CI if Lift dropped
by more than N percentage points — i.e., your CLAUDE.md edit made the
context worse.

## Cost and tokens

A pack of ~1000 tokens prepended to every prompt adds ~1000 input
tokens × N cases × M attempts. For a 233-case run with 3 attempts on
Sonnet, that's roughly +0.7M input tokens. Use small subsets when
iterating on context, full runs only at known-good checkpoints.

`context-compare` now reports this footprint directly, aggregated from
`CaseResult` totals in each tracker. The footer appears only when at
least one run recorded non-zero usage (mock-only smoke tests stay
clean):

```
  Total tokens used:
    bare    in=   15,000  out=   5,200  total=   20,200  $  0.08
    team    in=   28,000  out=   5,400  total=   33,400  $  0.14  +87% input vs bare
    expert  in=   31,000  out=   5,500  total=   36,500  $  0.16  +107% input vs bare
```

The `+NN% input vs bare` delta is the direct cost of prepending the
pack on every prompt — use this to tune the pack length vs Lift gain
trade-off. `cost_usd` is whatever `litellm.cost_per_completion`
returned at run time; `mock` and CLI-mode runs report `$0.00`.

## See also

- `scripts/smoke_test_context_pack.py` — verifies `claude -p` actually
  receives the pack
- `src/embedeval/context_pack.py` — pack resolution and hashing
- `src/embedeval/context_compare.py` — comparison logic
- `plans/PLAN-context-quality-mode.md` — design decisions and rationale
