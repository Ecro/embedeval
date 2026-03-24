# /test — Run EmbedEval Benchmark

Run LLM benchmark, save detailed results, generate failure analysis report.

## Usage

```
/test <model> [category] [--attempts N]
```

**Examples:**
```
/test sonnet                          # All 200 cases with Sonnet
/test sonnet kconfig                  # Only kconfig category (10 cases)
/test sonnet isr-concurrency          # Only isr-concurrency
/test sonnet security,ble             # Multiple categories (comma-separated)
/test sonnet --attempts 5             # 5 attempts per case (for pass@5)
/test sonnet kconfig --attempts 3     # Category + attempts
/test opus                            # All cases with Opus
/test haiku gpio-basic                # GPIO cases with Haiku
```

## Arguments

- `$ARGUMENTS` is parsed as: `<model> [category] [--attempts N]`
- Model: passed to `claude-code://<model>` (e.g., sonnet, opus, haiku, claude-sonnet-4-6)
- Category: optional, one of the 20 EmbedEval categories (comma-separated for multiple)
- Attempts: optional, default 1

## Implementation

Parse the arguments from `$ARGUMENTS`:

```
args = "$ARGUMENTS"
```

1. **Parse arguments**: Extract model, optional category, optional --attempts from args
2. **Run benchmark**: Execute `uv run embedeval run` with appropriate flags
3. **Show results**: Display leaderboard + failure report
4. **Save to memory**: Record key findings for TC improvement reference

### Step 1: Parse and Run

```bash
# Parse model (first arg), category (second arg if not --), attempts (--attempts N)
# Example: "sonnet kconfig --attempts 3" → model=sonnet, category=kconfig, attempts=3

# Build the command
CMD="uv run embedeval run --model claude-code://{model} --cases cases/"
if category:
    CMD += " -c {category}"  # for each category if comma-separated, run separately
if attempts:
    CMD += " --attempts {attempts}"

# Clean previous results for this model
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
- Reference: `memory/llm-embedded-failure-patterns.md` for LLM failure patterns
