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

  Category              n     Bare   Team Expert     Lift     Gap
  ----------------------------------------------------------------
  isr-concurrency      10      30%    60%    80%   +30pp   +20pp
  ----------------------------------------------------------------
  OVERALL              10      30%    60%    80%   +30pp   +20pp

  Lift = team − bare  (effect of team's context pack)
  Gap  = expert − team  (room to improve toward expert pack)
  Gap < 5pp on a category → likely an LLM hard-limit, not a context problem.
```

Read this as: "Our CLAUDE.md gets us +30pp on ISR cases. The expert pack
adds another +20pp, so there's still room to strengthen our context.
Most of the improvement is in our reach."

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

## See also

- `scripts/smoke_test_context_pack.py` — verifies `claude -p` actually
  receives the pack
- `src/embedeval/context_pack.py` — pack resolution and hashing
- `src/embedeval/context_compare.py` — comparison logic
- `plans/PLAN-context-quality-mode.md` — design decisions and rationale
