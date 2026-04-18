# /negatives — Interactive mutation-oracle authoring

## Communication Protocol

- Be direct. No preamble, no ceremony, no encouragement.
- Show the user concrete content (code, check names, reference snippets) before asking questions.
- Ask ONE decision per AskUserQuestion call — never batch multiple unrelated decisions.
- Never guess judgment calls. If unclear, ask.
- Never skip the oracle gate. A negative that doesn't pass oracle is not landed.

Sequentially author `negatives.py` for every case that lacks one,
with interactive judgment gates where LLM cannot reliably decide.

---

## Usage

```
/negatives                         # sync + resume — work the next pending case
/negatives --status                # sync + print progress table and exit
/negatives --case TC_ID            # sync + work a specific case
/negatives --category dma          # sync + cycle pending cases in a category
/negatives --sync                  # ONLY reconcile progress file with cases/, print diff, exit
/negatives --skip TC_ID reason     # mark TC as skipped with reason (won't revisit)
/negatives --reset TC_ID           # re-open a done case
/negatives --init                  # nuke progress file and rebuild from scratch (destructive)
```

**Every invocation runs auto-sync first** — the progress file is always reconciled
with the current `cases/` directory before any action. Newly added TCs (from
Yocto/Linux expansion, new categories, etc.) appear automatically as `pending`
without manual bookkeeping. Removed TCs are flagged as `orphaned` (not deleted —
may be a rename/typo).

---

## Progress File

Location: `plans/negatives-progress.json`

Schema:
```json
{
  "version": 1,
  "generated": "YYYY-MM-DD",
  "cases": [
    {
      "case_id": "dma-002",
      "category": "dma",
      "priority": 1,
      "status": "pending | in-progress | done | skipped | orphaned",
      "started_at": "YYYY-MM-DD" or null,
      "completed_at": "YYYY-MM-DD" or null,
      "notes": "skip reason or oracle warnings" or null
    }
  ]
}
```

**Field ownership:**
- `status`, `category`, `priority`, `completed_at`, `notes`: written by `sync_negatives_progress.py`.
- `started_at`: written by the `/negatives` command itself when a TC first
  transitions to `in-progress` (Step 3 below). The sync script never touches it.

Priority order (from PLAN-hiloop-transpile-readiness, weakest Haiku first):
1. `dma` (priority 1) — Haiku 7.7%
2. `isr-concurrency` (priority 2) — Haiku 38%
3. `threading` (priority 3)
4. `memory-opt` (priority 4)
5. `dma`/`isr`/`threading`/`memory-opt` subtle remainder (priority 5)
6. all other categories (priority 6)

---

## Implementation

### Step 1. Auto-sync progress file (ALWAYS runs first)

**Rule:** Every invocation reconciles the progress file with the live
`cases/` directory. Additive — existing state (status, notes, timestamps)
is preserved. New TCs added to `cases/` (e.g. future Yocto/Linux
expansion) appear as `pending` automatically.

Delegate to `scripts/sync_negatives_progress.py`:

```bash
uv run python scripts/sync_negatives_progress.py \
    --cases cases/ \
    --progress plans/negatives-progress.json
```

The sync script implements the following merge rules:

| Case state on disk | Case state in file | Action |
|---|---|---|
| has `static.py`, new to file | — | Add entry: `status=pending`, priority by category |
| has `negatives.py`, new to file | — | Add entry: `status=done` (pre-existing), auto-marked |
| has `negatives.py`, file says `pending` or `in-progress` | existing | Promote to `done` (someone authored outside command) |
| no `negatives.py`, file says `done` | existing | Demote to `pending`, add note "regression: file removed" |
| in file, not on disk | existing | Keep entry but mark `status=orphaned`, note "case dir missing" |
| any other | existing | Preserve status/notes/timestamps unchanged |

Sync output (printed by the script):
```
📊 Progress sync — cases/ vs plans/negatives-progress.json
  + 3 new TCs added (yocto-009, yocto-010, linux-driver-009)
  ✓ 2 auto-promoted to done (manually authored outside command)
  ⚠ 0 regressions (negatives.py deleted)
  ⚠ 0 orphaned entries (case dir missing)

Totals: 189 pending / 33 done / 0 in-progress / 0 skipped / 0 orphaned
```

