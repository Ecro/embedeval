# EmbedEval

Professional-grade LLM benchmark for embedded firmware development (Zephyr RTOS, FreeRTOS, ESP-IDF, STM32 HAL, Linux kernel drivers, Yocto/Embedded Linux).

## Project Context

- **Vault Project:** embedeval
- **Repository:** /home/noel/embedeval
- **TODO Sync:** Enabled
- **GitHub:** https://github.com/Ecro/embedeval
- **Private Cases:** https://github.com/Ecro/embedeval-private (48 held-out TCs)

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.12+ |
| Package Manager | uv | latest |
| LLM Client | litellm | latest |
| CLI | typer | latest |
| Models | pydantic | v2 |
| Container | Docker | latest |
| Target SDKs | Zephyr RTOS, FreeRTOS, ESP-IDF, STM32 HAL, Linux kernel, Yocto | various |
| CI | GitHub Actions | - |

## Project Structure

```
embedeval/
├── src/embedeval/       # Core library
│   ├── models.py        # Pydantic models (EvalResult, BenchmarkReport, etc.)
│   ├── evaluator.py     # 5-layer evaluation pipeline (L0-L4)
│   ├── runner.py        # Benchmark runner orchestration
│   ├── scorer.py        # Score aggregation (pass@1, pass@5, layer rates)
│   ├── reporter.py      # JSON + Markdown report generation
│   ├── llm_client.py    # LiteLLM wrapper with retry logic
│   └── cli.py           # Typer CLI (run, list, validate, report)
├── cases/               # Public test cases (179 TCs)
│   ├── kconfig-001/
│   ├── device-tree-001/
│   └── isr-concurrency-001/
│                        # Private cases in separate repo: ../embedeval-private/cases/
├── tests/               # pytest test suite
├── docs/                # METHODOLOGY.md, CONTRIBUTING.md
└── .github/workflows/   # CI, case validation, benchmark dispatch
```

## Commands

| Command | Purpose |
|---------|---------|
| `uv run pytest` | Run all tests |
| `uv run ruff check src/ tests/` | Lint |
| `uv run ruff format src/ tests/` | Format |
| `uv run mypy src/` | Type check |
| `uv run embedeval --help` | CLI help |
| `uv run embedeval list --cases cases/` | List cases |
| `uv run embedeval validate --cases cases/` | Validate cases |
| `uv run embedeval run ... --private-cases ../embedeval-private/cases/ --include-private` | Include private cases |

## Available Workflow Commands

- `/research` - Gather best practices, explore options
- `/myplan [task]` - Analyze, design, and plan implementation
- `/execute [task]` - Implement and test
- `/review [task]` - Code review and quality check
- `/wrapup [task]` - Finalize, commit, PR, and complete

## Documentation Auto-Sync (MANDATORY)

**At `/wrapup` or before any commit that changes `cases/`, `src/`, or `tests/`:**

```bash
uv run python scripts/sync_docs.py
```

This auto-updates:
- `docs/METHODOLOGY.md` — TC count, platform/difficulty distribution, negatives count
- `README.md` — test count, module count, case count, insights count

**Always commit the updated docs together with code changes.**

If `sync_docs.py` output shows "already up to date", no action needed.

## 23 Evaluation Categories

Platform-agnostic: `gpio-basic`, `uart`, `adc`, `pwm`, `spi-i2c`, `dma`, `isr-concurrency`, `threading`, `timer`, `sensor-driver`, `networking`, `ble`, `security`, `storage`

System-level: `kconfig`, `device-tree`, `boot`, `ota`, `power-mgmt`, `watchdog`

Platform-specific: `yocto`, `linux-driver`, `memory-opt`

## 5-Layer Evaluation Architecture

- **L0 Static**: Pattern matching, required includes, structure checks
- **L1 Compile**: Docker-based SDK compilation (west build, idf.py, make)
- **L2 Runtime**: QEMU/native_sim execution with timeout
- **L3 Behavioral**: Output validation against expected patterns
- **L4 Mutation**: Robustness testing with code mutations

## Boundaries

- NO placeholder code or TODO comments
- NO skipping tests
- NO adding dependencies without justification
- All new test cases must include reference solutions that pass all layers

## Quality Gates (MANDATORY before commit)

