# /test — Run EmbedEval Benchmark

## Communication Protocol

- Be direct and matter-of-fact. No flattery, no preamble, no "Great question!"
- If reasoning is flawed, say so immediately with specific evidence
- Don't fold arguments on pushback — maintain position unless new evidence is presented
- Lead with concerns before agreement
- When you agree, explain WHY with specific reasoning — not just validation

Run LLM benchmark, save detailed results, generate failure analysis report.

## Usage

```
/test <model> [category] [--attempts N] [--retest-only] [--with-private]
```

**Examples:**
```
/test help                            # Show this help + category list
/test list                            # Show all categories with case counts
/test sonnet                          # All 179 public cases with Sonnet
/test sonnet kconfig                  # Only kconfig category
/test sonnet isr-concurrency          # Only isr-concurrency
/test sonnet security,ble             # Multiple categories (comma-separated)
/test sonnet --attempts 5             # 5 attempts per case (for pass@5)
/test sonnet kconfig --attempts 3     # Category + attempts
/test opus                            # All cases with Opus
/test haiku gpio-basic                # GPIO cases with Haiku
/test sonnet --retest-only            # Only re-run cases that changed since last test
/test haiku dma --retest-only         # Retest only changed DMA cases
/test sonnet --with-private           # Include 48 held-out private cases
/test haiku --with-private --retest-only  # Retest changed cases including private
```

## Arguments

- `$ARGUMENTS` is parsed as: `<model> [category] [--attempts N] [--retest-only] [--with-private]`
- Model: passed to `claude-code://<model>` (e.g., sonnet, opus, haiku, claude-sonnet-4-6)
- Category: optional, one of the 23 EmbedEval categories (comma-separated for multiple)
- Attempts: optional, default 1
- `--retest-only`: only run cases where TC changed since last test (uses test_tracker.json)
- `--with-private`: include 48 held-out private cases from `../embedeval-private/cases/`

## Implementation

Parse the arguments from `$ARGUMENTS`:

```
args = "$ARGUMENTS"
```

1. **Parse arguments**: Extract model, optional category, optional --attempts from args
2. **Run benchmark**: Execute `uv run embedeval run` with appropriate flags
3. **Show results**: Display leaderboard + failure report
4. **Save to memory**: Record key findings for TC improvement reference

### Step 0: Handle help/list

If first arg is `help` or `list`:

**`/test help`**: Show usage examples + run `uv run embedeval categories --cases cases/`

**`/test list`**: Run `uv run embedeval categories --cases cases/` and display the result.

Then STOP (don't run benchmark).

### Step 1: Parse and Run

```bash
# Parse model (first arg), category (second arg if not --), attempts (--attempts N)
# Example: "sonnet kconfig --attempts 3" → model=sonnet, category=kconfig, attempts=3

# Enable Docker-based compilation (L1/L2 layers)
export EMBEDEVAL_ENABLE_BUILD=docker

# Build the command
CMD="uv run embedeval run --model claude-code://{model} --cases cases/"
if category:
    # Support comma-separated: "kconfig,ble" → run with -c kconfig, then -c ble
    for each cat in categories:
        CMD += " -c {cat}"
if attempts:
    CMD += " --attempts {attempts}"
if --retest-only:
    CMD += " --retest-only"
if --with-private:
    CMD += " --private-cases ../embedeval-private/cases/ --include-private"

# Clean previous results for this model (skip if --retest-only to preserve tracker)
if not --retest-only:
    rm -rf results/claude-code*

# Run
{CMD} -v
```

### Step 2: Show Results

After the benchmark completes:
1. Read `results/LEADERBOARD.md` and display it
2. Read the run's `report.md` and display failure analysis
3. Show per-case details for failed cases

### Step 3: Analyze Failures

For each failed case:
1. Read the detailed JSON from `results/runs/DATE_MODEL/details/CASE.json`
2. Show which specific checks failed and why
3. Show the first 30 lines of generated code for context

### Step 3.5: Verify Results (False Result Detection)

After analyzing failures, run the verification script to cross-check results:

```bash
uv run python scripts/verify_results.py results/runs/{run_dir}/ --verbose
```

This script:
1. **Re-runs check scripts** on each case's generated code and compares with stored results
2. **Runs reference solutions** through the same checks — if reference fails = check script bug
3. Reports:
   - **FALSE NEGATIVES**: Reference solution fails a check → the check script has a bug
   - **DISCREPANCIES**: Stored result differs from re-run → data integrity issue

If issues are found:
- For FALSE NEGATIVES: Show the problematic check script and the reference code, explain the bug
- For DISCREPANCIES: Note them but these usually mean checks were updated after the run
- Summarize how many cases verified OK vs issues found

### Step 4: Summary Output

```markdown
## Benchmark Complete

**Model:** {model}
**Cases:** {total} ({passed} pass, {failed} fail)
**pass@1:** {rate}%

### Failed Cases
| Case | Layer | Failed Checks | Failure Pattern |
|------|-------|--------------|----------------|
| ... | ... | ... | ... |

### Key Findings
- {finding 1}
- {finding 2}

### TC Improvement Suggestions
- {if all pass: "consider harder cases"}
- {if specific pattern: "add more X-type checks"}

Detailed results: results/runs/{run_dir}/
```

## Notes

- Uses `claude-code://` provider (subscription, no API key needed)
- Results preserved in `results/runs/` with per-case JSONs
- History appended to `results/history.json`
- Test tracker at `results/test_tracker.json` — tracks per-case results with content hashes
- `results/TEST_RESULTS.md` — human-readable test result doc, auto-updated after each run
- `--retest-only` compares current case content hash to stored hash, only runs changed cases
- `--with-private` loads 48 held-out cases from `../embedeval-private/cases/` (separate private repo)
- Private cases repo: `git@github.com:Ecro/embedeval-private.git`
- Reference: `memory/llm-embedded-failure-patterns.md` for LLM failure patterns