**`--init` flag**: destructive — delete progress file and rebuild from scratch.
Loses notes, timestamps, skip reasons. Only use if file is corrupted.

**`--sync` flag**: run sync, print diff, exit. No case selection or authoring.

### Step 2. Select next case

| Flag | Behavior |
|---|---|
| `--status` | Render progress table: category × (pending/in-progress/done/skipped), exit |
| `--case TC_ID` | Jump to TC_ID regardless of priority |
| `--category CAT` | Work all pending in CAT in priority order |
| none (default) | Pick first pending entry ordered by (priority, case_id) |

If no pending cases: print "All 186 cases have negatives. Run `uv run python scripts/verify_negatives_oracle.py` to verify oracle gate." and exit.

### Step 3. Load TC context + mark in-progress

Before presenting context, update the TC's progress entry:
- `status`: `in-progress`
- `started_at`: today's date `YYYY-MM-DD` if currently null (preserve earlier value on resume)

Then read and present:

For the chosen case, read and present:

1. `cases/{TC_ID}/metadata.yaml` — id, category, title, difficulty, platform, sdk_version.
2. `cases/{TC_ID}/checks/static.py` — extract all `check_name` strings.
3. `cases/{TC_ID}/checks/behavior.py` — extract all `check_name` strings.
4. `cases/{TC_ID}/reference/main.c` (or .bb/.conf/.yaml fallback) — full file.
5. If negatives.py already exists (in-progress recovery): show current state.

Output a summary:
```
=== TC: dma-002 ===
Category: dma | Difficulty: medium | Platform: native_sim
Title: DMA Scatter-Gather Configuration

Checks (static.py):    12 checks
Checks (behavior.py):  8 checks
Reference: reference/main.c (842 bytes)

(first 30 lines of reference/main.c preview)
```

### Step 4. Decision 1 — which checks to mutate (ASK USER)

Show the full check list with category:
```
Static checks:
  [1]  dma_header_included      — "zephyr/drivers/dma.h" import
  [2]  dma_config_struct        — struct dma_config present
  [3]  dma_block_config_struct  — struct dma_block_config present
  ...
Behavior checks:
  [13] callback_registered      — callback fn assigned to config
  [14] error_return_checked     — dma_config() return checked
  ...
```

Use **AskUserQuestion** with options:
- `all` — mutate every check (can be expensive; for short check lists only)
- `high-value` — LLM picks 3–5 checks that are hardest for LLMs (API-specific, structural, non-trivial)
- `let me pick` — user enters comma-separated IDs (e.g. "2,3,5,13")
- `skip this case` — mark skipped with reason; go to next TC

For `high-value`: LLM applies these heuristics:
- Prefer checks on API presence (`dma_config_called`) over mere header inclusion
- Prefer structural checks (`struct X defined`) over substring keywords
- Prefer checks covering known weak factors (concurrency, memory ordering, ISR safety)
- Cap at 5 to keep oracle runtime reasonable

### Step 5. For EACH selected check — propose mutation (LLM draft + user approve)

For each `check_name` to mutate:

5a. **LLM drafts** a mutation by inspecting the reference. Rules:
   - Prefer `str.replace()` over `re.sub` (readable, deterministic).
   - The replacement MUST produce code where the check fails.
   - The replacement MUST NOT fabricate text not present in the reference — check reference contents first.
   - Do NOT use `lambda code: ""` (evaluator rejects unchanged → empty as "did not change"; but empty is a cop-out, not a mutation).
   - Each mutation targets ONE check (unless two are inseparable, e.g. renaming a struct type breaks both `struct_defined` and `struct_used` — acceptable).

5b. **Factor ID tagging**: LLM picks the best-fit factor_id from `docs/LLM-EMBEDDED-FAILURE-FACTORS.md`. If no good match, use `null` and note it.

5c. **Preview what the mutation produces**: run the lambda against reference, show a 10-line diff around the change.

5d. **AskUserQuestion** with options:
   - `approve` — accept this mutation as drafted
   - `modify` — user provides replacement lambda or replacement strategy description; LLM rewrites
   - `skip` — drop this check from the negatives list (note why in progress file)
   - `abort TC` — stop working this TC; status stays in-progress for next session