1. **Self-review `git diff`** — Read every changed line before committing. Check:
   - API contracts: does the function I'm calling return what I expect?
   - Redundant calls: am I calling a function that was already called upstream?
   - Edge cases: what happens with empty input, None, malformed data?

2. **New feature = new tests** — Every new CLI option, module, or code path needs at least 3 tests:
   - Happy path
   - Edge case (empty, None, boundary)
   - Error case (invalid input, timeout)

3. **Check function signatures before calling** — Read the function definition before using it.
   Don't assume what it returns. Don't wrap it in "defensive" double-processing.

## Pre-commit Hook (one-time setup per clone)

CI's Lint job (`ruff format --check src/` + `ruff check src/`) is mirrored in
`.githooks/pre-commit`. Activate it once per clone:

```bash
git config core.hooksPath .githooks
```

`core.hooksPath` is a local-only git config, so it is **not** inherited on clone
— every fresh clone must run the command above, or CI will keep catching
format drift after push.

## Learned Corrections

### 2026
- 2026-09-08: [embedeval] Running the benchmark on an **aarch64 host** needs `EMBEDEVAL_NATIVE_SIM_BOARD=native_sim/native/64` — the plain 32-bit `native_sim` target aborts at CMake configure ("target native_sim/native/64 instead") because the arm64 Zephyr CI image has no 32-bit toolchain. Two follow-on traps came with the remap: (1) Zephyr resolves board overlays as `boards/<board with / as _>.overlay`, so `boards/native_sim.overlay` is silently ignored for the qualified board and every DT node vanishes — `_alias_native_sim_overlay` copies it to `boards/native_sim_native_64.overlay`; (2) L2's `board != "native_sim"` test classified the remapped board as hardware and **auto-passed runtime for ~60 cases** — use `_is_native_sim_board()`. Symptom to watch for: a model showing 0 L2 failures where another model had ~18.
- 2026-09-08: [embedeval] L3 (`static_heuristic`) pass rates are **not** model-comparable until the failures are inspected — 8/8 spot-checked cases where opus5 failed L3 but claude-sonnet-5 passed were check artifacts, not code defects. Two recurring root causes: (a) ordering checks using `generated_code.find(...)` on **raw text including comments** invert when a model documents the API in a header comment (ota-001 `check_before_confirm`, power-mgmt-004, ota-006, yocto-006 `no_manual_patch_in_do_compile` tripped by a comment saying "never invoke patch here"); (b) checks demanding a literal idiom reject valid or better variants — `atomic_t`+`atomic_set` instead of `volatile` (dma-008, watchdog-007), `#define` constants instead of literal digits (timer-008 `bounded_loop`), `open(SPI_DEVICE, ...)` instead of `open("/dev/spidev0.0", ...)` (linux-userspace-006). Fix ordering checks with `scope='code_only'` and resolve macros before matching.
- 2026-09-08: [embedeval] `scripts/sync_docs.py` counts cases from `cases/` **plus** `../embedeval-private/cases/`; without the private clone it silently rewrote METHODOLOGY.md to "Total cases 219" and "Private held-out 0 cases (0%)". Since CLAUDE.md mandates running it before every commit that touches `cases/`/`src/`/`tests/`, that regression was one `git commit -a` away from shipping. The script now aborts unless `--allow-missing-private` is passed.
- 2026-09-08: [embedeval] `claude -p --output-format json` returns a single result **object** (CLI 2.1.x), not the list of events the parser assumed. Iterating a dict yields key strings → `AttributeError: 'str' object has no attribute 'get'`, which the runner's blanket `except Exception` converted into a silent FAIL@L0 for *every* case — a benchmark run that burns real API spend and reports 0% instead of crashing. `_parse_claude_code_json` now accepts both shapes and flags `is_error`/non-success `subtype` for retry. Lesson: any provider-output parser needs a unit test pinning the payload shape (there were none for `_call_claude_code`), and a run whose first ~10 cases all fail at the same layer must be killed and diagnosed, not left running.
- 2026-04-19: [embedeval] udev rule keys `ATTR{foo}` (singular) and `ENV{foo}` are DUAL-USE — they support both `==` match AND `=`/`+=` assignment (writing to sysfs attribute / setting env var). `ATTRS` (plural, walks parent chain) is strictly match-only — the kernel cannot write to a parent device attribute. Any match-only-vs-assign-only classification helper must exclude dual-use keys. Prior incident: Phase B `_UDEV_MATCH_ONLY_KEYS` initially included `ATTR`, causing false positives on valid `ATTR{brightness}="200"` style rules until `/review` caught it.
- 2026-04-19: [embedeval] TC prompts must NOT state byte counts / struct sizes / numeric constants that the reference implementation doesn't actually match. Writing "Push a 48-byte event struct" when the reference declares a ~24-byte struct produces a silent spec/reference drift — discriminating value is lost either way (LLM matching the reference fails the stated spec; LLM matching the spec fails the check). Either verify the numeric claim matches the reference, or phrase the requirement qualitatively + add a field-completeness check. Prior incident: linux-userspace-008 prompt claimed "48-byte" but reference was 24 bytes; fix was to drop the numeric claim and add `event_struct_has_pid_and_comm_fields` check.
- 2026-04-19: [embedeval] TC check regexes must NOT hardcode variable names from the reference. Extract the LHS from the assignment pattern (`(\w+)\s*=\s*kmalloc\(`) and then search with that captured name — never inline the reference's variable letter (`r`, `dev`, `priv`, `e`, `task`). A correct LLM submission using `rec`, `record`, `entry`, `event`, `t` silently fails checks that anchor on the reference spelling. **Recurring incidents**: linux-driver-009 (`isr_null_checks_alloc_result` hardcoded `r`), linux-userspace-007 (`error_propagation_r_lt_0` hardcoded `r`), linux-userspace-008 (`ringbuf_reserve_null_checked` hardcoded `e`, `no_raw_task_struct_deref` hardcoded `task`) — all caught only by `/review`. When authoring any check that matches `<var>->` / `if (!<var>)` / `if (<var> < 0)`, extract the LHS first via `(\w+)\s*=\s*<factory-call>`; don't inline a single-letter anchor.
- 2026-04-19: [embedeval] Implicit-prompt discipline — prompts authored for TC families that measure the 35%p explicit/implicit gap must NOT name target APIs (`devm_kzalloc`, `IRQF_ONESHOT`, `kthread_run`, `workqueue`, `INIT_WORK`, `IS_ERR`, `PTR_ERR`, `GFP_ATOMIC`). Describe the behavior / constraint / kernel facility class instead. Yocto recipes (directive-heavy: PACKAGECONFIG, FILESEXTRAPATHS, BBFILE_COLLECTIONS) and DTS preamble (`/dts-v1/;`) are category-level exempt — the directive names ARE the language surface being tested. Prior incident: 4 linux-driver TCs shipped with API names in prompts (015 named `devm_kzalloc` + `devm_platform_ioremap_resource` outright) until `/review` caught the violation.
- 2026-04-19: [embedeval] Public TC references/prompts/checks must NOT carry vendor prefixes from `~/EDGE/sources/meta-qcells-*` (the local BSP layer) into `cases/`. Use neutral identifiers like `vendor,*` or `embedeval,*` for DT compatible strings and driver names. Prior incident: linux-driver-013 pilot shipped `qcells,example-sensor` DT compatible + `qcells-example-sensor` driver name into public repo until `/review` caught it. Kernel/Yocto *versions* may track the user's BSP (5.15, kirkstone) — only *namespaces* must stay neutral.
- 2026-04-19: [embedeval] `scoped_contains` default scope is `stripped` (strips comments AND string literals), NOT what REQ-03 scope migration wants. When converting `"x" in generated_code` to `scoped_contains`, ALWAYS pass `scope='code_only'` explicitly — otherwise `#include "driver/gpio.h"` and similar patterns that match inside string literals break silently.
- 2026-04-19: [embedeval] `cases/` is now 2-level: `cases/<sdk>/<case-id>/metadata.yaml` with 5 SDK buckets (zephyr, embedded-linux, freertos, esp-idf, stm32-hal). Use `embedeval.runner.iter_case_dirs(cases_root)` in scripts instead of `cases_root.iterdir()`; the helper walks both SDK buckets and the legacy flat layout for transitional safety. Every `metadata.yaml` carries a required `sdk:` field matching its parent bucket dir.
- 2026-04-19: [embedeval] SDK-bucket migration rewrote every `metadata.yaml` (added `sdk:`, reordered keys). This changes `case_git_hash` for all 185 public + 48 private cases, so the first post-migration `--retest-only` run will flag 100% of cases for retest regardless of tracker state. Intentional — the hash reflects the new on-disk bytes. Callers managing API spend should expect one full re-run and can re-snapshot the tracker with a plain `run` on a cheap model first.
- 2026-04-19: [embedeval] `strip_comments` is C-specific and mis-treats `file://`, `git://`, `http://` in Yocto .bb refs as `//` line comments, silently deleting identifiers after the URL. Use `scope='raw'` for Yocto cases; .bb files use `#` comments which strip_comments doesn't touch anyway.
- 2026-04-19: [embedeval] Run-scoped artifacts (per_check_metrics.json, per-model details) MUST go under `run_dir/` not `output_dir/` — an n=3 benchmark invocation silently overwrites flat-root artifacts, clobbering n1 and n2 data. Contract consumers like Hiloop rely on `runs/<dir>/<artifact>` path convention.
- 2026-04-18: [embedeval] Context pack "harmful" effects are 2-class — real attention trade-off vs benchmark check brittleness. N=14 Haiku trade-off analysis: 1/2 harmful cases were dma_config vs dma_configure (valid API variants the check rejects), not actual capability degradation. Always inspect generated code before concluding pack hurt; check brittleness can masquerade as pack failure. See REVIEW-context-quality-mode Addendum 2.
- 2026-04-18: [embedeval] Context pack effect on LLM is NOT uniformly positive — empirical Haiku 5-TC × n=3 showed cases with +100pp, −100pp, and 0pp swings (mechanism: pack adds missing principles in some cases, distracts attention from structural correctness in others). Don't assume "expert > bare" in docs/UX; surface per-case effect direction explicitly. R8 in PLAN-context-quality-mode.md.
- 2026-04-18: [embedeval] Pydantic v2 plain `@property` is NOT serialized by `model_dump_json()` — use `@computed_field` + `@property` for derived fields exposed in JSON output. Plain `@property` works in code but silently drops from JSON, breaking CI integrations.
- 2026-04-18: [embedeval] When adding an optional CLI flag (e.g. `--context-pack`), audit ALL scenario branches AND every other subcommand for plumbing gaps. `run --scenario bugfix` and `agent` both silently dropped the flag in initial PR; fix is to either thread it through or reject the combination at the CLI boundary, never accept-and-ignore.
- 2026-03-30: [embedeval] L1/L2 must skip for non-compilable cases (no CMakeLists.txt) — kconfig/device-tree/boot/yocto generate config fragments, not C code
- 2026-03-30: [embedeval] L4 mutation lambdas must not hardcode literal values from reference — LLM may use #define macros instead
- 2026-03-30: [embedeval] Build error logs: extract `error:` lines first, then tail — raw truncation loses the actual compiler diagnostics
- 2026-03-29: [embedeval] Check regexes must accept API variants (k_msleep=k_sleep, printf=printk=LOG_*) — use shared check_utils utilities
- 2026-03-29: [embedeval] Check regexes must resolve #define macros — use extract_numeric/resolve_define, not bare \d+ patterns
- 2026-03-29: [embedeval] Use find("func(") not find("func") — avoids matching typedefs like esp_timer_create_args_t
- 2026-03-29: [embedeval] Content hashing must use file bytes, not st_mtime — mtime resets on git clone
- 2026-03-26: [embedeval] call_model() already extracts code — don't call _extract_code() again on generated_code
- 2026-03-26: [embedeval] L0 check failures have error=None, details in .details — must include failed check details in feedback prompts
- 2026-03-26: [embedeval] String date comparison needs format validation — use date.fromisoformat() before comparing
- 2026-03-25: [embedeval] Docker Zephyr CI image has toolchain only, not Zephyr source — need west init + west update
- 2026-03-25: [embedeval] native_sim has no DMA/WDT/sensor nodes — need DT overlays or nrf52840dk board target
- 2026-03-24: [embedeval] L3 "behavioral_assertion" is actually regex pattern matching — renamed to "static_heuristic"
