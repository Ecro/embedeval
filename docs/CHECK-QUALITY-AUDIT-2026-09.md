# Check Quality Audit — 2026-09

L3 (`static_heuristic`) checks were rewarding a *coding style* rather than
correctness. This audit came out of the Opus 5 run: it scored 5.9%p below
Claude Sonnet 5 while failing **more** L3 checks and **fewer** L0 checks, which
is not what a weaker model looks like.

## What was wrong

Of the 20 cases where Opus 5 failed L3 and Sonnet 5 passed, **20 were check
defects** — the submitted code was correct, sometimes more correct than the
reference idiom the check demanded. Four recurring classes:

### A. Ordering checks read comments as calls

`generated_code.find("boot_write_img_confirmed")` matches the API name inside a
header comment ("Unless the running firmware calls
`boot_write_img_confirmed()`, the image reverts"). That mention lands *before*
the real call, so every position comparison inverts. A model that documents its
work fails; a model that writes the same calls without comments passes.

Audit result: **97 case files** used raw `find()` on `generated_code`.

Fix: `check_utils.find_in_code()` — comments are blanked with spaces of equal
length (`blank_comments`), so matches inside comments disappear while offsets
stay valid for the 19 files that slice a window from the returned index.
BitBake recipes use `#` comments and embed `file://` URIs, so they use
`find_in_yocto()` instead.

Cases recovered: ota-001, ota-004, ota-005, ota-006, ota-008, power-mgmt-004,
security-005, networking-005.

### B. Literal idioms rejected better answers

| Case | Check demanded | Submission had |
|------|----------------|----------------|
| dma-008, watchdog-007 | `volatile` on the error flag | `atomic_t` + `atomic_set/get` — stronger, `volatile` alone gives no atomicity |
| timer-008 | `for (int i = 0; i < 10` (literal digit) | `i < MEASUREMENT_COUNT` |
| linux-userspace-006/007 | `open("/dev/spidev0.0"`, `"com.embedeval.Example"` inline | `#define SPI_DEVICE "..."` + `open(SPI_DEVICE` |
| adc-002 | `k_sleep` | `k_msleep` |
| power-mgmt-005 | `PM_DEVICE_ACTION_SUSPEND` ≥ 3 times | one loop over a three-device table |
| storage-012 | literal `K_MSEC(>=1000)` | `#define SAMPLE_PERIOD_MS 10000` + `k_sleep(K_TIMEOUT_ABS_MS(deadline))` |

Fixes: `expand_string_defines()` for string macros, `has_sleep_call()` for sleep
variants, identifier-or-literal loop bounds, and per-case acceptance of
`atomic_t` storage and table-driven iteration.

### C. Whole-file offsets break when code is factored

A re-arm helper defined above `main()` puts `uart_rx_enable` earlier in the file
than the `uart_callback_set` that actually runs first (uart-002); an
option-appending helper sits above the `coap_packet_init` call site
(networking-004); cleanup under `goto err_cdev_del:` labels is in no error block
at all (linux-driver-004); a reset delegated to `dfu_session_reset()` is not
literally in the disconnect handler (ble-006).

Fix: `ordered_in_same_function()` / `function_bodies()` judge order where it is
observable — inside one function — and per-case handling for the goto-label and
one-call-deep idioms.

### D. Checks that were simply wrong

- **linux-userspace-003**: required `StartLimitBurst`/`StartLimitIntervalSec` in
  `[Service]`. Since systemd v229 these keys belong in `[Unit]`; systemd 250
  **ignores** them under `[Service]`. The check was rewarding a unit file with
  no working rate limit. Now accepts either section.
- **yocto-006**: `no_manual_patch_in_do_compile` searched raw text, so a recipe
  commenting "patches are applied by do_patch() — never invoke `git apply`
  here" failed its own advice.

## Discrimination was not weakened

- Reference solutions: **219/219 pass** (unchanged).
- Mutation oracle (`scripts/verify_negatives_oracle.py`): **77/77 pass, 0 fail**.
- Cases without a `negatives.py` oracle were verified by seeding the bug by
  hand — wrong macro value, dropped table entry, loop bound cut to 2, sleep
  removed, all cleanup removed, reset call removed, `StartLimitBurst` deleted,
  `git apply` added to `do_compile` — **13/13 detected**.
- Two checks got *stronger*: power-mgmt-005 counted the
  `case PM_DEVICE_ACTION_SUSPEND:` label, so a two-device suspend still reached
  the ≥ 3 threshold; power-mgmt-004 counted `printk("pm_device_runtime_get
  failed")` as a call, inflating the get side.
- Re-scoring Opus 5's stored generations produced **0 pass→fail** changes and 22
  fail→pass.

## Effect on the Opus 5 result

Public slice (219 cases), same generations, four scoring passes:

| Scoring | pass@1 | L0 | L1 | L2 | L3 |
|---------|--------|----|----|----|----|
| aarch64 `native_sim` broken (superseded) | 55.3% | 12 | 53 | 0 | 33 |
| L2 auto-passing (superseded) | 68.0% | 11 | 4 | 0 | 55 |
| board + overlay + L2 gate fixed — **what the first 267-case publish used** | 63.0% | 11 | 4 | 20 | 46 |
| **check defects fixed (this audit)** | **73.1%** | 11 | 4 | 20 | 24 |

The first two rows were environment bugs (see the 2026-09-08 entries in
CLAUDE.md); the last two differ only in check quality, on identical code.

## Published 267-case result

The full set was re-published with the fixed checks: the 219 public cases
re-scored from their stored generations, the 48 held-out cases generated fresh
in the same environment.

| Slice | pass@1 | Cases |
|-------|--------|-------|
| public | 73.1% | 160/219 |
| private (held-out) | 56.2% | 27/48 |
| **total** | **70.0%** | **187/267** |

quality (L0+L3) 83.5%, CI [64.3%, 75.2%]. Layers: L0 15, L1 16, L2 20, L3 29
failures. `scripts/verify_results.py`: 267/267 verified, no false results.

### Leaderboard asymmetry — read before comparing

Only `claude-code://claude-opus-5` is scored with the fixed checks.
`claude-sonnet-5`, `sonnet` and `haiku` are replayed from `test_tracker.json`
verdicts produced by the **old** checks and cannot be re-scored: per-case detail
JSONs are gitignored (`results/runs/*/details/`), so those generations no longer
exist. Their numbers are a floor — every defect class above depressed them too,
wherever their code hit it. A symmetric leaderboard needs them re-generated
(`uv run embedeval run --model claude-code://<model>`); re-scoring is only
possible where a run's `details/` still exists.

## The private slice is depressed by broken cases, not by the model

Of Opus 5's 16 private-slice L1 failures, **12 are cases whose own reference
solution does not build in this environment** — no model can pass them:

| Cases | Cause |
|-------|-------|
| sensor-driver-009/010, spi-i2c-009, uart-003 | nrf52840dk DT alias/node absent (`__device_dts_ord_DT_N_ALIAS_*` undeclared) |
| ota-010 | `zephyr/dfu/dfu_target.h` missing — DFU module not in the image |
| ble-009/010, gpio-basic-010, networking-009, power-mgmt-009, storage-009, isr-concurrency-009 | link failure |

Only 16 of the 28 compilable private cases have a building reference
(`scripts/verify_references_build.py --cases ../embedeval-private/cases`), and
**all 12** of Opus 5's private-slice L1 failures are exactly those cases — it
made no genuine compile error in the held-out set. The same 12 penalise every
model, so they do not change the ranking, but the private slice should not be
read as a capability number until they are fixed or marked `l1_skip`.

Opus 5's four genuine compile failures are all in the **public** slice —
isr-concurrency-004/006/011 and threading-012, whose references build fine here
(10/10 isr-concurrency and 12/12 threading references OK). threading-012 fails
with `undefined reference to __device_dts_ord_19`: the code references a
devicetree node that its own overlay does not define.

An earlier revision of this document attributed those four to the private slice.
They came from tracker-merged stubs in a partial-run archive (the same stub
problem described below), not from private cases; the corrected attribution is
above.

## Remaining L3 failures (24)

Not investigated in this audit — both Opus 5 and Sonnet 5 fail most of them, so
they do not affect model ranking, but they are the next candidates for review:

ble-008, dma-005, esp-wifi-001, isr-concurrency-003, linux-driver-006,
linux-driver-011, linux-driver-016, linux-userspace-001, networking-kernel-002,
networking-kernel-003, networking-kernel-004, ota-011, ota-swupdate-001,
ota-swupdate-002, ota-swupdate-004, stm32-i2c-001, stm32-spi-001,
stm32-uart-001, storage-008, storage-013, threading-001, timer-007, yocto-005,
yocto-007

## Authoring rules that follow from this

1. Ordering checks: `find_in_code()`, never `generated_code.find()`. For
   recipes, `find_in_yocto()`.
2. Order across functions is not observable in text — use
   `ordered_in_same_function()` and accept the factored shape.
3. Never demand a literal where a macro is legal: `expand_string_defines()` for
   strings, `resolve_define()`/`extract_numeric()` for numbers.
4. Never demand one API spelling when the platform has equivalents
   (`has_sleep_call()`, `has_any_api_call()`).
5. `volatile` and `atomic_t` are both valid for an ISR/thread flag; atomics are
   usually better.
6. Count call sites (`api\s*\(`), not token occurrences — labels, log strings
   and comments inflate counts.
7. Every relaxation needs a seeded bug proving the check still fails it.
   Prefer adding it to `negatives.py` so the oracle guards it in CI.

## Two infrastructure bugs found while re-scoring

Both produced plausible-looking wrong numbers rather than errors, which is the
failure mode this repo can least afford.

- **Tracker-merged detail stubs.** A partial run (`--visibility private`, 48
  cases) archived per-case details for all 267 — the 219 not re-run were
  synthesised by `cli._build_comprehensive_results` from stored
  `passed`/`failed_layer` and carry `generated_code=""`. Copied into a re-score
  input set they overwrote the real details, and re-scoring empty code produced
  pass@1 10.1% with 223 L0 failures that looked like a model collapse.
  `generate_run_archive` no longer writes detail files for results with no
  submission, and `rescore_run.py` aborts on such a record instead of scoring
  it.
- **Leaked runtime containers.** L2 runs `west build -t run`, and embedded
  firmware loops forever. `subprocess`'s timeout killed only the local
  `docker run` client while the container kept executing; one leak per runtime
  case accumulated past 100 containers until the host ran out of memory and
  killed the benchmark process mid-run. The container command now carries
  `timeout --signal=KILL <RUNTIME_TIMEOUT>` so it self-terminates and `--rm`
  reaps it; exit codes 124/137 count as a normal firmware stop. Side effect:
  re-scoring got roughly 4x faster once builds stopped competing with orphans.