### Step 6. Assemble negatives.py and run Oracle gate

After all selected checks are approved:

6a. Write `cases/{TC_ID}/checks/negatives.py` using this template:

```python
"""Negative tests for {title}.

Reference: cases/{TC_ID}/reference/main.c
Checks:    cases/{TC_ID}/checks/static.py, behavior.py

Authored: {YYYY-MM-DD} via /negatives command
"""


NEGATIVES = [
    {
        "name": "<short_mutation_name>",
        "description": "<what bug was seeded; why check must detect>",
        "mutation": lambda code: <transform>,
        "must_fail": ["<check_name>"],
        "factor_id": "<F#.# or null>",
    },
    # ...
]
```

6b. Run oracle:
```bash
uv run python scripts/verify_negatives_oracle.py --case {TC_ID}
```

6c. Handle oracle outcome:
- **PASS**: mark TC done in progress file, print commit-suggested message, go to Step 7.
- **FAIL**: show the `missed` entries. For each missed negative, **AskUserQuestion**:
  - `revise` — LLM re-drafts that specific mutation (return to Step 5a for that check)
  - `downgrade to should_fail` — move from `must_fail` to `should_fail` (subtle negative, not oracle-gated)
  - `remove` — drop this negative from the file
  - `abort TC` — save current state with status "in-progress", continue next session

Never loop more than 3 revision attempts per mutation. After 3, force downgrade/remove decision.

### Step 7. Commit suggestion + next-case prompt

After oracle PASS and progress file updated:

Print:
```
✅ {TC_ID}: {N} negatives landed, oracle PASS.

Staged changes:
  cases/{TC_ID}/checks/negatives.py
  plans/negatives-progress.json

Suggested commit:
  test(negatives): add mutation oracle for {TC_ID} ({N} mutations)

Next pending: {TC_ID_next} ({category}, priority {p})
```

**AskUserQuestion**:
- `continue` — proceed to next pending case (Step 2)
- `commit + continue` — run git commit with suggested message, then next case
- `stop` — exit; user will review and commit manually

---

## Rules (NON-NEGOTIABLE)

1. **Oracle is the gate.** No TC marked `done` without oracle PASS on all `must_fail` entries.
2. **User decides intent. LLM drafts mechanics.** Never pick which checks to mutate without asking. Never modify a lambda the user explicitly approved.
3. **Never author `should_fail` subtle negatives automatically.** These require semantic insight (e.g., volatile-vs-atomic). If the user wants subtle, prompt them for the bug description first.
4. **Preserve approved mutations across sessions.** If TC is `in-progress` with partial negatives, recovery re-reads the negatives.py file rather than re-asking already-approved mutations.
5. **Never commit automatically without `commit + continue`.** Default path is save-file-only; user reviews diff.
6. **Never mutate `reference/main.c` itself.** Only transform via lambda at oracle time.

## Known Pitfalls (inline reminders for LLM)

- **API variants** (`k_msleep` vs `k_sleep`, `printf` vs `printk` vs `LOG_INF`) — if the check uses `has_any_api_call` from check_utils, the mutation must remove ALL variants, not just one.
- **`#define` macros** — resolve before mutating (e.g. `#define SIZE 64`; replacing `64` alone won't trip a check that uses `resolve_define`).
- **Comment-embedded identifiers** — now that P2 `scoped_contains` exists, checks ignore comments; mutations that move API calls into comments no longer work.
- **Structural checks** — e.g. `dma_config_struct` looks for `struct dma_config`. Renaming the struct to `struct fake` is clean. Mutating only a field name is NOT — check still finds the struct keyword.

## Files This Command Touches

- `plans/negatives-progress.json` — state, always
- `cases/{TC_ID}/checks/negatives.py` — new file per TC
- Nothing else. Does NOT modify `static.py`, `behavior.py`, `reference/`, `metadata.yaml`.

## Completion Criteria (overall, across all invocations)

- `find cases -name negatives.py | wc -l` equals `find cases -name static.py | wc -l` (186/186 per current count, accounting for 1 TC without static.py if any).
- `uv run python scripts/verify_negatives_oracle.py` exits 0.
- `plans/negatives-progress.json` shows zero pending/in-progress entries.
